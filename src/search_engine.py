from collections.abc import Iterable

from src.contracts.search_algorithm import SearchAlgorithm
from src.contracts.search_structure import SearchStructure
from src.contracts.search_structure_builder import SearchStructureBuilder
from src.models.match_candidate import MatchCandidate
from src.models.prepared_sentence import PreparedSentence


class SearchEngine:
    """Stable facade coordinating structure construction and searching."""

    def __init__(
        self,
        builder: SearchStructureBuilder,
        algorithm: SearchAlgorithm,
    ) -> None:
        self._builder = builder
        self._algorithm = algorithm
        self._structure: SearchStructure | None = None

    def build(self, sentences: Iterable[PreparedSentence]) -> None:
        """Build and retain the configured internal search structure."""
        self._structure = self._builder.build(sentences)

    def search(self, normalized_query: str) -> list[MatchCandidate]:
        """Search through the configured algorithm after a successful build."""
        if self._structure is None:
            raise RuntimeError("SearchEngine.build() must be called before search().")

        return self._algorithm.search(normalized_query, self._structure)
