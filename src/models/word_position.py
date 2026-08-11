from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WordPosition:
    """A normalized word and its half-open character range."""

    word: str
    start: int
    end: int
