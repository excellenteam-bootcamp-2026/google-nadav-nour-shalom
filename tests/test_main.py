from src.algorithms.bi_anchor_search_algorithm import BiAnchorSearchAlgorithm
from src.builders.bi_anchor_structure_builder import BiAnchorStructureBuilder
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
