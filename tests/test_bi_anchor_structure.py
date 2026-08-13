from dataclasses import FrozenInstanceError

import pytest

from src.builders.bi_anchor_structure_builder import BiAnchorStructureBuilder
from src.models.prepared_sentence import PreparedSentence
from src.structures.bi_anchor_search_structure import BiAnchorSearchStructure
from src.structures.hash_seed_lookup import HashSeedLookup


def _sentence(sentence_id: int, text: str) -> PreparedSentence:
    return PreparedSentence(
        sentence_id=sentence_id,
        original_text=text,
        normalized_text=text,
        source_path="archive/example.txt",
        offset=sentence_id + 1,
    )


def test_builder_defaults_to_q_three_and_builds_lookup() -> None:
    sentence = _sentence(4, "programming")

    structure = BiAnchorStructureBuilder().build([sentence])

    assert isinstance(structure, BiAnchorSearchStructure)
    assert isinstance(structure.seed_lookup, HashSeedLookup)
    assert structure.q == 3
    assert structure.sentences == (sentence,)
    assert structure.sentences_by_id[4] is sentence
    assert structure.seed_lookup.occurrences("ogr")[0].position == 2
    assert structure.build_stats.index_build_ns >= 0


def test_builder_accepts_configured_q() -> None:
    structure = BiAnchorStructureBuilder(q=2).build([_sentence(1, "banana")])

    assert structure.q == 2
    assert structure.seed_lookup.frequency("an") == 2


def test_builder_defaults_to_a_single_indexed_q() -> None:
    structure = BiAnchorStructureBuilder(q=3).build([_sentence(1, "banana")])

    assert structure.q_values == (3,)
    assert structure.seed_lookup.q_values == (3,)


def test_builder_indexes_every_configured_q_value() -> None:
    structure = BiAnchorStructureBuilder(q=3, q_values=(1, 2, 3)).build(
        [_sentence(1, "banana")]
    )

    assert structure.q == 3
    assert structure.q_values == (1, 2, 3)
    assert structure.seed_lookup.frequency("a") == 3
    assert structure.seed_lookup.frequency("an") == 2
    assert structure.seed_lookup.frequency("ana") == 2


def test_builder_rejects_a_primary_q_outside_the_indexed_values() -> None:
    with pytest.raises(ValueError, match="q=3"):
        BiAnchorStructureBuilder(q=3, q_values=(1, 2))


def test_builder_rejects_non_positive_q() -> None:
    with pytest.raises(ValueError, match="positive"):
        BiAnchorStructureBuilder(q=0)


def test_builder_rejects_duplicate_sentence_ids() -> None:
    builder = BiAnchorStructureBuilder()

    with pytest.raises(ValueError, match="sentence_id"):
        builder.build([_sentence(2, "first"), _sentence(2, "second")])


def test_structure_is_immutable_data_without_search_operations() -> None:
    structure = BiAnchorStructureBuilder().build([_sentence(1, "hello")])

    assert not hasattr(structure, "search")
    with pytest.raises(FrozenInstanceError):
        structure.q = 4
    with pytest.raises(TypeError):
        structure.sentences_by_id[2] = _sentence(2, "world")
