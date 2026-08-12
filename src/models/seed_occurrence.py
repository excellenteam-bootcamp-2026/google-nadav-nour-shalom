from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SeedOccurrence:
    """One seed's absolute position in a normalized corpus sentence."""

    sentence_id: int
    position: int
