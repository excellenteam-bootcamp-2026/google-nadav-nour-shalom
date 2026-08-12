from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CandidateContext:
    """Identity of one bounded target slice awaiting verification."""

    sentence_id: int
    start: int
    target_length: int
