from pathlib import Path

from .loader import FileLoader
from .models import PreparedSentence
from .normalizer import get_word_positions, normalize_text


class DataPreparer:
    """
    Person 1 - Offline data preparation.

    Output:
        list[PreparedSentence]

    This class does NOT build a Trie, HashMap or any search index.
    That belongs to Person 2.
    """

    def __init__(self) -> None:
        self.loader = FileLoader()

    def prepare(self, source: str | Path) -> list[PreparedSentence]:
        prepared: list[PreparedSentence] = []

        for text_file in self.loader.load(source):
            prepared.extend(
                self._prepare_file(
                    source_text=text_file.source_text,
                    content=text_file.content,
                )
            )

        return prepared

    def _prepare_file(
        self,
        source_text: str,
        content: str,
    ) -> list[PreparedSentence]:
        result: list[PreparedSentence] = []

        # According to the project design:
        # 1 line = 1 sentence.
        # offset is the 1-based line number in the source file.
        for line_number, line in enumerate(content.split("\n"), start=1):
            original_sentence = line.strip()

            if not original_sentence:
                continue

            normalized_sentence = normalize_text(original_sentence)

            if not normalized_sentence:
                continue

            result.append(
                PreparedSentence(
                    original_sentence=original_sentence,
                    normalized_sentence=normalized_sentence,
                    source_text=source_text,
                    offset=line_number,
                    word_positions=get_word_positions(normalized_sentence),
                )
            )

        return result
