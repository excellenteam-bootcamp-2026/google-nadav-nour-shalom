import sys
from collections.abc import Iterable
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Allow running this file directly (python src/main.py) and as a module
# (python -m src.main) by making the project root importable either way.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.algorithms.bi_anchor_search_algorithm import (  # noqa: E402
    BiAnchorSearchAlgorithm,
)
from src.autocomplete import DataPreparer  # noqa: E402
from src.autocomplete.engine import run  # noqa: E402
from src.builders.bi_anchor_structure_builder import (  # noqa: E402
    BiAnchorStructureBuilder,
)
from src.models.prepared_sentence import PreparedSentence  # noqa: E402
from src.search_engine import SearchEngine  # noqa: E402


def build_default_search_engine(
    prepared_sentences: Iterable[PreparedSentence],
) -> SearchEngine:
    """Build the correctness-gated default Bi-Anchor composition."""
    engine = SearchEngine(
        builder=BiAnchorStructureBuilder(),
        algorithm=BiAnchorSearchAlgorithm(),
    )
    engine.build(prepared_sentences)
    return engine


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

    search_engine = build_default_search_engine(prepared_sentences)
    print("Search engine is ready.")

    run(search_engine)


if __name__ == "__main__":
    main()
