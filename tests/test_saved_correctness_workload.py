from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path

from benchmark.code.archive3_benchmark import load_queries
from src.algorithms.bi_anchor_search_algorithm import BiAnchorSearchAlgorithm
from src.algorithms.naive_search_algorithm import NaiveSearchAlgorithm
from src.algorithms.qgram_search_algorithm import QGramSearchAlgorithm
from src.algorithms.qgram_trie_search_algorithm import QGramTrieSearchAlgorithm
from src.builders.bi_anchor_structure_builder import BiAnchorStructureBuilder
from src.builders.naive_structure_builder import NaiveStructureBuilder
from src.builders.qgram_structure_builder import QGramStructureBuilder
from src.models.match_candidate import MatchCandidate
from src.models.prepared_sentence import PreparedSentence
from src.search_engine import SearchEngine


FIXTURE_PATH = Path("tests/fixtures/search_correctness_queries.json")
REQUIRED_CATEGORIES = {
    "empty",
    "exact",
    "replacement",
    "insertion",
    "deletion",
    "whole_word",
    "inside_word",
    "cross_word",
    "repeated_characters",
    "repeated_qgrams",
    "query_beginning",
    "query_end",
    "sentence_boundary",
    "no_match",
    "many_match",
    "ambiguous_edit",
}


def _payload() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _corpus(payload: dict[str, object]) -> tuple[PreparedSentence, ...]:
    return tuple(PreparedSentence(**item) for item in payload["corpus"])


def _canonical(matches: list[MatchCandidate]) -> Counter[tuple[object, ...]]:
    return Counter(
        (
            match.sentence.sentence_id,
            match.match_start,
            match.edit_type,
            match.edit_index,
            match.correct_characters,
        )
        for match in matches
    )


def _engine(builder, algorithm, corpus) -> SearchEngine:
    engine = SearchEngine(builder, algorithm)
    engine.build(corpus)
    return engine


def test_saved_correctness_fixture_identity_and_coverage() -> None:
    payload = _payload()
    queries = load_queries(FIXTURE_PATH)
    canonical_corpus = json.dumps(
        payload["corpus"],
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    categories = {
        category for query in queries for category in query.categories
    }
    lengths = {query.query_length for query in queries}
    file_sha = hashlib.sha256(FIXTURE_PATH.read_bytes()).hexdigest()

    assert payload["fixture_version"] == 1
    assert payload["random_seed_used_to_create_it"] is None
    assert payload["corpus_fixture_version"] == 1
    assert payload["query_count"] == len(queries)
    assert payload["corpus_sha256"] == hashlib.sha256(canonical_corpus).hexdigest()
    assert len({query.query_id for query in queries}) == len(queries)
    assert set(range(0, 7)) <= lengths
    assert any(length > 6 for length in lengths)
    assert REQUIRED_CATEGORIES <= categories

    print(f"Saved correctness workload: {FIXTURE_PATH.resolve()}")
    print(f"Queries: {len(queries)}")
    print(f"SHA-256: {file_sha}")


def test_saved_workload_qgram_and_bi_anchor_match_naive_raw_results() -> None:
    payload = _payload()
    corpus = _corpus(payload)
    queries = load_queries(FIXTURE_PATH)
    naive = _engine(NaiveStructureBuilder(), NaiveSearchAlgorithm(), corpus)
    implementations = {
        "Q-Gram + Verifier": _engine(
            QGramStructureBuilder(q=3),
            QGramSearchAlgorithm(),
            corpus,
        ),
        "Selective Bi-Anchor": _engine(
            BiAnchorStructureBuilder(q=3),
            BiAnchorSearchAlgorithm(),
            corpus,
        ),
    }
    totals = {
        name: {"mismatch": 0, "false_negatives": 0, "false_positives": 0}
        for name in implementations
    }

    for query in queries:
        expected = _canonical(naive.search(query.normalized_query))
        for name, implementation in implementations.items():
            actual = _canonical(implementation.search(query.normalized_query))
            false_negatives = expected - actual
            false_positives = actual - expected
            totals[name]["mismatch"] += int(bool(false_negatives or false_positives))
            totals[name]["false_negatives"] += sum(false_negatives.values())
            totals[name]["false_positives"] += sum(false_positives.values())

    for name, values in totals.items():
        print(
            f"{name}: queries={len(queries)} "
            f"mismatch={values['mismatch']} "
            f"FN={values['false_negatives']} "
            f"FP={values['false_positives']}"
        )
        assert values == {
            "mismatch": 0,
            "false_negatives": 0,
            "false_positives": 0,
        }


def test_tree_known_non_equivalent_categories_remain_visible() -> None:
    payload = _payload()
    corpus = _corpus(payload)
    queries = {query.query_id: query for query in load_queries(FIXTURE_PATH)}
    naive = _engine(NaiveStructureBuilder(), NaiveSearchAlgorithm(), corpus)
    tree = QGramTrieSearchAlgorithm()
    tree.build(corpus)

    for query_id in (
        "inside-word",
        "cross-word",
        "replacement-no-shared-qgram",
        "ambiguous-insertion",
    ):
        query = queries[query_id].normalized_query
        assert _canonical(tree.search(query)) != _canonical(naive.search(query))


def test_tree_large_result_cap_is_exposed() -> None:
    corpus = tuple(
        PreparedSentence(
            sentence_id=index,
            original_text="alpha",
            normalized_text="alpha",
            source_path="many.txt",
            offset=index + 1,
        )
        for index in range(2001)
    )
    naive = _engine(NaiveStructureBuilder(), NaiveSearchAlgorithm(), corpus)
    tree = QGramTrieSearchAlgorithm()
    tree.build(corpus)

    tree_matches = tree.search("alpha")
    naive_matches = naive.search("alpha")

    assert len(tree_matches) == 2000
    assert len(naive_matches) > 2000
    assert _canonical(tree_matches) != _canonical(naive_matches)
