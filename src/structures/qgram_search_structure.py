from array import array
from dataclasses import dataclass, field
from collections.abc import Iterator

from src.autocomplete.models import PreparedSentence


POSITION_BITS = 32
POSITION_MASK = (1 << POSITION_BITS) - 1


@dataclass
class QGramSearchStructure:
    q: int = 3

    # q=3:
    # qgram -> compact array of packed (sentence_id, position)
    positional_index: dict[
        str,
        array
    ] = field(default_factory=dict)

    # q=1/q=2:
    # gram_size -> qgram -> compact packed occurrences
    short_positional_indexes: dict[
        int,
        dict[str, array]
    ] = field(default_factory=dict)

    # sentence_id is simply the position in this list.
    sentences: list[PreparedSentence] = field(
        default_factory=list
    )

    def __post_init__(self) -> None:
        for gram_size in range(1, self.q):
            self.short_positional_indexes.setdefault(
                gram_size,
                {},
            )

    def _get_index(
        self,
        gram_size: int,
    ) -> dict[str, array]:

        if gram_size == self.q:
            return self.positional_index

        return self.short_positional_indexes.setdefault(
            gram_size,
            {},
        )

    def _pack(
        self,
        sentence_id: int,
        position: int,
    ) -> int:

        return (
            (sentence_id << POSITION_BITS)
            | position
        )

    def _unpack(
        self,
        packed: int,
    ) -> tuple[int, int]:

        sentence_id = packed >> POSITION_BITS
        position = packed & POSITION_MASK

        return sentence_id, position

    def add_sentence(
        self,
        sentence_id: int,
        sentence: PreparedSentence,
    ) -> None:

        # Builder sends sequential IDs: 0, 1, 2, ...
        if sentence_id == len(self.sentences):
            self.sentences.append(sentence)
        else:
            raise ValueError(
                "Sentence IDs must be sequential"
            )

        text = sentence.normalized_sentence

        # Build positional indexes for q=1, q=2 and q=3.
        for gram_size in range(1, self.q + 1):

            if len(text) < gram_size:
                continue

            index = self._get_index(
                gram_size
            )

            for position in range(
                len(text) - gram_size + 1
            ):
                gram = text[
                    position:
                    position + gram_size
                ]

                postings = index.get(gram)

                if postings is None:
                    postings = array("Q")
                    index[gram] = postings

                postings.append(
                    self._pack(
                        sentence_id,
                        position,
                    )
                )

    def get_occurrences(
        self,
        qgram: str,
        gram_size: int | None = None,
    ) -> Iterator[tuple[int, int]]:

        if gram_size is None:
            gram_size = len(qgram)

        index = self._get_index(
            gram_size
        )

        postings = index.get(qgram)

        if postings is None:
            return

        for packed in postings:
            yield self._unpack(packed)

    def choose_q(
        self,
        query: str,
    ) -> int:

        length = len(query)

        if length <= 3:
            return 1

        if length <= 5:
            return 2

        return self.q

    def get_sentence(
        self,
        sentence_id: int,
    ) -> PreparedSentence | None:

        if (
            sentence_id < 0
            or sentence_id >= len(self.sentences)
        ):
            return None

        return self.sentences[sentence_id]
