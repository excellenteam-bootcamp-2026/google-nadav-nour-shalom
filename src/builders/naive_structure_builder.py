from collections.abc import Iterable

from src.contracts.search_structure_builder import SearchStructureBuilder
from src.models.prepared_sentence import PreparedSentence
from src.structures.naive_search_structure import NaiveSearchStructure


class NaiveStructureBuilder(SearchStructureBuilder):
    """Store prepared sentences in the Naive structure without indexing."""

    def build(
        self,
        sentences: Iterable[PreparedSentence],
    ) -> NaiveSearchStructure:
        return NaiveSearchStructure(sentences=tuple(sentences))
