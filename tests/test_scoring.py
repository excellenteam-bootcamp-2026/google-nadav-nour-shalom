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
    """Deletion (extra char) at position 2 applies the mid-range penalty (-4)."""
    candidate = _make_candidate(EditType.DELETION, 2, 5)
    assert calculate_score(candidate) == 10 - 4  # 6


def test_penalty_capped_at_last_position():
    """Any index beyond 4 must use the same penalty as index 4."""
    candidate_at_4  = _make_candidate(EditType.REPLACEMENT, 4, 5)
    candidate_at_10 = _make_candidate(EditType.REPLACEMENT, 10, 5)
    assert calculate_score(candidate_at_4) == calculate_score(candidate_at_10)
