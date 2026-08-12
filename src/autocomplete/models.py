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

    @property
    def original_text(self) -> str:
        return self.original_sentence

    @property
    def normalized_text(self) -> str:
        return self.normalized_sentence

    @property
    def source_path(self) -> str:
        return self.source_text
