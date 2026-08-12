"""End-to-end conformance tests against the Stage A specification.

These run the whole online pipeline — normalize, search, score, rank —
rather than any single layer, so a regression anywhere between the user's
keystrokes and the printed results is caught here.
"""
import pytest

from src.algorithms.naive_search_algorithm import NaiveSearchAlgorithm
from src.autocomplete.auto_completer import AutoCompleter
from src.autocomplete.auto_complete_data import AutoCompleteData
from src.autocomplete.normalizer import normalize_text
from src.builders.naive_structure_builder import NaiveStructureBuilder
from src.models.prepared_sentence import PreparedSentence
from src.search_engine import SearchEngine

# The sentence used by every worked example in the specification.
HAMLET = "להיות או לא להיות, זאת השאלה"


def _completer(*sentences: tuple[str, str, int]) -> AutoCompleter:
    """Build a full pipeline over the given (text, source_path, offset) rows."""
    prepared = [
        PreparedSentence(
            sentence_id=index,
            original_text=text,
            normalized_text=normalize_text(text),
            source_path=source_path,
            offset=offset,
        )
        for index, (text, source_path, offset) in enumerate(sentences)
    ]
    engine = SearchEngine(
        builder=NaiveStructureBuilder(),
        algorithm=NaiveSearchAlgorithm(),
    )
    engine.build(prepared)
    return AutoCompleter(engine)


@pytest.fixture
def hamlet() -> AutoCompleter:
    return _completer((HAMLET, "hamlet.txt", 1))


# --- Specification section 2: the five worked examples -------------------

@pytest.mark.parametrize(
    ("query", "expected_score", "reason"),
    [
        ("להיות או לא",  22, "exact substring, 11 correct characters"),
        ("להיות או לו",  19, "replacement at position 10 (4+) -> 20 - 1"),
        ("להיןת או לא",  18, "replacement at position 3 -> 20 - 2"),
        ("להייות או לא", 18, "deletion of extra char at position 3 -> 22 - 4"),
        ("להות או לא",   14, "insertion of missing char at position 2 -> 20 - 6"),
    ],
)
def test_specification_worked_examples(hamlet, query, expected_score, reason):
    """Every score printed in the specification must be reproduced exactly."""
    results = hamlet.get_best_k_completions(query)

    assert results, f"no match found for {query!r} ({reason})"
    assert results[0].completed_sentence == HAMLET
    assert results[0].score == expected_score, reason


# --- Specification section 1: one correction, anywhere in the sentence ---

def test_match_at_start_middle_and_end_of_sentence():
    """A query may match at the start, the middle, or the end."""
    completer = _completer(("the quick brown fox jumps", "a.txt", 1))

    for query in ("the quick", "brown fox", "jumps"):
        assert completer.get_best_k_completions(query), query


def test_two_corrections_are_rejected():
    """More than one correction must not produce a match."""
    completer = _completer(("python programming", "a.txt", 1))

    assert completer.get_best_k_completions("pxthxn") == []


# --- Specification section 3: normalization --------------------------------

@pytest.mark.parametrize(
    "query",
    [
        "TO BE OR NOT",          # case-insensitive
        "to be, or not",         # punctuation not required
        "to    be   or  not",    # runs of whitespace collapse
        "   to be or not   ",    # leading/trailing whitespace trimmed
        "To Be,   OR---NOT",     # all of the above at once
    ],
)
def test_normalization_rules(query):
    """The user need not type exact casing, punctuation, or spacing."""
    original = "To be, or not to be: that is the question!"
    completer = _completer((original, "hamlet.txt", 42))

    results = completer.get_best_k_completions(query)

    assert results, query
    # Section 3: the ORIGINAL text is what gets returned, punctuation intact.
    assert results[0].completed_sentence == original


def test_unicode_punctuation_is_ignored_too():
    """Curly quotes, dashes and ellipses are punctuation the user may skip."""
    original = "it’s a “quoted” phrase — really…"
    completer = _completer((original, "a.txt", 1))

    results = completer.get_best_k_completions("its a quoted phrase really")

    assert results
    assert results[0].completed_sentence == original


# --- Specification section 4: ranking --------------------------------------

def test_returns_at_most_five_completions():
    """At most the best 5 completions are returned."""
    completer = _completer(
        *[(f"shared prefix variant {index}", "a.txt", index) for index in range(9)]
    )

    assert len(completer.get_best_k_completions("shared prefix")) == 5


def test_sorted_by_score_descending_then_alphabetically():
    """Higher scores first; equal scores fall back to alphabetical order."""
    completer = _completer(
        ("zebra tail", "a.txt", 1),
        ("apple tail", "a.txt", 2),
        ("mango tail", "a.txt", 3),
        ("the tail exactly here", "a.txt", 4),
    )

    results = completer.get_best_k_completions("tail")
    scores = [result.score for result in results]

    assert scores == sorted(scores, reverse=True)
    tied = [r.completed_sentence for r in results if r.score == scores[0]]
    assert tied == sorted(tied)


# --- Specification section 5: the shape of each result ---------------------

def test_result_carries_sentence_source_offset_and_score():
    """Each result must expose the sentence, source file, offset, and score."""
    completer = _completer(("To be, or not to be", "rfc/hamlet.txt", 137))

    result = completer.get_best_k_completions("to be or not")[0]

    assert isinstance(result, AutoCompleteData)
    assert result.completed_sentence == "To be, or not to be"
    assert result.source_text == "rfc/hamlet.txt"
    assert result.offset == 137
    assert result.score == 24


def test_empty_prefix_returns_no_results():
    """A prefix that normalizes to nothing must not match everything."""
    completer = _completer(("anything at all", "a.txt", 1))

    assert completer.get_best_k_completions("   ") == []
    assert completer.get_best_k_completions("!!!") == []
