"""
Scoring logic for the online autocomplete layer (Step 4: Calculate Score).

Each MatchCandidate receives a score based on:
  - Base score: correct_characters * 2
  - Penalty: subtracted based on the edit type and the position of the error.
"""

from src.models.edit_type import EditType
from src.models.match_candidate import MatchCandidate

# Penalty table indexed by edit position (0 = first character).
# Positions beyond index 4 use the last value in the list.
#
# Per the specification, INSERTION and DELETION share one identical table:
# an added or a missing character costs the same at the same position.
_INSERT_DELETE_PENALTIES: list[int] = [-10, -8, -6, -4, -2]

_PENALTIES: dict[EditType, list[int]] = {
    EditType.REPLACEMENT: [-5, -4, -3, -2, -1],
    EditType.INSERTION:   _INSERT_DELETE_PENALTIES,
    EditType.DELETION:    _INSERT_DELETE_PENALTIES,
}


def calculate_score(candidate: MatchCandidate) -> int:
    """Return the final integer score for a single match candidate.

    Args:
        candidate: A MatchCandidate produced by the search engine.

    Returns:
        An integer score. Higher is better.
    """
    base = candidate.correct_characters * 2

    if candidate.edit_type == EditType.EXACT:
        return base

    penalty = _get_penalty(candidate.edit_type, candidate.edit_index)
    return base + penalty


def _get_penalty(edit_type: EditType, edit_index: int) -> int:
    """Return the penalty (a negative integer) for a given edit.

    Args:
        edit_type: The type of edit (REPLACEMENT, INSERTION, or DELETION).
        edit_index: Zero-based position of the edit in the normalized query.

    Returns:
        A negative integer representing the penalty.
    """
    penalties = _PENALTIES[edit_type]
    index = min(edit_index, len(penalties) - 1)
    return penalties[index]
