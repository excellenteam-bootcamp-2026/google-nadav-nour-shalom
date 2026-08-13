from collections.abc import Mapping
from dataclasses import dataclass

from src.contracts.search_structure import SearchStructure
from src.contracts.seed_lookup import SeedLookup
from src.models.prepared_sentence import PreparedSentence
from src.structures.hash_seed_lookup import HashSeedIndexStats


@dataclass(frozen=True, slots=True)
class BiAnchorBuildStats:
    index_build_ns: int
    index: HashSeedIndexStats


@dataclass(frozen=True, slots=True)
class BiAnchorSearchStructure(SearchStructure):
    """Immutable prepared corpus and seed access for Bi-Anchor search."""

    sentences: tuple[PreparedSentence, ...]
    sentences_by_id: Mapping[int, PreparedSentence]
    seed_lookup: SeedLookup
    q: int
    q_values: tuple[int, ...]
    build_stats: BiAnchorBuildStats
