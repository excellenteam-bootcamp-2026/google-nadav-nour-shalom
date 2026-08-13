"""Permanent four-algorithm benchmark orchestrator.

Run the normal trustworthy benchmark with::

    python benchmark/code/benchmark_all_algorithms.py --source data/Archive3.zip

The file imports production preparation, builders, and search algorithms. It
contains benchmark infrastructure only; no matching implementation is copied.
"""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import cProfile
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
import gc
import hashlib
import json
from math import ceil
from pathlib import Path
import platform
from statistics import fmean, median, stdev
from time import perf_counter_ns
import tracemalloc
import traceback
from typing import Callable
import os
import io
import pstats
import subprocess
import sys

# Direct execution sets sys.path[0] to benchmark/code. Add the repository root
# so production imports keep working with the documented path-based command.
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from benchmark.code.archive3_benchmark import (
    canonical_signature,
    generate_workload,
    load_queries,
)
from src.autocomplete.preparation import DataPreparer
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


DEFAULT_SOURCE = "data/Archive2.zip"
REQUIRED_ALGORITHM_IDS = (
    "naive",
    "qgram_verifier",
    "qgram_tree_hybrid",
    "bi_anchor",
)


@dataclass(frozen=True, slots=True)
class ModeDefaults:
    query_count: int
    repetitions: int
    build_repetitions: int
    short_queries_per_length: int


MODE_DEFAULTS = {
    "quick": ModeDefaults(125, 1, 1, 12),
    "standard": ModeDefaults(700, 3, 3, 50),
    "deep": ModeDefaults(2000, 7, 5, 80),
}


@dataclass(frozen=True, slots=True)
class BenchmarkConfig:
    mode: str
    source: Path
    output_base: Path
    query_count: int
    repetitions: int
    build_repetitions: int
    short_queries_per_length: int
    seed: int
    query_file: Path | None
    q_study: bool
    overwrite: bool
    full_corpus: bool = True

    @property
    def expected_timed_searches(self) -> int:
        return self.query_count * len(REQUIRED_ALGORITHM_IDS) * self.repetitions


@dataclass(frozen=True, slots=True)
class AlgorithmSpec:
    algorithm_id: str
    conceptual_name: str
    implementation: str
    builder_structure: str
    factory: Callable[..., object] | None = None


@dataclass(slots=True)
class SearchRuntime:
    algorithm_id: str
    algorithm: object
    structure: object | None
    owns_structure: bool = False
    stats: object | None = None
    tree_metrics: dict[str, int] | None = None

    def search(self, query: str) -> list[object]:
        if self.owns_structure:
            return self.algorithm.search(query)
        return self.algorithm.search(query, self.structure)

    def work_snapshot(self) -> dict[str, object]:
        if self.stats is not None:
            return asdict(self.stats)
        return dict(self.tree_metrics or {})

    def structure_metrics(self) -> dict[str, object]:
        if self.algorithm_id == "naive":
            return {"sentence_count": len(self.structure.sentences)}
        if self.algorithm_id == "qgram_verifier":
            structure = self.structure
            if not isinstance(structure, QGramSearchStructure):
                raise TypeError("invalid positional Q-Gram runtime")
            posting_lengths = [
                len(postings)
                for _size, index in structure.indexes()
                for postings in index.values()
            ]
            return {
                "q": structure.q,
                "qgram_keys": sum(
                    len(index) for _size, index in structure.indexes()
                ),
                "posting_lists": len(posting_lengths),
                "posting_entries": sum(posting_lengths),
                "largest_posting_length": max(posting_lengths, default=0),
                "median_posting_length": (
                    float(median(posting_lengths)) if posting_lengths else 0.0
                ),
                "p95_posting_length": _nearest_rank(posting_lengths, 95),
            }
        if self.algorithm_id == "qgram_tree_hybrid":
            stack = [self.algorithm._root]
            nodes = terminals = occurrences = 0
            while stack:
                node = stack.pop()
                nodes += 1
                if node.word is not None:
                    terminals += 1
                    occurrences += len(node.occurrences)
                stack.extend(node.children.values())
            qgrams = self.algorithm._qgrams
            return {
                "q": self.algorithm.Q,
                "qgram_keys": len(qgrams),
                "qgram_references": sum(len(items) for items in qgrams.values()),
                "tree_nodes": nodes,
                "tree_edges": max(0, nodes - 1),
                "terminals": terminals,
                "word_occurrences": occurrences,
            }
        if self.algorithm_id == "bi_anchor":
            structure = self.structure
            if not isinstance(structure, BiAnchorSearchStructure):
                raise TypeError("invalid Bi-Anchor runtime")
            index_stats = structure.build_stats.index
            metrics = {
                "unique_words": index_stats.unique_words,
                "word_occurrences": index_stats.word_occurrences,
                "intra_word_seed_keys": index_stats.intra_word_seed_keys,
                "intra_word_seed_references": index_stats.intra_word_seed_references,
                "boundary_seed_keys": index_stats.boundary_seed_keys,
                "boundary_occurrences": index_stats.boundary_occurrences,
                "per_q": {
                    str(q): asdict(item)
                    for q, item in index_stats.per_q.items()
                },
            }
            frequencies: list[int] = []
            indexed_seeds = getattr(structure.seed_lookup, "indexed_seeds", None)
            if indexed_seeds is not None:
                for q in structure.q_values:
                    frequencies.extend(
                        structure.seed_lookup.frequency(seed)
                        for seed in indexed_seeds(q)
                    )
            metrics.update({
                "q": structure.q,
                "q_values": list(structure.q_values),
                "largest_seed_frequency": max(frequencies, default=0),
                "median_seed_frequency": (
                    float(median(frequencies)) if frequencies else 0.0
                ),
                "p95_seed_frequency": _nearest_rank(frequencies, 95),
            })
            return metrics
        return {}


def _instrument_tree(algorithm: QGramTrieSearchAlgorithm) -> dict[str, int]:
    counters = {
        "query_count": 0,
        "query_qgrams": 0,
        "tree_lookups": 0,
        "candidate_words": 0,
        "candidate_occurrences": 0,
        "verifier_calls": 0,
    }
    original_candidates = algorithm._get_candidates
    original_compare = algorithm._fuzzy_compare

    def observed_candidates(query: str):
        counters["query_count"] += 1
        counters["query_qgrams"] += max(0, len(query) - algorithm.Q + 1)
        counters["tree_lookups"] += 1
        candidates = original_candidates(query)
        counters["candidate_words"] += len(candidates)
        counters["candidate_occurrences"] += sum(
            len(node.occurrences) for node in candidates
        )
        return candidates

    def observed_compare(query: str, word: str):
        counters["verifier_calls"] += 1
        return original_compare(query, word)

    algorithm._get_candidates = observed_candidates
    algorithm._fuzzy_compare = observed_compare
    return counters


def _make_naive(sentences: tuple[object, ...], *, instrument: bool) -> SearchRuntime:
    stats = NaiveSearchStats() if instrument else None
    return SearchRuntime(
        "naive",
        NaiveSearchAlgorithm(stats=stats),
        NaiveStructureBuilder().build(sentences),
        stats=stats,
    )


def _make_qgram(
    sentences: tuple[object, ...], *, instrument: bool, q: int = 3
) -> SearchRuntime:
    stats = QGramSearchStats() if instrument else None
    return SearchRuntime(
        "qgram_verifier",
        QGramSearchAlgorithm(stats=stats),
        QGramStructureBuilder(q=q).build(sentences),
        stats=stats,
    )


def _make_tree(
    sentences: tuple[object, ...], *, instrument: bool, q: int = 3
) -> SearchRuntime:
    algorithm = QGramTrieSearchAlgorithm()
    algorithm.Q = q
    algorithm.build(sentences)
    counters = _instrument_tree(algorithm) if instrument else None
    return SearchRuntime(
        "qgram_tree_hybrid",
        algorithm,
        None,
        owns_structure=True,
        tree_metrics=counters,
    )


def _make_bi_anchor(
    sentences: tuple[object, ...], *, instrument: bool, q: int = 3
) -> SearchRuntime:
    stats = BiAnchorSearchStats() if instrument else None
    return SearchRuntime(
        "bi_anchor",
        BiAnchorSearchAlgorithm(stats=stats),
        BiAnchorStructureBuilder(q=q).build(sentences),
        stats=stats,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=DEFAULT_SOURCE)
    parser.add_argument("--output", default="benchmark/output")
    parser.add_argument("--queries", type=int)
    parser.add_argument("--repetitions", type=int)
    parser.add_argument("--build-repetitions", type=int)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--query-file", type=Path)
    parser.add_argument("--q-study", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--quick", action="store_true")
    modes.add_argument("--standard", action="store_true")
    modes.add_argument("--deep", action="store_true")
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def resolve_config(namespace: argparse.Namespace) -> BenchmarkConfig:
    mode = (
        "quick" if namespace.quick
        else "deep" if namespace.deep
        else "standard"
    )
    defaults = MODE_DEFAULTS[mode]
    query_count = namespace.queries or defaults.query_count
    repetitions = namespace.repetitions or defaults.repetitions
    build_repetitions = (
        namespace.build_repetitions or defaults.build_repetitions
    )
    for name, value in (
        ("queries", query_count),
        ("repetitions", repetitions),
        ("build repetitions", build_repetitions),
    ):
        if value <= 0:
            raise ValueError(f"{name} must be positive")
    return BenchmarkConfig(
        mode=mode,
        source=Path(namespace.source),
        output_base=Path(namespace.output),
        query_count=query_count,
        repetitions=repetitions,
        build_repetitions=build_repetitions,
        short_queries_per_length=min(
            defaults.short_queries_per_length,
            max(1, query_count // 6),
        ),
        seed=namespace.seed,
        query_file=namespace.query_file,
        q_study=bool(namespace.q_study or mode == "deep"),
        overwrite=namespace.overwrite,
    )


def algorithm_specs() -> tuple[AlgorithmSpec, ...]:
    return (
        AlgorithmSpec(
            "naive",
            "Naive",
            "NaiveSearchAlgorithm",
            "NaiveStructureBuilder / NaiveSearchStructure",
            _make_naive,
        ),
        AlgorithmSpec(
            "qgram_verifier",
            "Q-Gram + Verifier",
            "QGramSearchAlgorithm",
            "QGramStructureBuilder / QGramSearchStructure",
            _make_qgram,
        ),
        AlgorithmSpec(
            "qgram_tree_hybrid",
            "Q-Gram + Tree Hybrid",
            "QGramTrieSearchAlgorithm",
            "internal TrieNode + q-gram map",
            _make_tree,
        ),
        AlgorithmSpec(
            "bi_anchor",
            "Selective Bi-Anchor",
            "BiAnchorSearchAlgorithm",
            "BiAnchorStructureBuilder / BiAnchorSearchStructure",
            _make_bi_anchor,
        ),
    )


def validate_algorithm_specs(specs: tuple[AlgorithmSpec, ...]) -> None:
    actual = tuple(spec.algorithm_id for spec in specs)
    if actual != REQUIRED_ALGORITHM_IDS:
        missing = [item for item in REQUIRED_ALGORITHM_IDS if item not in actual]
        unexpected = [item for item in actual if item not in REQUIRED_ALGORITHM_IDS]
        raise RuntimeError(
            "Mandatory algorithm registry is invalid; "
            f"missing={missing}, unexpected={unexpected}, order={actual}"
        )


def run_directory(config: BenchmarkConfig, timestamp: datetime) -> Path:
    stamp = timestamp.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return config.output_base / config.source.stem / stamp


def allocate_run_directory(config: BenchmarkConfig, timestamp: datetime) -> Path:
    target = run_directory(config, timestamp)
    if not target.exists() or config.overwrite:
        return target
    suffix = 2
    while target.with_name(f"{target.name}-{suffix}").exists():
        suffix += 1
    return target.with_name(f"{target.name}-{suffix}")


def summarize_ns(samples: list[int]) -> dict[str, object]:
    if not samples:
        return {
            "samples": [], "min_ns": 0, "median_ns": 0.0,
            "mean_ns": 0.0, "p75_ns": 0, "p90_ns": 0,
            "p95_ns": None, "p99_ns": 0, "max_ns": 0,
            "stdev_ns": 0.0,
        }
    return {
        "samples": list(samples),
        "min_ns": min(samples),
        "median_ns": float(median(samples)),
        "mean_ns": float(fmean(samples)),
        "p75_ns": _nearest_rank(samples, 75),
        "p90_ns": _nearest_rank(samples, 90),
        # A per-call p95 from one or three repetitions is not meaningful.
        # Workload p95 is calculated later across independent query medians.
        "p95_ns": _nearest_rank(samples, 95) if len(samples) >= 5 else None,
        "p99_ns": _nearest_rank(samples, 99),
        "max_ns": max(samples),
        "stdev_ns": float(stdev(samples)) if len(samples) > 1 else 0.0,
    }


def _nearest_rank(samples: list[int | float], percentile: int) -> int | float:
    if not samples:
        return 0
    ordered = sorted(samples)
    return ordered[max(0, ceil(len(ordered) * percentile / 100) - 1)]


def _runtime_structure_metrics(runtime: object) -> dict[str, object]:
    method = getattr(runtime, "structure_metrics", None)
    if method is None:
        return {}
    return dict(method())


def measure_builds(
    specs: tuple[AlgorithmSpec, ...],
    sentences: tuple[object, ...],
    *,
    repetitions: int,
) -> tuple[dict[str, dict[str, object]], dict[str, object]]:
    """Time pure builds, measure one separate build, then retain one final build."""
    if repetitions <= 0:
        raise ValueError("build repetitions must be positive")
    results: dict[str, dict[str, object]] = {}
    runtimes: dict[str, object] = {}
    for spec in specs:
        if spec.factory is None:
            raise RuntimeError(
                f"{spec.algorithm_id} cannot be instantiated: factory is missing"
            )
        samples: list[int] = []
        for _ in range(repetitions):
            gc.collect()
            started = perf_counter_ns()
            timed_runtime = spec.factory(sentences, instrument=False)
            samples.append(perf_counter_ns() - started)
            del timed_runtime

        gc.collect()
        tracemalloc.start()
        memory_runtime = spec.factory(sentences, instrument=False)
        retained_bytes, peak_bytes = tracemalloc.get_traced_memory()
        structure_metrics = _runtime_structure_metrics(memory_runtime)
        tracemalloc.stop()
        del memory_runtime
        gc.collect()

        final_runtime = spec.factory(sentences, instrument=True)
        runtimes[spec.algorithm_id] = final_runtime
        results[spec.algorithm_id] = {
            "algorithm_id": spec.algorithm_id,
            "build_repetitions": repetitions,
            "build_time_ns": summarize_ns(samples),
            "memory_method": "tracemalloc dedicated build",
            "peak_build_memory_bytes": peak_bytes,
            "approx_retained_memory_bytes": retained_bytes,
            "structure_metrics": structure_metrics,
            "final_online_build_separate": True,
        }
    return results, runtimes


def rotated_algorithm_order(offset: int) -> tuple[str, ...]:
    rotation = offset % len(REQUIRED_ALGORITHM_IDS)
    return (
        REQUIRED_ALGORITHM_IDS[rotation:]
        + REQUIRED_ALGORITHM_IDS[:rotation]
    )


def _candidate_key(match: object) -> tuple[object, ...]:
    sentence = match.sentence
    return (
        sentence.sentence_id,
        sentence.source_path,
        sentence.offset,
        match.match_start,
        match.edit_type.value,
        match.edit_index,
        match.correct_characters,
    )


def _canonical_observation(matches: list[object]) -> dict[str, object]:
    return {
        "signature": canonical_signature(matches),
        "counter": (
            Counter(_candidate_key(match) for match in matches)
            if len(matches) <= 50_000
            else None
        ),
    }


def _work_snapshot(runtime: object) -> dict[str, object]:
    method = getattr(runtime, "work_snapshot", None)
    return dict(method()) if method is not None else {}


def _work_delta(
    before: dict[str, object], after: dict[str, object]
) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in after.items():
        previous = before.get(key)
        if isinstance(value, (int, float)) and isinstance(previous, (int, float)):
            result[key] = value - previous
        elif value != previous:
            result[key] = value
    return result


def _query_metadata(query: object) -> dict[str, object]:
    categories = tuple(
        getattr(query, "categories", (getattr(query, "category", "exact"),))
    )
    return {
        "query_id": query.query_id,
        "query_text": query.query_text,
        "normalized_query": query.normalized_query,
        "query_length": query.query_length,
        "length_bucket": query.length_bucket,
        "category": getattr(query, "primary_category", categories[0]),
        "categories": list(categories),
    }


def run_search_phase(
    config: BenchmarkConfig,
    queries: tuple[object, ...],
    runtimes: dict[str, object],
    progress: Callable[[int, int, float, float], None] | None = None,
) -> dict[str, object]:
    """Run one controlled search stream and reuse timed results everywhere."""
    if tuple(runtimes) != REQUIRED_ALGORITHM_IDS:
        raise RuntimeError("all four ordered algorithm runtimes are required")
    if not queries:
        raise ValueError("at least one query is required")

    warmup_query = max(queries, key=lambda item: item.query_length)
    errors: list[dict[str, object]] = []
    for algorithm_id in REQUIRED_ALGORITHM_IDS:
        try:
            runtimes[algorithm_id].search(warmup_query.normalized_query)
        except Exception as error:  # benchmark must retain the failure
            errors.append({
                "phase": "warmup",
                "algorithm_id": algorithm_id,
                "query_id": warmup_query.query_id,
                "exception": repr(error),
                "traceback": traceback.format_exc(),
            })

    timing_rows: list[dict[str, object]] = []
    correctness_rows: list[dict[str, object]] = []
    work_rows: list[dict[str, object]] = []
    actual_timed_searches = 0
    phase_started = perf_counter_ns()

    for query_index, query in enumerate(queries):
        samples: dict[str, list[int]] = {
            algorithm_id: [] for algorithm_id in REQUIRED_ALGORITHM_IDS
        }
        positions: dict[str, list[int]] = {
            algorithm_id: [] for algorithm_id in REQUIRED_ALGORITHM_IDS
        }
        observations: dict[str, dict[str, object]] = {}
        work: dict[str, dict[str, object]] = {}
        failed: set[str] = set()

        for repetition in range(config.repetitions):
            order = rotated_algorithm_order(query_index + repetition)
            for position, algorithm_id in enumerate(order):
                if algorithm_id in failed:
                    continue
                runtime = runtimes[algorithm_id]
                before = _work_snapshot(runtime)
                gc_was_enabled = gc.isenabled()
                gc.disable()
                try:
                    started = perf_counter_ns()
                    matches = runtime.search(query.normalized_query)
                    elapsed = perf_counter_ns() - started
                    actual_timed_searches += 1
                except Exception as error:
                    actual_timed_searches += 1
                    failed.add(algorithm_id)
                    errors.append({
                        "phase": "search",
                        "algorithm_id": algorithm_id,
                        "query_id": query.query_id,
                        "query": query.normalized_query,
                        "repetition": repetition,
                        "exception": repr(error),
                        "traceback": traceback.format_exc(),
                    })
                    continue
                finally:
                    if gc_was_enabled:
                        gc.enable()

                after = _work_snapshot(runtime)
                samples[algorithm_id].append(elapsed)
                positions[algorithm_id].append(position)
                if algorithm_id not in observations:
                    observations[algorithm_id] = _canonical_observation(matches)
                    work[algorithm_id] = _work_delta(before, after)

        metadata = _query_metadata(query)
        oracle = observations.get("naive")
        for algorithm_id in REQUIRED_ALGORITHM_IDS:
            values = samples[algorithm_id]
            observation = observations.get(algorithm_id)
            timing_rows.append({
                **metadata,
                "algorithm_id": algorithm_id,
                "repetitions_requested": config.repetitions,
                "repetitions_completed": len(values),
                "raw_samples_ns": values,
                "order_positions": positions[algorithm_id],
                "timing": summarize_ns(values),
                "result_count": (
                    observation["signature"]["count"] if observation else None
                ),
            })
            work_rows.append({
                "query_id": query.query_id,
                "algorithm_id": algorithm_id,
                "metrics": work.get(algorithm_id, {}),
            })

            if algorithm_id == "naive" and observation is not None:
                correctness = {
                    "correct": True,
                    "status": "oracle",
                    "false_negatives": 0,
                    "false_positives": 0,
                }
            elif oracle is None or observation is None:
                correctness = {
                    "correct": False,
                    "status": "error_or_missing_result",
                    "false_negatives": None,
                    "false_positives": None,
                }
            elif observation["signature"] == oracle["signature"]:
                correctness = {
                    "correct": True,
                    "status": "raw_results_match",
                    "false_negatives": 0,
                    "false_positives": 0,
                }
            else:
                expected_counter = oracle["counter"]
                actual_counter = observation["counter"]
                if expected_counter is not None and actual_counter is not None:
                    false_negatives = sum(
                        (expected_counter - actual_counter).values()
                    )
                    false_positives = sum(
                        (actual_counter - expected_counter).values()
                    )
                else:
                    false_negatives = None
                    false_positives = None
                correctness = {
                    "correct": False,
                    "status": "raw_result_mismatch",
                    "false_negatives": false_negatives,
                    "false_positives": false_positives,
                }
            correctness_rows.append({
                "query_id": query.query_id,
                "algorithm_id": algorithm_id,
                "oracle_source": "timed_naive_result",
                "oracle_signature": oracle["signature"] if oracle else None,
                "actual_signature": (
                    observation["signature"] if observation else None
                ),
                **correctness,
            })
        if progress is not None:
            completed = query_index + 1
            elapsed = (perf_counter_ns() - phase_started) / 1_000_000_000
            eta = (elapsed / completed) * (len(queries) - completed)
            progress(completed, len(queries), elapsed, eta)

    return {
        "expected_timed_searches": (
            len(queries) * len(REQUIRED_ALGORITHM_IDS) * config.repetitions
        ),
        "actual_timed_searches": actual_timed_searches,
        "warmup_calls": len(REQUIRED_ALGORITHM_IDS),
        "clock": "time.perf_counter_ns",
        "gc_disabled_uniformly_during_timed_calls": True,
        "timing_rows": timing_rows,
        "correctness_rows": correctness_rows,
        "work_rows": work_rows,
        "errors": errors,
    }


LENGTH_BUCKETS = ("1", "2", "3", "4", "5", "6", "7-8", "9-12", "13-20", "21+")
CATEGORY_BUCKETS = (
    "exact", "whole_word", "inside_word", "cross_word", "replacement",
    "insertion", "deletion", "repeated", "common", "rare",
    "high_result_count", "low_result_count", "no_match", "near_miss",
    "multi_word", "near_boundary", "repeated_pattern",
    "boundary_near_start", "boundary_near_end",
)
RESULT_COUNT_BUCKETS = ("0", "1-5", "6-20", "21-100", "101-1000", "1000+")
TIE_TOLERANCE = 0.02


def _distribution(values: list[float]) -> dict[str, float]:
    if not values:
        return {
            "min_ns": 0.0, "median_ns": 0.0, "mean_ns": 0.0,
            "p75_ns": 0.0, "p90_ns": 0.0, "p95_ns": 0.0,
            "p99_ns": 0.0, "max_ns": 0.0, "stdev_ns": 0.0,
        }
    return {
        "min_ns": float(min(values)),
        "median_ns": float(median(values)),
        "mean_ns": float(fmean(values)),
        "p75_ns": float(_nearest_rank(values, 75)),
        "p90_ns": float(_nearest_rank(values, 90)),
        "p95_ns": float(_nearest_rank(values, 95)),
        "p99_ns": float(_nearest_rank(values, 99)),
        "max_ns": float(max(values)),
        "stdev_ns": float(stdev(values)) if len(values) > 1 else 0.0,
    }


def _result_count_bucket(count: int) -> str:
    if count == 0:
        return "0"
    if count <= 5:
        return "1-5"
    if count <= 20:
        return "6-20"
    if count <= 100:
        return "21-100"
    if count <= 1000:
        return "101-1000"
    return "1000+"


def _winner_for_query(
    query_id: str,
    timing: dict[tuple[str, str], dict[str, object]],
    correctness: dict[tuple[str, str], dict[str, object]],
) -> tuple[str, ...]:
    eligible = {
        algorithm_id: float(
            timing[(query_id, algorithm_id)]["timing"]["median_ns"]
        )
        for algorithm_id in REQUIRED_ALGORITHM_IDS
        if (
            (query_id, algorithm_id) in timing
            and correctness.get((query_id, algorithm_id), {}).get("correct")
            and timing[(query_id, algorithm_id)]["repetitions_completed"] > 0
        )
    }
    if not eligible:
        return ()
    fastest = min(eligible.values())
    return tuple(
        algorithm_id for algorithm_id, value in eligible.items()
        if value <= fastest * (1.0 + TIE_TOLERANCE)
    )


def _group_analysis(
    query_ids: list[str],
    timing: dict[tuple[str, str], dict[str, object]],
    correctness: dict[tuple[str, str], dict[str, object]],
) -> dict[str, object]:
    algorithms: dict[str, object] = {}
    for algorithm_id in REQUIRED_ALGORITHM_IDS:
        rows = [
            timing[(query_id, algorithm_id)]
            for query_id in query_ids
            if (query_id, algorithm_id) in timing
            and timing[(query_id, algorithm_id)]["repetitions_completed"] > 0
        ]
        values = [float(row["timing"]["median_ns"]) for row in rows]
        algorithms[algorithm_id] = {
            **_distribution(values),
            "correct_queries": sum(
                bool(correctness.get((query_id, algorithm_id), {}).get("correct"))
                for query_id in query_ids
            ),
        }
    wins = Counter()
    ties = 0
    for query_id in query_ids:
        winners = _winner_for_query(query_id, timing, correctness)
        if len(winners) == 1:
            wins[winners[0]] += 1
        elif len(winners) > 1:
            ties += 1
    fastest = max(REQUIRED_ALGORITHM_IDS, key=lambda item: wins[item]) if query_ids else None
    return {
        "query_count": len(query_ids),
        "algorithms": algorithms,
        "fastest_correct_algorithm": fastest if wins[fastest] else None,
        "wins": dict(wins),
        "ties": ties,
        "win_percent": {
            algorithm_id: 100.0 * wins[algorithm_id] / max(1, len(query_ids))
            for algorithm_id in REQUIRED_ALGORITHM_IDS
        },
    }


def analyze_dataset(
    config: BenchmarkConfig,
    queries: tuple[object, ...],
    builds: dict[str, dict[str, object]],
    dataset: dict[str, object],
    *,
    environment: dict[str, object] | None = None,
    corpus: dict[str, object] | None = None,
) -> dict[str, object]:
    """Derive every report table from stored observations only."""
    timing = {
        (row["query_id"], row["algorithm_id"]): row
        for row in dataset["timing_rows"]
    }
    correctness = {
        (row["query_id"], row["algorithm_id"]): row
        for row in dataset["correctness_rows"]
    }
    work = {
        (row["query_id"], row["algorithm_id"]): row["metrics"]
        for row in dataset["work_rows"]
    }
    query_by_id = {query.query_id: query for query in queries}

    overall = {
        algorithm_id: _distribution([
            float(row["timing"]["median_ns"])
            for (query_id, row_algorithm), row in timing.items()
            if row_algorithm == algorithm_id and row["repetitions_completed"] > 0
        ])
        for algorithm_id in REQUIRED_ALGORITHM_IDS
    }
    correctness_summary = {}
    for algorithm_id in REQUIRED_ALGORITHM_IDS:
        rows = [
            correctness.get((query.query_id, algorithm_id), {})
            for query in queries
        ]
        incomplete_difference = any(
            bool(row) and not row.get("correct", False)
            and (
                row.get("false_negatives") is None
                or row.get("false_positives") is None
            )
            for row in rows
        )
        correctness_summary[algorithm_id] = {
            "queries_checked": sum(bool(row) for row in rows),
            "matching_result_sets": sum(bool(row.get("correct")) for row in rows),
            "mismatches": sum(bool(row) and not row.get("correct", False) for row in rows),
            "false_negatives": None if incomplete_difference else sum(
                row.get("false_negatives") or 0 for row in rows
            ),
            "false_positives": None if incomplete_difference else sum(
                row.get("false_positives") or 0 for row in rows
            ),
            "complete_counts": all(
                row.get("false_negatives") is not None
                and row.get("false_positives") is not None
                for row in rows if row
            ),
        }

    length_ids = {bucket: [] for bucket in LENGTH_BUCKETS}
    category_ids = {bucket: [] for bucket in CATEGORY_BUCKETS}
    result_ids = {bucket: [] for bucket in RESULT_COUNT_BUCKETS}
    for query in queries:
        length_ids.setdefault(query.length_bucket, []).append(query.query_id)
        for category in query.categories:
            category_ids.setdefault(category, []).append(query.query_id)
        naive_row = timing.get((query.query_id, "naive"))
        if naive_row and naive_row["result_count"] is not None:
            result_ids[_result_count_bucket(int(naive_row["result_count"]))].append(
                query.query_id
            )
    by_length = {
        bucket: _group_analysis(ids, timing, correctness)
        for bucket, ids in length_ids.items()
    }
    by_category = {
        bucket: _group_analysis(ids, timing, correctness)
        for bucket, ids in category_ids.items()
    }
    by_result_count = {
        bucket: _group_analysis(ids, timing, correctness)
        for bucket, ids in result_ids.items()
    }
    all_ids = [query.query_id for query in queries]
    overall_wins = _group_analysis(all_ids, timing, correctness)

    speedups: dict[str, object] = {}
    for algorithm_id in REQUIRED_ALGORITHM_IDS[1:]:
        ratios = []
        for query in queries:
            naive = timing.get((query.query_id, "naive"))
            optimized = timing.get((query.query_id, algorithm_id))
            if not naive or not optimized or optimized["repetitions_completed"] == 0:
                continue
            ratios.append(
                float(naive["timing"]["median_ns"])
                / max(1.0, float(optimized["timing"]["median_ns"]))
            )
        speedups[algorithm_id] = {
            "median": float(median(ratios)) if ratios else 0.0,
            "mean": float(fmean(ratios)) if ratios else 0.0,
            "p75": float(_nearest_rank(ratios, 75)) if ratios else 0.0,
            "p90": float(_nearest_rank(ratios, 90)) if ratios else 0.0,
            "best": max(ratios, default=0.0),
            "worst": min(ratios, default=0.0),
        }

    worst_cases: dict[str, object] = {}
    best_cases: dict[str, object] = {}
    for algorithm_id in REQUIRED_ALGORITHM_IDS:
        rows = sorted(
            (
                row for (query_id, row_algorithm), row in timing.items()
                if row_algorithm == algorithm_id and row["repetitions_completed"] > 0
            ),
            key=lambda row: float(row["timing"]["median_ns"]),
            reverse=True,
        )
        worst_cases[algorithm_id] = [
            {
                "query_id": row["query_id"],
                "query": row["query_text"],
                "length": row["query_length"],
                "categories": row["categories"],
                "result_count": row["result_count"],
                "median_ns": row["timing"]["median_ns"],
                "internal_work": work.get((row["query_id"], algorithm_id), {}),
            }
            for row in rows[:25]
        ]
        if algorithm_id != "naive":
            best_cases[algorithm_id] = sorted(
                (
                    {
                        "query_id": query.query_id,
                        "query": query.query_text,
                        "speedup_vs_naive": (
                            float(timing[(query.query_id, "naive")]["timing"]["median_ns"])
                            / max(1.0, float(timing[(query.query_id, algorithm_id)]["timing"]["median_ns"]))
                        ),
                        "internal_work": work.get((query.query_id, algorithm_id), {}),
                    }
                    for query in queries
                    if (query.query_id, "naive") in timing
                    and (query.query_id, algorithm_id) in timing
                    and timing[(query.query_id, algorithm_id)]["repetitions_completed"] > 0
                ),
                key=lambda row: row["speedup_vs_naive"],
                reverse=True,
            )[:20]

    naive_build = float(builds["naive"]["build_time_ns"]["median_ns"])
    break_even = {}
    for algorithm_id in REQUIRED_ALGORITHM_IDS[1:]:
        savings = []
        for query in queries:
            naive = timing.get((query.query_id, "naive"))
            optimized = timing.get((query.query_id, algorithm_id))
            if naive and optimized and optimized["repetitions_completed"] > 0:
                savings.append(
                    float(naive["timing"]["median_ns"])
                    - float(optimized["timing"]["median_ns"])
                )
        mean_saving = fmean(savings) if savings else 0.0
        extra_build = max(
            0.0,
            float(builds[algorithm_id]["build_time_ns"]["median_ns"])
            - naive_build,
        )
        break_even[algorithm_id] = (
            ceil(extra_build / mean_saving) if mean_saving > 0 else None
        )

    return {
        "benchmark_mode": config.mode.upper(),
        "configuration": {
            "query_count": len(queries),
            "timing_repetitions": config.repetitions,
            "build_repetitions": config.build_repetitions,
            "seed": config.seed,
            "full_corpus": config.full_corpus,
            "tie_tolerance_fraction": TIE_TOLERANCE,
        },
        "query_workload": query_workload_metadata(config, queries),
        "source": {"path": str(config.source), "full_corpus": config.full_corpus},
        "environment": environment or {},
        "corpus": corpus or {},
        "algorithms": {
            spec.algorithm_id: {
                "conceptual_name": spec.conceptual_name,
                "implementation": spec.implementation,
                "builder_structure": spec.builder_structure,
            }
            for spec in algorithm_specs()
        },
        "correctness": correctness_summary,
        "build": builds,
        "memory": {
            algorithm_id: {
                "peak_build_memory_bytes": builds[algorithm_id]["peak_build_memory_bytes"],
                "approx_retained_memory_bytes": builds[algorithm_id]["approx_retained_memory_bytes"],
                "method": builds[algorithm_id]["memory_method"],
            }
            for algorithm_id in REQUIRED_ALGORITHM_IDS
        },
        "overall_latency": overall,
        "by_length": by_length,
        "by_category": by_category,
        "by_result_count": by_result_count,
        "win_rates": {
            "overall": overall_wins,
            "by_length": by_length,
            "by_category": by_category,
            "by_result_count": by_result_count,
        },
        "speedup_vs_naive": speedups,
        "worst_cases": worst_cases,
        "best_cases": best_cases,
        "break_even": break_even,
        "execution_counts": {
            "timed_searches": dataset["actual_timed_searches"],
            "expected_timed_searches": dataset["expected_timed_searches"],
            "separate_naive_oracle_searches": 0,
            "previous_full_example_timed_searches": 1500 * 4 * 10,
            "reduction_vs_previous_full_example_percent": (
                100.0
                * (1.0 - float(dataset["expected_timed_searches"]) / (1500 * 4 * 10))
            ),
        },
        "errors": dataset["errors"],
    }


def _markdown_table(headers: tuple[str, ...], rows: list[tuple[object, ...]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend(
        "| " + " | ".join(str(value) for value in row) + " |"
        for row in rows
    )
    return "\n".join(lines)


def _milliseconds(value: object) -> str:
    return f"{float(value) / 1_000_000:.3f}"


def _best_for_group(group: dict[str, object]) -> str:
    winner = group.get("fastest_correct_algorithm")
    if winner is None:
        return "insufficient correct data"
    return str(winner)


def render_report(summary: dict[str, object]) -> str:
    mode = summary["benchmark_mode"]
    configuration = summary["configuration"]
    query_workload = summary["query_workload"]
    algorithms = summary["algorithms"]
    correctness = summary["correctness"]
    builds = summary["build"]
    overall = summary["overall_latency"]
    quick_warning = (
        "\n> **QUICK BENCHMARK — NOT FINAL PERFORMANCE EVIDENCE**\n"
        if mode == "QUICK" else ""
    )
    mapping_rows = [
        (
            item["conceptual_name"], item["implementation"],
            item["builder_structure"],
        )
        for item in algorithms.values()
    ]
    correctness_rows = [
        (
            algorithms[algorithm_id]["conceptual_name"],
            correctness[algorithm_id]["queries_checked"],
            correctness[algorithm_id]["mismatches"],
            correctness[algorithm_id]["false_negatives"],
            correctness[algorithm_id]["false_positives"],
        )
        for algorithm_id in REQUIRED_ALGORITHM_IDS
    ]
    build_rows = [
        (
            algorithms[algorithm_id]["conceptual_name"],
            _milliseconds(builds[algorithm_id]["build_time_ns"]["min_ns"]),
            _milliseconds(builds[algorithm_id]["build_time_ns"]["median_ns"]),
            _milliseconds(builds[algorithm_id]["build_time_ns"]["mean_ns"]),
            _milliseconds(builds[algorithm_id]["build_time_ns"]["max_ns"]),
        )
        for algorithm_id in REQUIRED_ALGORITHM_IDS
    ]
    overall_rows = [
        (
            algorithms[algorithm_id]["conceptual_name"],
            _milliseconds(overall[algorithm_id]["median_ns"]),
            _milliseconds(overall[algorithm_id]["mean_ns"]),
            _milliseconds(overall[algorithm_id]["p95_ns"]),
            _milliseconds(overall[algorithm_id]["p99_ns"]),
            _milliseconds(overall[algorithm_id]["max_ns"]),
        )
        for algorithm_id in REQUIRED_ALGORITHM_IDS
    ]
    length_rows = []
    for bucket in LENGTH_BUCKETS:
        group = summary["by_length"][bucket]
        length_rows.append((
            bucket,
            group["query_count"],
            *(
                f"{_milliseconds(group['algorithms'][algorithm_id]['median_ns'])} / "
                f"{_milliseconds(group['algorithms'][algorithm_id]['p95_ns'])}"
                for algorithm_id in REQUIRED_ALGORITHM_IDS
            ),
            _best_for_group(group),
            f"{max(group['win_percent'].values(), default=0.0):.2f}%",
            "/".join(
                str(group["algorithms"][algorithm_id]["correct_queries"])
                for algorithm_id in REQUIRED_ALGORITHM_IDS
            ),
        ))
    category_rows = []
    for category in CATEGORY_BUCKETS:
        group = summary["by_category"][category]
        category_rows.append((
            category, group["query_count"],
            *(
                f"{_milliseconds(group['algorithms'][algorithm_id]['median_ns'])} / "
                f"{_milliseconds(group['algorithms'][algorithm_id]['p95_ns'])}"
                for algorithm_id in REQUIRED_ALGORITHM_IDS
            ),
            _best_for_group(group),
            f"{max(group['win_percent'].values(), default=0.0):.2f}%",
            "/".join(
                str(group["algorithms"][algorithm_id]["correct_queries"])
                for algorithm_id in REQUIRED_ALGORITHM_IDS
            ),
        ))
    count_rows = []
    for bucket in RESULT_COUNT_BUCKETS:
        group = summary["by_result_count"][bucket]
        count_rows.append((
            bucket, group["query_count"],
            *(
                _milliseconds(group["algorithms"][algorithm_id]["median_ns"])
                for algorithm_id in REQUIRED_ALGORITHM_IDS
            ),
        ))
    wins = summary["win_rates"]["overall"]
    win_rows = [
        (
            algorithms[algorithm_id]["conceptual_name"],
            wins["wins"].get(algorithm_id, 0),
            f"{wins['win_percent'][algorithm_id]:.2f}%",
        )
        for algorithm_id in REQUIRED_ALGORITHM_IDS
    ]
    win_rows.append(("Ties", wins["ties"], f"{100.0 * wins['ties'] / max(1, wins['query_count']):.2f}%"))
    memory_rows = [
        (
            algorithms[algorithm_id]["conceptual_name"],
            summary["memory"][algorithm_id]["peak_build_memory_bytes"],
            summary["memory"][algorithm_id]["approx_retained_memory_bytes"],
            summary["memory"][algorithm_id]["method"],
        )
        for algorithm_id in REQUIRED_ALGORITHM_IDS
    ]
    complete_algorithms = [
        algorithm_id for algorithm_id in REQUIRED_ALGORITHM_IDS
        if correctness[algorithm_id]["mismatches"] == 0
    ]
    fastest = min(
        complete_algorithms,
        key=lambda algorithm_id: overall[algorithm_id]["median_ns"],
        default=None,
    )
    cheapest_build = min(
        REQUIRED_ALGORITHM_IDS,
        key=lambda algorithm_id: builds[algorithm_id]["build_time_ns"]["median_ns"],
    )
    least_memory = min(
        REQUIRED_ALGORITHM_IDS,
        key=lambda algorithm_id: summary["memory"][algorithm_id]["approx_retained_memory_bytes"],
    )
    correctness_answers = [
        f"{algorithms[algorithm_id]['conceptual_name']} correctness: "
        + (
            "all checked raw result sets matched Naive."
            if correctness[algorithm_id]["mismatches"] == 0
            else f"INCORRECT on {correctness[algorithm_id]['mismatches']} queries; "
            f"FN={correctness[algorithm_id]['false_negatives']}, "
            f"FP={correctness[algorithm_id]['false_positives']}."
        )
        for algorithm_id in REQUIRED_ALGORITHM_IDS[1:]
    ]
    optimized_losers = [
        algorithm_id for algorithm_id in REQUIRED_ALGORITHM_IDS[1:]
        if correctness[algorithm_id]["false_negatives"] not in (0, None)
        or correctness[algorithm_id]["false_positives"] not in (0, None)
        or correctness[algorithm_id]["mismatches"] > 0
    ]
    dominated = [
        algorithm_id for algorithm_id in REQUIRED_ALGORITHM_IDS
        if wins["wins"].get(algorithm_id, 0) == 0
    ]
    worst_measured = max(
        (
            (algorithm_id, cases[0])
            for algorithm_id, cases in summary["worst_cases"].items()
            if cases
        ),
        key=lambda item: item[1]["median_ns"],
        default=(None, None),
    )
    conclusions = [
        f"Fastest overall correct algorithm: `{fastest or 'none'}`.",
        *(
            f"Best for length {length}: `{_best_for_group(summary['by_length'][str(length)])}`."
            for length in range(1, 7)
        ),
        f"Best for medium queries (9–12): `{_best_for_group(summary['by_length']['9-12'])}`.",
        f"Best for long queries (21+): `{_best_for_group(summary['by_length']['21+'])}`.",
        f"Best inside-word: `{_best_for_group(summary['by_category']['inside_word'])}`.",
        f"Best cross-word: `{_best_for_group(summary['by_category']['cross_word'])}`.",
        f"Best common: `{_best_for_group(summary['by_category']['common'])}`.",
        f"Best rare: `{_best_for_group(summary['by_category']['rare'])}`.",
        f"Best no-match: `{_best_for_group(summary['by_category']['no_match'])}`.",
        f"Cheapest measured build: `{cheapest_build}`.",
        f"Least approximate retained/index memory: `{least_memory}`.",
        *correctness_answers,
        "Optimized algorithms that lost or added raw matches: "
        + (", ".join(optimized_losers) if optimized_losers else "none" )
        + ".",
        "Algorithms with zero per-query wins in this workload: "
        + (", ".join(dominated) if dominated else "none")
        + "; this is the measured dominance indicator, not a proof for every workload.",
        (
            f"Largest measured latency bottleneck: `{worst_measured[0]}` on "
            f"query `{worst_measured[1]['query']}` at "
            f"{_milliseconds(worst_measured[1]['median_ns'])} ms; its stored "
            f"work counters are `{json.dumps(worst_measured[1]['internal_work'])}`."
            if worst_measured[1] is not None
            else "Largest measured latency bottleneck: insufficient data."
        ),
        "Correctness is based on the retained timed Naive result; no separate Naive oracle search was run.",
        "Next experiment: target the largest counter in the worst stored correct-algorithm case, then rerun the saved `queries.json` without changing match semantics.",
    ]
    sections = [
        "# Benchmark Configuration",
        quick_warning,
        f"Mode: **{mode}**  ",
        f"Queries: {configuration['query_count']}  ",
        f"Timing repetitions: {configuration['timing_repetitions']}  ",
        f"Build repetitions: {configuration['build_repetitions']}  ",
        f"Expected timed search executions: {summary['execution_counts']['expected_timed_searches']}",
        f"Query source: **{query_workload['source']}**  ",
        f"Query file: `{query_workload['file']}`  ",
        f"Query count: {query_workload['query_count']}  ",
        f"Query file SHA-256: `{query_workload['sha256']}`",
        "",
        "# Environment", "", "```json\n" + json.dumps(summary["environment"], indent=2) + "\n```",
        "", "# Corpus Summary", "", "```json\n" + json.dumps(summary["corpus"], indent=2) + "\n```",
        "", "# Algorithm Mapping", "", _markdown_table(("Concept", "Implementation", "Builder / structure"), mapping_rows),
        "", "# Correctness", "", _markdown_table(("Algorithm", "Queries", "Mismatches", "FN", "FP"), correctness_rows),
        "", "# Build Time", "", _markdown_table(("Algorithm", "Min ms", "Median ms", "Mean ms", "Max ms"), build_rows),
        "", "# Memory", "", _markdown_table(("Algorithm", "Peak build B", "Retained B", "Method"), memory_rows),
        "", "# Overall Search Performance", "", _markdown_table(("Algorithm", "Median ms", "Mean ms", "P95 ms", "P99 ms", "Max ms"), overall_rows),
        "", "# Query Length 1–6", "", _markdown_table(("Length", "N", "Naive med/p95", "QG+V med/p95", "Tree med/p95", "Bi med/p95", "Fastest correct", "Winner %", "Correct N/Q/T/B"), length_rows[:6]),
        "", "# Longer Query Length Groups", "", _markdown_table(("Length", "N", "Naive med/p95", "QG+V med/p95", "Tree med/p95", "Bi med/p95", "Fastest correct", "Winner %", "Correct N/Q/T/B"), length_rows[6:]),
        "", "# Query Categories", "", _markdown_table(("Category", "N", "Naive med/p95", "QG+V med/p95", "Tree med/p95", "Bi med/p95", "Fastest correct", "Winner %", "Correct N/Q/T/B"), category_rows),
        "", "# Match Count Analysis", "", _markdown_table(("Raw matches", "N", "Naive", "QG+V", "Tree", "Bi"), count_rows),
        "", "# Win Rates", "", _markdown_table(("Algorithm", "Wins", "Percent"), win_rows),
        "", "# Speedup vs Naive", "", "```json\n" + json.dumps(summary["speedup_vs_naive"], indent=2) + "\n```",
        "", "# Worst Queries", "", "```json\n" + json.dumps(summary["worst_cases"], indent=2) + "\n```",
        "", "# Best Queries", "", "```json\n" + json.dumps(summary["best_cases"], indent=2) + "\n```",
        "", "# Internal Work Metrics", "", "Worst/best entries above include their stored counters. The complete per-query data is in `internal_work_metrics.json`; no search was rerun to create this report.",
        "", "# Build/Search Break-Even", "", "```json\n" + json.dumps(summary["break_even"], indent=2) + "\n```",
    ]
    if mode == "DEEP":
        sections.extend(("", "# Scaling", "", "```json\n" + json.dumps(summary.get("deep_studies", {}).get("scaling", {}), indent=2) + "\n```", "", "# q Study", "", "```json\n" + json.dumps(summary.get("deep_studies", {}).get("q_study", {}), indent=2) + "\n```"))
    sections.extend((
        "", "# Conclusions", "", *conclusions,
        "", "Algorithm redesign is outside this benchmark run.",
    ))
    return "\n".join(sections).replace("\n\n\n", "\n\n") + "\n"


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def write_run_artifacts(
    output: Path,
    *,
    config: BenchmarkConfig,
    environment: dict[str, object],
    corpus: dict[str, object],
    queries: tuple[object, ...],
    builds: dict[str, dict[str, object]],
    dataset: dict[str, object],
    summary: dict[str, object],
) -> None:
    output.mkdir(parents=True, exist_ok=True)
    _write_json(output / "environment.json", environment)
    _write_json(output / "corpus_summary.json", corpus)
    _write_json(output / "queries.json", {
        "seed": summary["query_workload"]["seed"],
        "query_source": summary["query_workload"]["source"],
        "query_file": summary["query_workload"]["file"],
        "query_file_sha256": summary["query_workload"]["sha256"],
        "query_count": len(queries),
        "queries": [asdict(query) for query in queries],
    })
    _write_json(output / "build_results.json", builds)
    _write_json(output / "correctness_results.json", dataset["correctness_rows"])
    _write_json(output / "raw_timings.json", {
        "clock": dataset["clock"],
        "expected_timed_searches": dataset["expected_timed_searches"],
        "actual_timed_searches": dataset["actual_timed_searches"],
        "rows": dataset["timing_rows"],
    })
    _write_json(output / "internal_work_metrics.json", dataset["work_rows"])
    _write_json(output / "summary.json", summary)
    if dataset["errors"]:
        _write_json(output / "errors.json", dataset["errors"])

    correctness = {
        (row["query_id"], row["algorithm_id"]): row
        for row in dataset["correctness_rows"]
    }
    work = {
        (row["query_id"], row["algorithm_id"]): row["metrics"]
        for row in dataset["work_rows"]
    }
    naive_medians = {
        row["query_id"]: float(row["timing"]["median_ns"])
        for row in dataset["timing_rows"]
        if row["algorithm_id"] == "naive" and row["repetitions_completed"]
    }
    fields = (
        "query_id", "query_text", "query_length", "category", "algorithm",
        "correctness_status", "result_count", "min_ms", "median_ms",
        "mean_ms", "max_ms", "p95_ms", "speedup_vs_naive",
        "fallback_used", "candidate_count", "verifier_calls",
        "posting_count", "tree_nodes_visited", "selected_seed_A",
        "selected_seed_B", "frequency_A", "frequency_B",
    )
    with (output / "per_query_results.csv").open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=fields)
        writer.writeheader()
        for row in dataset["timing_rows"]:
            key = (row["query_id"], row["algorithm_id"])
            metrics = work.get(key, {})
            timing_values = row["timing"]
            selected = metrics.get("last_selected_seeds") or []
            first = selected[0] if len(selected) > 0 else {}
            second = selected[1] if len(selected) > 1 else {}
            median_value = float(timing_values["median_ns"])
            writer.writerow({
                "query_id": row["query_id"],
                "query_text": row["query_text"],
                "query_length": row["query_length"],
                "category": row["category"],
                "algorithm": row["algorithm_id"],
                "correctness_status": correctness.get(key, {}).get("status", "missing"),
                "result_count": row["result_count"],
                "min_ms": float(timing_values["min_ns"]) / 1_000_000,
                "median_ms": median_value / 1_000_000,
                "mean_ms": float(timing_values["mean_ns"]) / 1_000_000,
                "max_ms": float(timing_values["max_ns"]) / 1_000_000,
                "p95_ms": (
                    "" if timing_values["p95_ns"] is None
                    else float(timing_values["p95_ns"]) / 1_000_000
                ),
                "speedup_vs_naive": (
                    naive_medians.get(row["query_id"], 0.0) / max(1.0, median_value)
                ),
                "fallback_used": metrics.get("fallback_count", ""),
                "candidate_count": next((metrics[name] for name in (
                    "candidate_starts_after_dedup", "candidate_contexts_after_dedup",
                    "candidate_words",
                ) if name in metrics), ""),
                "verifier_calls": metrics.get("verifier_calls", ""),
                "posting_count": metrics.get("posting_entries_scanned", ""),
                "tree_nodes_visited": metrics.get("tree_nodes_visited", ""),
                "selected_seed_A": first.get("text", ""),
                "selected_seed_B": second.get("text", ""),
                "frequency_A": first.get("frequency", ""),
                "frequency_B": second.get("frequency", ""),
            })
    (output / "benchmark_report.md").write_text(
        render_report(summary), encoding="utf-8"
    )


def prepare_queries(
    sentences: tuple[object, ...], config: BenchmarkConfig
) -> tuple[object, ...]:
    if config.query_file is not None:
        if not config.query_file.is_file():
            raise FileNotFoundError(config.query_file)
        return load_queries(config.query_file)
    return generate_workload(
        sentences,
        seed=config.seed,
        target_count=config.query_count,
        per_short_length=config.short_queries_per_length,
    )


def query_workload_metadata(
    config: BenchmarkConfig,
    queries: tuple[object, ...],
) -> dict[str, object]:
    """Describe the exact ordered workload used by one benchmark run."""
    if config.query_file is None:
        return {
            "source": "GENERATED",
            "file": None,
            "query_count": len(queries),
            "sha256": None,
            "seed": config.seed,
        }

    payload = json.loads(config.query_file.read_text(encoding="utf-8"))
    seed = (
        payload["random_seed_used_to_create_it"]
        if "random_seed_used_to_create_it" in payload
        else payload.get("seed")
    )
    return {
        "source": "SAVED",
        "file": str(config.query_file.resolve()),
        "query_count": len(queries),
        "sha256": _sha256(config.query_file),
        "seed": seed,
    }


def validity_reasons(
    config: BenchmarkConfig,
    queries: tuple[object, ...],
    builds: dict[str, dict[str, object]],
    dataset: dict[str, object],
    corpus: dict[str, object],
) -> list[str]:
    reasons: list[str] = []
    if corpus.get("corpus_fraction") != 1.0:
        reasons.append("100% of the selected source corpus was not processed")
    if tuple(builds) != REQUIRED_ALGORITHM_IDS:
        reasons.append("build results do not contain all four algorithms")
    if "qgram_verifier" not in builds:
        reasons.append("Q-GRAM + VERIFIER is missing")
    lengths = {query.query_length for query in queries}
    for length in range(1, 7):
        if length not in lengths:
            reasons.append(f"query length {length} is not represented")
    expected_pairs = {
        (query.query_id, algorithm_id)
        for query in queries for algorithm_id in REQUIRED_ALGORITHM_IDS
    }
    for row_name in ("timing_rows", "correctness_rows", "work_rows"):
        actual_pairs = {
            (row["query_id"], row["algorithm_id"])
            for row in dataset.get(row_name, [])
        }
        if actual_pairs != expected_pairs:
            reasons.append(f"{row_name} is missing query/algorithm observations")
    if config.mode == "standard" and config.repetitions < 2:
        reasons.append("STANDARD did not use multiple timing repetitions")
    incomplete_timing = [
        row for row in dataset.get("timing_rows", [])
        if row["repetitions_completed"] != config.repetitions
    ]
    if incomplete_timing:
        reasons.append("one or more per-query timing repetitions are incomplete")
    if dataset.get("errors"):
        reasons.append("one or more mandatory algorithm/query executions failed")
    incorrect_algorithms = sorted({
        row["algorithm_id"]
        for row in dataset.get("correctness_rows", [])
        if row["algorithm_id"] != "naive" and not row.get("correct", False)
    })
    for algorithm_id in incorrect_algorithms:
        reasons.append(
            f"{algorithm_id} has one or more raw-result correctness mismatches"
        )
    if not builds or any(
        not result.get("build_time_ns", {}).get("samples")
        for result in builds.values()
    ):
        reasons.append("build timing is missing")
    if builds and any(
        "peak_build_memory_bytes" not in result for result in builds.values()
    ):
        reasons.append("separate memory measurement is missing")
    return reasons


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def environment_metadata(
    config: BenchmarkConfig, timestamp: datetime
) -> dict[str, object]:
    def git(*args: str) -> str:
        completed = subprocess.run(
            ("git", *args), capture_output=True, text=True, check=False
        )
        return completed.stdout.strip() or "unavailable"

    return {
        "timestamp_utc": timestamp.astimezone(timezone.utc).isoformat(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "cpu": platform.processor()
        or os.environ.get("PROCESSOR_IDENTIFIER", "unknown"),
        "process_architecture": platform.architecture()[0],
        "git_branch": git("branch", "--show-current"),
        "git_commit_sha": git("rev-parse", "HEAD"),
        "source_path": str(config.source.resolve()),
        "source_size_bytes": config.source.stat().st_size,
        "source_sha256": _sha256(config.source),
        "benchmark_mode": config.mode.upper(),
        "benchmark_arguments": {
            "queries": config.query_count,
            "repetitions": config.repetitions,
            "build_repetitions": config.build_repetitions,
            "seed": config.seed,
            "query_file": str(config.query_file) if config.query_file else None,
            "q_study": config.q_study,
        },
    }


def corpus_statistics(
    sentences: tuple[object, ...], preparation_time_ns: int
) -> dict[str, object]:
    lengths = [len(sentence.normalized_text) for sentence in sentences]
    words = [
        word
        for sentence in sentences
        for word in sentence.normalized_text.split()
    ]
    return {
        "corpus_fraction": 1.0,
        "source_files": len({sentence.source_path for sentence in sentences}),
        "prepared_sentences": len(sentences),
        "total_original_characters": sum(
            len(sentence.original_text) for sentence in sentences
        ),
        "total_normalized_characters": sum(lengths),
        "word_occurrences": len(words),
        "unique_normalized_words": len(set(words)),
        "preparation_time_ns": preparation_time_ns,
        "sentence_length": {
            "min": min(lengths, default=0),
            "mean": float(fmean(lengths)) if lengths else 0.0,
            "median": float(median(lengths)) if lengths else 0.0,
            "p75": _nearest_rank(lengths, 75),
            "p90": _nearest_rank(lengths, 90),
            "p95": _nearest_rank(lengths, 95),
            "p99": _nearest_rank(lengths, 99),
            "max": max(lengths, default=0),
        },
    }


def _print_configuration(config: BenchmarkConfig, specs: tuple[AlgorithmSpec, ...]) -> None:
    print("=" * 66)
    print(f"Benchmark mode: {config.mode.upper()}")
    print(f"Source: {config.source}")
    print("Corpus: 100%")
    print(f"Queries: {config.query_count}")
    print(f"Timing repetitions: {config.repetitions}")
    print(f"Build repetitions: {config.build_repetitions}")
    print(f"Algorithms: {len(specs)}")
    print(f"Expected timed search executions: {config.expected_timed_searches}")
    print("=" * 66)
    print("Conceptual algorithm       Actual implementation")
    print("-" * 66)
    for spec in specs:
        print(f"{spec.conceptual_name:<27}{spec.implementation}")
    if config.mode == "quick":
        print("QUICK BENCHMARK — NOT FINAL PERFORMANCE EVIDENCE")


def secondary_study_plan(config: BenchmarkConfig) -> dict[str, bool]:
    deep = config.mode == "deep"
    return {
        "profiling": deep,
        "scaling": deep,
        "q_study": bool(config.q_study),
        "repeatability": deep,
    }


def even_corpus_slice(
    sentences: tuple[object, ...], fraction: float
) -> tuple[object, ...]:
    if not 0 < fraction <= 1:
        raise ValueError("fraction must be in (0, 1]")
    if fraction == 1.0:
        return sentences
    wanted = max(1, ceil(len(sentences) * fraction))
    if wanted == 1:
        return (sentences[0],)
    indexes = [
        round(index * (len(sentences) - 1) / (wanted - 1))
        for index in range(wanted)
    ]
    return tuple(sentences[index] for index in indexes)


def run_deep_studies(
    config: BenchmarkConfig,
    sentences: tuple[object, ...],
    queries: tuple[object, ...],
    specs: tuple[AlgorithmSpec, ...],
    runtimes: dict[str, object],
    primary_dataset: dict[str, object],
) -> dict[str, object]:
    """Run expensive diagnostics only after the primary stored dataset exists."""
    plan = secondary_study_plan(config)
    result: dict[str, object] = {}

    if plan["profiling"]:
        profiles: list[dict[str, object]] = []
        for spec in specs:
            profiles.append(_profile_call(
                f"build:{spec.algorithm_id}",
                spec.factory,
                sentences,
                instrument=False,
            ))
        naive_rows = sorted(
            (
                row for row in primary_dataset["timing_rows"]
                if row["algorithm_id"] == "naive"
                and row["repetitions_completed"] > 0
            ),
            key=lambda row: float(row["timing"]["median_ns"]),
        )
        selected_rows = []
        if naive_rows:
            selected_rows = [
                naive_rows[0], naive_rows[len(naive_rows) // 2], naive_rows[-1]
            ]
        query_by_id = {query.query_id: query for query in queries}
        for row in selected_rows:
            query = query_by_id[row["query_id"]]
            for algorithm_id in REQUIRED_ALGORITHM_IDS:
                profiles.append(_profile_call(
                    f"search:{algorithm_id}:{query.query_id}",
                    runtimes[algorithm_id].search,
                    query.normalized_query,
                ))
        result["profiling"] = {
            "status": "completed", "profiles": profiles
        }
    else:
        result["profiling"] = {"status": "not run outside DEEP"}

    study_queries = tuple(queries[: min(20, len(queries))])
    if plan["scaling"]:
        scaling_rows = []
        for fraction in (0.10, 0.25, 0.50, 0.75, 1.0):
            corpus_slice = even_corpus_slice(sentences, fraction)
            scale_builds, scale_runtimes = measure_builds(
                specs, corpus_slice, repetitions=1
            )
            scale_config = replace(
                config,
                mode="quick",
                query_count=len(study_queries),
                repetitions=1,
                build_repetitions=1,
            )
            scale_dataset = run_search_phase(
                scale_config, study_queries, scale_runtimes
            )
            scaling_rows.append({
                "fraction": fraction,
                "sentences": len(corpus_slice),
                "build": scale_builds,
                "online_latency": {
                    algorithm_id: _distribution([
                        float(row["timing"]["median_ns"])
                        for row in scale_dataset["timing_rows"]
                        if row["algorithm_id"] == algorithm_id
                        and row["repetitions_completed"] > 0
                    ])
                    for algorithm_id in REQUIRED_ALGORITHM_IDS
                },
                "errors": scale_dataset["errors"],
            })
        result["scaling"] = {
            "status": "completed", "rows": scaling_rows
        }
    else:
        result["scaling"] = {"status": "not run outside DEEP"}

    if plan["q_study"]:
        q_rows = []
        for q in (2, 3, 4):
            q_specs = _q_algorithm_specs(q)
            q_builds, q_runtimes = measure_builds(
                q_specs, sentences, repetitions=1
            )
            algorithm_rows = {}
            for algorithm_id, runtime in q_runtimes.items():
                samples = []
                errors = []
                for query in study_queries:
                    try:
                        started = perf_counter_ns()
                        runtime.search(query.normalized_query)
                        samples.append(perf_counter_ns() - started)
                    except Exception as error:
                        errors.append({
                            "query_id": query.query_id,
                            "exception": repr(error),
                            "traceback": traceback.format_exc(),
                        })
                algorithm_rows[algorithm_id] = {
                    "latency": _distribution([float(item) for item in samples]),
                    "errors": errors,
                }
            q_rows.append({"q": q, "build": q_builds, "algorithms": algorithm_rows})
        result["q_study"] = {"status": "completed", "rows": q_rows}
    else:
        result["q_study"] = {"status": "not requested"}

    if plan["repeatability"]:
        repeat_queries = tuple(queries[: min(100, len(queries))])
        repeat_config = replace(
            config, mode="quick", query_count=len(repeat_queries), repetitions=1
        )
        repeat_dataset = run_search_phase(
            repeat_config, repeat_queries, runtimes
        )
        primary = {
            (row["query_id"], row["algorithm_id"]): float(
                row["timing"]["median_ns"]
            )
            for row in primary_dataset["timing_rows"]
            if row["repetitions_completed"] > 0
        }
        deltas: dict[str, list[float]] = {
            algorithm_id: [] for algorithm_id in REQUIRED_ALGORITHM_IDS
        }
        for row in repeat_dataset["timing_rows"]:
            key = (row["query_id"], row["algorithm_id"])
            if key not in primary or row["repetitions_completed"] == 0:
                continue
            second = float(row["timing"]["median_ns"])
            deltas[row["algorithm_id"]].append(
                100.0 * (second - primary[key]) / max(1.0, primary[key])
            )
        result["repeatability"] = {
            "status": "completed",
            "query_count": len(repeat_queries),
            "median_percent_change": {
                algorithm_id: float(median(values)) if values else None
                for algorithm_id, values in deltas.items()
            },
            "errors": repeat_dataset["errors"],
        }
    else:
        result["repeatability"] = {"status": "not run outside DEEP"}
    return result


def _profile_call(label: str, function: Callable[..., object], *args, **kwargs) -> dict[str, object]:
    profiler = cProfile.Profile()
    started = perf_counter_ns()
    profiler.enable()
    try:
        function(*args, **kwargs)
        error = None
    except Exception as caught:
        error = repr(caught)
    finally:
        profiler.disable()
    stream = io.StringIO()
    pstats.Stats(profiler, stream=stream).strip_dirs().sort_stats("cumulative").print_stats(20)
    return {
        "label": label,
        "elapsed_ns": perf_counter_ns() - started,
        "error": error,
        "top_cumulative": stream.getvalue(),
    }


def _q_algorithm_specs(q: int) -> tuple[AlgorithmSpec, ...]:
    return (
        AlgorithmSpec(
            "qgram_verifier", "Q-Gram + Verifier",
            "QGramSearchAlgorithm", f"QGramSearchStructure(q={q})",
            lambda sentences, *, instrument, selected_q=q: _make_qgram(
                sentences, instrument=instrument, q=selected_q
            ),
        ),
        AlgorithmSpec(
            "qgram_tree_hybrid", "Q-Gram + Tree Hybrid",
            "QGramTrieSearchAlgorithm", f"Trie + q-gram map(q={q})",
            lambda sentences, *, instrument, selected_q=q: _make_tree(
                sentences, instrument=instrument, q=selected_q
            ),
        ),
        AlgorithmSpec(
            "bi_anchor", "Selective Bi-Anchor",
            "BiAnchorSearchAlgorithm", f"BiAnchorSearchStructure(q={q})",
            lambda sentences, *, instrument, selected_q=q: _make_bi_anchor(
                sentences, instrument=instrument, q=selected_q
            ),
        ),
    )


def main(argv: list[str] | None = None) -> int:
    config = resolve_config(parse_args(argv))
    if not config.source.is_file():
        raise FileNotFoundError(config.source)
    specs = algorithm_specs()
    validate_algorithm_specs(specs)
    timestamp = datetime.now(timezone.utc)
    output = allocate_run_directory(config, timestamp)
    output.mkdir(parents=True, exist_ok=True)
    _print_configuration(config, specs)

    print("[1/8] Preparing corpus...", flush=True)
    started = perf_counter_ns()
    sentences = tuple(DataPreparer().prepare(config.source))
    preparation_time = perf_counter_ns() - started
    corpus = corpus_statistics(sentences, preparation_time)
    print(f"      100% - {len(sentences):,} sentences", flush=True)

    print("[2/8] Generating/loading queries...", flush=True)
    queries = prepare_queries(sentences, config)
    if len(queries) != config.query_count and config.query_file is None:
        raise RuntimeError(
            f"query generator returned {len(queries)} of {config.query_count} queries"
        )
    if config.query_file is not None:
        config = replace(config, query_count=len(queries))
    print(f"      {len(queries):,} unique queries", flush=True)
    print(
        f"      Expected timed search executions: "
        f"{config.expected_timed_searches:,}",
        flush=True,
    )

    print("[3/8] Pure build timing, separate memory, and final builds...", flush=True)
    builds, runtimes = measure_builds(
        specs, sentences, repetitions=config.build_repetitions
    )
    for spec in specs:
        print(f"      {spec.conceptual_name:<27}done", flush=True)

    print("[4/8] Warm-up is performed uniformly inside the search phase.", flush=True)
    print("[5/8] Benchmarking sequential search calls...", flush=True)
    search_started = perf_counter_ns()
    progress_interval = max(1, len(queries) // 20)

    def report_progress(
        completed: int, total: int, elapsed: float, eta: float
    ) -> None:
        if completed == total or completed % progress_interval == 0:
            print(
                f"      Query {completed:,} / {total:,}; "
                f"elapsed: {elapsed:.1f}s; ETA: {eta:.1f}s",
                flush=True,
            )

    dataset = run_search_phase(config, queries, runtimes, progress=report_progress)
    elapsed_seconds = (perf_counter_ns() - search_started) / 1_000_000_000
    print(
        f"      {len(queries):,}/{len(queries):,} queries; "
        f"elapsed: {elapsed_seconds:.1f}s; ETA: 0s",
        flush=True,
    )

    print("[6/8] Running DEEP-only diagnostics when selected...", flush=True)
    deep_studies = run_deep_studies(
        config, sentences, queries, specs, runtimes, dataset
    )
    environment = environment_metadata(config, timestamp)

    print("[7/8] Analyzing stored results...", flush=True)
    summary = analyze_dataset(
        config,
        queries,
        builds,
        dataset,
        environment=environment,
        corpus=corpus,
    )
    summary["deep_studies"] = deep_studies
    reasons = validity_reasons(config, queries, builds, dataset, corpus)
    summary["validity"] = {
        "complete": not reasons,
        "reasons": reasons,
    }

    print("[8/8] Writing report and machine-readable artifacts...", flush=True)
    write_run_artifacts(
        output,
        config=config,
        environment=environment,
        corpus=corpus,
        queries=queries,
        builds=builds,
        dataset=dataset,
        summary=summary,
    )
    if reasons:
        print("BENCHMARK INCOMPLETE")
        for reason in reasons:
            print(f"- {reason}")
        print(f"Artifacts: {output}")
        return 1
    if config.mode == "quick":
        print("QUICK BENCHMARK FINISHED — NOT FINAL PERFORMANCE EVIDENCE")
    else:
        print("BENCHMARK COMPLETE")
    print(f"Artifacts: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
