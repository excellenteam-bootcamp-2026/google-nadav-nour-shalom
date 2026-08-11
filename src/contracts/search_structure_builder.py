from abc import ABC, abstractmethod
from collections.abc import Iterable

from src.contracts.search_structure import SearchStructure
from src.models.prepared_sentence import PreparedSentence


class SearchStructureBuilder(ABC):
    """Build a search structure from already-prepared sentences."""

    @abstractmethod
    def build(
        self,
        sentences: Iterable[PreparedSentence],
    ) -> SearchStructure:
        """Return ready search data without performing any search."""
        raise NotImplementedError
