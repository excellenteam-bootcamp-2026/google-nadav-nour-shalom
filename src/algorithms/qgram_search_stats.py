from dataclasses import dataclass


@dataclass(slots=True)
class QGramSearchStats:
    """Optional cumulative work counters for positional Q-Gram search."""

    query_count: int = 0
    query_qgrams: int = 0
    posting_lists_accessed: int = 0
    posting_entries_scanned: int = 0
    candidate_starts_before_dedup: int = 0
    candidate_starts_after_dedup: int = 0
    target_contexts: int = 0
    verifier_calls: int = 0
    fallback_count: int = 0
