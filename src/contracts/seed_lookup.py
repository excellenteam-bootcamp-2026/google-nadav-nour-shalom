from abc import ABC, abstractmethod

from src.models.seed_occurrence import SeedOccurrence


class SeedLookup(ABC):
    """Unified seed statistics and corpus-occurrence access."""

    @abstractmethod
    def frequency(self, seed: str) -> int:
        """Return the number of corpus occurrences lookup will expand."""
        raise NotImplementedError

    @abstractmethod
    def occurrences(self, seed: str) -> tuple[SeedOccurrence, ...]:
        """Return unified absolute corpus positions for the seed."""
        raise NotImplementedError
