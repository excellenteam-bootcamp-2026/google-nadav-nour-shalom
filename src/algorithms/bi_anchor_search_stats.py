from dataclasses import dataclass, field

from src.models.seed_candidate import SeedCandidate


@dataclass(slots=True)
class BiAnchorSearchStats:
    """Optional cumulative instrumentation for search evaluation."""

    query_count: int = 0
    anchored_query_count: int = 0
    fallback_count: int = 0
    zero_frequency_returns: int = 0
    seed_occurrences_expanded: int = 0
    candidate_contexts_generated: int = 0
    candidate_contexts_after_dedup: int = 0
    verifier_calls: int = 0
    selected_seed_frequency_sum: int = 0
    last_selected_seeds: tuple[SeedCandidate, SeedCandidate] | None = None
    last_selected_q: int | None = None
    last_pair_cost_by_q: dict[int, int] = field(default_factory=dict)
    selected_q_counts: dict[int, int] = field(default_factory=dict)
    q_candidates_evaluated: int = 0
