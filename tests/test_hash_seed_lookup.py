from src.autocomplete.normalizer import get_word_positions
from src.models.prepared_sentence import PreparedSentence
from src.models.seed_occurrence import SeedOccurrence
from src.structures.hash_seed_lookup import HashSeedLookup


def _sentence(
    sentence_id: int,
    text: str,
    *,
    include_word_positions: bool = True,
) -> PreparedSentence:
    return PreparedSentence(
        sentence_id=sentence_id,
        original_text=text,
        normalized_text=text,
        source_path="archive/example.txt",
        offset=sentence_id + 1,
        word_positions=(
            get_word_positions(text) if include_word_positions else ()
        ),
    )


def test_intra_word_frequency_weights_offsets_and_corpus_occurrences() -> None:
    lookup = HashSeedLookup.build(
        (
            _sentence(1, "banana split"),
            _sentence(2, "banana bread"),
        ),
        q=3,
    )

    assert lookup.frequency("ana") == 4
    assert lookup.occurrences("ana") == (
        SeedOccurrence(1, 1),
        SeedOccurrence(2, 1),
        SeedOccurrence(1, 3),
        SeedOccurrence(2, 3),
    )


def test_boundary_lookup_returns_absolute_full_sentence_positions() -> None:
    lookup = HashSeedLookup.build((_sentence(9, "hello world"),), q=3)

    assert lookup.frequency("lo ") == 1
    assert lookup.occurrences("lo ") == (SeedOccurrence(9, 3),)
    assert lookup.occurrences("o w") == (SeedOccurrence(9, 4),)
    assert lookup.occurrences(" wo") == (SeedOccurrence(9, 5),)


def test_unknown_seed_has_zero_frequency_and_no_occurrences() -> None:
    lookup = HashSeedLookup.build((_sentence(1, "programming"),), q=3)

    assert lookup.frequency("xyz") == 0
    assert lookup.occurrences("xyz") == ()


def test_word_ranges_are_derived_when_preparation_metadata_is_absent() -> None:
    lookup = HashSeedLookup.build(
        (_sentence(4, "programming", include_word_positions=False),),
        q=3,
    )

    assert lookup.occurrences("ogr") == (SeedOccurrence(4, 2),)


def test_index_statistics_count_compact_vocabulary_and_references() -> None:
    lookup = HashSeedLookup.build(
        (
            _sentence(1, "banana split"),
            _sentence(2, "banana bread"),
            _sentence(3, "hello world"),
        ),
        q=3,
    )

    assert lookup.stats.unique_words == 5
    assert lookup.stats.word_occurrences == 6
    assert lookup.stats.intra_word_seed_references == 16
    assert lookup.stats.boundary_occurrences == 9
    assert lookup.stats.intra_word_seed_keys > 0
    assert lookup.stats.boundary_seed_keys > 0
