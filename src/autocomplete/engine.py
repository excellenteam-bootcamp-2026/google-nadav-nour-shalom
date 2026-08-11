def run(prepared_sentences) -> None:
    """
    Main loop of the online autocomplete system.

    Receives raw user queries one at a time, skips empty input,
    and will progressively delegate to normalization, search,
    scoring, and ranking in later steps.

    Args:
        prepared_sentences: List of PreparedSentence objects built
                            by the offline data preparation stage.
    """
    print("System ready. Start typing to search (press Ctrl+C to exit):")

    while True:
        try:
            query = input(">> ")

            if not query.strip():
                continue  # Skip empty or whitespace-only input

            # Step 2 (Normalize) and beyond will be added here.
            print(f"[DEBUG] Received query: '{query}'")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
