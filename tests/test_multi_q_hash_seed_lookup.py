"""Multi-q seed indexing behaviour of the shared hash lookup.

The `SeedLookup` contract infers q from ``len(seed)``. These tests pin the
smallest cohesive extension of that contract: one lookup may hold several
q-sized indexes over one shared word-occurrence table.
"""

import pytest

from src.autocomplete.normalizer import get_word_positions
from src.models.prepared_sentence import PreparedSentence
from src.models.seed_occurrence import SeedOccurrence
from src.structures.hash_seed_lookup import HashSeedLookup


def _sentence(sentence_id: int, text: str) -> PreparedSentence:
    return PreparedSentence(
        sentence_id=sentence_id,
        original_text=text,
        normalized_text=text,
        source_path="archive/example.txt",
        offset=sentence_id + 1,
        word_positions=get_word_positions(text),
    )


CORPUS = (
    _sentence(1, "banana split"),
    _sentence(2, "banana bread"),
    _sentence(3, "hello world"),
)


def test_single_q_build_reports_only_that_q() -> None:
    lookup = HashSeedLookup.build(CORPUS, q=3)

    assert lookup.q_values == (3,)


def test_multi_q_build_serves_every_configured_length() -> None:
    lookup = HashSeedLookup.build_multi(CORPUS, (1, 2, 3))

    assert lookup.q_values == (1, 2, 3)
    # "banana" holds three 'a' in two sentences, "bread" one more.
    assert lookup.frequency("a") == 7
    assert lookup.frequency("an") == 4
    assert lookup.frequency("ana") == 4


def test_multi_q_occurrences_match_dedicated_single_q_indexes() -> None:
    multi = HashSeedLookup.build_multi(CORPUS, (1, 2, 3))

    for q in (1, 2, 3):
        single = HashSeedLookup.build(CORPUS, q=q)
        seeds = {
            sentence.normalized_text[start : start + q]
            for sentence in CORPUS
            for start in range(len(sentence.normalized_text) - q + 1)
        }
        for seed in sorted(seeds):
            assert multi.occurrences(seed) == single.occurrences(seed), seed
            assert multi.frequency(seed) == single.frequency(seed), seed


def test_multi_q_serves_boundary_seeds_for_every_length() -> None:
    lookup = HashSeedLookup.build_multi((_sentence(9, "hello world"),), (1, 2, 3))

    assert lookup.occurrences(" ") == (SeedOccurrence(9, 5),)
    assert lookup.occurrences("o ") == (SeedOccurrence(9, 4),)
    assert lookup.occurrences("lo ") == (SeedOccurrence(9, 3),)


def test_unindexed_seed_length_is_rejected_instead_of_reported_as_absent() -> None:
    """A silent zero would let the caller treat an unbuilt q as "no matches"."""
    lookup = HashSeedLookup.build_multi(CORPUS, (2, 3))

    with pytest.raises(ValueError, match="q=1"):
        lookup.frequency("a")
    with pytest.raises(ValueError, match="q=4"):
        lookup.occurrences("abcd")


def test_multi_q_shares_one_word_occurrence_table() -> None:
    lookup = HashSeedLookup.build_multi(CORPUS, (1, 2, 3))

    assert lookup.stats.unique_words == 5
    assert lookup.stats.word_occurrences == 6


def test_stats_expose_per_q_index_sizes() -> None:
    lookup = HashSeedLookup.build_multi(CORPUS, (2, 3))
    single_two = HashSeedLookup.build(CORPUS, q=2)
    single_three = HashSeedLookup.build(CORPUS, q=3)

    assert set(lookup.stats.per_q) == {2, 3}
    assert (
        lookup.stats.per_q[3].intra_word_seed_references
        == single_three.stats.per_q[3].intra_word_seed_references
    )
    assert lookup.stats.intra_word_seed_references == (
        single_two.stats.intra_word_seed_references
        + single_three.stats.intra_word_seed_references
    )


def test_indexed_seeds_expose_the_keys_of_one_q_without_private_access() -> None:
    lookup = HashSeedLookup.build_multi((_sentence(9, "hello world"),), (1, 2))

    assert set(lookup.indexed_seeds(1)) == set("helo wrd")
    assert "lo " not in set(lookup.indexed_seeds(2))
    assert {"he", "lo", "o ", " w"} <= set(lookup.indexed_seeds(2))

    with pytest.raises(ValueError, match="q=3"):
        lookup.indexed_seeds(3)


def test_build_multi_rejects_empty_or_non_positive_q_values() -> None:
    with pytest.raises(ValueError, match="q must be positive"):
        HashSeedLookup.build_multi(CORPUS, (0, 2))
    with pytest.raises(ValueError, match="At least one q"):
        HashSeedLookup.build_multi(CORPUS, ())
