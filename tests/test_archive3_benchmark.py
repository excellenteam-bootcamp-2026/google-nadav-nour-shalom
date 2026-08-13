from __future__ import annotations

import json
from pathlib import Path

from benchmark.code.archive3_benchmark import (
    ALGORITHM_IDS,
    Archive3Query,
    build_algorithms,
    canonical_signature,
    generate_workload,
    load_queries,
    nearest_rank,
    run_query_trials,
    rotated_algorithm_order,
    save_queries,
    structure_metrics,
    summarize_samples,
)
from src.models.edit_type import EditType
from src.models.match_candidate import MatchCandidate
from src.models.prepared_sentence import PreparedSentence


def _sentence(sentence_id: int, text: str, source: str) -> PreparedSentence:
    return PreparedSentence(
        sentence_id=sentence_id,
        original_text=text,
        normalized_text=text,
        source_path=source,
        offset=sentence_id + 1,
    )


def _corpus() -> tuple[PreparedSentence, ...]:
    texts = [
        "abcdefghij wholeword repeated aaaaa pattern",
        "cross word boundary supports python search",
        "rarelyobservedtoken common common common value",
        "replacement insertion deletion near beginning",
        "ending sentence boundary and multi word query",
        "0123456789 symbols αβγδεζηθικ unicode values",
    ]
    return tuple(
        _sentence(index, text, f"source-{index % 3}.txt")
        for index, text in enumerate(texts * 8)
    )


def test_generate_workload_is_unique_deterministic_and_stratified() -> None:
    sentences = _corpus()

    first = generate_workload(
        sentences,
        seed=20260812,
        target_count=80,
        per_short_length=2,
    )
    second = generate_workload(
        sentences,
        seed=20260812,
        target_count=80,
        per_short_length=2,
    )

    assert first == second
    assert len(first) == 80
    assert len({query.query_id for query in first}) == 80
    assert len({query.normalized_query for query in first}) == 80
    lengths = {length: 0 for length in range(1, 7)}
    for query in first:
        if query.query_length in lengths:
            lengths[query.query_length] += 1
    assert all(count >= 2 for count in lengths.values())
    categories = {category for query in first for category in query.categories}
    assert {
        "exact",
        "whole_word",
        "inside_word",
        "cross_word",
        "replacement",
        "insertion",
        "deletion",
        "repeated",
        "common",
        "rare",
        "no_match",
        "near_miss",
        "near_boundary",
        "multi_word",
    } <= categories
    assert {query.frequency_band for query in first if query.frequency_band} >= {
        "p50",
        "p75",
        "p90",
        "p95",
        "p99",
        "rare",
    }


def test_query_json_round_trip_preserves_exact_workload() -> None:
    queries = (
        Archive3Query(
            query_id="q000001",
            query_text="python",
            normalized_query="python",
            query_length=6,
            length_bucket="6",
            primary_category="exact",
            categories=("exact", "whole_word"),
            source_sentence_id=7,
            source_path="docs.txt",
            source_start=3,
            mutation_type=None,
            frequency_band="p90",
            qgram_frequency=100,
        ),
    )
    path = Path("benchmark/output/test-runs/archive3-queries-test.json")

    try:
        save_queries(path, queries, seed=20260812)

        assert load_queries(path) == queries
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["seed"] == 20260812
        assert payload["queries"][0]["query_id"] == "q000001"
    finally:
        path.unlink(missing_ok=True)


def test_canonical_signature_is_order_independent_and_complete() -> None:
    first = _sentence(1, "aaaa", "one.txt")
    second = _sentence(1, "aaaa", "two.txt")
    matches = [
        MatchCandidate(first, 0, EditType.INSERTION, 0, 3),
        MatchCandidate(first, 0, EditType.INSERTION, 0, 3),
        MatchCandidate(second, 0, EditType.INSERTION, 0, 3),
    ]

    signature = canonical_signature(matches)

    assert signature == canonical_signature(reversed(matches))
    assert signature["count"] == 3
    assert signature != canonical_signature(matches[:-1])
    changed = [
        MatchCandidate(first, 0, EditType.INSERTION, 1, 3),
        *matches[1:],
    ]
    assert signature != canonical_signature(changed)


def test_sample_summary_uses_per_query_samples_and_standard_deviation() -> None:
    assert nearest_rank([10, 20, 30, 40], 75) == 30
    assert summarize_samples([10, 20, 30, 40]) == {
        "samples": [10, 20, 30, 40],
        "count": 4,
        "min_ns": 10,
        "median_ns": 25.0,
        "mean_ns": 25.0,
        "p95_ns": 40,
        "max_ns": 40,
        "stdev_ns": 12.909944487358056,
    }


def test_all_four_algorithm_ids_are_mandatory() -> None:
    assert ALGORITHM_IDS == (
        "naive",
        "qgram_verifier",
        "qgram_tree_hybrid",
        "bi_anchor",
    )


def test_rotated_algorithm_order_is_deterministic_and_balanced() -> None:
    orders = [rotated_algorithm_order(index) for index in range(4)]

    assert orders == [
        ALGORITHM_IDS,
        ALGORITHM_IDS[1:] + ALGORITHM_IDS[:1],
        ALGORITHM_IDS[2:] + ALGORITHM_IDS[:2],
        ALGORITHM_IDS[3:] + ALGORITHM_IDS[:3],
    ]
    assert {order[0] for order in orders} == set(ALGORITHM_IDS)


def test_all_four_algorithms_build_independently_with_structure_metrics() -> None:
    builds, runtimes = build_algorithms(_corpus(), repetitions=2, q=3)

    assert tuple(runtimes) == ALGORITHM_IDS
    assert tuple(builds) == ALGORITHM_IDS
    for algorithm_id in ALGORITHM_IDS:
        result = builds[algorithm_id]
        assert result["build_repetitions"] == 2
        assert len(result["build_time_ns"]["samples"]) == 2
        assert result["peak_memory_bytes"] >= 0
        assert result["retained_memory_bytes"] >= 0
        assert result["structure_metrics"] == structure_metrics(
            algorithm_id, runtimes[algorithm_id]
        )
    assert builds["qgram_verifier"]["structure_metrics"]["posting_entries"] > 0
    assert builds["qgram_tree_hybrid"]["structure_metrics"]["trie_nodes"] > 0
    assert builds["bi_anchor"]["structure_metrics"]["word_occurrences"] > 0


def test_query_trials_keep_raw_samples_correctness_and_work_separate() -> None:
    sentences = _corpus()
    _builds, runtimes = build_algorithms(sentences, repetitions=1, q=3)
    queries = (
        Archive3Query(
            query_id="q000001",
            query_text="python",
            normalized_query="python",
            query_length=6,
            length_bucket="6",
            primary_category="exact",
            categories=("exact", "whole_word"),
            source_sentence_id=1,
            source_path="source-1.txt",
            source_start=29,
            mutation_type=None,
            frequency_band=None,
            qgram_frequency=None,
        ),
        Archive3Query(
            query_id="q000002",
            query_text="zzzznomatch",
            normalized_query="zzzznomatch",
            query_length=11,
            length_bucket="9-12",
            primary_category="no_match",
            categories=("no_match",),
            source_sentence_id=None,
            source_path=None,
            source_start=None,
            mutation_type="real_derived_no_match",
            frequency_band=None,
            qgram_frequency=None,
        ),
    )

    result = run_query_trials(
        queries,
        runtimes,
        warmups=1,
        repetitions={algorithm_id: 2 for algorithm_id in ALGORITHM_IDS},
    )

    assert result["warmups"] == 1
    assert len(result["timing_rows"]) == len(queries) * 4
    assert len(result["correctness_rows"]) == len(queries) * 4
    assert len(result["work_rows"]) == len(queries) * 4
    for row in result["timing_rows"]:
        assert len(row["timing"]["samples"]) == 2
        assert row["signature"]["count"] == row["result_count"]
        assert row["timing_order_positions"]
    naive_rows = [
        row for row in result["correctness_rows"]
        if row["algorithm_id"] == "naive"
    ]
    assert all(row["status"] == "oracle" for row in naive_rows)
    exact_rows = [
        row for row in result["correctness_rows"]
        if row["algorithm_id"] in {"qgram_verifier", "bi_anchor"}
    ]
    assert all(row["correct"] for row in exact_rows)
    assert all("verifier_calls" in row["metrics"] for row in result["work_rows"])
