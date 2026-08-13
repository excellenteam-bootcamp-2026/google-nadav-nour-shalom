from dataclasses import dataclass

from src.contracts.search_algorithm import SearchAlgorithm
from src.contracts.search_structure import SearchStructure
from src.models.candidate_context import CandidateContext
from src.models.match_candidate import MatchCandidate
from src.models.seed_candidate import SeedCandidate
from src.structures.bi_anchor_search_structure import BiAnchorSearchStructure
from src.structures.naive_search_structure import NaiveSearchStructure

from .bi_anchor_search_stats import BiAnchorSearchStats
from .naive_search_algorithm import NaiveSearchAlgorithm
from .naive_search_stats import NaiveSearchStats
from .one_edit_verifier import OneEditVerifier


@dataclass(frozen=True, slots=True)
class AnchorPlan:
    """The anchor configuration chosen for one query, before expansion."""

    q: int
    seeds: tuple[SeedCandidate, SeedCandidate]
    expansion_cost: int


class BiAnchorSearchAlgorithm(SearchAlgorithm):
    """Generate selective target contexts, then use shared verification.

    Anchor length is adaptive. Every q indexed by the structure with
    ``2 * q <= len(query)`` admits two non-overlapping query seed ranges, so
    every such q carries the same one-edit proof: a single edit can damage at
    most one of two disjoint ranges, leaving the other exact. Which q is used
    is therefore a pure performance choice, decided per query by the corpus
    expansion cost of the cheapest non-overlapping pair that q can offer.
    """

    def __init__(
        self,
        stats: BiAnchorSearchStats | None = None,
        minimum_anchor_length: int = 2,
    ) -> None:
        """``minimum_anchor_length`` is the measured routing floor.

        Queries shorter than it take the Naive path even when a valid q
        exists. It exists because a valid q can still be slower than Naive,
        never because a valid q would be wrong.
        """
        if minimum_anchor_length < 2:
            raise ValueError(
                "minimum_anchor_length must be at least 2; a single character "
                "cannot hold two non-overlapping anchors."
            )
        self._stats = stats
        self._minimum_anchor_length = minimum_anchor_length

    def search(
        self,
        normalized_query: str,
        structure: SearchStructure,
    ) -> list[MatchCandidate]:
        if not isinstance(structure, BiAnchorSearchStructure):
            raise TypeError(
                "BiAnchorSearchAlgorithm requires BiAnchorSearchStructure."
            )

        self._increment("query_count")
        if self._stats is not None:
            self._stats.last_selected_q = None
            self._stats.last_pair_cost_by_q = {}
        if not normalized_query:
            return []

        chosen = self.plan(normalized_query, structure)
        if chosen is None:
            return self._fallback(normalized_query, structure)

        selected_q, selected = chosen.q, chosen.seeds
        first_seed, second_seed = selected
        if self._stats is not None:
            self._stats.anchored_query_count += 1
            self._stats.last_selected_seeds = selected
            self._stats.last_selected_q = selected_q
            self._stats.selected_q_counts[selected_q] = (
                self._stats.selected_q_counts.get(selected_q, 0) + 1
            )
            self._stats.selected_seed_frequency_sum += (
                first_seed.frequency + second_seed.frequency
            )

        if first_seed.frequency == 0 and second_seed.frequency == 0:
            self._increment("zero_frequency_returns")
            return []

        contexts = self._candidate_contexts(
            normalized_query,
            structure,
            selected,
        )
        matches: list[MatchCandidate] = []
        for context in contexts:
            sentence = structure.sentences_by_id[context.sentence_id]
            target = sentence.normalized_text[
                context.start : context.start + context.target_length
            ]
            self._increment("verifier_calls")
            matches.extend(
                OneEditVerifier.compare(
                    normalized_query,
                    target,
                    sentence,
                    context.start,
                )
            )

        return self._deduplicate_matches(matches)

    def _fallback(
        self,
        normalized_query: str,
        structure: BiAnchorSearchStructure,
    ) -> list[MatchCandidate]:
        self._increment("fallback_count")
        fallback_stats = NaiveSearchStats()
        matches = NaiveSearchAlgorithm(stats=fallback_stats).search(
            normalized_query,
            NaiveSearchStructure(sentences=structure.sentences),
        )
        if self._stats is not None:
            self._stats.verifier_calls += fallback_stats.verifier_calls
            self._stats.candidate_contexts_generated += (
                fallback_stats.verifier_calls
            )
            self._stats.candidate_contexts_after_dedup += (
                fallback_stats.verifier_calls
            )
        return matches

    def plan(
        self,
        normalized_query: str,
        structure: BiAnchorSearchStructure,
    ) -> AnchorPlan | None:
        """Pick the q whose cheapest non-overlapping pair expands least.

        Every candidate q is equally correct. Shorter seeds widen the choice
        of disjoint ranges but have larger posting lists, so neither direction
        wins in general and the corpus decides per query. Ties keep the larger
        q, which is the configured default. ``None`` means no indexed q fits
        and the caller must take the Naive path.

        Exposed so instrumentation can read the decision and its predicted
        cost without paying for the expansion it predicts.
        """
        if (
            not normalized_query
            or len(normalized_query) < self._minimum_anchor_length
        ):
            return None

        best: AnchorPlan | None = None
        best_key: tuple[int, int] | None = None

        for q in structure.q_values:
            if 2 * q > len(normalized_query):
                continue
            self._increment("q_candidates_evaluated")
            pair = self._select_seed_pair(
                self._query_seeds(normalized_query, structure, q)
            )
            if pair is None:
                continue
            cost = pair[0].frequency + pair[1].frequency
            if self._stats is not None:
                self._stats.last_pair_cost_by_q[q] = cost
            key = (cost, -q)
            if best_key is None or key < best_key:
                best = AnchorPlan(q=q, seeds=pair, expansion_cost=cost)
                best_key = key

        return best

    @staticmethod
    def _query_seeds(
        query: str,
        structure: BiAnchorSearchStructure,
        q: int,
    ) -> tuple[SeedCandidate, ...]:
        return tuple(
            SeedCandidate(
                text=query[start : start + q],
                query_start=start,
                query_end=start + q,
                frequency=structure.seed_lookup.frequency(
                    query[start : start + q]
                ),
            )
            for start in range(len(query) - q + 1)
        )

    @staticmethod
    def _select_seed_pair(
        seeds: tuple[SeedCandidate, ...],
    ) -> tuple[SeedCandidate, SeedCandidate] | None:
        """Choose the cheapest pair; rarity is performance-only.

        Correctness needs only two non-overlapping query ranges. One edit
        affects at most one such range, so at least one seed survives exactly.
        Query positions provide deterministic tie-breaking.
        """
        best: tuple[SeedCandidate, SeedCandidate] | None = None
        best_key: tuple[int, int, int] | None = None
        for first_index, first in enumerate(seeds):
            for second in seeds[first_index + 1 :]:
                if first.query_end > second.query_start:
                    continue
                key = (
                    first.frequency + second.frequency,
                    first.query_start,
                    second.query_start,
                )
                if best_key is None or key < best_key:
                    best = (first, second)
                    best_key = key
        return best

    def _candidate_contexts(
        self,
        query: str,
        structure: BiAnchorSearchStructure,
        selected: tuple[SeedCandidate, SeedCandidate],
    ) -> tuple[CandidateContext, ...]:
        """Generate bounded contexts from independent starts and lengths.

        A single insertion or deletion before the surviving seed changes its
        alignment by at most one, hence the three starts. Target length is a
        separate edit-semantic dimension and is never inferred from that shift.
        """
        query_length = len(query)
        target_lengths = (
            query_length - 1,
            query_length,
            query_length + 1,
        )
        unique_contexts: dict[CandidateContext, None] = {}

        for seed in selected:
            occurrences = structure.seed_lookup.occurrences(seed.text)
            if self._stats is not None:
                self._stats.seed_occurrences_expanded += len(occurrences)

            for occurrence in occurrences:
                sentence = structure.sentences_by_id.get(
                    occurrence.sentence_id
                )
                if sentence is None:
                    continue
                base_start = occurrence.position - seed.query_start
                for start in (base_start - 1, base_start, base_start + 1):
                    for target_length in target_lengths:
                        # Python slices truncate silently. Only real target
                        # slices are allowed to become CandidateContexts.
                        if target_length <= 0:
                            continue
                        if start < 0:
                            continue
                        if start + target_length > len(sentence.normalized_text):
                            continue

                        self._increment("candidate_contexts_generated")
                        unique_contexts[CandidateContext(
                            sentence_id=occurrence.sentence_id,
                            start=start,
                            target_length=target_length,
                        )] = None

        if self._stats is not None:
            self._stats.candidate_contexts_after_dedup += len(unique_contexts)
        return tuple(unique_contexts)

    @staticmethod
    def _deduplicate_matches(
        matches: list[MatchCandidate],
    ) -> list[MatchCandidate]:
        unique: dict[
            tuple[int, int, object, int | None, int], MatchCandidate
        ] = {}
        for match in matches:
            key = (
                match.sentence.sentence_id,
                match.match_start,
                match.edit_type,
                match.edit_index,
                match.correct_characters,
            )
            unique.setdefault(key, match)
        return list(unique.values())

    def _increment(self, field_name: str) -> None:
        if self._stats is None:
            return
        setattr(self._stats, field_name, getattr(self._stats, field_name) + 1)
