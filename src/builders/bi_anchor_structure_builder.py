from collections.abc import Iterable
from time import perf_counter_ns
from types import MappingProxyType

from src.contracts.search_structure_builder import SearchStructureBuilder
from src.models.prepared_sentence import PreparedSentence
from src.structures.bi_anchor_search_structure import (
    BiAnchorBuildStats,
    BiAnchorSearchStructure,
)
from src.structures.hash_seed_lookup import HashSeedLookup


class BiAnchorStructureBuilder(SearchStructureBuilder):
    """Build immutable hash seed indexes for Selective Bi-Anchor search."""

    def __init__(self, q: int = 3) -> None:
        if q <= 0:
            raise ValueError("q must be positive.")
        self._q = q

    def build(
        self,
        sentences: Iterable[PreparedSentence],
    ) -> BiAnchorSearchStructure:
        corpus = tuple(sentences)
        sentences_by_id: dict[int, PreparedSentence] = {}
        for sentence in corpus:
            if sentence.sentence_id in sentences_by_id:
                raise ValueError(
                    f"Duplicate sentence_id: {sentence.sentence_id}"
                )
            sentences_by_id[sentence.sentence_id] = sentence

        started_at = perf_counter_ns()
        seed_lookup = HashSeedLookup.build(corpus, self._q)
        index_build_ns = perf_counter_ns() - started_at

        return BiAnchorSearchStructure(
            sentences=corpus,
            sentences_by_id=MappingProxyType(sentences_by_id),
            seed_lookup=seed_lookup,
            q=self._q,
            build_stats=BiAnchorBuildStats(
                index_build_ns=index_build_ns,
                index=seed_lookup.stats,
            ),
        )
