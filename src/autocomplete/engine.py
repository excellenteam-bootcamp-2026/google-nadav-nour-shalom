from src.autocomplete.normalizer import normalize_text
from src.autocomplete.scoring import calculate_score


def run(search_engine) -> None:
    """
    Main loop of the online autocomplete system.

    Normalizes each user query and delegates to the search engine.
    Scoring and ranking will be added in the next steps.

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

            normalized = normalize_text(query)            # Step 2: Normalize
            candidates = search_engine.search(normalized)  # Step 3: Search

            # Step 4: Score every candidate
            scored = [(c, calculate_score(c)) for c in candidates]
            top = max(scored, key=lambda x: x[1])[1] if scored else 0
            print(f"[DEBUG] {len(scored)} candidates, top score: {top}")  # Temporary

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
