from collections import Counter
from itertools import product
import random

from src.algorithms.bi_anchor_search_algorithm import BiAnchorSearchAlgorithm
from src.algorithms.naive_search_algorithm import NaiveSearchAlgorithm
from src.builders.bi_anchor_structure_builder import BiAnchorStructureBuilder
from src.builders.naive_structure_builder import NaiveStructureBuilder
from src.models.match_candidate import MatchCandidate
from src.models.prepared_sentence import PreparedSentence
from src.search_engine import SearchEngine


CURATED_QUERIES = (
    "programming",
    "progrxmming",
    "programing",
    "programxming",
    "xprogramming",
    "programmingx",
    "arogramming",
    "programminx",
    "gramm",
    "lo wo",
    "hello world",
    "xhello world",
    "hello worlx",
    "ello world",
    "hello worl",
    "aaaa",
    "aaaaa",
    "aaaaaaa",
    "abab",
    "ababa",
    "ab ab",
    "the the",
    "the there",
    "prefix",
    "suffix",
    "refix s",
    "cab cab",
    "abcdef",
    "xbcdef",
    "abcxef",
    "abcdex",
    "bcdef",
    "abcdefx",
    "ends here",
    "ends her",
    "xends here",
    "zzzzzz",
    "a",
    "aa",
    "",
)


def _sentence(sentence_id: int, text: str) -> PreparedSentence:
    return PreparedSentence(
        sentence_id=sentence_id,
        original_text=text,
        normalized_text=text,
        source_path="differential.txt",
        offset=sentence_id + 1,
    )


def _canonical(matches: list[MatchCandidate]) -> Counter:
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


def _engines(
    sentence_texts: tuple[str, ...],
    q: int,
) -> tuple[SearchEngine, SearchEngine]:
    sentences = tuple(
        _sentence(sentence_id, text)
        for sentence_id, text in enumerate(sentence_texts)
    )
    naive = SearchEngine(NaiveStructureBuilder(), NaiveSearchAlgorithm())
    bi_anchor = SearchEngine(
        BiAnchorStructureBuilder(q=q),
        BiAnchorSearchAlgorithm(),
    )
    naive.build(sentences)
    bi_anchor.build(sentences)
    return naive, bi_anchor


def _assert_queries_match(
    sentence_texts: tuple[str, ...],
    queries: tuple[str, ...],
    *,
    q: int,
) -> None:
    naive, bi_anchor = _engines(sentence_texts, q)
    for query in queries:
        expected = _canonical(naive.search(query))
        actual = _canonical(bi_anchor.search(query))
        false_negatives = expected - actual
        false_positives = actual - expected
        assert not false_negatives and not false_positives, (
            f"query={query!r}, false_negatives={false_negatives}, "
            f"false_positives={false_positives}"
        )


def test_curated_raw_candidates_match_naive() -> None:
    corpus = (
        "programming in python",
        "hello world",
        "aaaaaa",
        "ab ababa",
        "the the there",
        "prefix suffix",
        "cab cab",
        "ends here",
        "abcdef",
        "short",
    )

    _assert_queries_match(corpus, CURATED_QUERIES, q=3)


def test_fixed_seed_random_differential() -> None:
    generator = random.Random(20260812)
    alphabet = "ab "
    corpus = tuple(
        "".join(generator.choice(alphabet) for _ in range(generator.randrange(13)))
        for _ in range(100)
    )
    queries = tuple(
        "".join(generator.choice(alphabet) for _ in range(generator.randrange(11)))
        for _ in range(250)
    )

    _assert_queries_match(corpus, queries, q=2)


def test_exhaustive_small_alphabet_differential() -> None:
    alphabet = "ab "
    corpus = tuple(
        "".join(characters)
        for length in range(5)
        for characters in product(alphabet, repeat=length)
    )
    queries = tuple(
        "".join(characters)
        for length in range(6)
        for characters in product(alphabet, repeat=length)
    )

    assert len(corpus) == 121
    assert len(queries) == 364
    _assert_queries_match(corpus, queries, q=2)
