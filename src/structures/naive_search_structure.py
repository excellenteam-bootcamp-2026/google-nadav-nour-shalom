from dataclasses import dataclass

from src.contracts.search_structure import SearchStructure
from src.models.prepared_sentence import PreparedSentence


@dataclass(frozen=True, slots=True)
class NaiveSearchStructure(SearchStructure):
    """Immutable corpus storage for the brute-force implementation."""

    sentences: tuple[PreparedSentence, ...]
