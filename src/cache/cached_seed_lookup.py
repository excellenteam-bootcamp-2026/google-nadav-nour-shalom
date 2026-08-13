"""Memory-efficient SeedLookup backed by array.array for compact int storage.

Standard Python objects (like SeedOccurrence dataclasses) use ~48 bytes each.
With 50+ million boundary occurrences in the full 32MB corpus, that exceeds
8GB of RAM.  array.array('i') stores each int as a raw C int32 (4 bytes),
reducing memory by ~10x.

SeedOccurrence objects are created lazily: only during search when a specific
seed is queried (producing a handful of results), never in bulk.
"""

from __future__ import annotations

from array import array

from src.contracts.seed_lookup import SeedLookup
from src.models.seed_occurrence import SeedOccurrence


class CachedSeedLookup(SeedLookup):
    """SeedLookup using compact C-level int arrays instead of Python objects.

    All three index tables (word_occurrences, intra_word_seeds, boundary_seeds)
    store their int pairs as interleaved array.array('i') values:
        [val_a0, val_b0, val_a1, val_b1, ...]

    This keeps the full 32MB corpus index under ~500MB of RAM.
    """

    def __init__(
        self,
        q: int,
        word_occurrences: dict[int, array],
        intra_word_seeds: dict[str, array],
        boundary_seeds: dict[str, array],
    ) -> None:
        self.q = q
        self._word_occurrences = word_occurrences
        self._intra_word_seeds = intra_word_seeds
        self._boundary_seeds = boundary_seeds

    # -- SeedLookup interface --------------------------------------------------

    def frequency(self, seed: str) -> int:
        """Return the total number of corpus positions this seed appears at."""
        if " " in seed:
            arr = self._boundary_seeds.get(seed)
            return 0 if arr is None else len(arr) // 2

        total = 0
        intra = self._intra_word_seeds.get(seed)
        if intra:
            for i in range(0, len(intra), 2):
                word_id = intra[i]
                word_arr = self._word_occurrences.get(word_id)
                if word_arr:
                    total += len(word_arr) // 2
        return total

    def occurrences(self, seed: str) -> tuple[SeedOccurrence, ...]:
        """Return absolute corpus positions for the seed.

        SeedOccurrence objects are created here on-the-fly (lazily), so we
        only pay the object cost for the few seeds actually queried, not for
        the millions stored in the index.
        """
        if " " in seed:
            arr = self._boundary_seeds.get(seed)
            if not arr:
                return ()
            return tuple(
                SeedOccurrence(sentence_id=arr[i], position=arr[i + 1])
                for i in range(0, len(arr), 2)
            )

        intra = self._intra_word_seeds.get(seed)
        if not intra:
            return ()
        result: list[SeedOccurrence] = []
        for i in range(0, len(intra), 2):
            word_id = intra[i]
            seed_offset = intra[i + 1]
            word_arr = self._word_occurrences.get(word_id)
            if word_arr:
                for j in range(0, len(word_arr), 2):
                    result.append(
                        SeedOccurrence(
                            sentence_id=word_arr[j],
                            position=word_arr[j + 1] + seed_offset,
                        )
                    )
        return tuple(result)
