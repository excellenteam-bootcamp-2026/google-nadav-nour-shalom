"""
Unit tests for the completion module (Steps 5-7: Sort, Top 5, AutoCompleteData).
"""
from src.autocomplete.completion import get_best_k_completions
from src.autocomplete.auto_complete_data import AutoCompleteData
from src.models.edit_type import EditType
from src.models.match_candidate import MatchCandidate
from src.models.prepared_sentence import PreparedSentence


def _make_candidate(
    original_text: str,
    edit_type: EditType = EditType.EXACT,
    edit_index: int | None = None,
    correct_characters: int = 5,
    source_path: str = "file.txt",
    offset: int = 0,
) -> MatchCandidate:
    """Build a minimal MatchCandidate for completion tests."""
    sentence = PreparedSentence(
        sentence_id=0,
        original_text=original_text,
        normalized_text=original_text.lower(),
        source_path=source_path,
        offset=offset,
    )
    return MatchCandidate(
        sentence=sentence,
        match_start=0,
        edit_type=edit_type,
        edit_index=edit_index,
        correct_characters=correct_characters,
    )


def test_returns_all_when_fewer_than_k():
    """When there are fewer candidates than k, all are returned."""
    candidates = [_make_candidate(f"sentence {i}") for i in range(3)]
    results = get_best_k_completions(candidates, k=5)
    assert len(results) == 3


def test_returns_exactly_k_when_more_than_k():
    """When there are more candidates than k, exactly k results are returned."""
    candidates = [_make_candidate(f"sentence {i}") for i in range(10)]
    results = get_best_k_completions(candidates, k=5)
    assert len(results) == 5


def test_sorted_by_score_descending():
    """Results must be ordered highest score first."""
    candidates = [
        _make_candidate("low score",  EditType.REPLACEMENT, 0, correct_characters=5),
        _make_candidate("high score", EditType.EXACT,       None, correct_characters=8),
        _make_candidate("mid score",  EditType.DELETION,    2, correct_characters=6),
    ]
    results = get_best_k_completions(candidates)
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_tie_broken_alphabetically():
    """Candidates with identical scores must be sorted alphabetically."""
    candidates = [
        _make_candidate("zebra",  EditType.EXACT, None, correct_characters=5),
        _make_candidate("apple",  EditType.EXACT, None, correct_characters=5),
        _make_candidate("mango",  EditType.EXACT, None, correct_characters=5),
    ]
    results = get_best_k_completions(candidates)
    texts = [r.completed_sentence for r in results]
    assert texts == sorted(texts)


def test_duplicate_sentences_appear_only_once():
    """Repeated interpretations of one source record collapse to one result."""
    candidates = [
        _make_candidate("hello world"),
        _make_candidate("hello world"),
        _make_candidate("hello world"),
    ]
    results = get_best_k_completions(candidates)
    assert len(results) == 1
    assert results[0].completed_sentence == "hello world"


def test_identical_text_in_different_files_both_survive():
    """Same text, different source files: both are distinct results."""
    candidates = [
        _make_candidate("Status of This Memo", source_path="rfc8448.txt", offset=23),
        _make_candidate("Status of This Memo", source_path="rfc8452.txt", offset=26),
        _make_candidate("Status of This Memo", source_path="rfc8482.txt", offset=32),
    ]

    results = get_best_k_completions(candidates)

    assert len(results) == 3
    assert {(r.source_text, r.offset) for r in results} == {
        ("rfc8448.txt", 23),
        ("rfc8452.txt", 26),
        ("rfc8482.txt", 32),
    }


def test_identical_text_at_different_offsets_both_survive():
    """Same text repeated within one file is still two distinct results."""
    candidates = [
        _make_candidate("Abstract", source_path="rfc8448.txt", offset=15),
        _make_candidate("Abstract", source_path="rfc8448.txt", offset=402),
    ]

    results = get_best_k_completions(candidates)

    assert len(results) == 2
    assert {r.offset for r in results} == {15, 402}


def test_same_record_matched_twice_still_collapses():
    """Two interpretations of the exact same record keep only the best one."""
    candidates = [
        # Same text, file and offset: one record, matched two ways.
        _make_candidate("hello world", EditType.EXACT, None, correct_characters=8),
        _make_candidate(
            "hello world", EditType.REPLACEMENT, 0, correct_characters=5
        ),
    ]

    results = get_best_k_completions(candidates)

    assert len(results) == 1
    assert results[0].score == 16  # the EXACT interpretation, not 10 - 5


def test_result_is_auto_complete_data():
    """Each returned item must be an AutoCompleteData instance."""
    candidates = [_make_candidate("test sentence")]
    results = get_best_k_completions(candidates)
    assert all(isinstance(r, AutoCompleteData) for r in results)


def test_empty_candidates_returns_empty_list():
    """An empty candidate list must return an empty result list."""
    assert get_best_k_completions([]) == []
