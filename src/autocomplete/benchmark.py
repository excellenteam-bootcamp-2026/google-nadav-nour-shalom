from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
import json
from math import ceil
from pathlib import Path
import random
from statistics import fmean, median
from time import perf_counter_ns
import tracemalloc

from src.algorithms.bi_anchor_search_algorithm import BiAnchorSearchAlgorithm
from src.algorithms.bi_anchor_search_stats import BiAnchorSearchStats
from src.algorithms.naive_search_algorithm import NaiveSearchAlgorithm
from src.algorithms.naive_search_stats import NaiveSearchStats
from src.autocomplete.preparation import DataPreparer
from src.builders.bi_anchor_structure_builder import BiAnchorStructureBuilder
from src.builders.naive_structure_builder import NaiveStructureBuilder
from src.models.edit_type import EditType
from src.models.match_candidate import MatchCandidate
from src.models.prepared_sentence import PreparedSentence
from src.search_engine import SearchEngine


CandidateKey = tuple[int, int, EditType, int | None, int]


@dataclass(frozen=True, slots=True)
class BenchmarkQuery:
    category: str
    query: str


@dataclass(frozen=True, slots=True)
class LatencySummary:
    mean_ns: float
    median_ns: float
    p95_ns: float


@dataclass(frozen=True, slots=True)
class AlgorithmMetrics:
    latency: LatencySummary
    verifier_calls: int
    candidate_contexts: int


@dataclass(frozen=True, slots=True)
class CorrectnessMetrics:
    total_queries: int
    matching_result_sets: int
    mismatches: int
    false_negatives: int
    false_positives: int


@dataclass(frozen=True, slots=True)
class CategoryMetrics:
    queries: int
    naive: LatencySummary
    bi_anchor: LatencySummary
    speedup: float


@dataclass(frozen=True, slots=True)
class IndexMetrics:
    build_ns: int
    peak_memory_bytes: int
    unique_words: int
    word_occurrences: int
    intra_word_seed_keys: int
    intra_word_seed_references: int
    boundary_seed_keys: int
    boundary_occurrences: int


@dataclass(frozen=True, slots=True)
class SearchBenchmarkReport:
    dataset: str
    q: int
    corpus_sentences: int
    queries: int
    repeats: int
    correctness: CorrectnessMetrics
    naive: AlgorithmMetrics
    bi_anchor: AlgorithmMetrics
    categories: dict[str, CategoryMetrics]
    speedup: float
    candidate_reduction_ratio: float
    verifier_call_reduction_ratio: float
    fallback_rate: float
    average_selected_seed_frequency: float
    seed_occurrences_expanded: int
    candidate_contexts_before_dedup: int
    candidate_contexts_after_dedup: int
    index: IndexMetrics

    def to_dict(self) -> dict:
        return asdict(self)


def canonicalize_matches(
    matches: list[MatchCandidate],
) -> Counter[CandidateKey]:
    """Keep every semantically relevant raw candidate field."""
    return Counter(
        (
            match.sentence.sentence_id,
            match.match_start,
            match.edit_type,
            match.edit_index,
            match.correct_characters,
        )
        for match in matches
    )


def percentile_95(samples: list[int]) -> int:
    if not samples:
        return 0
    ordered = sorted(samples)
    return ordered[max(0, ceil(0.95 * len(ordered)) - 1)]


def _latency_summary(samples: list[int]) -> LatencySummary:
    if not samples:
        return LatencySummary(0.0, 0.0, 0.0)
    return LatencySummary(
        mean_ns=fmean(samples),
        median_ns=median(samples),
        p95_ns=float(percentile_95(samples)),
    )


def _speedup(naive_ns: float, bi_anchor_ns: float) -> float:
    return naive_ns / bi_anchor_ns if bi_anchor_ns else 0.0


def _reduction(original: int, optimized: int) -> float:
    return 1.0 - (optimized / original) if original else 0.0


def evaluate_search_algorithms(
    *,
    dataset_name: str,
    sentences: tuple[PreparedSentence, ...],
    queries: tuple[BenchmarkQuery, ...],
    q: int = 3,
    repeats: int = 5,
) -> SearchBenchmarkReport:
    if repeats <= 0:
        raise ValueError("repeats must be positive.")

    naive_structure = NaiveStructureBuilder().build(sentences)

    tracemalloc.start()
    bi_anchor_structure = BiAnchorStructureBuilder(q=q).build(sentences)
    _current_memory, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    naive_stats = NaiveSearchStats()
    bi_anchor_stats = BiAnchorSearchStats()
    naive_correctness = NaiveSearchAlgorithm(stats=naive_stats)
    bi_anchor_correctness = BiAnchorSearchAlgorithm(stats=bi_anchor_stats)

    matching = 0
    mismatches = 0
    false_negatives = 0
    false_positives = 0
    for item in queries:
        expected = canonicalize_matches(
            naive_correctness.search(item.query, naive_structure)
        )
        actual = canonicalize_matches(
            bi_anchor_correctness.search(item.query, bi_anchor_structure)
        )
        missing = expected - actual
        unexpected = actual - expected
        if missing or unexpected:
            mismatches += 1
        else:
            matching += 1
        false_negatives += sum(missing.values())
        false_positives += sum(unexpected.values())

    naive_timing = NaiveSearchAlgorithm()
    bi_anchor_timing = BiAnchorSearchAlgorithm()
    naive_samples: list[int] = []
    bi_anchor_samples: list[int] = []
    naive_by_category: dict[str, list[int]] = defaultdict(list)
    bi_anchor_by_category: dict[str, list[int]] = defaultdict(list)

    for item in queries:
        naive_timing.search(item.query, naive_structure)
        bi_anchor_timing.search(item.query, bi_anchor_structure)
        for _ in range(repeats):
            started_at = perf_counter_ns()
            naive_timing.search(item.query, naive_structure)
            naive_elapsed = perf_counter_ns() - started_at

            started_at = perf_counter_ns()
            bi_anchor_timing.search(item.query, bi_anchor_structure)
            bi_anchor_elapsed = perf_counter_ns() - started_at

            naive_samples.append(naive_elapsed)
            bi_anchor_samples.append(bi_anchor_elapsed)
            naive_by_category[item.category].append(naive_elapsed)
            bi_anchor_by_category[item.category].append(bi_anchor_elapsed)

    category_query_counts = Counter(item.category for item in queries)
    categories: dict[str, CategoryMetrics] = {}
    for category in sorted(category_query_counts):
        naive_latency = _latency_summary(naive_by_category[category])
        bi_anchor_latency = _latency_summary(bi_anchor_by_category[category])
        categories[category] = CategoryMetrics(
            queries=category_query_counts[category],
            naive=naive_latency,
            bi_anchor=bi_anchor_latency,
            speedup=_speedup(
                naive_latency.median_ns,
                bi_anchor_latency.median_ns,
            ),
        )

    index_stats = bi_anchor_structure.build_stats.index
    naive_latency = _latency_summary(naive_samples)
    bi_anchor_latency = _latency_summary(bi_anchor_samples)
    query_count = len(queries)
    average_seed_frequency = (
        bi_anchor_stats.selected_seed_frequency_sum
        / (2 * bi_anchor_stats.anchored_query_count)
        if bi_anchor_stats.anchored_query_count
        else 0.0
    )

    return SearchBenchmarkReport(
        dataset=dataset_name,
        q=q,
        corpus_sentences=len(sentences),
        queries=query_count,
        repeats=repeats,
        correctness=CorrectnessMetrics(
            total_queries=query_count,
            matching_result_sets=matching,
            mismatches=mismatches,
            false_negatives=false_negatives,
            false_positives=false_positives,
        ),
        naive=AlgorithmMetrics(
            latency=naive_latency,
            verifier_calls=naive_stats.verifier_calls,
            candidate_contexts=naive_stats.verifier_calls,
        ),
        bi_anchor=AlgorithmMetrics(
            latency=bi_anchor_latency,
            verifier_calls=bi_anchor_stats.verifier_calls,
            candidate_contexts=(
                bi_anchor_stats.candidate_contexts_after_dedup
            ),
        ),
        categories=categories,
        speedup=_speedup(naive_latency.median_ns, bi_anchor_latency.median_ns),
        candidate_reduction_ratio=_reduction(
            naive_stats.verifier_calls,
            bi_anchor_stats.candidate_contexts_after_dedup,
        ),
        verifier_call_reduction_ratio=_reduction(
            naive_stats.verifier_calls,
            bi_anchor_stats.verifier_calls,
        ),
        fallback_rate=(
            bi_anchor_stats.fallback_count / query_count if query_count else 0.0
        ),
        average_selected_seed_frequency=average_seed_frequency,
        seed_occurrences_expanded=bi_anchor_stats.seed_occurrences_expanded,
        candidate_contexts_before_dedup=(
            bi_anchor_stats.candidate_contexts_generated
        ),
        candidate_contexts_after_dedup=(
            bi_anchor_stats.candidate_contexts_after_dedup
        ),
        index=IndexMetrics(
            build_ns=bi_anchor_structure.build_stats.index_build_ns,
            peak_memory_bytes=peak_memory,
            unique_words=index_stats.unique_words,
            word_occurrences=index_stats.word_occurrences,
            intra_word_seed_keys=index_stats.intra_word_seed_keys,
            intra_word_seed_references=(
                index_stats.intra_word_seed_references
            ),
            boundary_seed_keys=index_stats.boundary_seed_keys,
            boundary_occurrences=index_stats.boundary_occurrences,
        ),
    )


def _ms(nanoseconds: float) -> float:
    return nanoseconds / 1_000_000


def print_report(report: SearchBenchmarkReport) -> None:
    correctness = report.correctness
    print(f"\nDataset: {report.dataset} (q={report.q})")
    print(
        "Algorithm       Correctness    Median ms    Mean ms    "
        "P95 ms    Verifier Calls"
    )
    print("-" * 86)
    correctness_text = (
        f"{correctness.matching_result_sets}/{correctness.total_queries}"
    )
    for name, metrics in (
        ("Naive", report.naive),
        ("BiAnchor", report.bi_anchor),
    ):
        print(
            f"{name:<15} {correctness_text:<14} "
            f"{_ms(metrics.latency.median_ns):>9.3f} "
            f"{_ms(metrics.latency.mean_ns):>10.3f} "
            f"{_ms(metrics.latency.p95_ns):>9.3f} "
            f"{metrics.verifier_calls:>17}"
        )
    print(
        f"Mismatches={correctness.mismatches}, "
        f"false negatives={correctness.false_negatives}, "
        f"false positives={correctness.false_positives}"
    )
    print(
        f"Overall speedup={report.speedup:.2f}x, "
        f"candidate reduction={report.candidate_reduction_ratio:.1%}, "
        "verifier-call reduction="
        f"{report.verifier_call_reduction_ratio:.1%}"
    )
    print(
        f"Fallback rate={report.fallback_rate:.1%}, "
        "average selected seed frequency="
        f"{report.average_selected_seed_frequency:.2f}"
    )
    print(
        f"Seed occurrences expanded={report.seed_occurrences_expanded}, "
        "contexts before/after dedup="
        f"{report.candidate_contexts_before_dedup}/"
        f"{report.candidate_contexts_after_dedup}"
    )
    print(
        f"Index build={_ms(report.index.build_ns):.3f} ms, "
        f"peak traced memory={report.index.peak_memory_bytes / 1024:.1f} KiB"
    )
    print(
        f"Index: {report.index.unique_words} unique words, "
        f"{report.index.word_occurrences} word occurrences, "
        f"{report.index.intra_word_seed_keys} intra-word keys/"
        f"{report.index.intra_word_seed_references} references, "
        f"{report.index.boundary_seed_keys} boundary keys/"
        f"{report.index.boundary_occurrences} occurrences"
    )
    for category, metrics in report.categories.items():
        print(
            f"  {category}: queries={metrics.queries}, "
            f"median {_ms(metrics.naive.median_ns):.3f}/"
            f"{_ms(metrics.bi_anchor.median_ns):.3f} ms, "
            f"speedup={metrics.speedup:.2f}x"
        )


def _prepared(sentence_id: int, text: str, dataset: str) -> PreparedSentence:
    return PreparedSentence(
        sentence_id=sentence_id,
        original_text=text,
        normalized_text=text,
        source_path=f"{dataset}.txt",
        offset=sentence_id + 1,
    )


def _query_category(query: str, q: int) -> str:
    if len(query) < 2 * q:
        return "short"
    if len(query) < 16:
        return "medium"
    return "long"


def _queries_from_sentences(
    sentences: tuple[PreparedSentence, ...],
    *,
    q: int,
    limit: int,
) -> tuple[BenchmarkQuery, ...]:
    queries: list[BenchmarkQuery] = []
    for sentence in sentences:
        text = sentence.normalized_text
        if len(text) < 2:
            continue
        query = text[: min(24, len(text))].strip()
        if not query:
            continue
        variants = [
            query,
            query[:-1] + ("x" if query[-1] != "x" else "z"),
            query[:-1],
            query + "x",
        ]
        for variant in variants:
            if variant:
                queries.append(
                    BenchmarkQuery(_query_category(variant, q), variant)
                )
                if len(queries) >= limit:
                    return tuple(queries)
    return tuple(queries)


def _synthetic_dataset(
    name: str,
    texts: list[str],
    *,
    q: int,
    query_limit: int,
) -> tuple[str, tuple[PreparedSentence, ...], tuple[BenchmarkQuery, ...]]:
    sentences = tuple(
        _prepared(sentence_id, text, name)
        for sentence_id, text in enumerate(texts)
    )
    return (
        name,
        sentences,
        _queries_from_sentences(sentences, q=q, limit=query_limit),
    )


def build_datasets(
    *,
    selection: str,
    archive: Path,
    q: int,
    max_sentences: int,
    max_queries: int,
) -> list[tuple[str, tuple[PreparedSentence, ...], tuple[BenchmarkQuery, ...]]]:
    datasets = []
    if selection in {"all", "archive"} and archive.exists():
        prepared = tuple(DataPreparer().prepare(archive)[:max_sentences])
        datasets.append(
            (
                "archive-real-sample",
                prepared,
                _queries_from_sentences(prepared, q=q, limit=max_queries),
            )
        )

    generator = random.Random(20260812)
    vocabulary = ("alpha", "beta", "gamma", "delta", "omega", "search")
    synthetic = [
        " ".join(generator.choice(vocabulary) for _ in range(10))
        for _ in range(max_sentences)
    ]
    repetitive = [
        ("a" * 80 if index % 2 == 0 else "the " * 20).strip()
        for index in range(max_sentences)
    ]
    high_frequency = [
        f"the search engine uses the common word value {index}"
        for index in range(max_sentences)
    ]
    cross_word = [
        f"hello world boundary query number {index}"
        for index in range(max_sentences)
    ]
    synthetic_sources = {
        "synthetic": synthetic,
        "repetitive": repetitive,
        "high-frequency": high_frequency,
        "cross-word": cross_word,
    }
    for name, texts in synthetic_sources.items():
        if selection not in {"all", name}:
            continue
        datasets.append(
            _synthetic_dataset(
                name,
                texts,
                q=q,
                query_limit=max_queries,
            )
        )
    return datasets


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare Naive and Bi-Anchor search.")
    parser.add_argument(
        "--dataset",
        choices=(
            "all",
            "archive",
            "synthetic",
            "repetitive",
            "high-frequency",
            "cross-word",
        ),
        default="all",
    )
    parser.add_argument("--archive", type=Path, default=Path("data/Archive.zip"))
    parser.add_argument("--q", type=int, default=3)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--max-sentences", type=int, default=300)
    parser.add_argument("--max-queries", type=int, default=12)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("benchmark-results.json"),
    )
    arguments = parser.parse_args()

    datasets = build_datasets(
        selection=arguments.dataset,
        archive=arguments.archive,
        q=arguments.q,
        max_sentences=arguments.max_sentences,
        max_queries=arguments.max_queries,
    )
    if not datasets:
        raise SystemExit("No requested benchmark dataset is available.")

    reports = []
    for name, sentences, queries in datasets:
        report = evaluate_search_algorithms(
            dataset_name=name,
            sentences=sentences,
            queries=queries,
            q=arguments.q,
            repeats=arguments.repeats,
        )
        print_report(report)
        reports.append(report.to_dict())

    arguments.output.write_text(
        json.dumps(reports, indent=2),
        encoding="utf-8",
    )
    print(f"\nWrote machine-readable results to {arguments.output}")


if __name__ == "__main__":
    main()
