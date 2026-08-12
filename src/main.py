import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Allow running this file directly (python src/main.py) and as a module
# (python -m src.main) by making the project root importable either way.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.algorithms.qgram_trie_search_algorithm import QGramTrieSearchAlgorithm  # noqa: E402
from src.autocomplete import DataPreparer  # noqa: E402
from src.autocomplete.engine import run  # noqa: E402


def main() -> None:
    source = PROJECT_ROOT / "data" / "Archive.zip"

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

    search_engine = QGramTrieSearchAlgorithm()
    search_engine.build(prepared_sentences)
    print("Search engine is ready.")

    run(search_engine)


if __name__ == "__main__":
    main()
