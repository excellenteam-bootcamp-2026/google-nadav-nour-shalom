from __future__ import annotations

from collections import Counter

import pytest

from src.algorithms.naive_search_algorithm import NaiveSearchAlgorithm
from src.algorithms.qgram_search_algorithm import QGramSearchAlgorithm
from src.algorithms.qgram_search_stats import QGramSearchStats
from src.builders.naive_structure_builder import NaiveStructureBuilder
from src.builders.qgram_structure_builder import QGramStructureBuilder
from src.models.match_candidate import MatchCandidate
from src.models.prepared_sentence import PreparedSentence
from src.search_engine import SearchEngine


def _sentence(sentence_id: int, text: str) -> PreparedSentence:
    return PreparedSentence(
        sentence_id=sentence_id,
        original_text=text,
        normalized_text=text,
        source_path="qgram.txt",
        offset=sentence_id + 1,
    )


def _canonical(matches: list[MatchCandidate]) -> Counter[tuple[object, ...]]:
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


def _engines(
    texts: list[str], *, q: int = 3, stats: QGramSearchStats | None = None
) -> tuple[SearchEngine, SearchEngine]:
    sentences = tuple(_sentence(index, text) for index, text in enumerate(texts))
    naive = SearchEngine(NaiveStructureBuilder(), NaiveSearchAlgorithm())
    qgram = SearchEngine(
        QGramStructureBuilder(q=q),
        QGramSearchAlgorithm(stats=stats),
    )
    naive.build(sentences)
    qgram.build(sentences)
    return naive, qgram


@pytest.mark.parametrize(
    "query",
    [
        "programming",
        "gramm",
        "ming in",
        "prograxming",
        "programing",
        "programmking",
        "aaaa",
        "a",
        "",
        "zzzzzz",
    ],
)
def test_qgram_raw_results_equal_naive_for_substrings_and_edits(query: str) -> None:
    naive, qgram = _engines(
        [
            "programming in python",
            "aaaaa repeated pattern",
            "cross word boundary",
        ]
    )

    assert _canonical(qgram.search(query)) == _canonical(naive.search(query))


def test_qgram_stats_expose_candidate_and_verifier_work() -> None:
    stats = QGramSearchStats()
    _naive, qgram = _engines(
        ["programming in python", "programming language"],
        stats=stats,
    )

    matches = qgram.search("programming")

    assert matches
    assert stats.query_count == 1
    assert stats.query_qgrams == 9
    assert stats.posting_lists_accessed == 9
    assert stats.posting_entries_scanned > 0
    assert stats.candidate_starts_before_dedup >= stats.candidate_starts_after_dedup
    assert stats.target_contexts >= stats.candidate_starts_after_dedup
    assert stats.verifier_calls == stats.target_contexts
    assert stats.fallback_count == 0


def test_qgram_short_query_records_exhaustive_fallback() -> None:
    stats = QGramSearchStats()
    naive, qgram = _engines(["abc", "cab"], stats=stats)

    actual = qgram.search("a")

    assert _canonical(actual) == _canonical(naive.search("a"))
    assert stats.fallback_count == 1
    assert stats.verifier_calls > 0


def test_qgram_rejects_wrong_structure() -> None:
    structure = NaiveStructureBuilder().build([_sentence(0, "python")])

    with pytest.raises(TypeError, match="QGramSearchStructure"):
        QGramSearchAlgorithm().search("python", structure)
