class CandidateSelector:
    def select(
        self,
        votes: dict[int, int],
        query_length: int,
        q: int,
    ) -> list[int]:

        if query_length < q:
            return list(votes.keys())

        number_of_qgrams = query_length - q + 1

        # One edit can damage up to q q-grams.
        minimum_votes = max(
            1,
            number_of_qgrams - q,
        )

        candidates = [
            sentence_id
            for sentence_id, vote_count in votes.items()
            if vote_count >= minimum_votes
        ]

        return candidates
