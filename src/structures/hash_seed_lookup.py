from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from re import finditer
from types import MappingProxyType

from src.contracts.seed_lookup import SeedLookup
from src.models.prepared_sentence import PreparedSentence
from src.models.seed_occurrence import SeedOccurrence


@dataclass(frozen=True, slots=True)
class HashSeedIndexStats:
    unique_words: int
    word_occurrences: int
    intra_word_seed_keys: int
    intra_word_seed_references: int
    boundary_seed_keys: int
    boundary_occurrences: int


@dataclass(frozen=True, slots=True)
class HashSeedLookup(SeedLookup):
    """Hash-based unified lookup over intra-word and boundary seeds."""

    q: int
    _word_occurrences: Mapping[int, tuple[tuple[int, int], ...]]
    _intra_word_seed_index: Mapping[str, tuple[tuple[int, int], ...]]
    _boundary_seed_index: Mapping[str, tuple[SeedOccurrence, ...]]
    stats: HashSeedIndexStats

    @classmethod
    def build(
        cls,
        sentences: Iterable[PreparedSentence],
        q: int,
    ) -> "HashSeedLookup":
        if q <= 0:
            raise ValueError("q must be positive.")

        corpus = tuple(sentences)
        word_ids: dict[str, int] = {}
        unique_words: list[str] = []
        word_occurrences: dict[int, list[tuple[int, int]]] = defaultdict(list)

        for sentence in corpus:
            for word, start in cls._word_ranges(sentence):
                word_id = word_ids.get(word)
                if word_id is None:
                    word_id = len(unique_words)
                    word_ids[word] = word_id
                    unique_words.append(word)
                word_occurrences[word_id].append((sentence.sentence_id, start))

        intra_word_seed_index: dict[str, list[tuple[int, int]]] = defaultdict(list)
        for word_id, word in enumerate(unique_words):
            for seed_offset in range(len(word) - q + 1):
                seed = word[seed_offset : seed_offset + q]
                intra_word_seed_index[seed].append((word_id, seed_offset))

        boundary_seed_index: dict[str, list[SeedOccurrence]] = defaultdict(list)
        for sentence in corpus:
            text = sentence.normalized_text
            for position in range(len(text) - q + 1):
                seed = text[position : position + q]
                if " " not in seed:
                    continue
                boundary_seed_index[seed].append(
                    SeedOccurrence(sentence.sentence_id, position)
                )

        frozen_word_occurrences = {
            word_id: tuple(occurrences)
            for word_id, occurrences in word_occurrences.items()
        }
        frozen_intra_index = {
            seed: tuple(references)
            for seed, references in intra_word_seed_index.items()
        }
        frozen_boundary_index = {
            seed: tuple(occurrences)
            for seed, occurrences in boundary_seed_index.items()
        }
        stats = HashSeedIndexStats(
            unique_words=len(unique_words),
            word_occurrences=sum(
                len(occurrences)
                for occurrences in frozen_word_occurrences.values()
            ),
            intra_word_seed_keys=len(frozen_intra_index),
            intra_word_seed_references=sum(
                len(references) for references in frozen_intra_index.values()
            ),
            boundary_seed_keys=len(frozen_boundary_index),
            boundary_occurrences=sum(
                len(occurrences) for occurrences in frozen_boundary_index.values()
            ),
        )
        return cls(
            q=q,
            _word_occurrences=MappingProxyType(frozen_word_occurrences),
            _intra_word_seed_index=MappingProxyType(frozen_intra_index),
            _boundary_seed_index=MappingProxyType(frozen_boundary_index),
            stats=stats,
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

    def frequency(self, seed: str) -> int:
        if " " in seed:
            return len(self._boundary_seed_index.get(seed, ()))

        return sum(
            len(self._word_occurrences[word_id])
            for word_id, _seed_offset in self._intra_word_seed_index.get(
                seed, ()
            )
        )

    def occurrences(self, seed: str) -> tuple[SeedOccurrence, ...]:
        if " " in seed:
            return self._boundary_seed_index.get(seed, ())

        return tuple(
            SeedOccurrence(
                sentence_id=sentence_id,
                position=word_start + seed_offset,
            )
            for word_id, seed_offset in self._intra_word_seed_index.get(seed, ())
            for sentence_id, word_start in self._word_occurrences[word_id]
        )
