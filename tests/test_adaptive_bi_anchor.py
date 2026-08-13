"""Adaptive multi-q anchor selection for short queries.

Correctness is unchanged: any q with ``2 * q <= len(query)`` supports the same
two-non-overlapping-anchor proof. Choosing among those q values is purely a
performance decision, so every test here either pins the *choice* or pins
equivalence with the Naive oracle.
"""

from collections import Counter

from src.algorithms.bi_anchor_search_algorithm import BiAnchorSearchAlgorithm
from src.algorithms.bi_anchor_search_stats import BiAnchorSearchStats
from src.algorithms.naive_search_algorithm import NaiveSearchAlgorithm
from src.builders.bi_anchor_structure_builder import BiAnchorStructureBuilder
from src.builders.naive_structure_builder import NaiveStructureBuilder
from src.models.match_candidate import MatchCandidate
from src.models.prepared_sentence import PreparedSentence
from src.search_engine import SearchEngine


def _sentences(*texts: str) -> tuple[PreparedSentence, ...]:
    return tuple(
        PreparedSentence(
            sentence_id=sentence_id,
            original_text=text,
            normalized_text=text,
            source_path="archive/example.txt",
            offset=sentence_id + 1,
        )
        for sentence_id, text in enumerate(texts)
    )


def _canonical(matches: list[MatchCandidate]) -> Counter:
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


def _adaptive(
    sentences: tuple[PreparedSentence, ...],
    *,
    q_values: tuple[int, ...] = (1, 2, 3),
    stats: BiAnchorSearchStats | None = None,
    minimum_anchor_length: int = 2,
) -> SearchEngine:
    engine = SearchEngine(
        BiAnchorStructureBuilder(q=max(q_values), q_values=q_values),
        BiAnchorSearchAlgorithm(
            stats=stats,
            minimum_anchor_length=minimum_anchor_length,
        ),
    )
    engine.build(sentences)
    return engine


def _naive(sentences: tuple[PreparedSentence, ...]) -> SearchEngine:
    engine = SearchEngine(NaiveStructureBuilder(), NaiveSearchAlgorithm())
    engine.build(sentences)
    return engine


def _assert_matches_naive(
    sentences: tuple[PreparedSentence, ...],
    queries: tuple[str, ...],
    *,
    q_values: tuple[int, ...] = (1, 2, 3),
) -> None:
    adaptive = _adaptive(sentences, q_values=q_values)
    naive = _naive(sentences)
    for query in queries:
        expected = _canonical(naive.search(query))
        actual = _canonical(adaptive.search(query))
        assert not (expected - actual), f"false negatives for {query!r}"
        assert not (actual - expected), f"false positives for {query!r}"


CORPUS = _sentences(
    "the fastest test of the tested system",
    "testing a short query path",
    "a test",
    "unrelated content here",
    "aaaa bbbb",
    "ab ab ab",
)


# 1-2. Short queries that used to be forced onto the Naive path.


def test_length_four_query_anchors_on_q_two_instead_of_falling_back() -> None:
    stats = BiAnchorSearchStats()

    _adaptive(CORPUS, stats=stats).search("test")

    assert stats.fallback_count == 0
    assert stats.last_selected_q == 2


def test_length_five_query_anchors_on_q_two() -> None:
    stats = BiAnchorSearchStats()

    _adaptive(CORPUS, stats=stats).search("tests")

    assert stats.fallback_count == 0
    assert stats.last_selected_q == 2


# 3-4. q is chosen by measured pair cost, not by a fixed formula.


def test_length_six_query_prefers_q_two_when_its_pair_is_cheaper() -> None:
    # "ab" only ever occurs inside "abc", "cd" is rare, "def" is everywhere:
    # the single q=3 pair (abc, def) expands far more than (ab, cd).
    corpus = _sentences(
        "abcdef",
        *(f"abcxyz row {index}" for index in range(50)),
        *(f"qdefq row {index}" for index in range(50)),
    )
    stats = BiAnchorSearchStats()

    _adaptive(corpus, q_values=(2, 3), stats=stats).search("abcdef")

    assert stats.last_selected_q == 2
    assert stats.last_selected_seeds is not None
    assert {seed.text for seed in stats.last_selected_seeds} == {"ab", "cd"}


def test_length_six_query_prefers_q_three_when_its_pair_is_cheaper() -> None:
    # Every 2-gram of the query is common, but "abc" and "def" are unique.
    corpus = _sentences(
        "abcdef",
        *(
            f"zabz zbcz zcdz zdez zefz row {index}"
            for index in range(50)
        ),
    )
    stats = BiAnchorSearchStats()

    _adaptive(corpus, q_values=(2, 3), stats=stats).search("abcdef")

    assert stats.last_selected_q == 3
    assert stats.last_selected_seeds is not None
    assert {seed.text for seed in stats.last_selected_seeds} == {"abc", "def"}


def test_equal_pair_cost_keeps_the_larger_default_q() -> None:
    stats = BiAnchorSearchStats()

    _adaptive(_sentences("abcdef"), q_values=(1, 2, 3), stats=stats).search(
        "abcdef"
    )

    assert stats.last_selected_q == 3


# 5-7. The shortest lengths.


def test_length_three_q_one_matches_naive() -> None:
    _assert_matches_naive(CORPUS, ("the", "tes", "tst", "a t"), q_values=(1,))


def test_length_two_q_one_matches_naive() -> None:
    _assert_matches_naive(CORPUS, ("te", "ab", "a ", " a", "zz"), q_values=(1,))


def test_length_two_query_anchors_on_q_one() -> None:
    stats = BiAnchorSearchStats()

    _adaptive(CORPUS, stats=stats).search("te")

    assert stats.fallback_count == 0
    assert stats.last_selected_q == 1


def test_length_one_query_uses_the_safe_naive_fallback() -> None:
    stats = BiAnchorSearchStats()

    matches = _adaptive(CORPUS, stats=stats).search("a")

    assert stats.fallback_count == 1
    assert stats.last_selected_q is None
    assert _canonical(matches) == _canonical(_naive(CORPUS).search("a"))


def test_minimum_anchor_length_routes_shorter_queries_to_naive() -> None:
    stats = BiAnchorSearchStats()

    _adaptive(CORPUS, stats=stats, minimum_anchor_length=4).search("tes")

    assert stats.fallback_count == 1
    assert stats.last_selected_q is None


def test_minimum_anchor_length_still_anchors_at_the_threshold() -> None:
    stats = BiAnchorSearchStats()

    _adaptive(CORPUS, stats=stats, minimum_anchor_length=4).search("test")

    assert stats.fallback_count == 0
    assert stats.last_selected_q == 2


# 8-13. Short-query shapes that must keep working.


def test_cross_word_short_query_matches_naive() -> None:
    _assert_matches_naive(CORPUS, ("e fa", "a te", "t of", "b ab", "ab a"))


def test_middle_of_word_short_substring_matches_naive() -> None:
    _assert_matches_naive(CORPUS, ("este", "aste", "sted", "ystem"))


def test_short_replacement_query_matches_naive() -> None:
    _assert_matches_naive(CORPUS, ("txst", "tesx", "xest", "tesxs"))


def test_short_insertion_query_matches_naive() -> None:
    _assert_matches_naive(CORPUS, ("tst", "est", "tes", "esti"))


def test_short_deletion_query_matches_naive() -> None:
    _assert_matches_naive(CORPUS, ("teest", "testt", "ttest", "teste"))


def test_repeated_character_short_query_matches_naive() -> None:
    _assert_matches_naive(CORPUS, ("aa", "aaa", "aaaa", "aaaaa", "abab"))


# 14. Everything at once.


def test_all_short_lengths_match_naive_raw_candidates() -> None:
    queries = tuple(
        text[start : start + length]
        for sentence in CORPUS
        for text in (sentence.normalized_text,)
        for length in range(1, 7)
        for start in range(len(text) - length + 1)
    )

    _assert_matches_naive(CORPUS, queries)


def test_plan_reports_the_choice_search_will_make_without_expanding() -> None:
    stats = BiAnchorSearchStats()
    engine = _adaptive(CORPUS, stats=stats)
    structure = engine._structure
    algorithm = BiAnchorSearchAlgorithm()

    plan = algorithm.plan("test", structure)
    engine.search("test")

    assert plan is not None
    assert plan.q == stats.last_selected_q
    assert plan.seeds == stats.last_selected_seeds
    assert plan.expansion_cost == sum(
        seed.frequency for seed in stats.last_selected_seeds
    )


def test_plan_is_none_when_no_indexed_q_fits_the_query() -> None:
    structure = _adaptive(CORPUS)._structure

    assert BiAnchorSearchAlgorithm().plan("a", structure) is None
    assert BiAnchorSearchAlgorithm().plan("", structure) is None


def test_plan_respects_the_minimum_anchor_length() -> None:
    structure = _adaptive(CORPUS)._structure

    planner = BiAnchorSearchAlgorithm(minimum_anchor_length=4)

    assert planner.plan("tes", structure) is None
    assert planner.plan("test", structure) is not None


def test_selected_q_distribution_is_recorded() -> None:
    stats = BiAnchorSearchStats()
    engine = _adaptive(CORPUS, stats=stats)

    for query in ("te", "tes", "test", "tests", "testin"):
        engine.search(query)

    assert sum(stats.selected_q_counts.values()) == 5
    assert set(stats.selected_q_counts) <= {1, 2, 3}
