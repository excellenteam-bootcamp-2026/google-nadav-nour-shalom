from src.contracts.search_algorithm import SearchAlgorithm
from src.contracts.search_structure import SearchStructure
from src.models.match_candidate import MatchCandidate
from src.models.prepared_sentence import PreparedSentence
from src.structures.naive_search_structure import NaiveSearchStructure

from .one_edit_verifier import OneEditVerifier


class NaiveSearchAlgorithm(SearchAlgorithm):
    """Correctness-first exhaustive implementation of ``SearchAlgorithm``."""

    def search(
        self,
        normalized_query: str,
        structure: SearchStructure,
    ) -> list[MatchCandidate]:
        """Return raw matches for a non-empty, already-normalized query.

        Multiple occurrences and multiple valid one-edit interpretations
        are intentionally preserved for the online scoring layer.
        """
        if not isinstance(structure, NaiveSearchStructure):
            raise TypeError("NaiveSearchAlgorithm requires NaiveSearchStructure.")

        if not normalized_query:
            return []

        matches: list[MatchCandidate] = []
        for sentence in structure.sentences:
            matches.extend(
                self._search_sentence(
                    query=normalized_query,
                    sentence=sentence,
                )
            )
        return matches

    def _search_sentence(
        self,
        query: str,
        sentence: PreparedSentence,
    ) -> list[MatchCandidate]:
        """Try every start position in one normalized sentence."""
        results: list[MatchCandidate] = []
        for start in range(len(sentence.normalized_text)):
            results.extend(
                self._check_from_position(
                    query=query,
                    text=sentence.normalized_text,
                    start=start,
                    sentence=sentence,
                )
            )
        return results

    def _check_from_position(
        self,
        query: str,
        text: str,
        start: int,
        sentence: PreparedSentence,
    ) -> list[MatchCandidate]:
        """Test only target lengths m, m + 1, and m - 1.

        A target length of zero is skipped: an empty target substring is
        never a valid completion match, including for a one-character query.
        """
        query_length = len(query)
        results: list[MatchCandidate] = []

        for target_length in (
            query_length,
            query_length + 1,
            query_length - 1,
        ):
            if target_length <= 0:
                continue

            end = start + target_length
            if end > len(text):
                continue

            results.extend(
                OneEditVerifier.compare(
                    query=query,
                    target=text[start:end],
                    sentence=sentence,
                    match_start=start,
                )
            )

        return results
