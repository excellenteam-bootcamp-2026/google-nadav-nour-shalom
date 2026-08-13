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

    def __init__(
        self,
        q: int = 3,
        q_values: Iterable[int] | None = None,
    ) -> None:
        """Index ``q_values`` seed lengths; ``q`` stays the default anchor.

        Extra q values only widen the choices available to adaptive anchor
        selection. Correctness is unchanged: any indexed q may be used as
        long as two non-overlapping seed ranges of that q fit the query.
        """
        if q <= 0:
            raise ValueError("q must be positive.")
        indexed = (q,) if q_values is None else tuple(sorted(set(q_values)))
        if any(value <= 0 for value in indexed):
            raise ValueError("q must be positive.")
        if q not in indexed:
            raise ValueError(
                f"The default q={q} must be one of the indexed q values "
                f"{list(indexed)}."
            )
        self._q = q
        self._q_values = indexed

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
        seed_lookup = HashSeedLookup.build_multi(corpus, self._q_values)
        index_build_ns = perf_counter_ns() - started_at

        return BiAnchorSearchStructure(
            sentences=corpus,
            sentences_by_id=MappingProxyType(sentences_by_id),
            seed_lookup=seed_lookup,
            q=self._q,
            q_values=self._q_values,
            build_stats=BiAnchorBuildStats(
                index_build_ns=index_build_ns,
                index=seed_lookup.stats,
            ),
        )
