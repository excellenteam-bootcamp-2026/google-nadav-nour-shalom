from collections.abc import Iterable

from src.autocomplete.models import PreparedSentence
from src.structures.qgram_search_structure import QGramSearchStructure


class QGramStructureBuilder:
    def __init__(self, q: int = 3) -> None:
        self.q = q

    def build(
        self,
        sentences: Iterable[PreparedSentence],
    ) -> QGramSearchStructure:

        structure = QGramSearchStructure(q=self.q)

        for sentence_id, sentence in enumerate(sentences):
            structure.add_sentence(
                sentence_id,
                sentence,
            )

        return structure