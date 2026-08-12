"""
Completion layer (Steps 5-7): rank candidates and return the top K results.

Pipeline:
  1. Score every MatchCandidate via calculate_score.
  2. Sort: highest score first; alphabetical on the original text as a tiebreaker.
  3. Deduplicate: keep only the best match per (text, source file, offset).
  4. Take the top K results and wrap each one in AutoCompleteData.
"""

from src.autocomplete.auto_complete_data import AutoCompleteData
from src.autocomplete.scoring import calculate_score
from src.models.match_candidate import MatchCandidate


def get_best_k_completions(
    candidates: list[MatchCandidate],
    k: int = 5,
) -> list[AutoCompleteData]:
    """Score, sort, deduplicate, and return the top K autocomplete results.

    Args:
        candidates: Raw matches returned by the search engine.
        k: Maximum number of results to return (default 5).

    Returns:
        A list of up to k AutoCompleteData objects, ordered best-first.
    """
    # Step 5a: attach a score to every candidate.
    scored = [(candidate, calculate_score(candidate)) for candidate in candidates]

    # Step 5b: sort — highest score first; alphabetical original text as tiebreaker.
    scored.sort(key=lambda pair: (-pair[1], pair[0].sentence.original_text))

    # Steps 6-7: deduplicate by source record, then take the top K.
    #
    # The key is the full identity of the source sentence, not its text
    # alone. Two sentences with identical text in different files (or at
    # different offsets in one file) are genuinely distinct results and
    # must both survive - RFC boilerplate such as "Status of This Memo"
    # appears once per document. Keying on text alone silently dropped
    # them. Because the list is already sorted best-first, this still
    # collapses the several interpretations search returns for the same
    # (sentence, position) match, keeping only the highest scoring one.
    seen: set[tuple[str, str, int]] = set()
    results: list[AutoCompleteData] = []

    for candidate, score in scored:
        sentence = candidate.sentence
        text = sentence.original_text
        key = (text, sentence.source_path, sentence.offset)
        if key in seen:
            continue
        seen.add(key)
        results.append(
            AutoCompleteData(
                completed_sentence=text,
                source_text=candidate.sentence.source_path,
                offset=candidate.sentence.offset,
                score=score,
            )
        )
        if len(results) == k:
            break

    return results
