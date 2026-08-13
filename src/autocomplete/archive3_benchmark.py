"""Trustworthy, reproducible benchmark runner for the complete Archive3 corpus."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass, fields
import csv
from datetime import datetime, timezone
import gc
import hashlib
import json
from math import ceil
import os
from pathlib import Path
import platform
import random
import re
import subprocess
import sys
from time import perf_counter_ns
import tracemalloc
from statistics import fmean, median, stdev
from typing import Iterable

from src.models.match_candidate import MatchCandidate
from src.models.prepared_sentence import PreparedSentence
from src.algorithms.bi_anchor_search_algorithm import BiAnchorSearchAlgorithm
from src.algorithms.bi_anchor_search_stats import BiAnchorSearchStats
from src.algorithms.naive_search_algorithm import NaiveSearchAlgorithm
from src.algorithms.naive_search_stats import NaiveSearchStats
from src.algorithms.qgram_search_algorithm import QGramSearchAlgorithm
from src.algorithms.qgram_search_stats import QGramSearchStats
from src.algorithms.qgram_trie_search_algorithm import QGramTrieSearchAlgorithm
from src.builders.bi_anchor_structure_builder import BiAnchorStructureBuilder
from src.builders.naive_structure_builder import NaiveStructureBuilder
from src.builders.qgram_structure_builder import QGramStructureBuilder
from src.structures.bi_anchor_search_structure import BiAnchorSearchStructure
from src.structures.qgram_search_structure import QGramSearchStructure
from src.autocomplete.preparation import DataPreparer


ALGORITHM_IDS = (
    "naive",
    "qgram_verifier",
    "qgram_tree_hybrid",
    "bi_anchor",
)

FREQUENCY_BANDS = ("p50", "p75", "p90", "p95", "p99")
SIGNATURE_MODULUS = 1 << 128


@dataclass(frozen=True, slots=True)
class Archive3Query:
    query_id: str
    query_text: str
    normalized_query: str
    query_length: int
    length_bucket: str
    primary_category: str
    categories: tuple[str, ...]
    source_sentence_id: int | None
    source_path: str | None
    source_start: int | None
    mutation_type: str | None
    frequency_band: str | None
    qgram_frequency: int | None


@dataclass(slots=True)
class BuiltAlgorithm:
    algorithm_id: str
    algorithm: object
    structure: object | None
    owns_structure: bool = False

    def search(self, query: str) -> list[MatchCandidate]:
        if self.owns_structure:
            return self.algorithm.search(query)  # type: ignore[attr-defined,no-any-return]
        return self.algorithm.search(query, self.structure)  # type: ignore[attr-defined,no-any-return]


def rotated_algorithm_order(offset: int) -> tuple[str, ...]:
    rotation = offset % len(ALGORITHM_IDS)
    return ALGORITHM_IDS[rotation:] + ALGORITHM_IDS[:rotation]


def _build_algorithm(
    algorithm_id: str,
    sentences: tuple[PreparedSentence, ...],
    q: int,
) -> BuiltAlgorithm:
    if algorithm_id == "naive":
        return BuiltAlgorithm(
            algorithm_id,
            NaiveSearchAlgorithm(),
            NaiveStructureBuilder().build(sentences),
        )
    if algorithm_id == "qgram_verifier":
        return BuiltAlgorithm(
            algorithm_id,
            QGramSearchAlgorithm(),
            QGramStructureBuilder(q=q).build(sentences),
        )
    if algorithm_id == "qgram_tree_hybrid":
        algorithm = QGramTrieSearchAlgorithm()
        algorithm.Q = q
        algorithm.build(sentences)
        return BuiltAlgorithm(algorithm_id, algorithm, None, owns_structure=True)
    if algorithm_id == "bi_anchor":
        return BuiltAlgorithm(
            algorithm_id,
            BiAnchorSearchAlgorithm(),
            BiAnchorStructureBuilder(q=q).build(sentences),
        )
    raise ValueError(f"unknown algorithm: {algorithm_id}")


def structure_metrics(
    algorithm_id: str,
    runtime: BuiltAlgorithm,
) -> dict[str, int]:
    if algorithm_id == "naive":
        sentences = runtime.structure.sentences  # type: ignore[union-attr]
        return {"sentences": len(sentences)}
    if algorithm_id == "qgram_verifier":
        structure = runtime.structure
        if not isinstance(structure, QGramSearchStructure):
            raise TypeError("invalid positional Q-Gram runtime")
        indexes = structure.indexes()
        posting_lengths = [
            len(postings)
            for _size, index in indexes
            for postings in index.values()
        ]
        return {
            "sentences": len(structure.sentences),
            "gram_keys": sum(len(index) for _size, index in indexes),
            "posting_lists": sum(len(index) for _size, index in indexes),
            "posting_entries": sum(
                len(postings)
                for _size, index in indexes
                for postings in index.values()
            ),
            "largest_posting_list": max(posting_lengths, default=0),
            "median_posting_length": int(median(posting_lengths)) if posting_lengths else 0,
            "p95_posting_length": int(nearest_rank(posting_lengths, 95)),
        }
    if algorithm_id == "qgram_tree_hybrid":
        algorithm = runtime.algorithm
        stack = [algorithm._root]  # type: ignore[attr-defined]
        nodes = words = occurrences = 0
        while stack:
            node = stack.pop()
            nodes += 1
            if node.word is not None:
                words += 1
                occurrences += len(node.occurrences)
            stack.extend(node.children.values())
        return {
            "trie_nodes": nodes,
            "unique_words": words,
            "word_occurrences": occurrences,
            "qgram_keys": len(algorithm._qgrams),  # type: ignore[attr-defined]
            "qgram_references": sum(
                len(items) for items in algorithm._qgrams.values()  # type: ignore[attr-defined]
            ),
        }
    if algorithm_id == "bi_anchor":
        structure = runtime.structure
        if not isinstance(structure, BiAnchorSearchStructure):
            raise TypeError("invalid Bi-Anchor runtime")
        index_stats = structure.build_stats.index
        base = {
            field.name: getattr(index_stats, field.name)
            for field in fields(index_stats)
            if field.name != "per_q"
        }
        lookup = structure.seed_lookup
        frequencies = [
            lookup.frequency(seed)
            for q in structure.q_values
            for seed in lookup.indexed_seeds(q)  # type: ignore[attr-defined]
        ]
        return {
            **base,
            "indexed_q_values": list(structure.q_values),
            "largest_expansion_frequency": max(frequencies, default=0),
            "median_seed_frequency": int(median(frequencies)) if frequencies else 0,
            "p95_seed_frequency": int(nearest_rank(frequencies, 95)),
            "p99_seed_frequency": int(nearest_rank(frequencies, 99)),
        }
    raise ValueError(f"unknown algorithm: {algorithm_id}")


def build_algorithms(
    sentences: tuple[PreparedSentence, ...],
    *,
    repetitions: int = 3,
    q: int = 3,
) -> tuple[dict[str, dict[str, object]], dict[str, BuiltAlgorithm]]:
    """Independently rebuild every runtime and retain the final repetition."""
    if repetitions < 1:
        raise ValueError("repetitions must be positive")
    results: dict[str, dict[str, object]] = {}
    runtimes: dict[str, BuiltAlgorithm] = {}
    for algorithm_id in ALGORITHM_IDS:
        samples: list[int] = []
        peaks: list[int] = []
        retained: list[int] = []
        runtime: BuiltAlgorithm | None = None
        for _ in range(repetitions):
            runtime = None
            gc.collect()
            tracemalloc.start()
            started = perf_counter_ns()
            runtime = _build_algorithm(algorithm_id, sentences, q)
            elapsed = perf_counter_ns() - started
            current_bytes, peak_bytes = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            samples.append(elapsed)
            peaks.append(peak_bytes)
            retained.append(current_bytes)
        assert runtime is not None
        runtimes[algorithm_id] = runtime
        results[algorithm_id] = {
            "algorithm_id": algorithm_id,
            "q": q if algorithm_id != "naive" else None,
            "build_repetitions": repetitions,
            "build_time_ns": summarize_samples(samples),
            "peak_memory_bytes": max(peaks),
            "peak_memory_samples_bytes": peaks,
            "retained_memory_bytes": retained[-1],
            "retained_memory_samples_bytes": retained,
            "structure_metrics": structure_metrics(algorithm_id, runtime),
        }
    return results, runtimes


def _default_repetitions(query: Archive3Query) -> dict[str, int]:
    # Positional Q-Gram and Bi-Anchor intentionally fall back to exhaustive
    # search below two non-overlapping q-grams, so they are not "cheap" there.
    return {
        "naive": 3,
        "qgram_verifier": 3 if query.query_length == 1 else 10,
        "qgram_tree_hybrid": 10,
        "bi_anchor": 3 if query.query_length < 6 else 10,
    }


def _work_metrics(
    algorithm_id: str,
    runtime: BuiltAlgorithm,
    query: str,
) -> dict[str, object]:
    if algorithm_id == "naive":
        stats = NaiveSearchStats()
        matches = NaiveSearchAlgorithm(stats=stats).search(query, runtime.structure)  # type: ignore[arg-type]
        return {**asdict(stats), "result_count": len(matches)}
    if algorithm_id == "qgram_verifier":
        stats = QGramSearchStats()
        matches = QGramSearchAlgorithm(stats=stats).search(query, runtime.structure)  # type: ignore[arg-type]
        return {**asdict(stats), "result_count": len(matches)}
    if algorithm_id == "qgram_tree_hybrid":
        algorithm = runtime.algorithm
        candidates = algorithm._get_candidates(query)  # type: ignore[attr-defined]
        qgrams = max(0, len(query) - algorithm.Q + 1)  # type: ignore[attr-defined]
        matches = runtime.search(query)
        return {
            "query_count": 1,
            "query_qgrams": qgrams,
            "candidate_words": len(candidates),
            "candidate_occurrences": sum(
                len(node.occurrences) for node in candidates
            ),
            "verifier_calls": len(candidates),
            "result_count": len(matches),
            "result_cap": 2000,
        }
    if algorithm_id == "bi_anchor":
        stats = BiAnchorSearchStats()
        matches = BiAnchorSearchAlgorithm(stats=stats).search(query, runtime.structure)  # type: ignore[arg-type]
        payload = asdict(stats)
        selected = payload.pop("last_selected_seeds")
        payload["last_selected_seeds"] = (
            list(selected) if selected else None
        )
        return {**payload, "result_count": len(matches)}
    raise ValueError(f"unknown algorithm: {algorithm_id}")


def _exact_small_actual_diff(
    oracle: list[MatchCandidate],
    actual_counter: Counter[tuple[object, ...]],
) -> dict[str, object]:
    """Exact FP/FN counts while retaining only the bounded actual multiset."""
    remaining = actual_counter.copy()
    intersection = 0
    for match in oracle:
        key = _candidate_key(match)
        if remaining[key] > 0:
            remaining[key] -= 1
            intersection += 1
    unexpected = sum(remaining.values())
    missing = len(oracle) - intersection
    sample = [list(key) for key, count in remaining.items() if count][:5]
    return {
        "missing_count": missing,
        "unexpected_count": unexpected,
        "unexpected_sample": sample,
        "difference_counts_exact": True,
    }


def run_query_trials(
    queries: tuple[Archive3Query, ...],
    runtimes: dict[str, BuiltAlgorithm],
    *,
    warmups: int = 1,
    repetitions: dict[str, int] | None = None,
    checkpoint_path: Path | None = None,
) -> dict[str, object]:
    """Measure online calls only, then collect correctness/work separately."""
    if tuple(runtimes) != ALGORITHM_IDS:
        raise ValueError("all four algorithms are mandatory and must be ordered")
    checkpoint: dict[str, object] = {}
    if checkpoint_path is not None and checkpoint_path.is_file():
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    timing_rows: list[dict[str, object]] = list(checkpoint.get("timing_rows", []))
    correctness_rows: list[dict[str, object]] = list(
        checkpoint.get("correctness_rows", [])
    )
    work_rows: list[dict[str, object]] = list(checkpoint.get("work_rows", []))
    completed_query_ids = {
        row["query_id"] for row in timing_rows
        if row["algorithm_id"] == "naive"
    }
    valid_query_ids = {query.query_id for query in queries}
    if not completed_query_ids <= valid_query_ids:
        raise ValueError("checkpoint belongs to a different query workload")

    # Warm the implementations/process once before any recorded timing. A
    # warmup for every query would add hundreds of full exhaustive passes and
    # is not required to remove interpreter/import cold start.
    for warmup_index in range(warmups):
        if not queries:
            break
        warmup_query = queries[warmup_index % len(queries)]
        for algorithm_id in rotated_algorithm_order(warmup_index):
            runtimes[algorithm_id].search(warmup_query.normalized_query)

    for query_index, query in enumerate(queries):
        if query.query_id in completed_query_ids:
            print(
                f"resuming past completed query {query_index + 1}/{len(queries)} "
                f"{query.query_id}",
                flush=True,
            )
            continue
        query_repetitions = repetitions or _default_repetitions(query)
        if set(query_repetitions) != set(ALGORITHM_IDS):
            raise ValueError("repetitions must name all four algorithms")

        samples = {algorithm_id: [] for algorithm_id in ALGORITHM_IDS}
        positions = {algorithm_id: [] for algorithm_id in ALGORITHM_IDS}
        signatures: dict[str, dict[str, int | str]] = {}
        small_counters: dict[str, Counter[tuple[object, ...]]] = {}
        max_repetitions = max(query_repetitions.values())
        for repetition_index in range(max_repetitions):
            order = rotated_algorithm_order(query_index + repetition_index)
            for order_position, algorithm_id in enumerate(order):
                if repetition_index >= query_repetitions[algorithm_id]:
                    continue
                gc_enabled = gc.isenabled()
                gc.disable()
                try:
                    started = perf_counter_ns()
                    matches = runtimes[algorithm_id].search(query.normalized_query)
                    elapsed = perf_counter_ns() - started
                finally:
                    if gc_enabled:
                        gc.enable()
                samples[algorithm_id].append(elapsed)
                positions[algorithm_id].append(order_position)
                if algorithm_id not in signatures:
                    signatures[algorithm_id] = canonical_signature(matches)
                    if len(matches) <= 50_000:
                        small_counters[algorithm_id] = Counter(
                            _candidate_key(match) for match in matches
                        )

        oracle_signature = signatures["naive"]
        for algorithm_id in ALGORITHM_IDS:
            signature = signatures[algorithm_id]
            timing_rows.append(
                {
                    "query_id": query.query_id,
                    "algorithm_id": algorithm_id,
                    "query_length": query.query_length,
                    "length_bucket": query.length_bucket,
                    "categories": list(query.categories),
                    "repetitions": query_repetitions[algorithm_id],
                    "timing_order_positions": positions[algorithm_id],
                    "timing": summarize_samples(samples[algorithm_id]),
                    "result_count": signature["count"],
                    "signature": signature,
                }
            )
            if algorithm_id == "naive":
                correctness = {
                    "status": "oracle",
                    "correct": True,
                    "missing_count": 0,
                    "unexpected_count": 0,
                    "difference_counts_exact": True,
                }
            elif signature == oracle_signature:
                correctness = {
                    "status": "signature_equal",
                    "correct": True,
                    "missing_count": 0,
                    "unexpected_count": 0,
                    "difference_counts_exact": True,
                }
            else:
                correctness = {
                    "status": "raw_candidate_mismatch",
                    "correct": False,
                    "missing_count": None,
                    "unexpected_count": None,
                    "difference_counts_exact": False,
                }
            correctness_rows.append(
                {
                    "query_id": query.query_id,
                    "algorithm_id": algorithm_id,
                    "oracle_signature": oracle_signature,
                    "actual_signature": signature,
                    **correctness,
                }
            )

        # The untimed Naive instrumentation pass doubles as the exact oracle
        # stream for any bounded mismatching result (notably the 2,000-result
        # tree cap), avoiding a redundant exhaustive corpus scan.
        naive_stats = NaiveSearchStats()
        naive_matches = NaiveSearchAlgorithm(stats=naive_stats).search(
            query.normalized_query, runtimes["naive"].structure  # type: ignore[arg-type]
        )
        work_rows.append({
            "query_id": query.query_id,
            "algorithm_id": "naive",
            "metrics": {**asdict(naive_stats), "result_count": len(naive_matches)},
        })
        for row in correctness_rows[-len(ALGORITHM_IDS):]:
            if row["correct"]:
                continue
            actual = small_counters.get(row["algorithm_id"])
            if actual is not None:
                row.update(_exact_small_actual_diff(naive_matches, actual))

        for algorithm_id in ALGORITHM_IDS[1:]:
            work_rows.append(
                {
                    "query_id": query.query_id,
                    "algorithm_id": algorithm_id,
                    "metrics": _work_metrics(
                        algorithm_id,
                        runtimes[algorithm_id],
                        query.normalized_query,
                    ),
                }
            )
        print(
            f"completed query {query_index + 1}/{len(queries)} "
            f"{query.query_id} length={query.query_length}",
            flush=True,
        )
        if checkpoint_path is not None:
            checkpoint_payload = {
                "warmups": warmups,
                "gc_disabled_during_timed_calls": True,
                "clock": "time.perf_counter_ns",
                "timing_rows": timing_rows,
                "correctness_rows": correctness_rows,
                "work_rows": work_rows,
            }
            temporary = checkpoint_path.with_suffix(".tmp")
            _write_json(temporary, checkpoint_payload)
            temporary.replace(checkpoint_path)

    return {
        "warmups": warmups,
        "gc_disabled_during_timed_calls": True,
        "clock": "time.perf_counter_ns",
        "timing_rows": timing_rows,
        "correctness_rows": correctness_rows,
        "work_rows": work_rows,
    }


def length_bucket(length: int) -> str:
    if length <= 6:
        return str(length)
    if length <= 8:
        return "7-8"
    if length <= 12:
        return "9-12"
    if length <= 20:
        return "13-20"
    return "21+"


def nearest_rank(values: Iterable[int | float], percentile: int) -> int | float:
    if not 1 <= percentile <= 100:
        raise ValueError("percentile must be in [1, 100]")
    ordered = sorted(values)
    if not ordered:
        return 0
    return ordered[max(0, ceil(len(ordered) * percentile / 100) - 1)]


def summarize_samples(values: Iterable[int]) -> dict[str, object]:
    samples = list(values)
    if not samples:
        return {
            "samples": [],
            "count": 0,
            "min_ns": 0,
            "median_ns": 0.0,
            "mean_ns": 0.0,
            "p95_ns": 0,
            "max_ns": 0,
            "stdev_ns": 0.0,
        }
    return {
        "samples": samples,
        "count": len(samples),
        "min_ns": min(samples),
        "median_ns": float(median(samples)),
        "mean_ns": float(fmean(samples)),
        "p95_ns": nearest_rank(samples, 95),
        "max_ns": max(samples),
        "stdev_ns": float(stdev(samples)) if len(samples) > 1 else 0.0,
    }


def _candidate_key(match: MatchCandidate) -> tuple[object, ...]:
    return (
        match.sentence.sentence_id,
        match.sentence.source_path,
        match.sentence.offset,
        match.match_start,
        match.edit_type.value,
        match.edit_index,
        match.correct_characters,
    )


def canonical_signature(
    matches: Iterable[MatchCandidate],
) -> dict[str, int | str]:
    """Order-independent multiset signature over every candidate field.

    Two independent 256-bit accumulators and the exact cardinality make this
    suitable for very large short-query result sets without materializing a
    second multi-million-key Counter. Detailed Counter diffs are still used
    for manageable mismatches.
    """
    count = 0
    total = 0
    squared_total = 0
    sentence_hashes: dict[tuple[int, str, int], int] = {}
    edit_codes = {
        "exact": 1,
        "replacement": 2,
        "insertion": 3,
        "deletion": 4,
    }

    def mix(value: int) -> int:
        # SplitMix-style 128-bit avalanche. Sentence/source identity is
        # cryptographically hashed once per sentence, rather than serializing
        # and hashing once per (potentially multi-million) candidate.
        value &= SIGNATURE_MODULUS - 1
        value ^= value >> 30
        value = (value * 0xbf58476d1ce4e5b9) % SIGNATURE_MODULUS
        value ^= value >> 27
        value = (value * 0x94d049bb133111eb) % SIGNATURE_MODULUS
        return value ^ (value >> 31)

    for match in matches:
        sentence_key = (
            match.sentence.sentence_id,
            match.sentence.source_path,
            match.sentence.offset,
        )
        sentence_value = sentence_hashes.get(sentence_key)
        if sentence_value is None:
            encoded = json.dumps(
                sentence_key, separators=(",", ":"), ensure_ascii=False
            ).encode("utf-8")
            sentence_value = int.from_bytes(
                hashlib.blake2b(encoded, digest_size=16).digest()
            )
            sentence_hashes[sentence_key] = sentence_value
        value = sentence_value
        value = mix(value ^ (match.match_start + 1))
        value = mix(value ^ (edit_codes[match.edit_type.value] << 32))
        value = mix(value ^ ((match.edit_index if match.edit_index is not None else -1) + 2 << 48))
        value = mix(value ^ ((match.correct_characters + 1) << 64))
        count += 1
        total = (total + value) % SIGNATURE_MODULUS
        squared_total = (squared_total + value * value) % SIGNATURE_MODULUS
    return {
        "count": count,
        "sum_mixed_128": f"{total:032x}",
        "sum_squares_mixed_128": f"{squared_total:032x}",
    }


def save_queries(
    path: Path,
    queries: tuple[Archive3Query, ...],
    *,
    seed: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "seed": seed,
                "query_count": len(queries),
                "queries": [asdict(query) for query in queries],
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def load_queries(path: Path) -> tuple[Archive3Query, ...]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return tuple(
        Archive3Query(
            **{
                **item,
                "categories": tuple(item["categories"]),
            }
        )
        for item in payload["queries"]
    )


def _stratified_sentences(
    sentences: tuple[PreparedSentence, ...],
    seed: int,
) -> list[PreparedSentence]:
    generator = random.Random(seed)
    grouped: dict[str, list[PreparedSentence]] = {}
    for sentence in sentences:
        grouped.setdefault(sentence.source_path, []).append(sentence)
    for group in grouped.values():
        generator.shuffle(group)
    sources = sorted(grouped)
    generator.shuffle(sources)
    result: list[PreparedSentence] = []
    while sources:
        remaining: list[str] = []
        for source in sources:
            group = grouped[source]
            result.append(group.pop())
            if group:
                remaining.append(source)
        sources = remaining
    return result


def generate_workload(
    sentences: tuple[PreparedSentence, ...],
    *,
    seed: int = 20260812,
    target_count: int = 1000,
    per_short_length: int = 50,
) -> tuple[Archive3Query, ...]:
    if target_count < per_short_length * 6:
        raise ValueError("target_count cannot cover requested lengths 1-6")
    if not sentences:
        return ()
    generator = random.Random(seed)
    ordered = _stratified_sentences(sentences, seed)
    corpus_text = "\n".join(sentence.normalized_text for sentence in sentences)
    words = [
        (match.group(), sentence, match.start(), match.end())
        for sentence in ordered
        for match in re.finditer(r"\S+", sentence.normalized_text)
    ]
    if not words:
        return ()
    word_counts = Counter(word for word, *_rest in words)
    gram_occurrences: dict[str, list[tuple[PreparedSentence, int]]] = {}
    for sentence in sentences:
        text = sentence.normalized_text
        for start in range(max(0, len(text) - 2)):
            gram_occurrences.setdefault(text[start : start + 3], []).append(
                (sentence, start)
            )
    gram_frequencies = {
        gram: len(occurrences) for gram, occurrences in gram_occurrences.items()
    }
    ordered_grams = sorted(
        gram_frequencies,
        key=lambda gram: (gram_frequencies[gram], gram),
    )
    drafts: list[dict[str, object]] = []
    seen: set[str] = set()
    draft_by_query: dict[str, dict[str, object]] = {}

    def add(
        text: str,
        categories: Iterable[str],
        *,
        sentence: PreparedSentence | None = None,
        start: int | None = None,
        mutation: str | None = None,
        frequency_band: str | None = None,
        qgram_frequency: int | None = None,
    ) -> bool:
        normalized = text.strip()
        if not normalized:
            return False
        category_tuple = tuple(dict.fromkeys(categories))
        if normalized in seen:
            existing = draft_by_query[normalized]
            existing["categories"] = tuple(
                dict.fromkeys((*existing["categories"], *category_tuple))
            )
            if existing.get("frequency_band") is None and frequency_band:
                existing["frequency_band"] = frequency_band
                existing["qgram_frequency"] = qgram_frequency
            return False
        seen.add(normalized)
        draft = {
                "query_text": normalized,
                "normalized_query": normalized,
                "query_length": len(normalized),
                "length_bucket": length_bucket(len(normalized)),
                "primary_category": category_tuple[0],
                "categories": category_tuple,
                "source_sentence_id": sentence.sentence_id if sentence else None,
                "source_path": sentence.source_path if sentence else None,
                "source_start": start,
                "mutation_type": mutation,
                "frequency_band": frequency_band,
                "qgram_frequency": qgram_frequency,
            }
        drafts.append(draft)
        draft_by_query[normalized] = draft
        return True

    # Exact real substrings with explicit substantial coverage for lengths 1-6.
    for wanted_length in range(1, 7):
        sentence_order = list(ordered)
        generator.shuffle(sentence_order)
        added = 0
        for sentence in sentence_order:
            text = sentence.normalized_text
            if len(text) < wanted_length:
                continue
            starts = list(range(len(text) - wanted_length + 1))
            generator.shuffle(starts)
            for start in starts[:4]:
                candidate = text[start : start + wanted_length]
                if len(candidate.strip()) != wanted_length:
                    continue
                if add(
                    candidate,
                    ("exact",),
                    sentence=sentence,
                    start=start,
                ):
                    added += 1
                if added >= per_short_length:
                    break
            if added >= per_short_length:
                break
        if added < per_short_length:
            for sentence in sentence_order:
                text = sentence.normalized_text
                for start in range(max(0, len(text) - wanted_length + 1)):
                    candidate = text[start : start + wanted_length]
                    if len(candidate.strip()) != wanted_length:
                        continue
                    if add(
                        candidate,
                        ("exact",),
                        sentence=sentence,
                        start=start,
                    ):
                        added += 1
                    if added >= per_short_length:
                        break
                if added >= per_short_length:
                    break

    # Whole words and their internal substrings.
    shuffled_words = list(words)
    generator.shuffle(shuffled_words)
    for word, sentence, start, _end in shuffled_words:
        if len(word) >= 2:
            categories = ["exact", "whole_word"]
            if word_counts[word] >= nearest_rank(word_counts.values(), 95):
                categories.extend(("common", "high_result_count"))
            elif word_counts[word] <= nearest_rank(word_counts.values(), 25):
                categories.extend(("rare", "low_result_count"))
            add(word, categories, sentence=sentence, start=start)
        if len(word) >= 7:
            internal_start = 1 + (len(word) % max(1, len(word) - 5))
            internal = word[internal_start : internal_start + min(8, len(word) - internal_start)]
            add(
                internal,
                ("exact", "inside_word"),
                sentence=sentence,
                start=start + internal_start,
            )
        if len(drafts) >= target_count // 2:
            break

    inside_item = next(item for item in shuffled_words if len(item[0]) >= 9)
    inside_word, inside_sentence, inside_start, _inside_end = inside_item
    add(
        inside_word[2:8],
        ("exact", "inside_word"),
        sentence=inside_sentence,
        start=inside_start + 2,
    )

    long_sentence = next(
        sentence for sentence in ordered if len(sentence.normalized_text) >= 30
    )
    add(
        long_sentence.normalized_text[2:18],
        ("exact", "inside_word"),
        sentence=long_sentence,
        start=2,
    )
    add(
        long_sentence.normalized_text[3:27],
        ("exact", "inside_word"),
        sentence=long_sentence,
        start=3,
    )

    repeated_item = next(
        (
            item
            for item in shuffled_words
            if re.search(r"(.)\1|(.{2,}).*\2", item[0])
        ),
        None,
    )
    if repeated_item is not None:
        word, sentence, start, _end = repeated_item
        add(
            word,
            ("exact", "repeated", "repeated_pattern", "whole_word"),
            sentence=sentence,
            start=start,
        )

    # Cross-word, multi-word, and boundary queries from real text.
    for sentence in ordered:
        text = sentence.normalized_text
        spaces = [index for index, char in enumerate(text) if char == " "]
        if spaces:
            boundary = spaces[len(spaces) // 2]
            start = max(0, boundary - 4)
            add(
                text[start : min(len(text), boundary + 5)],
                ("exact", "cross_word", "multi_word"),
                sentence=sentence,
                start=start,
            )
        if len(text) >= 6:
            add(
                text[: min(12, len(text))],
                ("exact", "near_boundary", "boundary_near_start"),
                sentence=sentence,
                start=0,
            )
            start = max(0, len(text) - min(12, len(text)))
            add(
                text[start:],
                ("exact", "near_boundary", "boundary_near_end"),
                sentence=sentence,
                start=start,
            )
        if len(drafts) >= target_count * 3 // 4:
            break

    # Deterministic one-edit mutations of real whole words.
    mutation_sources = [item for item in shuffled_words if len(item[0]) >= 6]
    for index, (word, sentence, start, _end) in enumerate(mutation_sources):
        edit_index = 1 + index % (len(word) - 2)
        replacement = (
            word[:edit_index]
            + ("x" if word[edit_index] != "x" else "z")
            + word[edit_index + 1 :]
        )
        add(
            replacement,
            ("replacement", "near_miss", "whole_word"),
            sentence=sentence,
            start=start,
            mutation="replacement",
        )
        add(
            word[:edit_index] + word[edit_index + 1 :],
            ("insertion", "near_miss", "whole_word"),
            sentence=sentence,
            start=start,
            mutation="missing_character",
        )
        add(
            word[:edit_index] + "x" + word[edit_index:],
            ("deletion", "near_miss", "whole_word"),
            sentence=sentence,
            start=start,
            mutation="extra_character",
        )
        if re.search(r"(.).*\1|(.{2,}).*\2", word):
            add(
                word,
                ("exact", "repeated", "repeated_pattern", "whole_word"),
                sentence=sentence,
                start=start,
            )
        if len(drafts) >= target_count - len(FREQUENCY_BANDS) - 10:
            break

    # Actual Archive frequency percentile probes, plus a rare probe.
    percentile_specs = ((50, "p50"), (75, "p75"), (90, "p90"), (95, "p95"), (99, "p99"))
    for percentile_value, band in percentile_specs:
        gram_index = max(0, ceil(len(ordered_grams) * percentile_value / 100) - 1)
        gram = ordered_grams[gram_index]
        occurrences = gram_occurrences[gram]
        for occurrence_index, (sentence, gram_start) in enumerate(occurrences):
            width = min(21, 6 + occurrence_index + percentile_value % 7)
            start = max(0, gram_start - width // 3)
            text = sentence.normalized_text[start : min(len(sentence.normalized_text), start + width)]
            if add(
                text,
                ("exact", "common", "frequency_probe"),
                sentence=sentence,
                start=start,
                frequency_band=band,
                qgram_frequency=gram_frequencies[gram],
            ):
                break
    rare_gram = ordered_grams[0]
    rare_sentence, rare_start = gram_occurrences[rare_gram][0]
    rare_text = rare_sentence.normalized_text[
        max(0, rare_start - 3) : min(len(rare_sentence.normalized_text), rare_start + 9)
    ]
    add(
        rare_text,
        ("exact", "rare", "frequency_probe"),
        sentence=rare_sentence,
        start=max(0, rare_start - 3),
        frequency_band="rare",
        qgram_frequency=gram_frequencies[rare_gram],
    )

    # Real-derived no-match queries.
    no_match_index = 0
    while len(drafts) < target_count:
        word, sentence, start, _end = shuffled_words[
            no_match_index % len(shuffled_words)
        ]
        no_match_index += 1
        candidate = f"{word}zz{no_match_index:x}"
        if candidate in corpus_text:
            continue
        add(
            candidate,
            ("no_match", "near_miss", "low_result_count"),
            sentence=sentence,
            start=start,
            mutation="real_derived_no_match",
        )

    return tuple(
        Archive3Query(query_id=f"q{index:06d}", **draft)
        for index, draft in enumerate(drafts[:target_count], start=1)
    )


def _representative_distribution(values: Iterable[float]) -> dict[str, float]:
    samples = list(values)
    if not samples:
        return {name: 0.0 for name in (
            "min_ns", "median_ns", "mean_ns", "p75_ns", "p90_ns",
            "p95_ns", "p99_ns", "max_ns", "stdev_ns",
        )}
    return {
        "min_ns": float(min(samples)),
        "median_ns": float(median(samples)),
        "mean_ns": float(fmean(samples)),
        "p75_ns": float(nearest_rank(samples, 75)),
        "p90_ns": float(nearest_rank(samples, 90)),
        "p95_ns": float(nearest_rank(samples, 95)),
        "p99_ns": float(nearest_rank(samples, 99)),
        "max_ns": float(max(samples)),
        "stdev_ns": float(stdev(samples)) if len(samples) > 1 else 0.0,
    }


def _result_bucket(count: int) -> str:
    if count == 0:
        return "0"
    if count <= 5:
        return "1-5"
    if count <= 20:
        return "6-20"
    if count <= 100:
        return "21-100"
    return "100+"


def derive_summary(
    queries: tuple[Archive3Query, ...],
    builds: dict[str, dict[str, object]],
    trials: dict[str, object],
    *,
    tie_tolerance: float = 0.02,
) -> dict[str, object]:
    timing_rows = trials["timing_rows"]
    correctness_rows = trials["correctness_rows"]
    timing = {(row["query_id"], row["algorithm_id"]): row for row in timing_rows}
    correctness = {
        (row["query_id"], row["algorithm_id"]): row
        for row in correctness_rows
    }
    naive_ns = {
        query.query_id: float(timing[(query.query_id, "naive")]["timing"]["median_ns"])
        for query in queries
    }
    overall: dict[str, object] = {}
    speedups: dict[str, object] = {}
    correctness_summary: dict[str, object] = {}
    for algorithm_id in ALGORITHM_IDS:
        values = [
            float(timing[(query.query_id, algorithm_id)]["timing"]["median_ns"])
            for query in queries
        ]
        overall[algorithm_id] = _representative_distribution(values)
        ratios = [
            naive_ns[query.query_id] / max(
                1.0,
                float(timing[(query.query_id, algorithm_id)]["timing"]["median_ns"]),
            )
            for query in queries
        ]
        speedups[algorithm_id] = {
            "median": float(median(ratios)),
            "mean": float(fmean(ratios)),
            "p75": float(nearest_rank(ratios, 75)),
            "p90": float(nearest_rank(ratios, 90)),
            "best": float(max(ratios)),
            "worst": float(min(ratios)),
        }
        rows = [correctness[(query.query_id, algorithm_id)] for query in queries]
        correctness_summary[algorithm_id] = {
            "queries": len(rows),
            "mismatches": sum(not row["correct"] for row in rows),
            "false_negatives": sum(
                (row["missing_count"] or 0)
                for row in rows if row["difference_counts_exact"]
            ),
            "false_positives": sum(
                (row["unexpected_count"] or 0)
                for row in rows if row["difference_counts_exact"]
            ),
            "all_difference_counts_exact": all(
                row["difference_counts_exact"] for row in rows
            ),
        }

    def grouped_summary(group_getter) -> dict[str, object]:
        groups: dict[str, list[Archive3Query]] = {}
        for query in queries:
            for group in group_getter(query):
                groups.setdefault(group, []).append(query)
        return {
            group: {
                "query_count": len(members),
                "algorithms": {
                    algorithm_id: {
                        **_representative_distribution(
                            float(timing[(query.query_id, algorithm_id)]["timing"]["median_ns"])
                            for query in members
                        ),
                        "correct_queries": sum(
                            bool(correctness[(query.query_id, algorithm_id)]["correct"])
                            for query in members
                        ),
                    }
                    for algorithm_id in ALGORITHM_IDS
                },
            }
            for group, members in groups.items()
        }

    wins = {algorithm_id: 0.0 for algorithm_id in ALGORITHM_IDS}
    per_query_winners: dict[str, list[str]] = {}
    for query in queries:
        eligible = {
            algorithm_id: float(timing[(query.query_id, algorithm_id)]["timing"]["median_ns"])
            for algorithm_id in ALGORITHM_IDS
            if correctness[(query.query_id, algorithm_id)]["correct"]
        }
        fastest = min(eligible.values())
        winners = [
            algorithm_id for algorithm_id, value in eligible.items()
            if value <= fastest * (1.0 + tie_tolerance)
        ]
        per_query_winners[query.query_id] = winners
        for winner in winners:
            wins[winner] += 1.0 / len(winners)

    result_groups: dict[str, list[Archive3Query]] = {}
    for query in queries:
        count = int(timing[(query.query_id, "naive")]["result_count"])
        result_groups.setdefault(_result_bucket(count), []).append(query)
    result_count_analysis = {
        bucket: {
            "query_count": len(members),
            "algorithms": {
                algorithm_id: _representative_distribution(
                    float(timing[(query.query_id, algorithm_id)]["timing"]["median_ns"])
                    for query in members
                )
                for algorithm_id in ALGORITHM_IDS
            },
        }
        for bucket, members in result_groups.items()
    }

    worst: dict[str, object] = {}
    best: dict[str, object] = {}
    for algorithm_id in ALGORITHM_IDS:
        ranked = sorted(
            queries,
            key=lambda query: float(timing[(query.query_id, algorithm_id)]["timing"]["median_ns"]),
            reverse=True,
        )
        worst[algorithm_id] = [
            {
                "query_id": query.query_id,
                "query": query.query_text,
                "length": query.query_length,
                "categories": list(query.categories),
                "result_count": timing[(query.query_id, algorithm_id)]["result_count"],
                "median_ns": timing[(query.query_id, algorithm_id)]["timing"]["median_ns"],
                "p95_ns": timing[(query.query_id, algorithm_id)]["timing"]["p95_ns"],
                "speedup_vs_naive": naive_ns[query.query_id] / max(
                    1.0, float(timing[(query.query_id, algorithm_id)]["timing"]["median_ns"])
                ),
            }
            for query in ranked[:25]
        ]
        if algorithm_id != "naive":
            best[algorithm_id] = sorted(
                (
                    {
                        "query_id": query.query_id,
                        "query": query.query_text,
                        "speedup_vs_naive": naive_ns[query.query_id] / max(
                            1.0,
                            float(timing[(query.query_id, algorithm_id)]["timing"]["median_ns"]),
                        ),
                    }
                    for query in queries
                ),
                key=lambda row: row["speedup_vs_naive"],
                reverse=True,
            )[:20]

    naive_build = float(builds["naive"]["build_time_ns"]["median_ns"])
    break_even: dict[str, int | None] = {}
    for algorithm_id in ALGORITHM_IDS[1:]:
        extra_build = max(
            0.0,
            float(builds[algorithm_id]["build_time_ns"]["median_ns"]) - naive_build,
        )
        average_saving = fmean(
            naive_ns[query.query_id]
            - float(timing[(query.query_id, algorithm_id)]["timing"]["median_ns"])
            for query in queries
        )
        break_even[algorithm_id] = (
            ceil(extra_build / average_saving) if average_saving > 0 else None
        )

    return {
        "query_count": len(queries),
        "tie_tolerance_fraction": tie_tolerance,
        "overall": overall,
        "correctness": correctness_summary,
        "speedup_vs_naive": speedups,
        "wins": {
            algorithm_id: {
                "wins": wins[algorithm_id],
                "win_percent": 100.0 * wins[algorithm_id] / max(1, len(queries)),
            }
            for algorithm_id in ALGORITHM_IDS
        },
        "per_query_winners": per_query_winners,
        "per_length": grouped_summary(lambda query: (query.length_bucket,)),
        "per_category": grouped_summary(lambda query: query.categories),
        "result_count_analysis": result_count_analysis,
        "worst_cases": worst,
        "best_cases": best,
        "break_even_queries_estimate": break_even,
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def environment_metadata(archive: Path) -> dict[str, object]:
    def git(*arguments: str) -> str:
        completed = subprocess.run(
            ("git", *arguments), capture_output=True, text=True, check=False
        )
        return completed.stdout.strip() or "unavailable"

    return {
        "benchmark_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor()
        or os.environ.get("PROCESSOR_IDENTIFIER", "unknown"),
        "architecture": platform.architecture()[0],
        "git_commit_sha": git("rev-parse", "HEAD"),
        "git_branch": git("branch", "--show-current"),
        "archive_path": str(archive.resolve()),
        "archive_size_bytes": archive.stat().st_size,
        "archive_sha256": _sha256(archive),
    }


def corpus_statistics(
    sentences: tuple[PreparedSentence, ...],
    *,
    preparation_time_ns: int,
    preparation_peak_memory_bytes: int,
) -> dict[str, object]:
    lengths = [len(sentence.normalized_text) for sentence in sentences]
    words = [
        word
        for sentence in sentences
        for word in sentence.normalized_text.split()
    ]
    return {
        "source_files": len({sentence.source_path for sentence in sentences}),
        "prepared_sentences": len(sentences),
        "total_original_characters": sum(
            len(sentence.original_text) for sentence in sentences
        ),
        "total_normalized_characters": sum(lengths),
        "word_occurrences": len(words),
        "unique_normalized_words": len(set(words)),
        "preparation_time_ns": preparation_time_ns,
        "preparation_peak_memory_bytes": preparation_peak_memory_bytes,
        "sentence_length": {
            "min": min(lengths, default=0),
            "mean": float(fmean(lengths)) if lengths else 0.0,
            "median": float(median(lengths)) if lengths else 0.0,
            "p75": nearest_rank(lengths, 75),
            "p90": nearest_rank(lengths, 90),
            "p95": nearest_rank(lengths, 95),
            "p99": nearest_rank(lengths, 99),
            "max": max(lengths, default=0),
        },
    }


def _write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _ms(value: object) -> str:
    return f"{float(value) / 1_000_000:.3f}"


def _markdown_table(headers: Iterable[str], rows: Iterable[Iterable[object]]) -> str:
    header = list(headers)
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    lines.extend("| " + " | ".join(str(cell) for cell in row) + " |" for row in rows)
    return "\n".join(lines)


def render_report(payload: dict[str, object]) -> str:
    environment = payload["environment"]
    corpus = payload["corpus"]
    builds = payload["builds"]
    summary = payload["summary"]
    secondary = payload.get("secondary_studies", {})
    algorithm_names = {
        "naive": "Naive",
        "qgram_verifier": "Q-Gram + Verifier",
        "qgram_tree_hybrid": "Q-Gram + Tree Hybrid",
        "bi_anchor": "Selective Bi-Anchor + One-Edit Verifier",
    }
    overall_rows = [
        (
            algorithm_names[algorithm_id],
            _ms(summary["overall"][algorithm_id]["median_ns"]),
            _ms(summary["overall"][algorithm_id]["mean_ns"]),
            _ms(summary["overall"][algorithm_id]["p95_ns"]),
            _ms(summary["overall"][algorithm_id]["p99_ns"]),
            _ms(summary["overall"][algorithm_id]["max_ns"]),
        )
        for algorithm_id in ALGORITHM_IDS
    ]
    length_order = ("1", "2", "3", "4", "5", "6", "7-8", "9-12", "13-20", "21+")
    length_rows = []
    for bucket in length_order:
        if bucket not in summary["per_length"]:
            continue
        item = summary["per_length"][bucket]
        length_rows.append((
            bucket,
            item["query_count"],
            *(
                _ms(item["algorithms"][algorithm_id]["median_ns"])
                for algorithm_id in ALGORITHM_IDS
            ),
        ))
    category_rows = [
        (
            category,
            item["query_count"],
            *(
                _ms(item["algorithms"][algorithm_id]["median_ns"])
                for algorithm_id in ALGORITHM_IDS
            ),
        )
        for category, item in sorted(summary["per_category"].items())
    ]
    correctness_rows = [
        (
            algorithm_names[algorithm_id],
            item["queries"], item["mismatches"],
            item["false_negatives"], item["false_positives"],
        )
        for algorithm_id in ALGORITHM_IDS
        for item in (summary["correctness"][algorithm_id],)
    ]
    build_rows = [
        (
            algorithm_names[algorithm_id],
            _ms(builds[algorithm_id]["build_time_ns"]["min_ns"]),
            _ms(builds[algorithm_id]["build_time_ns"]["median_ns"]),
            _ms(builds[algorithm_id]["build_time_ns"]["mean_ns"]),
            _ms(builds[algorithm_id]["build_time_ns"]["max_ns"]),
            builds[algorithm_id]["peak_memory_bytes"],
            builds[algorithm_id]["retained_memory_bytes"],
        )
        for algorithm_id in ALGORITHM_IDS
    ]
    winner = min(
        (
            algorithm_id for algorithm_id in ALGORITHM_IDS
            if summary["correctness"][algorithm_id]["mismatches"] == 0
        ),
        key=lambda algorithm_id: summary["overall"][algorithm_id]["median_ns"],
    )
    lines = [
        "# Trustworthy Archive3 Four-Algorithm Benchmark",
        "",
        "## 1. Environment",
        "",
        f"Python: `{environment['python_version'].splitlines()[0]}`  ",
        f"Platform/CPU: `{environment['platform']}` / `{environment['processor']}`  ",
        f"Git: `{environment['git_commit_sha']}` on `{environment['git_branch']}`  ",
        f"Archive SHA-256: `{environment['archive_sha256']}`",
        "",
        "## 2. Archive3 corpus",
        "",
        f"The production `DataPreparer` processed 100% of `{environment['archive_path']}`: "
        f"{corpus['source_files']} files, {corpus['prepared_sentences']} sentences, "
        f"{corpus['total_original_characters']} original and "
        f"{corpus['total_normalized_characters']} normalized characters, "
        f"{corpus['word_occurrences']} word occurrences, and "
        f"{corpus['unique_normalized_words']} unique normalized words. "
        f"Preparation took {_ms(corpus['preparation_time_ns'])} ms; measured peak "
        f"allocation was {corpus['preparation_peak_memory_bytes']} bytes.",
        "",
        "Sentence-length statistics: " + json.dumps(corpus["sentence_length"]),
        "",
        "## 3. Algorithms",
        "",
        _markdown_table(
            ("Concept", "Actual class", "Builder/structure"),
            (
                ("Naive", "NaiveSearchAlgorithm", "NaiveStructureBuilder / NaiveSearchStructure"),
                ("Q-Gram + Verifier", "QGramSearchAlgorithm", "QGramStructureBuilder / QGramSearchStructure"),
                ("Q-Gram + Tree Hybrid", "QGramTrieSearchAlgorithm", "internal build / TrieNode + q-gram map"),
                ("Selective Bi-Anchor", "BiAnchorSearchAlgorithm", "BiAnchorStructureBuilder / BiAnchorSearchStructure"),
            ),
        ),
        "",
        "Primary q is 3. All algorithms received the same in-memory sentence tuple and stored query list.",
        "",
        "## 4. Correctness",
        "",
        _markdown_table(("Algorithm", "Queries", "Mismatches", "FN", "FP"), correctness_rows),
        "",
        "Naive is the raw-candidate oracle. Canonical signatures include sentence ID, source path, line offset, match start, edit type/index, correct-character count, and multiplicity. Incorrect algorithms are excluded from wins.",
        "",
        "## 5. Offline build",
        "",
        _markdown_table(("Algorithm", "Min ms", "Median ms", "Mean ms", "Max ms", "Peak B", "Retained B"), build_rows),
        "",
        "Structure-specific counts are in `build_results.json`. Memory is Python allocation observed by `tracemalloc`, not a deep resident-set measurement.",
        "",
        "## 6. Overall online latency",
        "",
        _markdown_table(("Algorithm", "Median ms", "Mean ms", "p95 ms", "p99 ms", "Max ms"), overall_rows),
        "",
        "Each cell is calculated from one per-query median, not pooled repetitions.",
        "",
        "## 7. Per-length latency",
        "",
        _markdown_table(("Length", "N", "Naive", "QG+V", "QG+Tree", "Bi-Anchor"), length_rows),
        "",
        "## 8. Per-category latency",
        "",
        _markdown_table(("Category", "N", "Naive", "QG+V", "QG+Tree", "Bi-Anchor"), category_rows),
        "",
        "## 9. Per-query results",
        "",
        "See `per_query_results.csv` for every query/algorithm median and `raw_timings.json` for every nanosecond sample and deterministic timing-order position.",
        "",
        "## 10. Speedup vs Naive",
        "",
        "```json\n" + json.dumps(summary["speedup_vs_naive"], indent=2) + "\n```",
        "",
        "## 11. Win rates",
        "",
        _markdown_table(
            ("Algorithm", "Wins", "Win %"),
            ((algorithm_names[key], f"{value['wins']:.2f}", f"{value['win_percent']:.2f}") for key, value in summary["wins"].items()),
        ),
        "",
        f"A {summary['tie_tolerance_fraction'] * 100:.1f}% relative tolerance defines ties; tied credit is split equally.",
        "",
        "## 12. Internal work metrics",
        "",
        "Every per-query counter is retained in `internal_work_metrics.json`; instrumentation was rerun outside timed calls.",
        "",
        "## 13. Result-count analysis",
        "",
        "```json\n" + json.dumps(summary["result_count_analysis"], indent=2) + "\n```",
        "",
        "## 14. Worst 25 queries per algorithm",
        "",
        "```json\n" + json.dumps(summary["worst_cases"], indent=2) + "\n```",
        "",
        "## 15. Best cases",
        "",
        "```json\n" + json.dumps(summary["best_cases"], indent=2) + "\n```",
        "",
        "## 16. Build/query break-even",
        "",
        "Estimated query counts (median extra build / mean measured per-query saving): `" + json.dumps(summary["break_even_queries_estimate"]) + "`.",
        "",
        "## 17. Memory",
        "",
        _markdown_table(("Algorithm", "Peak build B", "Retained B"), ((algorithm_names[key], value["peak_memory_bytes"], value["retained_memory_bytes"]) for key, value in builds.items())),
        "",
        "## 18. Scaling",
        "",
        json.dumps(secondary.get("scaling", {"status": "not run; primary full-corpus cost made it impractical"}), indent=2),
        "",
        "## 19. Repeatability",
        "",
        json.dumps(secondary.get("repeatability", {"status": "not run"}), indent=2),
        "",
        "## 20. Secondary q study",
        "",
        json.dumps(secondary.get("q_study", {"status": "not run"}), indent=2),
        "",
        "## 21. Conclusions",
        "",
        f"The fastest correct algorithm by overall median is **{algorithm_names[winner]}**. Detailed length/category answers are the measured tables above; any incorrect implementation is explicitly ineligible. Cheapest build and least measured retained allocation follow directly from section 5.",
        "",
        "## 22. Next optimization recommendation",
        "",
        "Use `internal_work_metrics.json` to target the dominant measured posting expansion, fallback, or verifier-call source. Do not change matching semantics; rerun this exact stored workload after any optimization.",
        "",
        "## Reproduction command",
        "",
        "```powershell\npython -m src.autocomplete.archive3_benchmark --archive data/Archive3.zip --output benchmark/archive3 --reuse-queries\n```",
    ]
    return "\n".join(lines) + "\n"


def validate_artifacts(
    queries: tuple[Archive3Query, ...],
    builds: dict[str, dict[str, object]],
    trials: dict[str, object],
) -> None:
    expected = {
        (query.query_id, algorithm_id)
        for query in queries for algorithm_id in ALGORITHM_IDS
    }
    for name in ("timing_rows", "correctness_rows", "work_rows"):
        rows = trials[name]
        actual = {(row["query_id"], row["algorithm_id"]) for row in rows}
        if actual != expected or len(rows) != len(expected):
            raise ValueError(f"{name} is incomplete or duplicated")
    if tuple(builds) != ALGORITHM_IDS:
        raise ValueError("build results do not contain all four algorithms")
    for row in trials["timing_rows"]:
        if len(row["timing"]["samples"]) != row["repetitions"]:
            raise ValueError("raw timing sample count does not match metadata")


def write_artifacts(
    output: Path,
    *,
    environment: dict[str, object],
    corpus: dict[str, object],
    queries: tuple[Archive3Query, ...],
    seed: int,
    builds: dict[str, dict[str, object]],
    trials: dict[str, object],
    summary: dict[str, object],
    secondary_studies: dict[str, object] | None = None,
) -> None:
    validate_artifacts(queries, builds, trials)
    output.mkdir(parents=True, exist_ok=True)
    _write_json(output / "environment.json", environment)
    _write_json(output / "corpus_summary.json", corpus)
    save_queries(output / "queries.json", queries, seed=seed)
    _write_json(output / "build_results.json", builds)
    _write_json(output / "raw_timings.json", {
        "warmups": trials["warmups"],
        "clock": trials["clock"],
        "gc_disabled_during_timed_calls": trials["gc_disabled_during_timed_calls"],
        "rows": trials["timing_rows"],
    })
    _write_json(output / "correctness_results.json", trials["correctness_rows"])
    _write_json(output / "internal_work_metrics.json", trials["work_rows"])
    _write_json(output / "summary.json", {
        **summary,
        "secondary_studies": secondary_studies or {},
    })

    correctness = {
        (row["query_id"], row["algorithm_id"]): row
        for row in trials["correctness_rows"]
    }
    work = {
        (row["query_id"], row["algorithm_id"]): row["metrics"]
        for row in trials["work_rows"]
    }
    query_by_id = {query.query_id: query for query in queries}
    naive_medians = {
        row["query_id"]: float(row["timing"]["median_ns"])
        for row in trials["timing_rows"] if row["algorithm_id"] == "naive"
    }
    with (output / "per_query_results.csv").open(
        "w", encoding="utf-8", newline=""
    ) as destination:
        fieldnames = (
            "query_id", "query", "length", "length_bucket", "categories",
            "algorithm", "correct", "correctness_status", "result_count",
            "repetitions", "min_search_ms", "median_search_ms",
            "mean_search_ms", "p95_search_ms", "max_search_ms",
            "stdev_search_ms", "speedup_vs_naive", "fallback_used",
            "candidate_count", "verifier_calls",
        )
        writer = csv.DictWriter(destination, fieldnames=fieldnames)
        writer.writeheader()
        for row in trials["timing_rows"]:
            query = query_by_id[row["query_id"]]
            key = (row["query_id"], row["algorithm_id"])
            metrics = work[key]
            timing = row["timing"]
            candidate_count = next(
                (
                    metrics[name] for name in (
                        "candidate_starts_after_dedup",
                        "candidate_contexts_after_dedup",
                        "candidate_words",
                    ) if name in metrics
                ),
                "",
            )
            writer.writerow({
                "query_id": query.query_id,
                "query": query.query_text,
                "length": query.query_length,
                "length_bucket": query.length_bucket,
                "categories": "|".join(query.categories),
                "algorithm": row["algorithm_id"],
                "correct": correctness[key]["correct"],
                "correctness_status": correctness[key]["status"],
                "result_count": row["result_count"],
                "repetitions": row["repetitions"],
                "min_search_ms": float(timing["min_ns"]) / 1_000_000,
                "median_search_ms": float(timing["median_ns"]) / 1_000_000,
                "mean_search_ms": float(timing["mean_ns"]) / 1_000_000,
                "p95_search_ms": float(timing["p95_ns"]) / 1_000_000,
                "max_search_ms": float(timing["max_ns"]) / 1_000_000,
                "stdev_search_ms": float(timing["stdev_ns"]) / 1_000_000,
                "speedup_vs_naive": naive_medians[query.query_id]
                / max(1.0, float(timing["median_ns"])),
                "fallback_used": metrics.get("fallback_count", ""),
                "candidate_count": candidate_count,
                "verifier_calls": metrics.get("verifier_calls", ""),
            })
    report_payload = {
        "environment": environment,
        "corpus": corpus,
        "builds": builds,
        "summary": summary,
        "secondary_studies": secondary_studies or {},
    }
    (output / "benchmark_report.md").write_text(
        render_report(report_payload), encoding="utf-8"
    )


def run_benchmark(args: argparse.Namespace) -> None:
    archive = Path(args.archive)
    output = Path(args.output)
    if not archive.is_file():
        raise FileNotFoundError(archive)
    environment = environment_metadata(archive)
    print(f"preparing 100% of {archive}", flush=True)
    tracemalloc.start()
    started = perf_counter_ns()
    sentences = tuple(DataPreparer().prepare(archive))
    preparation_time = perf_counter_ns() - started
    _current, preparation_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    corpus = corpus_statistics(
        sentences,
        preparation_time_ns=preparation_time,
        preparation_peak_memory_bytes=preparation_peak,
    )
    print(
        f"prepared {len(sentences)} sentences in {preparation_time / 1e9:.3f}s",
        flush=True,
    )
    query_path = output / "queries.json"
    if args.reuse_queries and query_path.is_file():
        queries = load_queries(query_path)
    else:
        queries = generate_workload(
            sentences,
            seed=args.seed,
            target_count=args.target_queries,
            per_short_length=args.per_short_length,
        )
    output.mkdir(parents=True, exist_ok=True)
    _write_json(output / "environment.json", environment)
    _write_json(output / "corpus_summary.json", corpus)
    save_queries(query_path, queries, seed=args.seed)
    print(f"using {len(queries)} deterministic queries", flush=True)
    print("building all four algorithms independently", flush=True)
    builds, runtimes = build_algorithms(
        sentences, repetitions=args.build_repetitions, q=args.q
    )
    _write_json(output / "build_results.json", builds)
    print("build measurements complete; starting online trials", flush=True)
    trials = run_query_trials(
        queries,
        runtimes,
        warmups=args.warmups,
        checkpoint_path=output / "trial_checkpoint.json",
    )
    summary = derive_summary(queries, builds, trials)
    # These studies are intentionally explicit when not run; a full Naive call
    # costs 34-62 seconds on this corpus, so silent omission would be misleading.
    secondary = {
        "scaling": {"status": "not run in primary command; estimated cost was prohibitive"},
        "repeatability": {"status": "main per-query repetitions provide within-run stability only"},
        "q_study": {"status": "not run; primary default q=3 was frozen"},
    }
    write_artifacts(
        output,
        environment=environment,
        corpus=corpus,
        queries=queries,
        seed=args.seed,
        builds=builds,
        trials=trials,
        summary=summary,
        secondary_studies=secondary,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", default="data/Archive3.zip")
    parser.add_argument("--output", default="benchmark/archive3")
    parser.add_argument("--seed", type=int, default=20260812)
    parser.add_argument("--target-queries", type=int, default=55)
    parser.add_argument("--per-short-length", type=int, default=5)
    parser.add_argument("--build-repetitions", type=int, default=3)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--q", type=int, default=3)
    parser.add_argument("--reuse-queries", action="store_true")
    return parser.parse_args(argv)


def main() -> None:
    run_benchmark(parse_args())


if __name__ == "__main__":
    main()
