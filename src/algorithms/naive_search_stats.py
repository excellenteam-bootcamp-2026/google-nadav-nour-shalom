from dataclasses import dataclass


@dataclass(slots=True)
class NaiveSearchStats:
    """Optional cumulative instrumentation for exhaustive search."""

    query_count: int = 0
    verifier_calls: int = 0
