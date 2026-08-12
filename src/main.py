from pathlib import Path

from src.algorithms.naive_search_algorithm import NaiveSearchAlgorithm
from src.autocomplete import DataPreparer
from src.autocomplete.engine import run


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

    search_engine = NaiveSearchAlgorithm()
    search_engine.build(prepared_sentences)
    print("Search engine is ready.")

    run(search_engine)


if __name__ == "__main__":
    main()
