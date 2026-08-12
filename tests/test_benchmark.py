import json

from src.algorithms.naive_search_algorithm import NaiveSearchAlgorithm
from src.algorithms.naive_search_stats import NaiveSearchStats
from src.autocomplete.benchmark import (
    BenchmarkQuery,
    canonicalize_matches,
    evaluate_search_algorithms,
    percentile_95,
)
from src.builders.naive_structure_builder import NaiveStructureBuilder
from src.models.edit_type import EditType
from src.models.match_candidate import MatchCandidate
from src.models.prepared_sentence import PreparedSentence
from src.search_engine import SearchEngine


def _sentence(sentence_id: int, text: str) -> PreparedSentence:
    return PreparedSentence(
        sentence_id=sentence_id,
        original_text=text,
        normalized_text=text,
        source_path="benchmark.txt",
        offset=sentence_id + 1,
    )


def test_percentile_95_uses_nearest_rank() -> None:
    assert percentile_95([1, 2, 3, 4, 100]) == 100
    assert percentile_95([10]) == 10


def test_canonicalization_preserves_distinct_edit_interpretations() -> None:
    sentence = _sentence(1, "aaa")
    matches = [
        MatchCandidate(sentence, 0, EditType.INSERTION, 0, 2),
        MatchCandidate(sentence, 0, EditType.INSERTION, 1, 2),
    ]

    canonical = canonicalize_matches(matches)

    assert len(canonical) == 2
    assert canonical[
        (1, 0, EditType.INSERTION, 0, 2)
    ] == 1
    assert canonical[
        (1, 0, EditType.INSERTION, 1, 2)
    ] == 1


def test_naive_stats_count_shared_verifier_calls() -> None:
    stats = NaiveSearchStats()
    engine = SearchEngine(
        NaiveStructureBuilder(),
        NaiveSearchAlgorithm(stats=stats),
    )
    engine.build([_sentence(1, "abcdef")])

    engine.search("abcdef")

    assert stats.query_count == 1
    assert stats.verifier_calls == 3


def test_evaluation_reports_correctness_and_json_ready_metrics() -> None:
    sentences = (
        _sentence(1, "programming in python"),
        _sentence(2, "hello world"),
    )
    queries = (
        BenchmarkQuery("long", "programming"),
        BenchmarkQuery("boundary", "lo wo"),
    )

    report = evaluate_search_algorithms(
        dataset_name="unit",
        sentences=sentences,
        queries=queries,
        q=2,
        repeats=2,
    )
    payload = report.to_dict()

    assert report.correctness.total_queries == 2
    assert report.correctness.matching_result_sets == 2
    assert report.correctness.mismatches == 0
    assert report.correctness.false_negatives == 0
    assert report.correctness.false_positives == 0
    assert report.naive.verifier_calls > 0
    assert report.bi_anchor.verifier_calls > 0
    assert report.bi_anchor.latency.median_ns >= 0
    assert report.index.unique_words == 5
    assert payload["dataset"] == "unit"
    json.dumps(payload)
