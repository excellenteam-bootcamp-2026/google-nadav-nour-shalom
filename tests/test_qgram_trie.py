"""
Unit tests for QGramTrieSearchAlgorithm.

Tests cover: exact match, all three edit types, no-match, empty query,
short query fallback, return types, and a correctness comparison against
NaiveSearchAlgorithm using single-word sentences (to avoid cross-word-boundary
differences between the two algorithms).
"""
import pytest

from src.algorithms.naive_search_algorithm import NaiveSearchAlgorithm
from src.algorithms.qgram_trie_search_algorithm import QGramTrieSearchAlgorithm
from src.models.edit_type import EditType
from src.models.match_candidate import MatchCandidate
from src.models.prepared_sentence import PreparedSentence


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_sentence(
    text: str,
    sentence_id: int = 0,
    source: str = "test.txt",
    offset: int = 1,
) -> PreparedSentence:
    return PreparedSentence(
        sentence_id=sentence_id,
        original_text=text,
        normalized_text=text.lower(),
        source_path=source,
        offset=offset,
    )


def _build(texts: list[str]) -> QGramTrieSearchAlgorithm:
    sentences = [_make_sentence(t, i) for i, t in enumerate(texts)]
    engine = QGramTrieSearchAlgorithm()
    engine.build(sentences)
    return engine


# ---------------------------------------------------------------------------
# Basic behaviour
# ---------------------------------------------------------------------------

def test_exact_match():
    """A correctly typed word returns at least one EXACT result."""
    engine = _build(["python programming"])
    results = engine.search("python")
    assert results, "Expected at least one result for exact query"
    assert any(r.edit_type == EditType.EXACT for r in results)


def test_replacement_match():
    """A query with one wrong letter still returns a REPLACEMENT result."""
    engine = _build(["python programming"])
    # "pytxon": 'x' replaces 'h' at index 3
    results = engine.search("pytxon")
    assert results, "Expected results for one-replacement query"
    assert any(r.edit_type == EditType.REPLACEMENT for r in results)


def test_insertion_match():
    """A query missing one letter still returns an INSERTION result."""
    engine = _build(["python programming"])
    # "pyton": missing 'h' (position 3 of 'python')
    results = engine.search("pyton")
    assert results, "Expected results for one-insertion query"
    assert any(r.edit_type == EditType.INSERTION for r in results)


def test_deletion_match():
    """A query with one extra letter still returns a DELETION result."""
    engine = _build(["python programming"])
    # "pythoon": extra 'o' at index 5
    results = engine.search("pythoon")
    assert results, "Expected results for one-deletion query"
    assert any(r.edit_type == EditType.DELETION for r in results)


def test_no_match_for_unrelated_query():
    """A query sharing no Q-grams with any corpus word returns no results."""
    engine = _build(["python programming"])
    results = engine.search("zzzzz")
    assert results == []


def test_empty_query_returns_empty_list():
    """An empty query must return an empty list without errors."""
    engine = _build(["python programming"])
    results = engine.search("")
    assert results == []


def test_results_are_match_candidate_instances():
    """Every returned object must be a MatchCandidate instance."""
    engine = _build(["hello world"])
    results = engine.search("hello")
    assert all(isinstance(r, MatchCandidate) for r in results)


def test_short_query_fallback():
    """Queries shorter than Q=3 characters must still return results."""
    engine = _build(["hi there"])
    results = engine.search("hi")
    assert results, "Expected results for 2-character query (below Q threshold)"


def test_multiple_sentences_matched():
    """A query word that appears in multiple sentences returns candidates from all."""
    engine = _build(["hello world", "hello there", "goodbye world"])
    results = engine.search("hello")
    matched_sentences = {r.sentence.original_text for r in results}
    assert "hello world" in matched_sentences
    assert "hello there" in matched_sentences


# ---------------------------------------------------------------------------
# Correctness vs NaiveSearchAlgorithm
# ---------------------------------------------------------------------------

def test_same_results_as_naive_for_single_word_sentences():
    """For single-word sentences the two algorithms must find identical sentence sets.

    Single-word sentences eliminate cross-word-boundary matches, which is the
    only structural difference between the naive (substring) and Trie (prefix)
    approaches.
    """
    texts = ["python", "programming", "hello", "learning"]
    sentences = [_make_sentence(t, i) for i, t in enumerate(texts)]

    naive = NaiveSearchAlgorithm()
    naive.build(sentences)

    trie = QGramTrieSearchAlgorithm()
    trie.build(sentences)

    # Queries chosen so that at least one trigram survives the edit.
    queries = ["python", "hello", "pythn", "pyton", "pythoon", "learing"]

    for query in queries:
        naive_texts = {r.sentence.original_text for r in naive.search(query)}
        trie_texts = {r.sentence.original_text for r in trie.search(query)}
        assert naive_texts == trie_texts, (
            f"Mismatch for query '{query}': "
            f"naive={sorted(naive_texts)}, trie={sorted(trie_texts)}"
        )
