"""Output model returned to the user after ranking (Step 7)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AutoCompleteData:
    """The final result object presented to the user.

    Attributes:
        completed_sentence: The original (non-normalized) sentence text.
        source_text: Path of the source file the sentence came from.
        offset: Line number (or sentence index) within the source file.
        score: Integer score computed by the scoring layer.
    """

    completed_sentence: str
    source_text: str
    offset: int
    score: int
