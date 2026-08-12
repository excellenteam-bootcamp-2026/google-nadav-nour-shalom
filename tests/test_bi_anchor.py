from src.algorithms.bi_anchor_search_algorithm import BiAnchorSearchAlgorithm
from src.algorithms.bi_anchor_search_stats import BiAnchorSearchStats
from src.builders.bi_anchor_structure_builder import BiAnchorStructureBuilder
from src.models.edit_type import EditType
from src.models.prepared_sentence import PreparedSentence
from src.search_engine import SearchEngine


def _sentence(text: str, sentence_id: int = 1) -> PreparedSentence:
    return PreparedSentence(
        sentence_id=sentence_id,
        original_text=text,
        normalized_text=text,
        source_path="archive/example.txt",
        offset=sentence_id,
    )


def _search(
    query: str,
    target: str,
    *,
    q: int = 3,
    stats: BiAnchorSearchStats | None = None,
):
    engine = SearchEngine(
        BiAnchorStructureBuilder(q=q),
        BiAnchorSearchAlgorithm(stats=stats),
    )
    engine.build([_sentence(target)])
    return engine.search(query)


def _at_start(matches, edit_type: EditType, start: int = 0):
    return [
        match
        for match in matches
        if match.match_start == start and match.edit_type is edit_type
    ]


def test_exact_match_uses_anchored_path() -> None:
    stats = BiAnchorSearchStats()

    matches = _at_start(
        _search("programming", "programming", stats=stats),
        EditType.EXACT,
    )

    assert len(matches) == 1
    assert stats.fallback_count == 0
    assert stats.verifier_calls > 0


def test_replacement_match() -> None:
    matches = _at_start(
        _search("progrxmming", "programming"),
        EditType.REPLACEMENT,
    )

    assert [match.edit_index for match in matches] == [5]


def test_missing_query_character_is_insertion() -> None:
    matches = _at_start(
        _search("programing", "programming"),
        EditType.INSERTION,
    )

    assert {match.edit_index for match in matches} == {6, 7}


def test_extra_query_character_is_deletion() -> None:
    matches = _at_start(
        _search("programxming", "programming"),
        EditType.DELETION,
    )

    assert [match.edit_index for match in matches] == [7]


def test_substring_inside_word_uses_seed_index() -> None:
    stats = BiAnchorSearchStats()

    matches = _at_start(
        _search("gramm", "programming", q=2, stats=stats),
        EditType.EXACT,
        start=3,
    )

    assert len(matches) == 1
    assert stats.fallback_count == 0


def test_cross_word_match_uses_boundary_index() -> None:
    stats = BiAnchorSearchStats()

    matches = _at_start(
        _search("lo wo", "hello world", q=2, stats=stats),
        EditType.EXACT,
        start=3,
    )

    assert len(matches) == 1
    assert stats.fallback_count == 0


def test_repeated_seed_text_uses_non_overlapping_query_ranges() -> None:
    stats = BiAnchorSearchStats()

    matches = _at_start(
        _search("aaaa", "aaaaa", q=2, stats=stats),
        EditType.INSERTION,
    )

    assert {match.edit_index for match in matches} == {0, 1, 2, 3, 4}
    assert stats.last_selected_seeds is not None
    first, second = stats.last_selected_seeds
    assert first.text == second.text == "aa"
    assert first.query_end <= second.query_start


def test_both_selected_seed_frequencies_zero_returns_without_verifying() -> None:
    stats = BiAnchorSearchStats()

    assert _search("xyzxyz", "programming", stats=stats) == []
    assert stats.zero_frequency_returns == 1
    assert stats.verifier_calls == 0


def test_strict_bounds_exclude_truncated_slices_before_verification() -> None:
    stats = BiAnchorSearchStats()

    _search("abcdef", "abcdef", stats=stats)

    assert stats.candidate_contexts_generated == 6
    assert stats.candidate_contexts_after_dedup == 3
    assert stats.verifier_calls == 3


def test_short_query_delegates_to_naive() -> None:
    stats = BiAnchorSearchStats()

    matches = _at_start(
        _search("aa", "aaa", stats=stats),
        EditType.INSERTION,
    )

    assert {match.edit_index for match in matches} == {0, 1, 2}
    assert stats.fallback_count == 1


def test_wrong_structure_type_is_rejected() -> None:
    from src.structures.naive_search_structure import NaiveSearchStructure

    algorithm = BiAnchorSearchAlgorithm()

    try:
        algorithm.search("abcdef", NaiveSearchStructure((_sentence("abcdef"),)))
    except TypeError as error:
        assert "BiAnchorSearchStructure" in str(error)
    else:
        raise AssertionError("Expected Bi-Anchor structure validation.")
