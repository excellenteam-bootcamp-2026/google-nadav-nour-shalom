"""Main entry point for the autocomplete search engine.

Startup strategy
----------------
1. If a valid Bi-Anchor cache exists (data/bi_anchor.cache), load the full
   search index from it in seconds (skips ZIP parsing, normalization, AND
   index construction).
2. Otherwise, read and prepare sentences from the source archive, build the
   Bi-Anchor index using memory-efficient arrays, save to cache, and proceed.
3. Run the interactive search loop.

Cache invalidation
------------------
A companion fingerprint file stores a hash of the source archive's size and
modification time.  When the source changes the cache is rebuilt automatically.
"""

import sys
from pathlib import Path
from types import MappingProxyType

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.algorithms.bi_anchor_search_algorithm import BiAnchorSearchAlgorithm  # noqa: E402
from src.autocomplete import DataPreparer  # noqa: E402
from src.autocomplete.engine import run  # noqa: E402
from src.cache.bi_anchor_cache import (  # noqa: E402
    build_and_save,
    cache_is_valid,
    load_cache,
    source_fingerprint,
)
from src.search_engine import SearchEngine  # noqa: E402
from src.structures.bi_anchor_search_structure import (  # noqa: E402
    BiAnchorBuildStats,
    BiAnchorSearchStructure,
)
from src.builders.bi_anchor_structure_builder import BiAnchorStructureBuilder  # noqa: E402
from src.structures.hash_seed_lookup import HashSeedIndexStats  # noqa: E402

CACHE_FILE = PROJECT_ROOT / "data" / "bi_anchor.cache"
FINGERPRINT_FILE = PROJECT_ROOT / "data" / "bi_anchor.fingerprint"
SOURCE_FILE = PROJECT_ROOT / "data" / "Archive.zip"
Q = 3


def build_default_search_engine(sentences) -> SearchEngine:
    """Build a Bi-Anchor search engine the standard way (for tests / small data)."""
    engine = SearchEngine(
        builder=BiAnchorStructureBuilder(),
        algorithm=BiAnchorSearchAlgorithm(),
    )
    engine.build(sentences)
    return engine


def main() -> None:
    # ---- Step 1: obtain sentences + seed_lookup ----------------------
    if cache_is_valid(SOURCE_FILE, CACHE_FILE, FINGERPRINT_FILE):
        # Fast path: everything is ready on disk.
        sentences, seed_lookup = load_cache(CACHE_FILE)
    else:
        # Slow path (first run only): read ZIP, build index, save cache.
        print("Reading and preparing data from archive (first run only)...")
        preparer = DataPreparer()

        try:
            sentence_list = preparer.prepare(SOURCE_FILE)
        except (FileNotFoundError, ValueError) as error:
            print(f"Error: {error}")
            return

        stats = preparer.loader.stats
        print(f"Loaded files:              {stats.loaded_files}")
        print(f"Duplicate files skipped:   {stats.skipped_duplicates}")
        print(f"Invalid files skipped:     {stats.skipped_invalid}")
        print(f"Prepared sentences:        {len(sentence_list):,}")

        # Build + save the full Bi-Anchor index using memory-efficient arrays.
        seed_lookup = build_and_save(sentence_list, CACHE_FILE, q=Q)
        FINGERPRINT_FILE.write_text(
            source_fingerprint(SOURCE_FILE), encoding="utf-8",
        )
        sentences = sentence_list

    # ---- Step 2: assemble search engine from loaded data -------------
    print("Assembling search engine...")
    sentences_tuple = tuple(sentences)
    sentences_by_id = {s.sentence_id: s for s in sentences_tuple}

    structure = BiAnchorSearchStructure(
        sentences=sentences_tuple,
        sentences_by_id=MappingProxyType(sentences_by_id),
        seed_lookup=seed_lookup,
        q=Q,
        build_stats=BiAnchorBuildStats(
            index_build_ns=0,
            index=HashSeedIndexStats(
                unique_words=0,
                word_occurrences=0,
                intra_word_seed_keys=len(seed_lookup._intra_word_seeds),
                intra_word_seed_references=0,
                boundary_seed_keys=len(seed_lookup._boundary_seeds),
                boundary_occurrences=0,
            ),
        ),
    )

    algorithm = BiAnchorSearchAlgorithm()
    engine = SearchEngine(
        builder=None,  # type: ignore[arg-type]
        algorithm=algorithm,
    )
    engine._structure = structure  # bypass builder — structure is pre-loaded

    print("Search engine is ready.")

    # ---- Step 3: interactive loop ------------------------------------
    run(engine)


if __name__ == "__main__":
    main()
