from abc import ABC, abstractmethod

from src.contracts.search_structure import SearchStructure
from src.models.match_candidate import MatchCandidate


class SearchAlgorithm(ABC):
    """Search an already-built structure without owning corpus state."""

    @abstractmethod
    def search(
        self,
        normalized_query: str,
        structure: SearchStructure,
    ) -> list[MatchCandidate]:
        """Return every raw valid match for an already-normalized query.

        Results may contain different occurrences or start positions in
        the same sentence and different valid one-edit interpretations.
        Search implementations must not score, rank, or deduplicate at the
        sentence level. The online completion layer scores every candidate,
        keeps the best candidate per sentence, ranks sentences, applies the
        alphabetical tie-break, and selects the top five.

        An empty query returns no candidates.
        """
        raise NotImplementedError
