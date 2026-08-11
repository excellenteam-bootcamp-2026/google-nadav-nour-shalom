from dataclasses import dataclass

from .edit_type import EditType
from .prepared_sentence import PreparedSentence


@dataclass(frozen=True, slots=True)
class MatchCandidate:
    """One raw valid match interpretation returned by search.

    ``match_start`` is a zero-based index in
    ``sentence.normalized_text``. ``edit_index`` is zero-based and relative
    to the normalized user query: it is ``None`` for an exact match, the
    affected character for replacement/deletion, and a query insertion
    slot for insertion. Insertion slots range from zero through the query
    length, inclusive. ``match_start`` is not converted back into an index
    in ``sentence.original_text``.
    """

    sentence: PreparedSentence
    match_start: int
    edit_type: EditType
    edit_index: int | None
    correct_characters: int
