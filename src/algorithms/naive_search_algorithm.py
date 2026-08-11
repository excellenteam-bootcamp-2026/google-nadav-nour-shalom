from collections.abc import Iterable

from src.contracts.search_algorithm import SearchAlgorithm
from src.models.edit_type import EditType
from src.models.match_candidate import MatchCandidate
from src.models.prepared_sentence import PreparedSentence


class NaiveSearchAlgorithm(SearchAlgorithm):
    """Correctness-first exhaustive implementation of ``SearchAlgorithm``."""

    def __init__(self) -> None:
        self._sentences: tuple[PreparedSentence, ...] = ()

    def build(self, sentences: Iterable[PreparedSentence]) -> None:
        """Store prepared sentences; this implementation builds no index."""
        self._sentences = tuple(sentences)

    def search(self, normalized_query: str) -> list[MatchCandidate]:
        """Return raw matches for a non-empty, already-normalized query.

        Multiple occurrences and multiple valid one-edit interpretations
        are intentionally preserved for the online scoring layer.
        """
        if not normalized_query:
            return []

        matches: list[MatchCandidate] = []
        for sentence in self._sentences:
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
                self._compare(
                    query=query,
                    target=text[start:end],
                    sentence=sentence,
                    match_start=start,
                )
            )

        return results

    def _compare(
        self,
        query: str,
        target: str,
        sentence: PreparedSentence,
        match_start: int,
    ) -> list[MatchCandidate]:
        """Return all interpretations requiring at most one correction."""
        if len(query) == len(target):
            return self._check_equal_length(
                query=query,
                target=target,
                sentence=sentence,
                match_start=match_start,
            )

        if len(target) == len(query) + 1:
            return self._check_missing_character(
                query=query,
                target=target,
                sentence=sentence,
                match_start=match_start,
            )

        if len(query) == len(target) + 1:
            return self._check_extra_character(
                query=query,
                target=target,
                sentence=sentence,
                match_start=match_start,
            )

        return []

    def _check_equal_length(
        self,
        query: str,
        target: str,
        sentence: PreparedSentence,
        match_start: int,
    ) -> list[MatchCandidate]:
        """Classify equal lengths as exact, one replacement, or invalid."""
        mismatch_indices = [
            index
            for index, (query_char, target_char) in enumerate(
                zip(query, target)
            )
            if query_char != target_char
        ]

        if not mismatch_indices:
            return [
                MatchCandidate(
                    sentence=sentence,
                    match_start=match_start,
                    edit_type=EditType.EXACT,
                    edit_index=None,
                    correct_characters=len(query),
                )
            ]

        if len(mismatch_indices) == 1:
            return [
                MatchCandidate(
                    sentence=sentence,
                    match_start=match_start,
                    edit_type=EditType.REPLACEMENT,
                    edit_index=mismatch_indices[0],
                    correct_characters=len(query) - 1,
                )
            ]

        return []

    def _check_missing_character(
        self,
        query: str,
        target: str,
        sentence: PreparedSentence,
        match_start: int,
    ) -> list[MatchCandidate]:
        """Return every slot where one target character fits the query."""
        results: list[MatchCandidate] = []
        for insertion_slot in range(len(query) + 1):
            target_without_inserted_character = (
                target[:insertion_slot] + target[insertion_slot + 1 :]
            )
            if query != target_without_inserted_character:
                continue

            results.append(
                MatchCandidate(
                    sentence=sentence,
                    match_start=match_start,
                    edit_type=EditType.INSERTION,
                    edit_index=insertion_slot,
                    correct_characters=len(query),
                )
            )
        return results

    def _check_extra_character(
        self,
        query: str,
        target: str,
        sentence: PreparedSentence,
        match_start: int,
    ) -> list[MatchCandidate]:
        """Return every query index whose deletion produces the target."""
        results: list[MatchCandidate] = []
        for deletion_index in range(len(query)):
            if query[:deletion_index] + query[deletion_index + 1 :] != target:
                continue

            results.append(
                MatchCandidate(
                    sentence=sentence,
                    match_start=match_start,
                    edit_type=EditType.DELETION,
                    edit_index=deletion_index,
                    correct_characters=len(query) - 1,
                )
            )
        return results
