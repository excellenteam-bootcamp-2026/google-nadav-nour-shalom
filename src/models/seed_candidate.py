from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SeedCandidate:
    """One q-length seed occurrence at a specific query range."""

    text: str
    query_start: int
    query_end: int
    frequency: int
