"""
Unit tests for the scoring module (Step 4: Calculate Score).

Each test constructs a MatchCandidate with known fields and asserts
that calculate_score returns the expected value based on the penalty table.
"""
from unittest.mock import MagicMock

import pytest

from src.autocomplete.scoring import calculate_score
from src.models.edit_type import EditType
from src.models.match_candidate import MatchCandidate
from src.models.prepared_sentence import PreparedSentence


def _make_candidate(
    edit_type: EditType,
    edit_index: int | None,
    correct_characters: int,
) -> MatchCandidate:
    """Build a minimal MatchCandidate for scoring tests."""
    sentence = PreparedSentence(
        sentence_id=0,
        original_text="test sentence",
        normalized_text="test sentence",
        source_path="test.txt",
        offset=0,
    )
    return MatchCandidate(
        sentence=sentence,
        match_start=0,
        edit_type=edit_type,
        edit_index=edit_index,
        correct_characters=correct_characters,
    )


def test_exact_match_no_penalty():
    """An exact match returns base score only: correct_characters * 2."""
    candidate = _make_candidate(EditType.EXACT, None, 6)
    assert calculate_score(candidate) == 12


def test_replacement_at_index_0():
    """Replacement at position 0 applies the highest replacement penalty (-5)."""
    candidate = _make_candidate(EditType.REPLACEMENT, 0, 5)
    assert calculate_score(candidate) == 10 - 5  # 5


def test_replacement_at_index_4():
    """Replacement at position 4 applies the minimum replacement penalty (-1)."""
    candidate = _make_candidate(EditType.REPLACEMENT, 4, 5)
    assert calculate_score(candidate) == 10 - 1  # 9


def test_insertion_at_index_0():
    """Insertion (missing char) at position 0 applies the highest penalty (-10)."""
    candidate = _make_candidate(EditType.INSERTION, 0, 6)
    assert calculate_score(candidate) == 12 - 10  # 2


def test_deletion_at_index_2():
    """Deletion (extra char) at position 2 applies the same penalty as insertion (-6)."""
    candidate = _make_candidate(EditType.DELETION, 2, 5)
    assert calculate_score(candidate) == 10 - 6  # 4


def test_penalty_capped_at_last_position():
    """Any index beyond 4 must use the same penalty as index 4."""
    candidate_at_4  = _make_candidate(EditType.REPLACEMENT, 4, 5)
    candidate_at_10 = _make_candidate(EditType.REPLACEMENT, 10, 5)
    assert calculate_score(candidate_at_4) == calculate_score(candidate_at_10)


@pytest.mark.parametrize("edit_index", [0, 1, 2, 3, 4, 5, 12])
def test_insertion_and_deletion_tables_are_identical(edit_index):
    """The spec gives insertion and deletion one shared penalty table."""
    insertion = _make_candidate(EditType.INSERTION, edit_index, 5)
    deletion  = _make_candidate(EditType.DELETION,  edit_index, 5)
    assert calculate_score(insertion) == calculate_score(deletion)


@pytest.mark.parametrize(
    ("edit_type", "expected_penalties"),
    [
        (EditType.REPLACEMENT, [-5, -4, -3, -2, -1, -1, -1]),
        (EditType.INSERTION,   [-10, -8, -6, -4, -2, -2, -2]),
        (EditType.DELETION,    [-10, -8, -6, -4, -2, -2, -2]),
    ],
)
def test_full_penalty_table_matches_spec(edit_type, expected_penalties):
    """Re-derive every penalty position directly from the specification."""
    base = 10  # correct_characters=5 -> 5 * 2
    actual = [
        calculate_score(_make_candidate(edit_type, index, 5)) - base
        for index in range(len(expected_penalties))
    ]
    assert actual == expected_penalties


def test_deletion_of_extra_character_worked_example():
    """Spec example: 'להייות או לא' -> base 22, deletion at position 3 -> 18."""
    candidate = _make_candidate(EditType.DELETION, 3, 11)
    assert calculate_score(candidate) == 22 - 4  # 18
