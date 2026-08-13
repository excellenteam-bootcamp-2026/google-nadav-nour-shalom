from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from re import finditer
from types import MappingProxyType

from src.contracts.seed_lookup import SeedLookup
from src.models.prepared_sentence import PreparedSentence
from src.models.seed_occurrence import SeedOccurrence


@dataclass(frozen=True, slots=True)
class SeedIndexStats:
    """Size of the seed maps built for one q."""

    q: int
    intra_word_seed_keys: int
    intra_word_seed_references: int
    boundary_seed_keys: int
    boundary_occurrences: int


@dataclass(frozen=True, slots=True)
class HashSeedIndexStats:
    """Word-table size plus seed sizes summed over every indexed q."""

    unique_words: int
    word_occurrences: int
    intra_word_seed_keys: int
    intra_word_seed_references: int
    boundary_seed_keys: int
    boundary_occurrences: int
    per_q: Mapping[int, SeedIndexStats]


@dataclass(frozen=True, slots=True)
class _QSeedIndex:
    """Intra-word and boundary maps for one seed length.

    ``intra_word_frequency`` is precomputed because adaptive q selection
    prices several seeds per query before expanding any of them. Summing a
    posting list per price quote costs tens of milliseconds for a common
    short seed, which would swamp the retrieval it is meant to avoid.
    Boundary frequency needs no cache: it is the posting length itself.
    """

    q: int
    intra_word: Mapping[str, tuple[tuple[int, int], ...]]
    intra_word_frequency: Mapping[str, int]
    boundary: Mapping[str, tuple[SeedOccurrence, ...]]

    @property
    def stats(self) -> SeedIndexStats:
        return SeedIndexStats(
            q=self.q,
            intra_word_seed_keys=len(self.intra_word),
            intra_word_seed_references=sum(
                len(references) for references in self.intra_word.values()
            ),
            boundary_seed_keys=len(self.boundary),
            boundary_occurrences=sum(
                len(occurrences) for occurrences in self.boundary.values()
            ),
        )


@dataclass(frozen=True, slots=True)
class HashSeedLookup(SeedLookup):
    """Hash-based unified lookup over intra-word and boundary seeds.

    One instance may hold several seed lengths at once. The public contract
    stays ``frequency(seed)``/``occurrences(seed)``: q is inferred from
    ``len(seed)``, so callers never name a storage detail. Every q shares one
    word-occurrence table, so adding a q costs only its own seed maps.
    """

    q_values: tuple[int, ...]
    _unique_words: tuple[str, ...]
    _word_occurrences: Mapping[int, tuple[tuple[int, int], ...]]
    _seed_indexes: Mapping[int, _QSeedIndex]
    stats: HashSeedIndexStats

    @classmethod
    def build(
        cls,
        sentences: Iterable[PreparedSentence],
        q: int,
    ) -> "HashSeedLookup":
        """Build a single-q lookup (the historical configuration)."""
        return cls.build_multi(sentences, (q,))

    @classmethod
    def build_multi(
        cls,
        sentences: Iterable[PreparedSentence],
        q_values: Iterable[int],
    ) -> "HashSeedLookup":
        """Build one lookup serving every requested seed length."""
        requested = tuple(sorted(set(q_values)))
        if not requested:
            raise ValueError("At least one q is required.")
        if any(q <= 0 for q in requested):
            raise ValueError("q must be positive.")

        corpus = tuple(sentences)
        unique_words, word_occurrences = cls._build_word_table(corpus)

        seed_indexes = {
            q: cls._build_seed_index(corpus, unique_words, word_occurrences, q)
            for q in requested
        }
        per_q = {q: index.stats for q, index in seed_indexes.items()}
        stats = HashSeedIndexStats(
            unique_words=len(unique_words),
            word_occurrences=sum(
                len(occurrences) for occurrences in word_occurrences.values()
            ),
            intra_word_seed_keys=sum(
                item.intra_word_seed_keys for item in per_q.values()
            ),
            intra_word_seed_references=sum(
                item.intra_word_seed_references for item in per_q.values()
            ),
            boundary_seed_keys=sum(
                item.boundary_seed_keys for item in per_q.values()
            ),
            boundary_occurrences=sum(
                item.boundary_occurrences for item in per_q.values()
            ),
            per_q=MappingProxyType(per_q),
        )
        return cls(
            q_values=requested,
            _unique_words=unique_words,
            _word_occurrences=MappingProxyType(word_occurrences),
            _seed_indexes=MappingProxyType(seed_indexes),
            stats=stats,
        )

    @classmethod
    def _build_word_table(
        cls,
        corpus: tuple[PreparedSentence, ...],
    ) -> tuple[tuple[str, ...], dict[int, tuple[tuple[int, int], ...]]]:
        """Collect the vocabulary and its corpus positions exactly once."""
        word_ids: dict[str, int] = {}
        unique_words: list[str] = []
        occurrences: dict[int, list[tuple[int, int]]] = defaultdict(list)

        for sentence in corpus:
            for word, start in cls._word_ranges(sentence):
                word_id = word_ids.get(word)
                if word_id is None:
                    word_id = len(unique_words)
                    word_ids[word] = word_id
                    unique_words.append(word)
                occurrences[word_id].append((sentence.sentence_id, start))

        return (
            tuple(unique_words),
            {
                word_id: tuple(positions)
                for word_id, positions in occurrences.items()
            },
        )

    @staticmethod
    def _build_seed_index(
        corpus: tuple[PreparedSentence, ...],
        unique_words: tuple[str, ...],
        word_occurrences: Mapping[int, tuple[tuple[int, int], ...]],
        q: int,
    ) -> _QSeedIndex:
        """Index one seed length over the shared vocabulary and boundaries."""
        intra_word: dict[str, list[tuple[int, int]]] = defaultdict(list)
        intra_word_frequency: dict[str, int] = defaultdict(int)
        for word_id, word in enumerate(unique_words):
            word_frequency = len(word_occurrences[word_id])
            for seed_offset in range(len(word) - q + 1):
                seed = word[seed_offset : seed_offset + q]
                intra_word[seed].append((word_id, seed_offset))
                intra_word_frequency[seed] += word_frequency

        boundary: dict[str, list[SeedOccurrence]] = defaultdict(list)
        for sentence in corpus:
            text = sentence.normalized_text
            for position in range(len(text) - q + 1):
                seed = text[position : position + q]
                if " " not in seed:
                    continue
                boundary[seed].append(
                    SeedOccurrence(sentence.sentence_id, position)
                )

        return _QSeedIndex(
            q=q,
            intra_word=MappingProxyType(
                {seed: tuple(references) for seed, references in intra_word.items()}
            ),
            intra_word_frequency=MappingProxyType(dict(intra_word_frequency)),
            boundary=MappingProxyType(
                {seed: tuple(items) for seed, items in boundary.items()}
            ),
        )

    @staticmethod
    def _word_ranges(
        sentence: PreparedSentence,
    ) -> tuple[tuple[str, int], ...]:
        if sentence.word_positions:
            return tuple(
                (position.word, position.start)
                for position in sentence.word_positions
            )

        return tuple(
            (match.group(), match.start())
            for match in finditer(r"\S+", sentence.normalized_text)
        )

    def _index_for(self, seed: str) -> _QSeedIndex:
        """Resolve the index by seed length; never guess an unbuilt q."""
        index = self._seed_indexes.get(len(seed))
        if index is None:
            raise ValueError(
                f"No seed index for q={len(seed)}; "
                f"built q values are {list(self.q_values)}."
            )
        return index

    def indexed_seeds(self, q: int) -> tuple[str, ...]:
        """Return every seed key held for one q, intra-word and boundary."""
        index = self._seed_indexes.get(q)
        if index is None:
            raise ValueError(
                f"No seed index for q={q}; "
                f"built q values are {list(self.q_values)}."
            )
        return (*index.intra_word, *index.boundary)

    def frequency(self, seed: str) -> int:
        index = self._index_for(seed)
        if " " in seed:
            return len(index.boundary.get(seed, ()))

        return index.intra_word_frequency.get(seed, 0)

    def occurrences(self, seed: str) -> tuple[SeedOccurrence, ...]:
        index = self._index_for(seed)
        if " " in seed:
            return index.boundary.get(seed, ())

        return tuple(
            SeedOccurrence(
                sentence_id=sentence_id,
                position=word_start + seed_offset,
            )
            for word_id, seed_offset in index.intra_word.get(seed, ())
            for sentence_id, word_start in self._word_occurrences[word_id]
        )
