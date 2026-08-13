from unittest.mock import patch

from src.algorithms.bi_anchor_search_algorithm import BiAnchorSearchAlgorithm
from src.builders.bi_anchor_structure_builder import BiAnchorStructureBuilder
from src.cache.cached_seed_lookup import CachedSeedLookup
from src import main as main_module
from src.main import build_default_search_engine
from src.models.prepared_sentence import PreparedSentence


def test_default_runtime_engine_uses_bi_anchor_after_correctness_gate() -> None:
    sentence = PreparedSentence(
        sentence_id=1,
        original_text="programming",
        normalized_text="programming",
        source_path="example.txt",
        offset=1,
    )

    engine = build_default_search_engine([sentence])

    assert isinstance(engine._builder, BiAnchorStructureBuilder)
    assert isinstance(engine._algorithm, BiAnchorSearchAlgorithm)
    assert engine.search("programming")


def test_cached_runtime_assembles_current_adaptive_structure() -> None:
    """Catch stale cache adapters that omit current Bi-Anchor metadata."""
    sentence = PreparedSentence(
        sentence_id=0,
        original_text="alpha",
        normalized_text="alpha",
        source_path="cached.txt",
        offset=1,
    )
    lookup = CachedSeedLookup(
        q=3,
        word_occurrences={},
        intra_word_seeds={},
        boundary_seeds={},
    )
    received_engines = []

    with (
        patch.object(main_module, "cache_is_valid", return_value=True),
        patch.object(
            main_module,
            "load_cache",
            return_value=([sentence], lookup),
        ),
        patch.object(
            main_module,
            "run",
            side_effect=received_engines.append,
        ),
    ):
        main_module.main()

    assert len(received_engines) == 1
    engine = received_engines[0]
    assert engine._structure.q_values == (3,)
    assert tuple(engine._structure.build_stats.index.per_q) == (3,)
    assert engine.search("a")
