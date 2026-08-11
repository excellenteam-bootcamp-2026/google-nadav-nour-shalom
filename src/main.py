from pathlib import Path

from src.autocomplete import DataPreparer


def main() -> None:
    source = Path("data/Archive.zip")

    print("Loading the files and preparing the system...")

    preparer = DataPreparer()

    try:
        prepared_sentences = preparer.prepare(source)
    except (FileNotFoundError, ValueError) as error:
        print(error)
        return

    stats = preparer.loader.stats

    print(f"Loaded files: {stats.loaded_files}")
    print(f"Duplicate files skipped: {stats.skipped_duplicates}")
    print(f"Invalid files skipped: {stats.skipped_invalid}")
    print(f"Prepared sentences: {len(prepared_sentences)}")
    print("Person 1 data preparation is ready.")

    # Small preview only - not part of the search logic.
    for sentence in prepared_sentences[:3]:
        print(
            f"- {sentence.original_text} "
            f"({sentence.source_path} {sentence.offset})"
        )


if __name__ == "__main__":
    main()
