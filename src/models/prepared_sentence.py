from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PreparedSentence:
    """A source sentence prepared for search.

    ``original_text`` is preserved for the final result, while
    ``normalized_text`` is the only text searched. ``offset`` is the
    source line/sentence position supplied by preprocessing; it is
    independent source metadata, not a byte offset and not a character
    position in either text representation.
    """

    sentence_id: int
    original_text: str
    normalized_text: str
    source_path: str
    offset: int
