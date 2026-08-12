from src.algorithms.candidate_selector import CandidateSelector
from src.algorithms.one_edit_verifier import OneEditVerifier
from src.algorithms.qgram_voting import QGramVoter
from src.autocomplete.models import PreparedSentence
from src.structures.qgram_search_structure import QGramSearchStructure


class QGramSearchAlgorithm:
    def __init__(self) -> None:
        self.voter = QGramVoter()
        self.selector = CandidateSelector()
        self.verifier = OneEditVerifier()

    def search(
        self,
        query: str,
        structure: QGramSearchStructure,
    ) -> list[PreparedSentence]:

        if not query:
            return []

        # A one-character query cannot be filtered
        # safely when one edit is allowed.
        if len(query) == 1:
            return self._linear_fallback(
                query,
                structure,
            )

        active_q = structure.choose_q(
            query
        )

        votes = self.voter.vote(
            query=query,
            structure=structure,
            gram_size=active_q,
        )

        candidate_ids = self.selector.select(
            votes=votes,
            query_length=len(query),
            q=active_q,
        )

        results: list[PreparedSentence] = []

        for sentence_id in candidate_ids:

            sentence = structure.get_sentence(
                sentence_id
            )

            if sentence is None:
                continue

            if self.verifier.verify(
                query,
                sentence.normalized_sentence,
            ):
                results.append(sentence)

        return results

    def _linear_fallback(
        self,
        query: str,
        structure: QGramSearchStructure,
    ) -> list[PreparedSentence]:

        results: list[PreparedSentence] = []

        for sentence in structure.sentences.values():

            if self.verifier.verify(
                query,
                sentence.normalized_sentence,
            ):
                results.append(sentence)

        return results
