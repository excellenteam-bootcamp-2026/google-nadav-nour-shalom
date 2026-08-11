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
