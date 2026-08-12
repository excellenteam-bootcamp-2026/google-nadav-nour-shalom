from src.models.edit_type import EditType
from src.models.match_candidate import MatchCandidate
from src.models.prepared_sentence import PreparedSentence


class OneEditVerifier:
    """Classify one target slice using the project's frozen edit semantics."""

    @staticmethod
    def compare(
        query: str,
        target: str,
        sentence: PreparedSentence,
        match_start: int,
    ) -> list[MatchCandidate]:
        """Return all interpretations requiring at most one correction."""
        if len(query) == len(target):
            return OneEditVerifier._check_equal_length(
                query=query,
                target=target,
                sentence=sentence,
                match_start=match_start,
            )

        if len(target) == len(query) + 1:
            return OneEditVerifier._check_missing_character(
                query=query,
                target=target,
                sentence=sentence,
                match_start=match_start,
            )

        if len(query) == len(target) + 1:
            return OneEditVerifier._check_extra_character(
                query=query,
                target=target,
                sentence=sentence,
                match_start=match_start,
            )

        return []

    @staticmethod
    def _check_equal_length(
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

    @staticmethod
    def _check_missing_character(
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

    @staticmethod
    def _check_extra_character(
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
