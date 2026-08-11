from abc import ABC, abstractmethod
from collections.abc import Iterable

from src.models.prepared_sentence import PreparedSentence
from src.models.match_candidate import MatchCandidate


class SearchAlgorithm(ABC):

    @abstractmethod
    def build(
        self,
        sentences: Iterable[PreparedSentence],
    ) -> None:
        """Prepare the internal search structure."""
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        normalized_query: str,
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
