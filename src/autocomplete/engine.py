from src.autocomplete.auto_completer import get_best_k_completions, init_completions
from src.autocomplete.scoring import calculate_score
from src.models.match_candidate import MatchCandidate


def print_raw_candidates(candidates: list[MatchCandidate]) -> None:
    """Print every raw MatchCandidate exactly as search returned it.

    No scoring order, no sentence-level deduplication: the same sentence
    appears once per matching position and once per valid one-edit
    interpretation. This is a diagnostic view of the search output that
    sits before the completion layer.
    """
    print(f"--- raw candidates: {len(candidates)} ---")

    for number, candidate in enumerate(candidates, start=1):
        sentence = candidate.sentence
        print(
            f"[{number}] sentence={sentence.sentence_id} "
            f"start={candidate.match_start} "
            f"edit={candidate.edit_type.value} "
            f"edit_index={candidate.edit_index} "
            f"correct={candidate.correct_characters} "
            f"score={calculate_score(candidate)}"
        )
        print(f"    {sentence.original_text}")
        print(f"    ({sentence.source_path}, line {sentence.offset})")

    print("--- end of raw candidates ---")


RESET_COMMAND = "#"


def run(search_engine, debug: bool = False) -> None:
    """Main loop of the online autocomplete system.

    The prefix accumulates across inputs: each line the user types is
    appended to the sentence built so far, so the suggestions narrow as
    they keep typing. Entering ``#`` on its own discards the accumulated
    prefix and starts a fresh sentence.

    For each user query:
      1. Normalize the accumulated prefix.
      2. Search for matching candidates.
      3. Rank and deduplicate via get_best_k_completions.
      4. Print the top results to the user.

    Args:
        search_engine: A built SearchAlgorithm instance ready to accept
                       normalized queries and return MatchCandidate lists.
        debug: When True, dump every raw MatchCandidate before ranking.
    """
    print("System ready. Start typing to search (press Ctrl+C to exit):")
    print(f"Enter {RESET_COMMAND} on its own line to start a new sentence.")

    init_completions(
        search_engine,
        on_candidates=print_raw_candidates if debug else None,
    )
    prefix_parts: list[str] = []

    while True:
        try:
            entered = input(">> ")

            # Step 1b: '#' resets to a fresh sentence/prefix state. This is
            # checked before normalization, which would strip '#' entirely.
            if entered.strip() == RESET_COMMAND:
                prefix_parts.clear()
                print("Starting a new sentence.")
                continue

            if not entered.strip():
                continue  # Skip empty or whitespace-only input

            prefix_parts.append(entered.strip())
            query = " ".join(prefix_parts)
            print(f"Current sentence: {query}")

            # Steps 2-7: normalize, search, score, rank, top 5.
            results = get_best_k_completions(query)

            if not results:
                print("No results found.")
                continue

            for i, result in enumerate(results, start=1):
                print(
                    f"{i}. {result.completed_sentence} "
                    f"({result.source_text}, line {result.offset}) "
                    f"[score: {result.score}]"
                )

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
