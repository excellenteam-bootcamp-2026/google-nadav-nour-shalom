from pathlib import Path

from src.normalization.project_text_normalizer import ProjectTextNormalizer

from .loader import FileLoader
from .models import PreparedSentence
from .normalizer import get_word_positions


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
        self.normalizer = ProjectTextNormalizer()
        self._next_sentence_id = 0

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
            if not line.strip():
                continue

            original_text = line

            normalized_text = self.normalizer.normalize(original_text)

            if not normalized_text:
                continue

            result.append(
                PreparedSentence(
                    sentence_id=self._next_sentence_id,
                    original_text=original_text,
                    normalized_text=normalized_text,
                    source_path=source_text,
                    offset=line_number,
                    word_positions=get_word_positions(normalized_text),
                )
            )
            self._next_sentence_id += 1

        return result
