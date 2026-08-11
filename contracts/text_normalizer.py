from abc import ABC, abstractmethod


class TextNormalizer(ABC):
    """Shared normalization contract for offline and online processing."""

    @abstractmethod
    def normalize(self, text: str) -> str:
        """Convert text to the canonical form used for matching."""
        raise NotImplementedError
