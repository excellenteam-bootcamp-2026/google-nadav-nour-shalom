from dataclasses import FrozenInstanceError

import pytest

from src.contracts.seed_lookup import SeedLookup
from src.models.candidate_context import CandidateContext
from src.models.seed_candidate import SeedCandidate
from src.models.seed_occurrence import SeedOccurrence


def test_seed_candidate_identity_includes_query_range() -> None:
    first = SeedCandidate("aa", 0, 2, 7)
    second = SeedCandidate("aa", 2, 4, 7)

    assert first != second
    assert {first, second} == {first, second}


def test_identical_candidate_contexts_deduplicate_without_shift_state() -> None:
    first = CandidateContext(sentence_id=4, start=9, target_length=6)
    duplicate = CandidateContext(sentence_id=4, start=9, target_length=6)

    assert {first, duplicate} == {first}
    assert not hasattr(first, "shift")


def test_models_are_immutable() -> None:
    seed = SeedCandidate("abc", 0, 3, 2)
    context = CandidateContext(1, 0, 3)
    occurrence = SeedOccurrence(1, 5)

    with pytest.raises(FrozenInstanceError):
        seed.frequency = 10
    with pytest.raises(FrozenInstanceError):
        context.start = 1
    with pytest.raises(FrozenInstanceError):
        occurrence.position = 6


def test_seed_lookup_is_an_abstract_two_operation_contract() -> None:
    assert SeedLookup.__abstractmethods__ == frozenset(
        {"frequency", "occurrences"}
    )
    with pytest.raises(TypeError):
        SeedLookup()
