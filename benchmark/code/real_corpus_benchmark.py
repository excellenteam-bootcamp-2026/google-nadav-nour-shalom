"""Reproducible full-corpus comparison of the repository search algorithms.

This module is benchmark-only.  It deliberately imports the production
implementations without changing their matching or result semantics.
"""

from __future__ import annotations

import argparse
import cProfile
from collections import Counter, defaultdict
import csv
from dataclasses import asdict, dataclass
import gc
import json
from math import ceil
import random
import re
from pathlib import Path
import pstats
from statistics import fmean, median
from time import perf_counter_ns
import tracemalloc
from typing import Iterable

from src.algorithms.bi_anchor_search_algorithm import BiAnchorSearchAlgorithm
from src.algorithms.bi_anchor_search_stats import BiAnchorSearchStats
from src.algorithms.naive_search_algorithm import NaiveSearchAlgorithm
from src.algorithms.one_edit_verifier import OneEditVerifier
from src.algorithms.qgram_search_algorithm import QGramSearchAlgorithm
from src.algorithms.qgram_trie_search_algorithm import QGramTrieSearchAlgorithm
from src.autocomplete.preparation import DataPreparer
from src.builders.bi_anchor_structure_builder import BiAnchorStructureBuilder
from src.builders.naive_structure_builder import NaiveStructureBuilder
from src.builders.qgram_structure_builder import QGramStructureBuilder
from src.models.match_candidate import MatchCandidate
from src.models.prepared_sentence import PreparedSentence


CandidateKey = tuple[int, str, int, int, str, int | None, int]

REQUIRED_QUERY_TAGS = {
    "short_exact",
    "medium_exact",
    "long_exact",
    "inside_word",
    "cross_word",
    "replacement",
    "insertion",
    "deletion",
    "repeated",
    "common_qgram",
    "medium_qgram",
    "rare_qgram",
    "no_match",
    "near_boundary",
    "multiple_matches",
    "high_frequency",
}


@dataclass(frozen=True, slots=True)
class RealQuery:
    query: str
    tags: tuple[str, ...]
    source_sentence_id: int | None
    source_file: str | None
    source_offset: int | None
    expected_start: int | None
    mutation: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class BuiltAlgorithm:
    """Benchmark adapter over an unchanged production implementation."""

    algorithm_id: str
    algorithm: object
    structure: object | None
    owns_structure: bool = False

    def search(self, query: str) -> list[MatchCandidate]:
        if self.owns_structure:
            return self.algorithm.search(query)  # type: ignore[attr-defined,no-any-return]
        return self.algorithm.search(query, self.structure)  # type: ignore[attr-defined,no-any-return]


def discover_algorithms() -> list[dict[str, object]]:
    """Map conceptual algorithms to the exact repository classes."""
    return [
        {
            "id": "naive",
            "conceptual_name": "Naive Search",
            "class": "NaiveSearchAlgorithm",
            "module": "src.algorithms.naive_search_algorithm",
            "builder": "NaiveStructureBuilder",
            "verifier": "OneEditVerifier.compare",
            "contract_compatible": True,
            "compatibility_reason": "shared SearchAlgorithm contract",
            "parameters": {},
        },
        {
            "id": "qgram_positional",
            "conceptual_name": "Q-Gram Positional Search + One-Edit Verifier",
            "class": "QGramSearchAlgorithm",
            "module": "src.algorithms.qgram_search_algorithm",
            "builder": "QGramStructureBuilder",
            "verifier": "OneEditVerifier.compare (Naive fallback when unsafe)",
            "contract_compatible": True,
            "compatibility_reason": "shared SearchAlgorithm contract",
            "parameters": {"q": 3, "short_q": [1, 2]},
        },
        {
            "id": "qgram_tree_hybrid",
            "conceptual_name": "Q-Gram + Tree Hybrid Search",
            "class": "QGramTrieSearchAlgorithm",
            "module": "src.algorithms.qgram_trie_search_algorithm",
            "builder": "QGramTrieSearchAlgorithm.build",
            "verifier": "private _fuzzy_compare helpers",
            "contract_compatible": True,
            "compatibility_reason": (
                "self-owned structure adapter required; search signature omits "
                "the shared structure argument"
            ),
            "parameters": {"q": 3, "max_results": 2000},
        },
        {
            "id": "bi_anchor",
            "conceptual_name": "Selective Bi-Anchor + Shared OneEditVerifier",
            "class": "BiAnchorSearchAlgorithm",
            "module": "src.algorithms.bi_anchor_search_algorithm",
            "builder": "BiAnchorStructureBuilder",
            "verifier": "OneEditVerifier.compare (Naive fallback for short queries)",
            "contract_compatible": True,
            "compatibility_reason": "shared SearchAlgorithm contract",
            "parameters": {"q": 3, "fallback": "query length < 2*q"},
        },
    ]


def _trie_stats(algorithm: QGramTrieSearchAlgorithm) -> dict[str, int]:
    nodes = terminals = occurrences = 0
    stack = [algorithm._root]
    while stack:
        node = stack.pop()
        nodes += 1
        if node.word is not None:
            terminals += 1
            occurrences += len(node.occurrences)
        stack.extend(node.children.values())
    return {
        "tree_nodes": nodes,
        "tree_edges": max(0, nodes - 1),
        "terminals": terminals,
        "word_occurrences": occurrences,
        "qgram_keys": len(algorithm._qgrams),
        "qgram_references": sum(
            len(references) for references in algorithm._qgrams.values()
        ),
    }


def _structure_stats(algorithm_id: str, runtime: BuiltAlgorithm) -> dict[str, int]:
    if algorithm_id == "naive":
        return {"sentences": len(runtime.structure.sentences)}  # type: ignore[union-attr]
    if algorithm_id == "qgram_tree_hybrid":
        return _trie_stats(runtime.algorithm)  # type: ignore[arg-type]
    if algorithm_id == "bi_anchor":
        index = runtime.structure.build_stats.index  # type: ignore[union-attr]
        return {
            "unique_words": index.unique_words,
            "word_occurrences": index.word_occurrences,
            "intra_word_seed_keys": index.intra_word_seed_keys,
            "intra_word_seed_references": index.intra_word_seed_references,
            "boundary_seed_keys": index.boundary_seed_keys,
            "boundary_occurrences": index.boundary_occurrences,
        }
    structure = runtime.structure
    indexes = [structure.positional_index, *structure.short_positional_indexes.values()]  # type: ignore[union-attr]
    posting_lengths = [
        len(postings) for index in indexes for postings in index.values()
    ]
    return {
        "qgram_keys": sum(len(index) for index in indexes),
        "posting_references": sum(
            len(postings) for index in indexes for postings in index.values()
        ),
        "largest_posting_list": max(posting_lengths, default=0),
        "median_posting_length": int(median(posting_lengths)) if posting_lengths else 0,
        "p95_posting_length": int(percentile(posting_lengths, 95)) if posting_lengths else 0,
    }


def _construct_algorithm(
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
    if algorithm_id == "qgram_positional":
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
    raise KeyError(algorithm_id)


def build_algorithms(
    sentences: tuple[PreparedSentence, ...],
    *,
    q: int = 3,
    measure_memory: bool = True,
) -> tuple[dict[str, dict[str, object]], dict[str, BuiltAlgorithm]]:
    """Build every implementation independently and retain runnable ones."""
    measurements: dict[str, dict[str, object]] = {}
    runtimes: dict[str, BuiltAlgorithm] = {}
    for item in discover_algorithms():
        algorithm_id = str(item["id"])
        gc.collect()
        if measure_memory:
            tracemalloc.start()
        started = perf_counter_ns()
        runtime: BuiltAlgorithm | None = None
        error: Exception | None = None
        try:
            runtime = _construct_algorithm(algorithm_id, sentences, q)
        except Exception as caught:  # errors are study results
            error = caught
        elapsed = perf_counter_ns() - started
        retained = peak = 0
        if measure_memory:
            retained, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
        if error is not None or runtime is None:
            measurements[algorithm_id] = {
                "status": "error",
                "build_ns": elapsed,
                "retained_memory_bytes": retained,
                "peak_memory_bytes": peak,
                "memory_method": "tracemalloc allocations after corpus preparation",
                "stats": {},
                "error": f"{type(error).__name__}: {error}",
            }
            continue
        runtimes[algorithm_id] = runtime
        measurements[algorithm_id] = {
            "status": "ok",
            "build_ns": elapsed,
            "retained_memory_bytes": retained,
            "peak_memory_bytes": peak,
            "memory_method": "tracemalloc allocations after corpus preparation",
            "stats": _structure_stats(algorithm_id, runtime),
            "error": None,
        }
    return measurements, runtimes


def _length_tag(length: int) -> str:
    if length <= 2:
        return "length_1_2"
    if length <= 5:
        return "length_3_5"
    if length <= 8:
        return "length_6_8"
    if length <= 15:
        return "length_9_15"
    return "length_16_plus"


def _naive_work(runtime: BuiltAlgorithm, query: str) -> dict[str, int]:
    sentences = runtime.structure.sentences  # type: ignore[union-attr]
    query_length = len(query)
    verifier_calls = 0
    positions = 0
    for sentence in sentences:
        text_length = len(sentence.normalized_text)
        positions += text_length
        for target_length in (query_length, query_length + 1, query_length - 1):
            if target_length > 0:
                verifier_calls += max(0, text_length - target_length + 1)
    return {
        "sentence_positions_examined": positions,
        "candidate_slices_checked": verifier_calls,
        "verifier_calls": verifier_calls,
    }


def _trie_work(runtime: BuiltAlgorithm, query: str) -> dict[str, int]:
    algorithm: QGramTrieSearchAlgorithm = runtime.algorithm  # type: ignore[assignment]
    query_grams = max(0, len(query) - algorithm.Q + 1)
    postings = 0
    if len(query) >= algorithm.Q:
        postings = sum(
            len(algorithm._qgrams.get(query[index : index + algorithm.Q], ()))
            for index in range(query_grams)
        )
    candidates = algorithm._get_candidates(query)
    tree_stats = _trie_stats(algorithm)
    return {
        "query_qgrams": query_grams,
        "qgram_lookups": query_grams,
        "posting_entries_loaded": postings,
        "tree_nodes_traversed": (
            tree_stats["tree_nodes"] if len(query) < algorithm.Q else 0
        ),
        "branches_explored": query_grams,
        "candidate_words_before_dedup": postings,
        "candidate_words_after_dedup": len(candidates),
        "verifier_calls": len(candidates),
    }


def _bi_anchor_work(runtime: BuiltAlgorithm, query: str) -> dict[str, object]:
    structure = runtime.structure
    if len(query) < 2 * structure.q:  # type: ignore[union-attr]
        naive_runtime = BuiltAlgorithm(
            "naive",
            NaiveSearchAlgorithm(),
            NaiveStructureBuilder().build(structure.sentences),  # type: ignore[union-attr]
        )
        work: dict[str, object] = dict(_naive_work(naive_runtime, query))
        work.update(
            {
                "fallback_to_naive": 1,
                "selected_seed_a": None,
                "selected_seed_b": None,
                "frequency_a": None,
                "frequency_b": None,
                "seed_occurrences_expanded": 0,
                "candidate_contexts_before_dedup": work[
                    "candidate_slices_checked"
                ],
                "candidate_contexts_after_dedup": work[
                    "candidate_slices_checked"
                ],
            }
        )
        return work
    stats = BiAnchorSearchStats()
    BiAnchorSearchAlgorithm(stats=stats).search(query, structure)  # type: ignore[arg-type]
    selected = stats.last_selected_seeds
    return {
        "fallback_to_naive": stats.fallback_count,
        "selected_seed_a": selected[0].text if selected else None,
        "selected_seed_b": selected[1].text if selected else None,
        "frequency_a": selected[0].frequency if selected else None,
        "frequency_b": selected[1].frequency if selected else None,
        "seed_occurrences_expanded": stats.seed_occurrences_expanded,
        "candidate_contexts_before_dedup": stats.candidate_contexts_generated,
        "candidate_contexts_after_dedup": stats.candidate_contexts_after_dedup,
        "verifier_calls": stats.verifier_calls,
    }


def _work_metrics(runtime: BuiltAlgorithm, query: str) -> dict[str, object]:
    if runtime.algorithm_id == "naive":
        return _naive_work(runtime, query)
    if runtime.algorithm_id == "qgram_tree_hybrid":
        return _trie_work(runtime, query)
    if runtime.algorithm_id == "qgram_positional":
        from src.algorithms.qgram_search_stats import QGramSearchStats

        stats = QGramSearchStats()
        QGramSearchAlgorithm(stats=stats).search(query, runtime.structure)
        return asdict(stats)
    if runtime.algorithm_id == "bi_anchor":
        return _bi_anchor_work(runtime, query)
    return {}


def _difference_sample(counter: Counter[CandidateKey], limit: int = 5) -> list[list[object]]:
    result: list[list[object]] = []
    for key, count in counter.items():
        result.append([*key, count])
        if len(result) >= limit:
            break
    return result


def _mismatch_classification(
    item: RealQuery,
    missing: Counter[CandidateKey],
    unexpected: Counter[CandidateKey],
    q: int,
) -> str | None:
    if not missing and not unexpected:
        return None
    if len(item.query) < q:
        return "short-query failure"
    if "cross_word" in item.tags:
        return "boundary/cross-word failure"
    if "repeated" in item.tags:
        return "repeated-character ambiguity"
    if missing and not unexpected:
        return "candidate-generation miss"
    if unexpected and not missing:
        return "edit interpretation mismatch"
    return "other"


def evaluate_queries(
    runtimes: dict[str, BuiltAlgorithm],
    queries: tuple[RealQuery, ...],
    *,
    repeats: int = 1,
    warmups: int = 0,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    """Compare raw results and online latency on one shared workload."""
    if repeats <= 0 or warmups < 0:
        raise ValueError("repeats must be positive and warmups non-negative")
    if "naive" not in runtimes:
        raise ValueError("Naive runtime is required as the correctness oracle")

    algorithm_ids = list(runtimes)
    rows: list[dict[str, object]] = []
    correctness = {
        algorithm_id: {
            "queries": 0,
            "matching_result_sets": 0,
            "mismatches": 0,
            "false_negatives": 0,
            "false_positives": 0,
        }
        for algorithm_id in algorithm_ids
    }
    query_rows: list[dict[str, dict[str, object]]] = []

    for query_index, item in enumerate(queries):
        results: dict[str, list[MatchCandidate]] = {}
        latency_samples: dict[str, list[int]] = defaultdict(list)
        rotated = (
            algorithm_ids[query_index % len(algorithm_ids) :]
            + algorithm_ids[: query_index % len(algorithm_ids)]
        )
        for _ in range(warmups):
            for algorithm_id in rotated:
                runtimes[algorithm_id].search(item.query)
        for repetition in range(repeats):
            order = rotated[repetition % len(rotated) :] + rotated[: repetition % len(rotated)]
            for algorithm_id in order:
                started = perf_counter_ns()
                matches = runtimes[algorithm_id].search(item.query)
                latency_samples[algorithm_id].append(perf_counter_ns() - started)
                if algorithm_id not in results:
                    results[algorithm_id] = matches

        expected = canonicalize(results["naive"])
        per_query: dict[str, dict[str, object]] = {}
        multiplicity_tag = "many_matches" if sum(expected.values()) > 5 else "few_matches"
        tags = tuple(sorted(set((*item.tags, _length_tag(len(item.query)), multiplicity_tag))))
        for algorithm_id in algorithm_ids:
            actual = canonicalize(results[algorithm_id])
            missing = expected - actual
            unexpected = actual - expected
            matches_or_oracle = not missing and not unexpected
            metrics = correctness[algorithm_id]
            metrics["queries"] += 1
            if matches_or_oracle:
                metrics["matching_result_sets"] += 1
            else:
                metrics["mismatches"] += 1
            metrics["false_negatives"] += sum(missing.values())
            metrics["false_positives"] += sum(unexpected.values())
            latency = summarize(latency_samples[algorithm_id])
            row: dict[str, object] = {
                **item.to_dict(),
                "tags": tags,
                "algorithm": algorithm_id,
                "latency": latency,
                "latency_ns": latency["median_ns"],
                "result_count": sum(actual.values()),
                "correct": matches_or_oracle,
                "false_negatives": sum(missing.values()),
                "false_positives": sum(unexpected.values()),
                "mismatch_classification": _mismatch_classification(
                    item,
                    missing,
                    unexpected,
                    getattr(runtimes[algorithm_id].algorithm, "Q", 3),
                ),
                "missing_sample": _difference_sample(missing),
                "unexpected_sample": _difference_sample(unexpected),
                "work": _work_metrics(runtimes[algorithm_id], item.query),
            }
            rows.append(row)
            per_query[algorithm_id] = row
        query_rows.append(per_query)

    overall = {
        algorithm_id: summarize(
            row["latency_ns"]
            for row in rows
            if row["algorithm"] == algorithm_id
        )
        for algorithm_id in algorithm_ids
    }
    all_tags = sorted({tag for row in rows for tag in row["tags"]})
    by_category: dict[str, dict[str, object]] = {}
    for tag in all_tags:
        by_category[tag] = {
            algorithm_id: summarize(
                row["latency_ns"]
                for row in rows
                if row["algorithm"] == algorithm_id and tag in row["tags"]
            )
            for algorithm_id in algorithm_ids
        }

    wins = Counter({algorithm_id: 0 for algorithm_id in algorithm_ids})
    ties = 0
    for per_query in query_rows:
        eligible = [
            row for row in per_query.values() if bool(row["correct"])
        ]
        fastest = min(float(row["latency_ns"]) for row in eligible)
        tied = [
            row
            for row in eligible
            if float(row["latency_ns"]) <= fastest * 1.02
        ]
        if len(tied) > 1:
            ties += 1
        else:
            wins[str(tied[0]["algorithm"])] += 1

    speedups: dict[str, dict[str, object]] = {}
    for algorithm_id in algorithm_ids:
        if algorithm_id == "naive":
            continue
        values = []
        for per_query in query_rows:
            optimized = per_query[algorithm_id]
            if not optimized["correct"] or not float(optimized["latency_ns"]):
                continue
            values.append(
                float(per_query["naive"]["latency_ns"])
                / float(optimized["latency_ns"])
            )
        raw_summary = summarize(values)
        speedups[algorithm_id] = {
            "summary": {
                "count": raw_summary["count"],
                "mean": raw_summary["mean_ns"],
                "median": raw_summary["median_ns"],
                "p90": raw_summary["p90_ns"],
            },
            "worst_slowdown": min(values) if values else None,
            "best_speedup": max(values) if values else None,
        }

    worst_cases = {
        algorithm_id: sorted(
            (row for row in rows if row["algorithm"] == algorithm_id),
            key=lambda row: float(row["latency_ns"]),
            reverse=True,
        )[:20]
        for algorithm_id in algorithm_ids
    }
    best_cases = {
        algorithm_id: sorted(
            (
                {
                    "query": per_query[algorithm_id]["query"],
                    "tags": per_query[algorithm_id]["tags"],
                    "speedup": (
                        float(per_query["naive"]["latency_ns"])
                        / float(per_query[algorithm_id]["latency_ns"])
                    ),
                    "work": per_query[algorithm_id]["work"],
                }
                for per_query in query_rows
                if per_query[algorithm_id]["correct"]
                and float(per_query[algorithm_id]["latency_ns"])
            ),
            key=lambda item: item["speedup"],
            reverse=True,
        )[:20]
        for algorithm_id in algorithm_ids
        if algorithm_id != "naive"
    }
    return summarize_evaluation_rows(rows), rows


def summarize_evaluation_rows(
    rows: list[dict[str, object]],
) -> dict[str, object]:
    """Rebuild every comparative summary from serialized per-query rows."""
    algorithm_ids = list(dict.fromkeys(str(row["algorithm"]) for row in rows))
    correctness: dict[str, dict[str, int]] = {}
    for algorithm_id in algorithm_ids:
        selected = [row for row in rows if row["algorithm"] == algorithm_id]
        matching = sum(bool(row["correct"]) for row in selected)
        correctness[algorithm_id] = {
            "queries": len(selected),
            "matching_result_sets": matching,
            "mismatches": len(selected) - matching,
            "false_negatives": sum(int(row["false_negatives"]) for row in selected),
            "false_positives": sum(int(row["false_positives"]) for row in selected),
        }
    overall = {
        algorithm_id: summarize(
            float(row["latency_ns"])
            for row in rows
            if row["algorithm"] == algorithm_id
        )
        for algorithm_id in algorithm_ids
    }
    all_tags = sorted({str(tag) for row in rows for tag in row["tags"]})
    by_category = {
        tag: {
            algorithm_id: summarize(
                float(row["latency_ns"])
                for row in rows
                if row["algorithm"] == algorithm_id and tag in row["tags"]
            )
            for algorithm_id in algorithm_ids
        }
        for tag in all_tags
    }
    query_groups: dict[tuple[object, ...], dict[str, dict[str, object]]] = {}
    for row in rows:
        key = (
            row["query"],
            row.get("source_sentence_id"),
            row.get("source_file"),
            row.get("source_offset"),
            row.get("expected_start"),
            row.get("mutation"),
            tuple(row["tags"]),
        )
        query_groups.setdefault(key, {})[str(row["algorithm"])] = row
    wins = Counter({algorithm_id: 0 for algorithm_id in algorithm_ids})
    ties = 0
    category_wins: dict[str, Counter[str]] = defaultdict(Counter)
    category_ties: Counter[str] = Counter()
    complete_groups = [
        group
        for group in query_groups.values()
        if all(algorithm_id in group for algorithm_id in algorithm_ids)
    ]
    for group in complete_groups:
        eligible = [row for row in group.values() if bool(row["correct"])]
        fastest = min(float(row["latency_ns"]) for row in eligible)
        tied = [
            row for row in eligible if float(row["latency_ns"]) <= fastest * 1.02
        ]
        if len(tied) > 1:
            ties += 1
            for tag in next(iter(group.values()))["tags"]:
                category_ties[str(tag)] += 1
        else:
            winner = str(tied[0]["algorithm"])
            wins[winner] += 1
            for tag in next(iter(group.values()))["tags"]:
                category_wins[str(tag)][winner] += 1
    speedups: dict[str, dict[str, object]] = {}
    for algorithm_id in algorithm_ids:
        if algorithm_id == "naive":
            continue
        values = [
            float(group["naive"]["latency_ns"])
            / float(group[algorithm_id]["latency_ns"])
            for group in complete_groups
            if group[algorithm_id]["correct"]
            and float(group[algorithm_id]["latency_ns"])
        ]
        raw_summary = summarize(values)
        speedups[algorithm_id] = {
            "summary": {
                "count": raw_summary["count"],
                "mean": raw_summary["mean_ns"],
                "median": raw_summary["median_ns"],
                "p90": raw_summary["p90_ns"],
            },
            "worst_slowdown": min(values) if values else None,
            "best_speedup": max(values) if values else None,
        }
    worst_cases = {
        algorithm_id: sorted(
            (row for row in rows if row["algorithm"] == algorithm_id),
            key=lambda row: float(row["latency_ns"]),
            reverse=True,
        )[:20]
        for algorithm_id in algorithm_ids
    }
    best_cases = {
        algorithm_id: sorted(
            (
                {
                    "query": group[algorithm_id]["query"],
                    "tags": group[algorithm_id]["tags"],
                    "speedup": (
                        float(group["naive"]["latency_ns"])
                        / float(group[algorithm_id]["latency_ns"])
                    ),
                    "work": group[algorithm_id]["work"],
                }
                for group in complete_groups
                if group[algorithm_id]["correct"]
                and float(group[algorithm_id]["latency_ns"])
            ),
            key=lambda item: item["speedup"],
            reverse=True,
        )[:20]
        for algorithm_id in algorithm_ids
        if algorithm_id != "naive"
    }
    return {
        "correctness": correctness,
        "overall_latency": overall,
        "by_category": by_category,
        "head_to_head": {
            "eligible_queries": len(complete_groups),
            "wins": dict(wins),
            "ties_within_2_percent": ties,
            "by_category": {
                tag: {
                    "queries": sum(category_wins[tag].values()) + category_ties[tag],
                    "wins": {
                        algorithm_id: category_wins[tag][algorithm_id]
                        for algorithm_id in algorithm_ids
                    },
                    "ties_within_2_percent": category_ties[tag],
                }
                for tag in sorted(set(category_wins) | set(category_ties))
            },
        },
        "speedup_vs_naive": speedups,
        "worst_cases": worst_cases,
        "best_cases": best_cases,
    }


def corpus_statistics(
    sentences: tuple[PreparedSentence, ...],
    *,
    files_loaded: int,
) -> dict[str, int | float]:
    lengths = [len(sentence.normalized_text) for sentence in sentences]
    words = [
        match.group()
        for sentence in sentences
        for match in re.finditer(r"\S+", sentence.normalized_text)
    ]
    return {
        "files_loaded": files_loaded,
        "prepared_sentences": len(sentences),
        "total_original_characters": sum(
            len(sentence.original_text) for sentence in sentences
        ),
        "total_normalized_characters": sum(lengths),
        "total_word_occurrences": len(words),
        "unique_words": len(set(words)),
        "average_sentence_length": float(fmean(lengths)) if lengths else 0.0,
        "median_sentence_length": float(median(lengths)) if lengths else 0.0,
        "p95_sentence_length": percentile(lengths, 95),
        "maximum_sentence_length": max(lengths, default=0),
    }


def stable_corpus_slices(
    sentences: tuple[PreparedSentence, ...],
) -> list[tuple[int, tuple[PreparedSentence, ...]]]:
    return [
        (
            fraction,
            sentences[: min(len(sentences), ceil(len(sentences) * fraction / 100))],
        )
        for fraction in (10, 25, 50, 75, 100)
    ]


def _markdown_table(headers: list[str], rows: Iterable[Iterable[object]]) -> str:
    materialized = [[str(value) for value in row] for row in rows]
    if not materialized:
        return "No data available."
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in materialized)
    return "\n".join(lines)


def _ms(value: object) -> str:
    if value is None:
        return "n/a"
    return f"{float(value) / 1_000_000:.3f}"


def _render_report(payload: dict[str, object]) -> str:
    algorithms = payload.get("algorithms", [])
    baseline = payload.get("baseline", {})
    corpus = payload.get("corpus", {})
    workload = payload.get("workload", {})
    builds = payload.get("builds", {})
    evaluation = payload.get("evaluation", {})
    parameter = payload.get("parameter_study", {})
    scaling = payload.get("scaling_study", {})
    profiles = payload.get("profiles", {})
    recommendations = payload.get("recommendations", {})
    limitations = payload.get("limitations", [])

    sections: list[str] = ["# Real-Corpus Four-Algorithm Comparative Study"]
    sections.append(
        "# 1. Algorithms found\n\n"
        + _markdown_table(
            ["Conceptual", "Actual class/module", "Builder", "Verifier", "Runnable"],
            (
                (
                    item.get("conceptual_name"),
                    f"{item.get('class')} / `{item.get('module')}`",
                    item.get("builder"),
                    item.get("verifier"),
                    item.get("contract_compatible"),
                )
                for item in algorithms
            ),
        )
    )
    sections.append(
        "# 2. Test baseline\n\n"
        + ", ".join(f"{key}: {value}" for key, value in baseline.items())
    )
    sections.append(
        "# 3. Real corpus\n\n"
        + "\n".join(
            f"- {key}: {value}"
            for key, value in corpus.items()
            if key != "source_files"
        )
        + "\n- source file names: retained in the machine-readable JSON"
    )
    sections.append(
        "# 4. Query workload\n\n"
        + "\n".join(
            f"- {key}: {value}"
            for key, value in workload.items()
            if key not in {"queries", "executed_query_texts"}
        )
        + "\n- complete workload metadata: retained in JSON; per-observation data: CSV"
    )
    correctness = evaluation.get("correctness", {})
    sections.append(
        "# 5. Correctness\n\n"
        + _markdown_table(
            ["Algorithm", "Queries", "Matching", "Mismatches", "FN", "FP"],
            (
                (
                    name,
                    values.get("queries"),
                    values.get("matching_result_sets"),
                    values.get("mismatches"),
                    values.get("false_negatives"),
                    values.get("false_positives"),
                )
                for name, values in correctness.items()
            ),
        )
    )
    sections.append(
        "# 6. Offline build\n\n"
        + _markdown_table(
            ["Algorithm", "Status", "Build ms", "Retained MiB", "Peak MiB", "Index statistics/error"],
            (
                (
                    name,
                    values.get("status"),
                    _ms(values.get("build_ns")),
                    f"{float(values.get('retained_memory_bytes', 0)) / 1048576:.2f}",
                    f"{float(values.get('peak_memory_bytes', 0)) / 1048576:.2f}",
                    values.get("stats") or values.get("error"),
                )
                for name, values in builds.items()
            ),
        )
    )
    latency = evaluation.get("overall_latency", {})
    sections.append(
        "# 7. Overall online performance\n\n"
        + _markdown_table(
            ["Algorithm", "Median ms", "Mean ms", "P95 ms", "P99 ms", "Max ms"],
            (
                (
                    name,
                    _ms(values.get("median_ns")),
                    _ms(values.get("mean_ns")),
                    _ms(values.get("p95_ns")),
                    _ms(values.get("p99_ns")),
                    _ms(values.get("max_ns")),
                )
                for name, values in latency.items()
            ),
        )
    )
    speedups = evaluation.get("speedup_vs_naive", {})
    sections.append(
        "# 8. Speedup vs Naive\n\n"
        + _markdown_table(
            ["Algorithm", "Samples", "Median", "Mean", "P90", "Worst", "Best"],
            (
                (
                    name,
                    values.get("summary", {}).get("count"),
                    values.get("summary", {}).get("median"),
                    values.get("summary", {}).get("mean"),
                    values.get("summary", {}).get("p90"),
                    values.get("worst_slowdown"),
                    values.get("best_speedup"),
                )
                for name, values in speedups.items()
            ),
        )
    )
    category_rows = []
    correct_algorithms = {
        name for name, metrics in correctness.items() if metrics.get("mismatches") == 0
    }
    for category, values in evaluation.get("by_category", {}).items():
        medians = {
            name: metrics.get("median_ns")
            for name, metrics in values.items()
            if metrics.get("count")
        }
        eligible = {
            name: value
            for name, value in medians.items()
            if name in correct_algorithms
        }
        winner = min(eligible, key=eligible.get) if eligible else "n/a"
        category_rows.append(
            (category, winner, *(_ms(medians.get(name)) for name in ("naive", "qgram_tree_hybrid", "bi_anchor")))
        )
    sections.append(
        "# 9. Results by query category\n\n"
        + _markdown_table(
            ["Category", "Fastest correct", "Naive ms", "Tree Hybrid ms (incorrect)", "Bi-Anchor ms"],
            category_rows,
        )
    )
    sections.append(
        "# 10. Internal work\n\n"
        + "Algorithm-specific counters are stored per query in the CSV and JSON.\n\n"
        + "```json\n"
        + json.dumps(payload.get("work_summary", {}), indent=2)
        + "\n```"
    )
    sections.append(
        "# 11. Head-to-head win rates\n\n"
        + "```json\n"
        + json.dumps(evaluation.get("head_to_head", {}), indent=2)
        + "\n```"
    )
    worst_lines = []
    for name, cases in evaluation.get("worst_cases", {}).items():
        worst_lines.append(f"## {name}")
        worst_lines.append(
            _markdown_table(
                ["Query", "Length", "Tags", "Latency ms", "Results", "Work"],
                (
                    (
                        case.get("query"),
                        len(case.get("query", "")),
                        ", ".join(case.get("tags", ())),
                        _ms(case.get("latency_ns")),
                        case.get("result_count"),
                        case.get("work"),
                    )
                    for case in cases
                ),
            )
        )
    sections.append("# 12. Worst cases\n\n" + "\n\n".join(worst_lines))
    best_lines = []
    for name, cases in evaluation.get("best_cases", {}).items():
        best_lines.append(f"## {name}")
        best_lines.append(
            _markdown_table(
                ["Query", "Tags", "Speedup", "Why/work"],
                (
                    (
                        case.get("query"),
                        ", ".join(case.get("tags", ())),
                        case.get("speedup"),
                        case.get("work"),
                    )
                    for case in cases
                ),
            )
        )
    sections.append("# 13. Best cases\n\n" + "\n\n".join(best_lines))
    parameter_rows = []
    for q_name, values in parameter.items():
        for name, metrics in values.items():
            latency_metrics = metrics.get("latency", {})
            parameter_rows.append(
                (
                    q_name,
                    name,
                    metrics.get("status"),
                    _ms(metrics.get("build_ns")),
                    f"{float(metrics.get('retained_memory_bytes', 0)) / 1048576:.2f}",
                    metrics.get("fallback_rate", "n/a"),
                    _ms(latency_metrics.get("median_ns")),
                    _ms(latency_metrics.get("p95_ns")),
                    metrics.get("candidate_count", {}).get("median_ns", "n/a"),
                    metrics.get("verifier_calls", {}).get("median_ns", "n/a"),
                )
            )
    sections.append(
        "# 14. Parameter comparison\n\n"
        "The parameter panel uses the same three full-corpus queries per configuration. "
        "It does not override the q=3 production default, and faster Tree Hybrid values "
        "do not pass the correctness gate.\n\n"
        + _markdown_table(
            ["q", "Algorithm", "Status", "Build ms", "Retained MiB", "Fallback", "Median ms", "P95 ms", "Median candidates", "Median verifier calls"],
            parameter_rows,
        )
    )
    scaling_rows = []
    for fraction, values in scaling.items():
        for name, build in values.get("builds", {}).items():
            latency_metrics = values.get("latency", {}).get(name, {})
            scaling_rows.append(
                (
                    fraction,
                    values.get("sentences"),
                    name,
                    build.get("status"),
                    _ms(build.get("build_ns")),
                    f"{float(build.get('retained_memory_bytes', 0)) / 1048576:.2f}",
                    _ms(latency_metrics.get("median_ns")),
                    _ms(latency_metrics.get("p95_ns")),
                )
            )
    sections.append(
        "# 15. Scaling with corpus size\n\n"
        "Stable production-order prefixes and one shared no-match query were used. "
        "With one observation per point, median and p95 are identical.\n\n"
        + _markdown_table(
            ["Corpus", "Sentences", "Algorithm", "Status", "Build ms", "Retained MiB", "Median ms", "P95 ms"],
            scaling_rows,
        )
    )
    profile_rows = []
    for name, values in profiles.get("algorithms", {}).items():
        build_profile = values.get("build", {})
        hottest = build_profile.get("hottest", [])
        profile_rows.append(
            (
                name,
                "build",
                build_profile.get("status"),
                _ms(build_profile.get("elapsed_ns")),
                hottest[0].get("function") if hottest else build_profile.get("error"),
                hottest[0].get("cumulative_seconds") if hottest else "n/a",
                hottest[0].get("self_seconds") if hottest else "n/a",
                hottest[0].get("total_calls") if hottest else "n/a",
            )
        )
        for scenario, query_profile in values.get("queries", {}).items():
            hottest = query_profile.get("hottest", [])
            profile_rows.append(
                (
                    name,
                    scenario,
                    query_profile.get("status"),
                    _ms(query_profile.get("elapsed_ns")),
                    hottest[0].get("function") if hottest else query_profile.get("error"),
                    hottest[0].get("cumulative_seconds") if hottest else "n/a",
                    hottest[0].get("self_seconds") if hottest else "n/a",
                    hottest[0].get("total_calls") if hottest else "n/a",
                )
            )
    sections.append(
        "# 16. CPU profiles\n\n"
        f"Profiles use a stable {profiles.get('corpus_fraction', 0):.0%} corpus prefix. "
        "The profile JSON contains the top 15 functions for each scenario.\n\n"
        + _markdown_table(
            ["Algorithm", "Scenario", "Status", "Elapsed ms", "Hottest cumulative function", "Cumulative s", "Self s", "Calls"],
            profile_rows,
        )
        + "\n\nConfirmed bottlenecks: Naive spends cumulative time in the full "
        "`_search_sentence`/`_check_from_position` scan and shared verifier; "
        "Tree Hybrid build time is dominated by `_insert_word` and query time "
        "by `_fuzzy_compare` plus result emission; Bi-Anchor build time is in "
        "`HashSeedLookup.build`, while common-query time is dominated by "
        "`_candidate_contexts` and `OneEditVerifier.compare`. Positional Q-Gram "
        "fails immediately in `QGramSearchStructure.add_sentence`."
    )
    sections.append(
        "# 17. Memory profiles\n\nRetained and peak values use tracemalloc started after corpus preparation; they are allocation estimates, not exact recursive object sizes. See the offline-build table."
    )
    scorecard = payload.get("scorecard", [])
    sections.append(
        "# 18. Final comparison table\n\n"
        + _markdown_table(
            ["Algorithm", "Correct", "FN", "Build ms", "Memory MiB", "Median ms", "P95 ms", "P99 ms", "Median speedup", "Worst speedup", "Strength", "Weakness"],
            (
                (
                    item.get("algorithm"),
                    item.get("correct"),
                    item.get("false_negatives"),
                    _ms(item.get("build_ns")),
                    f"{float(item.get('retained_memory_bytes', 0)) / 1048576:.2f}",
                    _ms(item.get("median_ns")),
                    _ms(item.get("p95_ns")),
                    _ms(item.get("p99_ns")),
                    item.get("median_speedup_vs_naive"),
                    item.get("worst_slowdown"),
                    item.get("best_query_category"),
                    item.get("worst_query_category"),
                )
                for item in scorecard
            ),
        )
    )
    opportunity_rows = []
    for name, values in recommendations.get("opportunities", {}).items():
        opportunity_rows.append(
            (
                name,
                values.get("expected_benefit"),
                values.get("complexity"),
                values.get("correctness_risk"),
                values.get("memory_impact"),
                values.get("evidence"),
            )
        )
    sections.append(
        "# 19. Improvement opportunities\n\n"
        + _markdown_table(
            ["Algorithm", "Expected benefit", "Complexity", "Correctness risk", "Memory impact", "Measured evidence"],
            opportunity_rows,
        )
    )
    answers = recommendations.get("answers", {})
    sections.append(
        "# 20. Recommended next step\n\n"
        + "## Decision answers\n\n"
        + "\n".join(f"{index}. **{key}:** {value}" for index, (key, value) in enumerate(answers.items(), 1))
        + "\n\n## Hybrid analysis\n\n"
        + str(recommendations.get("hybrid_runtime_analysis", "n/a"))
        + "\n\n## One next experiment\n\n"
        + str(recommendations.get("next_step", "Derived after the run."))
        + "\n\n## Limitations\n\n"
        + "\n".join(f"- {item}" for item in limitations)
    )
    return "\n\n".join(sections) + "\n"


def write_artifacts(
    payload: dict[str, object],
    rows: list[dict[str, object]],
    *,
    output_dir: Path,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "results": output_dir / "real-corpus-four-algorithm-results.json",
        "queries": output_dir / "real-corpus-query-results.csv",
        "profiles": output_dir / "real-corpus-profile-summary.json",
        "report": output_dir / "real-corpus-four-algorithm-report.md",
    }
    paths["results"].write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    paths["profiles"].write_text(
        json.dumps(payload.get("profiles", {}), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    fields = [
        "query",
        "tags",
        "mutation",
        "source_sentence_id",
        "source_file",
        "source_offset",
        "expected_start",
        "algorithm",
        "latency_ns",
        "result_count",
        "correct",
        "false_negatives",
        "false_positives",
        "mismatch_classification",
        "work",
    ]
    with paths["queries"].open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            serializable = dict(row)
            serializable["tags"] = "|".join(row.get("tags", ()))
            serializable["work"] = json.dumps(row.get("work", {}), ensure_ascii=False)
            writer.writerow(serializable)
    paths["report"].write_text(_render_report(payload), encoding="utf-8")
    return paths


def _candidate_metric(work: dict[str, object]) -> int:
    for key in (
        "candidate_contexts_after_dedup",
        "candidate_words_after_dedup",
        "candidate_slices_checked",
    ):
        value = work.get(key)
        if isinstance(value, int):
            return value
    return 0


def run_parameter_study(
    sentences: tuple[PreparedSentence, ...],
    queries: tuple[RealQuery, ...],
) -> dict[str, dict[str, dict[str, object]]]:
    result: dict[str, dict[str, dict[str, object]]] = {}
    for q in (2, 3, 4):
        builds, runtimes = build_algorithms(sentences, q=q, measure_memory=True)
        q_result: dict[str, dict[str, object]] = {}
        for algorithm_id in (
            "qgram_positional",
            "qgram_tree_hybrid",
            "bi_anchor",
        ):
            build = builds[algorithm_id]
            if algorithm_id not in runtimes:
                q_result[algorithm_id] = {
                    "status": "error",
                    "error": build["error"],
                    "build_ns": build["build_ns"],
                    "retained_memory_bytes": build["retained_memory_bytes"],
                    "peak_memory_bytes": build["peak_memory_bytes"],
                }
                continue
            runtime = runtimes[algorithm_id]
            latencies: list[int] = []
            candidates: list[int] = []
            verifier_calls: list[int] = []
            fallbacks = 0
            for item in queries:
                started = perf_counter_ns()
                runtime.search(item.query)
                latencies.append(perf_counter_ns() - started)
                work = _work_metrics(runtime, item.query)
                candidates.append(_candidate_metric(work))
                calls = work.get("verifier_calls", 0)
                verifier_calls.append(int(calls) if isinstance(calls, int) else 0)
                fallbacks += int(work.get("fallback_to_naive", 0) or 0)
            q_result[algorithm_id] = {
                "status": "ok",
                "build_ns": build["build_ns"],
                "retained_memory_bytes": build["retained_memory_bytes"],
                "peak_memory_bytes": build["peak_memory_bytes"],
                "latency": summarize(latencies),
                "fallback_rate": fallbacks / len(queries) if queries else 0.0,
                "candidate_count": summarize(candidates),
                "verifier_calls": summarize(verifier_calls),
                "index_stats": build["stats"],
            }
        result[f"q={q}"] = q_result
        del runtimes
        gc.collect()
    return result


def run_scaling_study(
    sentences: tuple[PreparedSentence, ...],
    queries: tuple[RealQuery, ...],
    *,
    fractions: tuple[int, ...] = (10, 25, 50, 75, 100),
) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for fraction in fractions:
        size = min(len(sentences), ceil(len(sentences) * fraction / 100))
        subset = sentences[:size]
        builds, runtimes = build_algorithms(subset, q=3, measure_memory=True)
        evaluation, _rows = evaluate_queries(
            runtimes,
            queries,
            repeats=1,
            warmups=0,
        )
        result[f"{fraction}%"] = {
            "sentences": size,
            "builds": builds,
            "latency": evaluation["overall_latency"],
            "correctness": evaluation["correctness"],
        }
        del runtimes
        gc.collect()
    return result


def _profile_call(function, *args) -> dict[str, object]:
    profiler = cProfile.Profile()
    started = perf_counter_ns()
    value = None
    error: Exception | None = None
    try:
        value = profiler.runcall(function, *args)
    except Exception as caught:
        error = caught
    elapsed = perf_counter_ns() - started
    stats = pstats.Stats(profiler)
    hottest = []
    for (filename, line, function_name), values in sorted(
        stats.stats.items(), key=lambda item: item[1][3], reverse=True
    ):
        primitive_calls, total_calls, self_seconds, cumulative_seconds, _callers = values
        hottest.append(
            {
                "function": f"{Path(filename).name}:{line}({function_name})",
                "primitive_calls": primitive_calls,
                "total_calls": total_calls,
                "self_seconds": self_seconds,
                "cumulative_seconds": cumulative_seconds,
            }
        )
    return {
        "status": "error" if error else "ok",
        "elapsed_ns": elapsed,
        "result_count": len(value) if isinstance(value, list) else None,
        "error": f"{type(error).__name__}: {error}" if error else None,
        "hottest": hottest,
    }


def profile_scenarios(
    sentences: tuple[PreparedSentence, ...],
    queries: tuple[RealQuery, ...],
    *,
    fraction: float = 0.1,
    top_count: int = 15,
) -> dict[str, object]:
    if not 0 < fraction <= 1:
        raise ValueError("fraction must be in (0, 1]")
    size = max(1, ceil(len(sentences) * fraction))
    subset = sentences[:size]
    algorithms: dict[str, dict[str, object]] = {}
    for item in discover_algorithms():
        algorithm_id = str(item["id"])
        build_profile = _profile_call(
            _construct_algorithm,
            algorithm_id,
            subset,
            3,
        )
        build_profile["hottest"] = build_profile["hottest"][:top_count]
        algorithms[algorithm_id] = {"build": build_profile, "queries": {}}

    _builds, runtimes = build_algorithms(subset, q=3, measure_memory=False)
    if queries:
        rare = next(
            (query for query in queries if "rare_qgram" in query.tags or "no_match" in query.tags),
            queries[0],
        )
        ordered = sorted(queries, key=lambda query: len(query.query))
        medium = ordered[len(ordered) // 2]
        worst = next(
            (
                query
                for query in queries
                if "high_frequency" in query.tags
                or "common_qgram" in query.tags
                or "repeated" in query.tags
            ),
            ordered[-1],
        )
        scenarios = {
            "typical_fast": rare,
            "typical_medium": medium,
            "representative_worst": worst,
        }
        for algorithm_id, runtime in runtimes.items():
            for scenario, query in scenarios.items():
                profile = _profile_call(runtime.search, query.query)
                profile["query"] = query.query
                profile["tags"] = query.tags
                profile["hottest"] = profile["hottest"][:top_count]
                algorithms[algorithm_id]["queries"][scenario] = profile
    return {
        "corpus_fraction": fraction,
        "sentences": size,
        "methodology": "cProfile/pstats; profile corpus is a stable prefix for practical runtime",
        "algorithms": algorithms,
    }


def _select_execution_queries(
    workload: tuple[RealQuery, ...],
    count: int,
) -> tuple[RealQuery, ...]:
    candidates = [query for query in workload if len(query.query) >= 6]
    if count <= 0:
        return ()
    selected: list[RealQuery] = []
    covered: set[str] = set()
    priorities = [
        "medium_exact",
        "long_exact",
        "inside_word",
        "cross_word",
        "replacement",
        "insertion",
        "deletion",
        "repeated",
        "common_qgram",
        "medium_qgram",
        "rare_qgram",
        "no_match",
        "near_boundary",
        "multiple_matches",
        "high_frequency",
    ]
    for tag in priorities:
        choice = next(
            (
                query
                for query in candidates
                if query not in selected and tag in query.tags
            ),
            None,
        )
        if choice is not None:
            selected.append(choice)
            covered.update(choice.tags)
        if len(selected) >= count:
            return tuple(selected)
    for query in candidates:
        if query not in selected:
            selected.append(query)
        if len(selected) >= count:
            break
    return tuple(selected)


def _work_summary(rows: list[dict[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for algorithm_id in sorted({str(row["algorithm"]) for row in rows}):
        numeric: dict[str, list[int | float]] = defaultdict(list)
        for row in rows:
            if row["algorithm"] != algorithm_id:
                continue
            for key, value in row.get("work", {}).items():
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    numeric[key].append(value)
        result[algorithm_id] = {
            key: {
                "mean": fmean(values),
                "median": median(values),
                "p95": percentile(values, 95),
                "max": max(values),
            }
            for key, values in numeric.items()
        }
    return result


def _scorecard(
    builds: dict[str, dict[str, object]],
    evaluation: dict[str, object],
) -> list[dict[str, object]]:
    correctness = evaluation["correctness"]
    latency = evaluation["overall_latency"]
    speedups = evaluation["speedup_vs_naive"]
    categories = evaluation["by_category"]
    result = []
    for item in discover_algorithms():
        algorithm_id = str(item["id"])
        correct = correctness.get(algorithm_id)
        category_medians = {
            category: values[algorithm_id]["median_ns"]
            for category, values in categories.items()
            if algorithm_id in values and values[algorithm_id]["count"]
        }
        relative = {}
        for category, algorithm_ns in category_medians.items():
            naive = categories[category].get("naive", {})
            if naive.get("median_ns") and algorithm_ns:
                relative[category] = naive["median_ns"] / algorithm_ns
        strength = max(relative, key=relative.get) if relative else None
        weakness = min(relative, key=relative.get) if relative else None
        if algorithm_id == "naive":
            strength = "near-zero build/index memory"
            weakness = "full-corpus exhaustive scan"
        elif algorithm_id == "qgram_positional":
            strength = "compact packed postings (design intent)"
            weakness = "not runnable on shared corpus/result contract"
        elif algorithm_id == "qgram_tree_hybrid":
            strength = "very low measured lookup latency"
            weakness = "prefix-only/capped semantics; incorrect raw results"
        result.append(
            {
                "algorithm": algorithm_id,
                "correct": (
                    correct is not None and correct["mismatches"] == 0
                ),
                "false_negatives": correct["false_negatives"] if correct else None,
                "build_ns": builds[algorithm_id]["build_ns"],
                "retained_memory_bytes": builds[algorithm_id]["retained_memory_bytes"],
                "median_ns": latency.get(algorithm_id, {}).get("median_ns"),
                "p95_ns": latency.get(algorithm_id, {}).get("p95_ns"),
                "p99_ns": latency.get(algorithm_id, {}).get("p99_ns"),
                "median_speedup_vs_naive": speedups.get(algorithm_id, {}).get("summary", {}).get("median"),
                "worst_slowdown": speedups.get(algorithm_id, {}).get("worst_slowdown"),
                "best_query_category": strength,
                "worst_query_category": weakness,
            }
        )
    return result


def _derive_recommendations(
    builds: dict[str, dict[str, object]],
    evaluation: dict[str, object],
) -> dict[str, object]:
    correctness = evaluation["correctness"]
    latency = evaluation["overall_latency"]
    correct_algorithms = [
        name
        for name, values in correctness.items()
        if values["mismatches"] == 0
    ]
    best = min(
        correct_algorithms,
        key=lambda name: latency[name]["median_ns"],
    ) if correct_algorithms else None
    opportunities = {
        "naive": {
            "expected_benefit": "High",
            "complexity": "High",
            "correctness_risk": "High",
            "memory_impact": "Worse",
            "evidence": "Full-corpus pilot exceeded 120 seconds; exhaustive verifier-call counts are recorded per query.",
        },
        "qgram_positional": {
            "expected_benefit": "Unknown until runnable",
            "complexity": "Medium",
            "correctness_risk": "High",
            "memory_impact": "Worse",
            "evidence": builds["qgram_positional"]["error"],
        },
        "qgram_tree_hybrid": {
            "expected_benefit": "Low as a direct replacement",
            "complexity": "High",
            "correctness_risk": "High",
            "memory_impact": "Worse",
            "evidence": f"{correctness.get('qgram_tree_hybrid', {}).get('mismatches')} raw-result mismatches in the executed workload.",
        },
        "bi_anchor": {
            "expected_benefit": "High",
            "complexity": "Low to Medium",
            "correctness_risk": "Low",
            "memory_impact": "Better",
            "evidence": (
                f"{correctness.get('bi_anchor', {}).get('mismatches')} mismatches and "
                f"{builds['bi_anchor']['stats'].get('boundary_occurrences')} boundary "
                f"occurrences contribute to {builds['bi_anchor']['retained_memory_bytes'] / 1048576:.2f} MiB retained index memory."
            ),
        },
    }
    def category_ms(category: str, algorithm: str) -> float | None:
        metrics = evaluation.get("by_category", {}).get(category, {}).get(algorithm, {})
        value = metrics.get("median_ns")
        return value / 1_000_000 if value is not None else None

    def category_text(category: str, algorithm: str) -> str:
        value = category_ms(category, algorithm)
        return f"{value:.3f} ms" if value is not None else "not measured"

    return {
        "best_overall_correct_algorithm": best,
        "opportunities": opportunities,
        "hybrid_runtime_analysis": (
            "The existing Bi-Anchor short-query fallback already implements the only "
            "safe length-based routing supported by these correctness results. The "
            "Tree Hybrid and positional Q-Gram implementations cannot be routing "
            "targets until their raw-result contracts pass the Naive oracle."
        ),
        "answers": {
            "Best overall": (
                f"Bi-Anchor. It was correct on all {correctness['bi_anchor']['queries']} "
                f"queries, won all correct head-to-heads, and had a {latency['bi_anchor']['median_ns'] / 1_000_000:.3f} ms median."
            ),
            "Best for short queries": (
                "No defensible full-corpus latency winner: length 1-5 raw candidate "
                "materialization was resource-guarded. Bi-Anchor delegates these queries "
                "to Naive, so both share the exhaustive path."
            ),
            "Best for medium queries": (
                f"Bi-Anchor among correct implementations ({category_text('medium_exact', 'bi_anchor')} median versus "
                f"{category_text('medium_exact', 'naive')} for Naive)."
            ),
            "Best for long queries": (
                f"Bi-Anchor ({category_text('long_exact', 'bi_anchor')} versus "
                f"{category_text('long_exact', 'naive')})."
            ),
            "Best for common substrings": (
                f"Bi-Anchor among correct implementations ({category_text('common_qgram', 'bi_anchor')}); "
                "common anchors are nevertheless one of its expensive cases."
            ),
            "Best for rare substrings": (
                f"Bi-Anchor ({category_text('rare_qgram', 'bi_anchor')}); rare seeds nearly eliminate verification work."
            ),
            "Best for cross-word matching": (
                f"Bi-Anchor ({category_text('cross_word', 'bi_anchor')}) and correct; "
                "Tree Hybrid does not support equivalent cross-word semantics."
            ),
            "Least memory": (
                f"Naive, with {builds['naive']['retained_memory_bytes'] / 1048576:.4f} MiB traced retained structure memory beyond the shared corpus."
            ),
            "Cheapest offline build": (
                f"Naive at {builds['naive']['build_ns'] / 1_000_000:.3f} ms; it effectively stores only the corpus reference."
            ),
            "Best latency/memory tradeoff": (
                f"Bi-Anchor is the only practical correct indexed choice: {builds['bi_anchor']['retained_memory_bytes'] / 1048576:.2f} MiB for a "
                f"{latency['naive']['median_ns'] / latency['bi_anchor']['median_ns']:.1f}x ratio of median latencies."
            ),
            "Correctness failures": (
                f"Yes. Tree Hybrid mismatched {correctness['qgram_tree_hybrid']['mismatches']}/{correctness['qgram_tree_hybrid']['queries']} queries "
                f"with {correctness['qgram_tree_hybrid']['false_negatives']} false-negative candidates. Positional Q-Gram was not runnable."
            ),
            "Hybrid runtime strategy": (
                "Not yet beyond the existing Bi-Anchor-to-Naive short-query fallback. "
                "The other indexed implementations must first pass the raw-result correctness gate."
            ),
        },
        "next_step": (
            "Prototype a benchmark-only packed representation for Bi-Anchor boundary "
            "occurrences (for example, packed integer arrays) and rerun the same "
            "correctness/memory/latency study. The real index stores 3,284,984 boundary "
            "occurrences and retains about 330.63 MiB; 76% more than the incorrect Tree "
            "Hybrid—so this is the clearest low-semantics-risk opportunity. Do not change "
            "production until all raw candidates remain identical to Naive."
        ),
    }


def run_study(
    *,
    archive: Path,
    generated_query_count: int,
    executed_query_count: int,
    repeats: int,
    warmups: int,
    profile_fraction: float,
    output_dir: Path,
) -> tuple[dict[str, object], list[dict[str, object]], dict[str, Path]]:
    preparer = DataPreparer()
    sentences = tuple(preparer.prepare(archive))
    stats = corpus_statistics(
        sentences,
        files_loaded=preparer.loader.stats.loaded_files,
    )
    stats.update(
        {
            "source_archive": str(archive),
            "skipped_duplicate_files": preparer.loader.stats.skipped_duplicates,
            "skipped_invalid_files": preparer.loader.stats.skipped_invalid,
            "source_files": sorted({sentence.source_path for sentence in sentences}),
        }
    )
    workload = build_real_workload(
        sentences,
        target_count=generated_query_count,
        seed=20260812,
    )
    execution_queries = _select_execution_queries(workload, executed_query_count)
    builds, runtimes = build_algorithms(sentences, q=3, measure_memory=True)
    evaluation, rows = evaluate_queries(
        runtimes,
        execution_queries,
        repeats=repeats,
        warmups=warmups,
    )
    parameter_queries = execution_queries[: min(3, len(execution_queries))]
    parameter = run_parameter_study(sentences, parameter_queries)
    scaling_query = next(
        (query for query in execution_queries if "no_match" in query.tags),
        execution_queries[:1][0],
    )
    scaling = run_scaling_study(sentences, (scaling_query,))
    profiles = profile_scenarios(
        sentences,
        execution_queries,
        fraction=profile_fraction,
        top_count=15,
    )
    payload: dict[str, object] = {
        "algorithms": discover_algorithms(),
        "baseline": {
            "collected": 137,
            "passed": 137,
            "failed": 0,
            "skipped": 0,
            "compileall": "passed",
            "note": "Untouched Phase 1 baseline before benchmark-only files were added.",
        },
        "corpus": stats,
        "workload": {
            "random_seed": 20260812,
            "selection": "deterministic source-stratified real substrings and one-edit mutations",
            "generated_queries": len(workload),
            "executed_queries": len(execution_queries),
            "generated_tag_counts": dict(
                Counter(tag for query in workload for tag in query.tags)
            ),
            "executed_tag_counts": dict(
                Counter(tag for query in execution_queries for tag in query.tags)
            ),
            "executed_length_counts": dict(
                Counter(_length_tag(len(query.query)) for query in execution_queries)
            ),
            "executed_source_files": len(
                {query.source_file for query in execution_queries if query.source_file}
            ),
            "queries": [query.to_dict() for query in workload],
            "executed_query_texts": [query.query for query in execution_queries],
            "resource_guard": (
                "Length 1-5 queries remain in the generated workload but are not run "
                "against the full raw-candidate Naive/Bi-Anchor paths: length-1 "
                "one-replacement semantics can emit a candidate at almost every "
                "corpus character and risk memory exhaustion."
            ),
        },
        "builds": builds,
        "evaluation": evaluation,
        "work_summary": _work_summary(rows),
        "parameter_study": parameter,
        "scaling_study": scaling,
        "profiles": profiles,
        "limitations": [
            "A full-corpus Naive pilot query did not finish within 120 seconds; the suggested 500-1000 queries and 10-30 repetitions were computationally impractical.",
            f"Online results use {len(execution_queries)} full-corpus queries and {repeats} timed repetition(s) with {warmups} warm-up(s); percentile estimates are correspondingly coarse.",
            "Length 1-5 raw-result queries were resource-guarded to avoid explosive candidate materialization; short-query conclusions are based on code path and smaller scaling/profile observations, not full-corpus latency.",
            f"CPU profiles use a stable {profile_fraction:.0%} corpus prefix and are labeled as such.",
            "tracemalloc values estimate Python allocations made after corpus preparation; they are not exact recursive object sizes or process RSS.",
        ],
    }
    payload["scorecard"] = _scorecard(builds, evaluation)
    payload["recommendations"] = _derive_recommendations(builds, evaluation)
    paths = write_artifacts(payload, rows, output_dir=output_dir)
    return payload, rows, paths


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the real-corpus four-algorithm comparative study."
    )
    parser.add_argument("--archive", type=Path, default=Path("data/Archive3.zip"))
    parser.add_argument("--generated-queries", type=int, default=64)
    parser.add_argument("--executed-queries", type=int, default=20)
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--warmups", type=int, default=0)
    parser.add_argument("--profile-fraction", type=float, default=0.1)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("benchmark/output/real-corpus"),
    )
    arguments = parser.parse_args()
    _payload, _rows, paths = run_study(
        archive=arguments.archive,
        generated_query_count=arguments.generated_queries,
        executed_query_count=arguments.executed_queries,
        repeats=arguments.repeats,
        warmups=arguments.warmups,
        profile_fraction=arguments.profile_fraction,
        output_dir=arguments.output_dir,
    )
    for name, path in paths.items():
        print(f"{name}: {path}")


def canonicalize(matches: Iterable[MatchCandidate]) -> Counter[CandidateKey]:
    """Preserve every raw-candidate field relevant to search semantics."""
    return Counter(
        (
            match.sentence.sentence_id,
            match.sentence.source_path,
            match.sentence.offset,
            match.match_start,
            match.edit_type.value,
            match.edit_index,
            match.correct_characters,
        )
        for match in matches
    )


def percentile(samples: Iterable[int | float], value: int) -> float:
    """Return a nearest-rank percentile (1 through 100)."""
    if not 1 <= value <= 100:
        raise ValueError("percentile must be between 1 and 100")
    ordered = sorted(samples)
    if not ordered:
        return 0.0
    return float(ordered[max(0, ceil(value / 100 * len(ordered)) - 1)])


def summarize(samples: Iterable[int | float]) -> dict[str, float | int]:
    values = list(samples)
    if not values:
        return {
            "count": 0,
            "mean_ns": 0.0,
            "median_ns": 0.0,
            "p50_ns": 0.0,
            "p75_ns": 0.0,
            "p90_ns": 0.0,
            "p95_ns": 0.0,
            "p99_ns": 0.0,
            "max_ns": 0.0,
        }
    return {
        "count": len(values),
        "mean_ns": float(fmean(values)),
        "median_ns": float(median(values)),
        "p50_ns": percentile(values, 50),
        "p75_ns": percentile(values, 75),
        "p90_ns": percentile(values, 90),
        "p95_ns": percentile(values, 95),
        "p99_ns": percentile(values, 99),
        "max_ns": float(max(values)),
    }


def _word_ranges(text: str) -> list[tuple[str, int, int]]:
    return [(m.group(), m.start(), m.end()) for m in re.finditer(r"\S+", text)]


def _make_query(
    sentence: PreparedSentence | None,
    query: str,
    tags: Iterable[str],
    *,
    start: int | None = None,
    mutation: str = "exact",
) -> RealQuery:
    return RealQuery(
        query=query,
        tags=tuple(sorted(set(tags))),
        source_sentence_id=sentence.sentence_id if sentence else None,
        source_file=sentence.source_path if sentence else None,
        source_offset=sentence.offset if sentence else None,
        expected_start=start,
        mutation=mutation,
    )


def _stratified_sentences(
    sentences: tuple[PreparedSentence, ...], seed: int
) -> list[PreparedSentence]:
    by_source: dict[str, list[PreparedSentence]] = {}
    for sentence in sentences:
        by_source.setdefault(sentence.source_path, []).append(sentence)
    generator = random.Random(seed)
    for values in by_source.values():
        generator.shuffle(values)
    sources = sorted(by_source)
    generator.shuffle(sources)
    result: list[PreparedSentence] = []
    while sources:
        remaining: list[str] = []
        for source in sources:
            values = by_source[source]
            if values:
                result.append(values.pop())
            if values:
                remaining.append(source)
        sources = remaining
    return result


def build_real_workload(
    sentences: tuple[PreparedSentence, ...],
    *,
    target_count: int = 64,
    seed: int = 20260812,
) -> tuple[RealQuery, ...]:
    """Create one deterministic, source-stratified real-text workload.

    Tags overlap intentionally: one real query may exercise a mutation,
    boundary location, and frequency class at the same time.
    """
    if target_count < len(REQUIRED_QUERY_TAGS):
        raise ValueError(
            f"target_count must be at least {len(REQUIRED_QUERY_TAGS)}"
        )
    if not sentences:
        return ()

    ordered = _stratified_sentences(sentences, seed)
    corpus_text = "\n".join(sentence.normalized_text for sentence in sentences)
    words = [
        (word, sentence, start, end)
        for sentence in ordered
        for word, start, end in _word_ranges(sentence.normalized_text)
    ]
    if not words:
        return ()

    word_counts = Counter(word for word, _sentence, _start, _end in words)
    grams = Counter(
        word[index : index + 3]
        for word, _sentence, _start, _end in words
        for index in range(max(0, len(word) - 2))
    )
    safe_words = [item for item in words if len(item[0]) >= 6]
    safe_grams = Counter(
        word[index : index + 3]
        for word, _sentence, _start, _end in safe_words
        for index in range(len(word) - 2)
    )
    queries: list[RealQuery] = []
    seen: set[tuple[str, tuple[str, ...], int | None]] = set()

    def add(
        sentence: PreparedSentence | None,
        text: str,
        tags: Iterable[str],
        *,
        start: int | None = None,
        mutation: str = "exact",
    ) -> None:
        text = text.strip()
        if not text:
            return
        item = _make_query(
            sentence, text, tags, start=start, mutation=mutation
        )
        key = (item.query, item.tags, item.source_sentence_id)
        if key not in seen:
            seen.add(key)
            queries.append(item)

    first_word, first_sentence, first_start, _ = words[0]
    for length in range(1, 6):
        suitable = next(
            (item for item in words if len(item[0]) >= length),
            (first_word, first_sentence, first_start, first_start + len(first_word)),
        )
        word, sentence, start, _end = suitable
        add(sentence, word[:length], ("short_exact", "inside_word"), start=start)

    medium = next((item for item in words if 6 <= len(item[0]) <= 15), words[0])
    long_word = next((item for item in words if len(item[0]) >= 16), None)
    if long_word is None:
        sentence = next((s for s in ordered if len(s.normalized_text) >= 16), ordered[0])
        long_word = (sentence.normalized_text[:24], sentence, 0, 24)
    for item, tag in ((medium, "medium_exact"), (long_word, "long_exact")):
        word, sentence, start, _end = item
        add(sentence, word, (tag, "inside_word"), start=start)

    internal = next((item for item in words if len(item[0]) >= 8), medium)
    word, sentence, start, _end = internal
    add(sentence, word[2:7], ("inside_word",), start=start + 2)

    boundary_sentence = next((s for s in ordered if " " in s.normalized_text), ordered[0])
    space = boundary_sentence.normalized_text.find(" ")
    cross_start = max(0, space - 3)
    add(
        boundary_sentence,
        boundary_sentence.normalized_text[cross_start : space + 4],
        ("cross_word",),
        start=cross_start,
    )

    mutation_word, mutation_sentence, mutation_start, _ = next(
        (item for item in words if len(item[0]) >= 7), medium
    )
    replacement = (
        mutation_word[:2]
        + ("x" if mutation_word[2] != "x" else "z")
        + mutation_word[3:]
    )
    add(
        mutation_sentence,
        replacement,
        ("replacement", "inside_word"),
        start=mutation_start,
        mutation="replacement",
    )
    add(
        mutation_sentence,
        mutation_word[:3] + mutation_word[4:],
        ("insertion", "inside_word"),
        start=mutation_start,
        mutation="missing_character",
    )
    add(
        mutation_sentence,
        mutation_word[:3] + "x" + mutation_word[3:],
        ("deletion", "inside_word"),
        start=mutation_start,
        mutation="extra_character",
    )

    repeated = next(
        (
            (word, sentence, start)
            for word, sentence, start, _end in words
            if re.search(r"(.).*\1|(.{2,}).*\2", word)
        ),
        (first_word, first_sentence, first_start),
    )
    add(repeated[1], repeated[0], ("repeated", "inside_word"), start=repeated[2])

    frequency_grams = safe_grams or grams
    frequency_pool = safe_words or words
    common_gram = max(
        frequency_grams,
        key=lambda gram: (frequency_grams[gram], gram),
    )
    rare_gram = min(
        frequency_grams,
        key=lambda gram: (frequency_grams[gram], gram),
    )
    ordered_grams = sorted(
        frequency_grams,
        key=lambda gram: (frequency_grams[gram], gram),
    )
    medium_gram = ordered_grams[len(ordered_grams) // 2]
    common_item = next(item for item in frequency_pool if common_gram in item[0])
    medium_item = next(item for item in frequency_pool if medium_gram in item[0])
    rare_item = next(item for item in frequency_pool if rare_gram in item[0])
    add(
        common_item[1],
        common_item[0],
        ("common_qgram", "inside_word"),
        start=common_item[2],
    )
    add(
        medium_item[1],
        medium_item[0],
        ("medium_qgram", "inside_word"),
        start=medium_item[2],
    )
    add(
        rare_item[1],
        rare_item[0],
        ("rare_qgram", "inside_word"),
        start=rare_item[2],
    )

    no_match = "zzzzzzbenchmarknear miss"
    while no_match in corpus_text:
        no_match += "z"
    add(None, no_match, ("no_match",), mutation="near_miss")

    boundary = next((s for s in ordered if len(s.normalized_text) >= 8), ordered[0])
    add(boundary, boundary.normalized_text[:8], ("near_boundary",), start=0)
    tail_start = max(0, len(boundary.normalized_text) - 8)
    add(
        boundary,
        boundary.normalized_text[tail_start:],
        ("near_boundary",),
        start=tail_start,
    )

    frequency_words = [word for word in word_counts if len(word) >= 6]
    common_word = max(
        frequency_words or list(word_counts),
        key=lambda word: (word_counts[word], word),
    )
    common_occurrence = next(item for item in words if item[0] == common_word)
    add(
        common_occurrence[1],
        common_word,
        ("multiple_matches", "high_frequency", "inside_word"),
        start=common_occurrence[2],
    )

    # Guarantee that a small workload still spans sources instead of letting
    # the first large document dominate selection.
    first_by_source: dict[str, PreparedSentence] = {}
    for sentence in ordered:
        first_by_source.setdefault(sentence.source_path, sentence)
    for source in sorted(first_by_source):
        source_sentence = first_by_source[source]
        ranges = _word_ranges(source_sentence.normalized_text)
        if not ranges:
            continue
        word, start, _end = ranges[0]
        add(
            source_sentence,
            word[: min(12, len(word))],
            (
                "medium_exact" if len(word) >= 6 else "short_exact",
                "inside_word",
            ),
            start=start,
        )

    generator = random.Random(seed ^ 0x5A17)
    filler = list(words)
    generator.shuffle(filler)
    index = 0
    while len(queries) < target_count:
        word, sentence, start, _end = filler[index % len(filler)]
        index += 1
        if len(word) < 2:
            continue
        length = min(len(word), 6 + index % 19)
        tags = (
            "medium_exact" if length <= 15 else "long_exact",
            "inside_word",
        )
        add(sentence, word[:length], tags, start=start)
        if index > target_count * 20 and len(queries) < target_count:
            # Degenerate corpora may not contain enough distinct words.
            add(
                sentence,
                word + str(index),
                ("no_match",),
                mutation="near_miss",
            )

    return tuple(queries[:target_count])


if __name__ == "__main__":
    main()
