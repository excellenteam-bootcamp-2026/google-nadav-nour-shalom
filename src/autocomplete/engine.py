from src.autocomplete.completion import get_best_k_completions
from src.autocomplete.normalizer import normalize_text


def run(search_engine) -> None:
    """Main loop of the online autocomplete system.

    For each user query:
      1. Normalize the raw input.
      2. Search for matching candidates.
      3. Rank and deduplicate via get_best_k_completions.
      4. Print the top results to the user.

    Args:
        search_engine: A built SearchAlgorithm instance ready to accept
                       normalized queries and return MatchCandidate lists.
    """
    print("System ready. Start typing to search (press Ctrl+C to exit):")

    while True:
        try:
            query = input(">> ")

            if not query.strip():
                continue  # Skip empty or whitespace-only input

            normalized = normalize_text(query)             # Step 2: Normalize
            candidates = search_engine.search(normalized)  # Step 3: Search
            results = get_best_k_completions(candidates)   # Steps 4-7: Score, rank, top 5

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
