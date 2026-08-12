from src.structures.qgram_search_structure import QGramSearchStructure


class QGramVoter:
    def vote(
        self,
        query: str,
        structure: QGramSearchStructure,
        gram_size: int,
    ) -> dict[int, int]:

        votes: dict[int, int] = {}

        if len(query) < gram_size:
            return votes

        for query_position in range(
            len(query) - gram_size + 1
        ):

            qgram = query[
                query_position:
                query_position + gram_size
            ]

            occurrences = structure.get_occurrences(
                qgram,
                gram_size,
            )

            voted_sentences: set[int] = set()

            for (
                sentence_id,
                sentence_position,
            ) in occurrences:

                # With one insertion/deletion the
                # expected position may shift by one.
                if abs(
                    sentence_position
                    - query_position
                ) > 1:
                    continue

                if sentence_id in voted_sentences:
                    continue

                votes[sentence_id] = (
                    votes.get(sentence_id, 0)
                    + 1
                )

                voted_sentences.add(
                    sentence_id
                )

        return votes
