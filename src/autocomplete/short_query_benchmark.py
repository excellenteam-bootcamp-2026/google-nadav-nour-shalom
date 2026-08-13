"""Short-query (length 1-6) study of the adaptive multi-q Bi-Anchor search.

Benchmark-only module. It imports the production implementations unchanged
and never alters matching semantics. Forced-q runtimes are produced by
narrowing ``q_values`` on a copy of one shared structure, so every
configuration reads the same index and no measurement is distorted by
building the corpus several times.

Naive costs tens of seconds per query on the full corpus, so the study is
tiered on purpose:

* correctness is gated against Naive on a stratified corpus slice, with the
  complete length 1-6 workload;
* latency for the anchored configurations is measured on the full corpus;
* the Naive baseline on the full corpus is sampled per length, because Naive
  scans the whole corpus regardless of the query and its per-length spread is
  reported so the reader can check that assumption.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, replace
import gc
import json
from math import ceil
from pathlib import Path
import random
import re
from statistics import fmean, median
from time import perf_counter_ns
import tracemalloc
from typing import Iterable

from src.algorithms.bi_anchor_search_algorithm import BiAnchorSearchAlgorithm
from src.algorithms.bi_anchor_search_stats import BiAnchorSearchStats
from src.algorithms.naive_search_algorithm import NaiveSearchAlgorithm
from src.autocomplete.preparation import DataPreparer
from src.builders.bi_anchor_structure_builder import BiAnchorStructureBuilder
from src.models.match_candidate import MatchCandidate
from src.models.prepared_sentence import PreparedSentence
from src.structures.bi_anchor_search_structure import BiAnchorSearchStructure
from src.structures.naive_search_structure import NaiveSearchStructure


LENGTHS = (1, 2, 3, 4, 5, 6)

REQUIRED_TAGS = frozenset(
    {
        "exact",
        "replacement",
        "insertion",
        "deletion",
        "inside_word",
        "cross_word",
        "common_seed",
        "rare_seed",
        "no_match",
    }
)

STUDY_Q_VALUES = (1, 2, 3)


@dataclass(frozen=True, slots=True)
class ShortQuery:
    query: str
    tags: tuple[str, ...]
    mutation: str
    source_file: str | None
    source_sentence_id: int | None
    expected_start: int | None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class AnchorRuntime:
    """One anchored configuration over a shared index."""

    name: str
    structure: BiAnchorSearchStructure
    stats: BiAnchorSearchStats
    algorithm: BiAnchorSearchAlgorithm

    def search(self, query: str) -> list[MatchCandidate]:
        return self.algorithm.search(query, self.structure)

    def reset(self) -> None:
        self.stats = BiAnchorSearchStats()
        self.algorithm = BiAnchorSearchAlgorithm(stats=self.stats)


def anchor_runtimes(
    structure: BiAnchorSearchStructure,
) -> dict[str, AnchorRuntime]:
    """Adaptive plus one forced-q runtime per indexed q, sharing one index."""
    runtimes: dict[str, AnchorRuntime] = {}
    configurations: list[tuple[str, tuple[int, ...]]] = [
        ("adaptive", structure.q_values)
    ]
    configurations.extend(
        (f"q{q}", (q,)) for q in structure.q_values
    )
    for name, q_values in configurations:
        stats = BiAnchorSearchStats()
        runtimes[name] = AnchorRuntime(
            name=name,
            structure=replace(
                structure, q=max(q_values), q_values=tuple(q_values)
            ),
            stats=stats,
            algorithm=BiAnchorSearchAlgorithm(stats=stats),
        )
    return runtimes


def canonicalize(matches: Iterable[MatchCandidate]) -> Counter:
    """Preserve every raw-candidate field relevant to search semantics."""
    return Counter(
        (
            match.sentence.sentence_id,
            match.match_start,
            match.edit_type.value,
            match.edit_index,
            match.correct_characters,
        )
        for match in matches
    )


def percentile(samples: Iterable[int | float], value: int) -> float:
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
            "p95_ns": 0.0,
            "max_ns": 0.0,
        }
    return {
        "count": len(values),
        "mean_ns": float(fmean(values)),
        "median_ns": float(median(values)),
        "p95_ns": percentile(values, 95),
        "max_ns": float(max(values)),
    }


def _word_ranges(text: str) -> list[tuple[str, int]]:
    return [(match.group(), match.start()) for match in re.finditer(r"\S+", text)]


def _stratified(
    sentences: tuple[PreparedSentence, ...], seed: int
) -> list[PreparedSentence]:
    """Round-robin across source files so no single document dominates."""
    by_source: dict[str, list[PreparedSentence]] = defaultdict(list)
    for sentence in sentences:
        by_source[sentence.source_path].append(sentence)
    generator = random.Random(seed)
    for values in by_source.values():
        generator.shuffle(values)
    sources = sorted(by_source)
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


def corpus_slice(
    sentences: tuple[PreparedSentence, ...],
    fraction: float,
    *,
    seed: int = 20260813,
) -> tuple[PreparedSentence, ...]:
    """A source-stratified slice, so a slice stays a real mixed corpus."""
    if not 0 < fraction <= 1:
        raise ValueError("fraction must be in (0, 1]")
    ordered = _stratified(sentences, seed)
    size = max(1, ceil(len(ordered) * fraction))
    return tuple(ordered[:size])


def build_short_query_workload(
    sentences: tuple[PreparedSentence, ...],
    *,
    per_length: int = 40,
    seed: int = 20260813,
) -> tuple[ShortQuery, ...]:
    """Deterministic real-text queries of every length in ``LENGTHS``.

    Each length gets the same mix of classes so per-length comparisons are
    not confounded by a different workload shape at each length.
    """
    if not sentences:
        raise ValueError("A non-empty corpus is required to sample queries.")
    if per_length < 1:
        raise ValueError("per_length must be positive.")

    ordered = _stratified(sentences, seed)
    words = [
        (word, sentence, start)
        for sentence in ordered
        for word, start in _word_ranges(sentence.normalized_text)
    ]
    if not words:
        raise ValueError("The corpus contains no words to sample from.")
    corpus_text = "\n".join(
        sentence.normalized_text for sentence in sentences
    )
    generator = random.Random(seed ^ 0x5170)
    result: list[ShortQuery] = []

    for length in LENGTHS:
        result.extend(
            _queries_for_length(
                length=length,
                ordered=ordered,
                words=words,
                corpus_text=corpus_text,
                per_length=per_length,
                generator=generator,
            )
        )
    return tuple(result)


def _absent_candidates(alphabet: str, length: int) -> Iterable[str]:
    """Yield a bounded set of candidate strings of exactly ``length``."""
    for character in alphabet:
        yield character * length
    for first in alphabet:
        for second in alphabet:
            candidate = (first + second) * length
            yield candidate[:length]


def _queries_for_length(
    *,
    length: int,
    ordered: list[PreparedSentence],
    words: list[tuple[str, PreparedSentence, int]],
    corpus_text: str,
    per_length: int,
    generator: random.Random,
) -> list[ShortQuery]:
    seen: set[str] = set()
    result: list[ShortQuery] = []

    def add(
        text: str,
        tags: Iterable[str],
        *,
        sentence: PreparedSentence | None = None,
        start: int | None = None,
        mutation: str = "exact",
    ) -> bool:
        if len(text) != length or text in seen:
            return False
        seen.add(text)
        result.append(
            ShortQuery(
                query=text,
                tags=tuple(sorted(set(tags))),
                mutation=mutation,
                source_file=sentence.source_path if sentence else None,
                source_sentence_id=sentence.sentence_id if sentence else None,
                expected_start=start,
            )
        )
        return True

    seed_counts = Counter(
        text[index : index + length]
        for sentence in ordered[: min(len(ordered), 4000)]
        for text in (sentence.normalized_text,)
        for index in range(len(text) - length + 1)
    )
    if not seed_counts:
        seed_counts = Counter({"a" * length: 1})
    by_frequency = sorted(seed_counts, key=lambda text: (-seed_counts[text], text))

    def locate(text: str) -> tuple[PreparedSentence, int] | None:
        for sentence in ordered:
            position = sentence.normalized_text.find(text)
            if position >= 0:
                return sentence, position
        return None

    # Frequency extremes: the anchors these produce are what the cost model
    # is meant to discriminate between.
    for text in by_frequency[:3]:
        found = locate(text)
        if found:
            sentence, position = found
            add(
                text,
                ("common_seed", "exact")
                + (("cross_word",) if " " in text else ("inside_word",)),
                sentence=sentence,
                start=position,
            )
    for text in reversed(by_frequency[-3:]):
        found = locate(text)
        if found:
            sentence, position = found
            add(
                text,
                ("rare_seed", "exact")
                + (("cross_word",) if " " in text else ("inside_word",)),
                sentence=sentence,
                start=position,
            )

    inside = [item for item in words if len(item[0]) >= length]
    crossing = [
        (sentence, position)
        for sentence in ordered
        for position in range(len(sentence.normalized_text) - length + 1)
        if " "
        in sentence.normalized_text[position + 1 : position + length]
    ]

    for word, sentence, start in inside[: per_length * 4]:
        offset = (len(word) - length) // 2
        if add(
            word[offset : offset + length],
            ("exact", "inside_word"),
            sentence=sentence,
            start=start + offset,
        ) and len(result) >= per_length // 3:
            break

    for sentence, position in crossing[: per_length * 4]:
        if add(
            sentence.normalized_text[position : position + length],
            ("exact", "cross_word"),
            sentence=sentence,
            start=position,
        ) and sum("cross_word" in item.tags for item in result) >= max(
            2, per_length // 6
        ):
            break

    # Mutations only exist for lengths that can still carry them.
    mutation_pool = [item for item in inside if len(item[0]) >= length + 1]
    for word, sentence, start in mutation_pool[: per_length * 4]:
        base = word[:length]
        replaced = ("q" if base[0] != "q" else "w") + base[1:]
        add(
            replaced,
            ("replacement", "inside_word"),
            sentence=sentence,
            start=start,
            mutation="replacement",
        )
        # One target character the query lacks -> INSERTION semantics.
        add(
            word[: length - 1] + word[length : length + 1],
            ("insertion", "inside_word"),
            sentence=sentence,
            start=start,
            mutation="missing_character",
        ) if length >= 2 else None
        # One extra query character -> DELETION semantics.
        add(
            word[: length - 1] + "q",
            ("deletion", "inside_word"),
            sentence=sentence,
            start=start,
            mutation="extra_character",
        )
        if len(result) >= per_length - 2:
            break

    # A length-1 query cannot always miss: some single character is bound to
    # occur. Search the printable alphabet for an absent string of exactly
    # this length and skip the class when none exists.
    alphabet = "qzxjkvwy0123456789"
    for attempt in _absent_candidates(alphabet, length):
        if attempt not in corpus_text:
            add(attempt, ("no_match",), mutation="near_miss")
            break

    # Fill the remainder with plain real substrings sampled across sources.
    attempts = 0
    while len(result) < per_length and attempts < per_length * 200:
        attempts += 1
        word, sentence, start = generator.choice(words)
        if len(word) < length:
            continue
        offset = generator.randrange(len(word) - length + 1)
        add(
            word[offset : offset + length],
            ("exact", "inside_word"),
            sentence=sentence,
            start=start + offset,
        )
    return result[:per_length]


def run_correctness_gate(
    sentences: tuple[PreparedSentence, ...],
    workload: tuple[ShortQuery, ...],
) -> dict[str, object]:
    """Compare every anchored configuration to Naive on identical input."""
    structure = BiAnchorStructureBuilder(
        q=max(STUDY_Q_VALUES), q_values=STUDY_Q_VALUES
    ).build(sentences)
    runtimes = anchor_runtimes(structure)
    naive = NaiveSearchAlgorithm()
    naive_structure = NaiveSearchStructure(sentences=tuple(sentences))

    metrics = {
        name: {
            "queries": 0,
            "matching_result_sets": 0,
            "mismatches": 0,
            "false_negatives": 0,
            "false_positives": 0,
        }
        for name in runtimes
    }
    failures: list[dict[str, object]] = []

    for item in workload:
        expected = canonicalize(naive.search(item.query, naive_structure))
        for name, runtime in runtimes.items():
            actual = canonicalize(runtime.search(item.query))
            missing = expected - actual
            unexpected = actual - expected
            entry = metrics[name]
            entry["queries"] += 1
            entry["false_negatives"] += sum(missing.values())
            entry["false_positives"] += sum(unexpected.values())
            if missing or unexpected:
                entry["mismatches"] += 1
                if len(failures) < 20:
                    failures.append(
                        {
                            "runtime": name,
                            "query": item.query,
                            "missing": list(missing)[:3],
                            "unexpected": list(unexpected)[:3],
                        }
                    )
            else:
                entry["matching_result_sets"] += 1

    return {
        "sentences": len(sentences),
        "queries": len(workload),
        "runtimes": metrics,
        "failures": failures,
    }


def _work_snapshot(before: BiAnchorSearchStats, after: BiAnchorSearchStats):
    return {
        "seed_occurrences_expanded": after.seed_occurrences_expanded
        - before.seed_occurrences_expanded,
        "candidate_contexts_generated": after.candidate_contexts_generated
        - before.candidate_contexts_generated,
        "candidate_contexts_after_dedup": after.candidate_contexts_after_dedup
        - before.candidate_contexts_after_dedup,
        "verifier_calls": after.verifier_calls - before.verifier_calls,
    }


def _runtime_q(name: str) -> int | None:
    return None if name == "adaptive" else int(name[1:])


def run_length_study(
    sentences: tuple[PreparedSentence, ...],
    workload: tuple[ShortQuery, ...],
    *,
    repeats: int = 3,
    naive_per_length: int = 2,
    naive_repeats: int = 1,
    include_naive: bool = True,
    expansion_guard: int | None = None,
) -> dict[str, object]:
    """Measure latency and internal work per query length.

    A configuration is only executed when it would actually anchor. A forced
    q whose anchors do not fit the query would silently run Naive instead, and
    reporting that as "q=k latency" would be a lie. ``expansion_guard`` skips
    execution when the planned pair predicts more occurrences than the given
    budget; the prediction is still reported, so a configuration too expensive
    to run is visible rather than absent.
    """
    if repeats <= 0 or naive_repeats <= 0:
        raise ValueError("repeats must be positive")

    structure = BiAnchorStructureBuilder(
        q=max(STUDY_Q_VALUES), q_values=STUDY_Q_VALUES
    ).build(sentences)
    runtimes = anchor_runtimes(structure)
    planner = BiAnchorSearchAlgorithm()
    naive = NaiveSearchAlgorithm()
    naive_structure = NaiveSearchStructure(sentences=tuple(sentences))

    by_length: dict[str, dict[str, object]] = {}
    rows: list[dict[str, object]] = []

    for length in LENGTHS:
        items = [item for item in workload if len(item.query) == length]
        latencies: dict[str, list[int]] = defaultdict(list)
        work: dict[str, list[dict[str, int]]] = defaultdict(list)
        fallbacks: Counter[str] = Counter()
        guarded: Counter[str] = Counter()
        predicted: dict[str, list[int]] = defaultdict(list)
        selected_q: Counter[int] = Counter()
        pair_costs: list[int] = []
        naive_latencies: list[int] = []

        for index, item in enumerate(items):
            names = list(runtimes)
            rotation = index % len(names)
            for name in names[rotation:] + names[:rotation]:
                runtime = runtimes[name]
                plan = planner.plan(item.query, runtime.structure)
                row: dict[str, object] = {
                    **item.to_dict(),
                    "length": length,
                    "runtime": name,
                    "selected_q": plan.q if plan else None,
                    "predicted_expansion": plan.expansion_cost if plan else None,
                }
                if plan is None:
                    fallbacks[name] += 1
                    rows.append({**row, "status": "naive_fallback"})
                    continue
                if name == "adaptive":
                    selected_q[plan.q] += 1
                    pair_costs.append(plan.expansion_cost)
                predicted[name].append(plan.expansion_cost)
                if (
                    expansion_guard is not None
                    and plan.expansion_cost > expansion_guard
                ):
                    guarded[name] += 1
                    rows.append({**row, "status": "guarded"})
                    continue

                stats = BiAnchorSearchStats()
                measured = BiAnchorSearchAlgorithm(stats=stats)
                samples: list[int] = []
                for _ in range(repeats):
                    started = perf_counter_ns()
                    measured.search(item.query, runtime.structure)
                    samples.append(perf_counter_ns() - started)
                latency = int(median(samples))
                latencies[name].append(latency)
                counters = {
                    "seed_occurrences_expanded": stats.seed_occurrences_expanded
                    // repeats,
                    "candidate_contexts_generated": (
                        stats.candidate_contexts_generated // repeats
                    ),
                    "candidate_contexts_after_dedup": (
                        stats.candidate_contexts_after_dedup // repeats
                    ),
                    "verifier_calls": stats.verifier_calls // repeats,
                }
                work[name].append(counters)
                rows.append(
                    {
                        **row,
                        "status": "executed",
                        "latency_ns": latency,
                        **counters,
                    }
                )

        if include_naive:
            for item in items[:naive_per_length]:
                samples = []
                for _ in range(naive_repeats):
                    started = perf_counter_ns()
                    naive.search(item.query, naive_structure)
                    samples.append(perf_counter_ns() - started)
                naive_latencies.append(int(median(samples)))
                rows.append(
                    {
                        **item.to_dict(),
                        "length": length,
                        "runtime": "naive",
                        "status": "executed",
                        "latency_ns": naive_latencies[-1],
                    }
                )

        entry: dict[str, object] = {
            "queries": len(items),
            "naive": {
                "valid": True,
                "sampled_queries": len(naive_latencies),
                "latency": summarize(naive_latencies),
            },
        }
        for name in runtimes:
            q_value = _runtime_q(name)
            valid = (
                2 * min(structure.q_values) <= length
                if q_value is None
                else 2 * q_value <= length
            )
            measurements: dict[str, object] = {
                "valid": bool(valid),
                "executed": len(latencies[name]),
                "guarded": guarded[name],
                "latency": summarize(latencies[name]),
                "predicted_expansion": summarize(predicted[name]),
                "fallback_rate": (
                    fallbacks[name] / len(items) if items else 0.0
                ),
            }
            for key in (
                "seed_occurrences_expanded",
                "candidate_contexts_generated",
                "candidate_contexts_after_dedup",
                "verifier_calls",
            ):
                measurements[key] = summarize(
                    sample[key] for sample in work[name]
                )
            if name == "adaptive":
                measurements["selected_q_counts"] = dict(sorted(selected_q.items()))
                measurements["selected_pair_cost"] = summarize(pair_costs)
            entry[name] = measurements
        by_length[str(length)] = entry

    return {"by_length": by_length, "rows": rows}


def per_length_table(study: dict[str, object]) -> str:
    """Render the per-length latency comparison as one markdown table."""
    headers = [
        "Length",
        "Naive ms",
        "q1 ms",
        "q2 ms",
        "q3 ms",
        "Adaptive ms",
        "Selected q",
        "Speedup vs Naive",
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    by_length: dict[str, dict] = study["by_length"]  # type: ignore[assignment]
    for length in LENGTHS:
        entry = by_length[str(length)]
        naive_ns = entry["naive"]["latency"]["median_ns"]
        adaptive_ns = entry["adaptive"]["latency"]["median_ns"]

        def cell(name: str) -> str:
            values = entry[name]
            if not values["valid"]:
                return "N/A"
            if not values["latency"]["count"]:
                return f"guarded (~{values['predicted_expansion']['median_ns']:.0f} occ)"
            return f"{values['latency']['median_ns'] / 1e6:.3f}"

        selected = entry["adaptive"].get("selected_q_counts") or {}
        if selected:
            label = ", ".join(f"q{q}x{count}" for q, count in selected.items())
        else:
            label = "fallback"
        speedup = (
            f"{naive_ns / adaptive_ns:.1f}x"
            if naive_ns and adaptive_ns
            else "n/a"
        )
        lines.append(
            "| "
            + " | ".join(
                [
                    str(length),
                    f"{naive_ns / 1e6:.3f}" if naive_ns else "n/a",
                    cell("q1"),
                    cell("q2"),
                    cell("q3"),
                    cell("adaptive"),
                    label,
                    speedup,
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def measure_index_configurations(
    sentences: tuple[PreparedSentence, ...],
    q_value_sets: tuple[tuple[int, ...], ...],
) -> dict[str, dict[str, object]]:
    """Build time, allocated memory and index sizes per indexed q set."""
    measured: dict[str, dict[str, object]] = {}
    for q_values in q_value_sets:
        name = "q={" + ",".join(str(q) for q in sorted(q_values)) + "}"
        gc.collect()
        tracemalloc.start()
        started = perf_counter_ns()
        structure = BiAnchorStructureBuilder(
            q=max(q_values), q_values=tuple(sorted(q_values))
        ).build(sentences)
        elapsed = perf_counter_ns() - started
        retained, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        index = structure.build_stats.index
        measured[name] = {
            "q_values": list(sorted(q_values)),
            "build_ns": elapsed,
            "retained_memory_bytes": retained,
            "peak_memory_bytes": peak,
            "unique_words": index.unique_words,
            "word_occurrences": index.word_occurrences,
            "intra_word_seed_keys": index.intra_word_seed_keys,
            "intra_word_seed_references": index.intra_word_seed_references,
            "boundary_seed_keys": index.boundary_seed_keys,
            "boundary_occurrences": index.boundary_occurrences,
            "per_q": {
                str(q): {
                    "intra_word_seed_keys": stats.intra_word_seed_keys,
                    "intra_word_seed_references": stats.intra_word_seed_references,
                    "boundary_seed_keys": stats.boundary_seed_keys,
                    "boundary_occurrences": stats.boundary_occurrences,
                }
                for q, stats in sorted(index.per_q.items())
            },
        }
        del structure
        gc.collect()
    return measured


def render_report(payload: dict[str, object]) -> str:
    sections = ["# Adaptive Multi-q Bi-Anchor: Short-Query Study"]
    corpus = payload.get("corpus", {})
    sections.append(
        "## Corpus\n\n"
        + "\n".join(f"- {key}: {value}" for key, value in corpus.items())
    )
    workload = payload.get("workload", {})
    sections.append(
        "## Workload\n\n"
        + "\n".join(f"- {key}: {value}" for key, value in workload.items())
    )
    correctness = payload.get("correctness", {})
    lines = [
        "| Runtime | Queries | Matching | Mismatches | FN | FP |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for name, values in correctness.get("runtimes", {}).items():
        lines.append(
            f"| {name} | {values['queries']} | "
            f"{values['matching_result_sets']} | {values['mismatches']} | "
            f"{values['false_negatives']} | {values['false_positives']} |"
        )
    sections.append(
        "## Correctness gate\n\n"
        f"Oracle: Naive on {correctness.get('sentences')} sentences.\n\n"
        + "\n".join(lines)
    )
    sections.append(
        "## Per-length results\n\n" + per_length_table(payload["length_study"])  # type: ignore[arg-type]
    )
    work_lines = [
        "| Length | Runtime | Median occurrences | Median contexts | "
        "Median verifier calls | Fallback rate |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    by_length: dict[str, dict] = payload["length_study"]["by_length"]  # type: ignore[index]
    for length in LENGTHS:
        entry = by_length[str(length)]
        for name in ("q1", "q2", "q3", "adaptive"):
            values = entry[name]
            if not values["valid"]:
                continue
            work_lines.append(
                f"| {length} | {name} | "
                f"{values['seed_occurrences_expanded']['median_ns']:.0f} | "
                f"{values['candidate_contexts_after_dedup']['median_ns']:.0f} | "
                f"{values['verifier_calls']['median_ns']:.0f} | "
                f"{values['fallback_rate']:.2f} |"
            )
    sections.append("## Internal work\n\n" + "\n".join(work_lines))
    index_lines = [
        "| Configuration | Build ms | Retained MiB | Peak MiB | "
        "Intra-word keys | Intra-word refs | Boundary keys | Boundary occ |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for name, values in payload.get("index_configurations", {}).items():
        index_lines.append(
            f"| {name} | {values['build_ns'] / 1e6:.0f} | "
            f"{values['retained_memory_bytes'] / 2**20:.1f} | "
            f"{values['peak_memory_bytes'] / 2**20:.1f} | "
            f"{values['intra_word_seed_keys']} | "
            f"{values['intra_word_seed_references']} | "
            f"{values['boundary_seed_keys']} | "
            f"{values['boundary_occurrences']} |"
        )
    sections.append("## Index configurations\n\n" + "\n".join(index_lines))
    return "\n\n".join(sections) + "\n"


def run_study(
    *,
    archive: Path,
    per_length: int = 40,
    repeats: int = 3,
    naive_per_length: int = 2,
    naive_repeats: int = 1,
    correctness_fraction: float = 0.02,
    latency_fraction: float = 1.0,
    expansion_guard: int | None = None,
    measure_index: bool = True,
    output_dir: Path = Path("."),
    prefix: str = "short-query",
) -> dict[str, object]:
    preparer = DataPreparer()
    sentences = tuple(preparer.prepare(archive))
    if not sentences:
        raise ValueError(f"No sentences prepared from {archive}")

    workload = build_short_query_workload(sentences, per_length=per_length)
    gate_corpus = corpus_slice(sentences, correctness_fraction)
    latency_corpus = (
        sentences
        if latency_fraction >= 1.0
        else corpus_slice(sentences, latency_fraction)
    )

    payload: dict[str, object] = {
        "corpus": {
            "source_archive": str(archive),
            "prepared_sentences": len(sentences),
            "normalized_characters": sum(
                len(sentence.normalized_text) for sentence in sentences
            ),
            "source_files": len({s.source_path for s in sentences}),
            "latency_fraction": latency_fraction,
            "latency_sentences": len(latency_corpus),
            "correctness_fraction": correctness_fraction,
            "correctness_sentences": len(gate_corpus),
            "expansion_guard": expansion_guard,
        },
        "workload": {
            "queries": len(workload),
            "per_length": per_length,
            "lengths": list(LENGTHS),
            "tags": dict(
                sorted(Counter(tag for q in workload for tag in q.tags).items())
            ),
        },
        "correctness": run_correctness_gate(gate_corpus, workload),
        "index_configurations": (
            measure_index_configurations(sentences, ((3,), (2, 3), (1, 2, 3)))
            if measure_index
            else {}
        ),
    }
    payload["length_study"] = run_length_study(
        latency_corpus,
        workload,
        repeats=repeats,
        naive_per_length=naive_per_length,
        naive_repeats=naive_repeats,
        expansion_guard=expansion_guard,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    rows = payload["length_study"].pop("rows")  # type: ignore[union-attr]
    (output_dir / f"{prefix}-study.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (output_dir / f"{prefix}-rows.json").write_text(
        json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (output_dir / f"{prefix}-report.md").write_text(
        render_report(payload), encoding="utf-8"
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Short-query study of adaptive multi-q Bi-Anchor search."
    )
    parser.add_argument("--archive", type=Path, default=Path("data/Archive3.zip"))
    parser.add_argument("--per-length", type=int, default=40)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--naive-per-length", type=int, default=2)
    parser.add_argument("--naive-repeats", type=int, default=1)
    parser.add_argument("--correctness-fraction", type=float, default=0.02)
    parser.add_argument("--latency-fraction", type=float, default=1.0)
    parser.add_argument("--expansion-guard", type=int, default=None)
    parser.add_argument("--skip-index-study", action="store_true")
    parser.add_argument("--prefix", default="short-query")
    parser.add_argument("--output-dir", type=Path, default=Path("benchmark"))
    arguments = parser.parse_args()
    payload = run_study(
        archive=arguments.archive,
        per_length=arguments.per_length,
        repeats=arguments.repeats,
        naive_per_length=arguments.naive_per_length,
        naive_repeats=arguments.naive_repeats,
        correctness_fraction=arguments.correctness_fraction,
        latency_fraction=arguments.latency_fraction,
        expansion_guard=arguments.expansion_guard,
        measure_index=not arguments.skip_index_study,
        output_dir=arguments.output_dir,
        prefix=arguments.prefix,
    )
    print(per_length_table(payload["length_study"]))  # type: ignore[arg-type]


if __name__ == "__main__":
    main()
