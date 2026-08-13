from src.algorithms.naive_search_algorithm import NaiveSearchAlgorithm
from src.algorithms.naive_search_stats import NaiveSearchStats
from src.algorithms.one_edit_verifier import OneEditVerifier
from src.algorithms.qgram_search_stats import QGramSearchStats
from src.contracts.search_algorithm import SearchAlgorithm
from src.contracts.search_structure import SearchStructure
from src.models.match_candidate import MatchCandidate
from src.structures.naive_search_structure import NaiveSearchStructure
from src.structures.qgram_search_structure import QGramSearchStructure


class QGramSearchAlgorithm(SearchAlgorithm):
    """Positional q-gram candidate generation plus shared one-edit verification.

    At least one query q-gram survives a single edit when the query contains
    at least twice the active gram size.  Every occurrence of every query gram
    therefore proposes starts at alignment shifts -1, 0, and +1.  The shared
    verifier remains the sole authority for exact/edit interpretation.
    """

    def __init__(self, stats: QGramSearchStats | None = None) -> None:
        self._stats = stats

    def search(
        self,
        normalized_query: str,
        structure: SearchStructure,
    ) -> list[MatchCandidate]:
        if not isinstance(structure, QGramSearchStructure):
            raise TypeError("QGramSearchAlgorithm requires QGramSearchStructure.")

        self._increment("query_count")
        if not normalized_query:
            return []

        active_q = structure.choose_q(normalized_query)
        if len(normalized_query) < 2 * active_q:
            return self._fallback(normalized_query, structure)

        candidate_starts: set[tuple[int, int]] = set()
        for query_position in range(len(normalized_query) - active_q + 1):
            self._increment("query_qgrams")
            self._increment("posting_lists_accessed")
            qgram = normalized_query[
                query_position : query_position + active_q
            ]
            for sentence_index, occurrence_position in structure.get_occurrences(
                qgram, active_q
            ):
                self._increment("posting_entries_scanned")
                aligned_start = occurrence_position - query_position
                for start in (
                    aligned_start - 1,
                    aligned_start,
                    aligned_start + 1,
                ):
                    self._increment("candidate_starts_before_dedup")
                    sentence = structure.get_sentence(sentence_index)
                    if sentence is None or start < 0:
                        continue
                    if start >= len(sentence.normalized_text):
                        continue
                    candidate_starts.add((sentence_index, start))

        if self._stats is not None:
            self._stats.candidate_starts_after_dedup += len(candidate_starts)

        query_length = len(normalized_query)
        matches: list[MatchCandidate] = []
        for sentence_index, start in candidate_starts:
            sentence = structure.get_sentence(sentence_index)
            if sentence is None:
                continue
            for target_length in (
                query_length,
                query_length + 1,
                query_length - 1,
            ):
                if target_length <= 0:
                    continue
                end = start + target_length
                if end > len(sentence.normalized_text):
                    continue
                self._increment("target_contexts")
                self._increment("verifier_calls")
                matches.extend(
                    OneEditVerifier.compare(
                        query=normalized_query,
                        target=sentence.normalized_text[start:end],
                        sentence=sentence,
                        match_start=start,
                    )
                )
        return matches

    def _fallback(
        self,
        query: str,
        structure: QGramSearchStructure,
    ) -> list[MatchCandidate]:
        self._increment("fallback_count")
        naive_stats = NaiveSearchStats()
        result = NaiveSearchAlgorithm(stats=naive_stats).search(
            query,
            NaiveSearchStructure(tuple(structure.sentences)),
        )
        if self._stats is not None:
            positions = sum(len(sentence.normalized_text) for sentence in structure.sentences)
            self._stats.candidate_starts_before_dedup += positions
            self._stats.candidate_starts_after_dedup += positions
            self._stats.target_contexts += naive_stats.verifier_calls
            self._stats.verifier_calls += naive_stats.verifier_calls
        return result

    def _increment(self, field_name: str) -> None:
        if self._stats is None:
            return
        setattr(self._stats, field_name, getattr(self._stats, field_name) + 1)
