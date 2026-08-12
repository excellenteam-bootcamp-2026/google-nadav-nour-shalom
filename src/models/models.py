from collections.abc import Iterator
from dataclasses import dataclass


@dataclass
class WordPosition:
    word: str
    start: int
    end: int


@dataclass
class PreparedSentence:
    original_sentence: str
    normalized_sentence: str
    source_text: str
    offset: int
    word_positions: list[WordPosition]

    def __iter__(self) -> Iterator[WordPosition]:
        return iter(self.word_positions)