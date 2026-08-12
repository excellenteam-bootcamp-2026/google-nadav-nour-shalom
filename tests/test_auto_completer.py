"""Tests for the public prefix-based entry point (spec signature)."""
import inspect

import pytest

from src.algorithms.naive_search_algorithm import NaiveSearchAlgorithm
from src.autocomplete import auto_completer
from src.autocomplete.auto_complete_data import AutoCompleteData
from src.autocomplete.auto_completer import (
    AutoCompleter,
    get_best_k_completions,
    init_completions,
)
from src.autocomplete.normalizer import normalize_text
from src.builders.naive_structure_builder import NaiveStructureBuilder
from src.models.prepared_sentence import PreparedSentence
from src.search_engine import SearchEngine

HAMLET = "To be, or not to be: that is the question!"


def _engine(*rows: tuple[str, str, int]) -> SearchEngine:
    """Build a search engine over (text, source_path, offset) rows."""
    prepared = [
        PreparedSentence(
            sentence_id=index,
            original_text=text,
            normalized_text=normalize_text(text),
            source_path=source_path,
            offset=offset,
        )
        for index, (text, source_path, offset) in enumerate(rows)
    ]
    engine = SearchEngine(
        builder=NaiveStructureBuilder(),
        algorithm=NaiveSearchAlgorithm(),
    )
    engine.build(prepared)
    return engine


@pytest.fixture(autouse=True)
def _reset_singleton():
    """Keep the module-level engine from leaking between tests."""
    auto_completer._default_completer = None
    yield
    auto_completer._default_completer = None


def test_module_level_function_has_the_specified_signature():
    """The spec requires a module-level get_best_k_completions(prefix)."""
    assert inspect.isfunction(get_best_k_completions)

    signature = inspect.signature(get_best_k_completions)
    parameters = list(signature.parameters.values())

    assert parameters[0].name == "prefix"
    assert parameters[0].annotation is str
    assert signature.return_annotation == list[AutoCompleteData]


def test_module_level_function_returns_results_end_to_end():
    """A raw prefix must flow through normalize -> search -> rank."""
    init_completions(_engine((HAMLET, "hamlet.txt", 42)))

    results = get_best_k_completions("to be or not")

    assert len(results) == 1
    assert isinstance(results[0], AutoCompleteData)
    assert results[0].completed_sentence == HAMLET
    assert results[0].source_text == "hamlet.txt"
    assert results[0].offset == 42
    assert results[0].score == 24


def test_module_level_function_normalizes_the_prefix():
    """Casing, punctuation and spacing are not required from the user."""
    init_completions(_engine((HAMLET, "hamlet.txt", 42)))

    assert get_best_k_completions("TO   BE,  or NOT")[0].completed_sentence == HAMLET


def test_module_level_function_respects_k():
    """k caps the number of returned completions."""
    init_completions(
        _engine(*[(f"shared prefix {i}", "a.txt", i) for i in range(9)])
    )

    assert len(get_best_k_completions("shared prefix")) == 5
    assert len(get_best_k_completions("shared prefix", k=2)) == 2


def test_module_level_function_before_init_raises():
    """Calling before init_completions must fail loudly, not silently."""
    with pytest.raises(RuntimeError, match="init_completions"):
        get_best_k_completions("anything")


def test_init_completions_returns_the_backing_completer():
    """init_completions hands back the AutoCompleter it installed."""
    completer = init_completions(_engine((HAMLET, "hamlet.txt", 42)))

    assert isinstance(completer, AutoCompleter)
    assert auto_completer._default_completer is completer


def test_class_and_module_level_paths_agree():
    """The explicit wrapper and the global must produce identical results."""
    engine = _engine((HAMLET, "hamlet.txt", 42))
    init_completions(engine)

    explicit = AutoCompleter(engine).get_best_k_completions("to be or not")
    via_global = get_best_k_completions("to be or not")

    assert explicit == via_global


def test_empty_and_punctuation_only_prefixes_return_nothing():
    """A prefix that normalizes away must not match every sentence."""
    init_completions(_engine((HAMLET, "hamlet.txt", 42)))

    assert get_best_k_completions("   ") == []
    assert get_best_k_completions("!!!") == []


def test_diagnostic_hook_sees_raw_candidates():
    """on_candidates receives the unranked candidate list."""
    seen: list[int] = []
    init_completions(
        _engine((HAMLET, "hamlet.txt", 42)),
        on_candidates=lambda candidates: seen.append(len(candidates)),
    )

    get_best_k_completions("to be")

    assert seen and seen[0] > 0
