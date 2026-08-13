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
    q_values: tuple[int, ...] | None = None,
) -> tuple[SearchEngine, SearchEngine]:
    sentences = tuple(
        _sentence(sentence_id, text)
        for sentence_id, text in enumerate(sentence_texts)
    )
    naive = SearchEngine(NaiveStructureBuilder(), NaiveSearchAlgorithm())
    bi_anchor = SearchEngine(
        BiAnchorStructureBuilder(q=q, q_values=q_values),
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
    q_values: tuple[int, ...] | None = None,
) -> None:
    naive, bi_anchor = _engines(sentence_texts, q, q_values)
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


SHORT_QUERY_CORPUS = (
    "the fastest test of the tested system",
    "testing a short query path",
    "a test",
    "unrelated content here",
    "aaaa bbbb",
    "ab ab ab",
    "hello world",
    "banana bread and banana split",
    "x",
    "zz",
)


def _short_query_lengths(length: int) -> tuple[str, ...]:
    """Every corpus substring of one length, plus one-edit neighbours."""
    substrings = {
        text[start : start + length]
        for sentence in SHORT_QUERY_CORPUS
        for text in (sentence,)
        for start in range(len(text) - length + 1)
    }
    mutated: set[str] = set()
    for text in substrings:
        for index in range(len(text)):
            mutated.add(text[:index] + "q" + text[index + 1 :])
            mutated.add(text[:index] + text[index + 1 :])
            mutated.add(text[:index] + "e" + text[index:])
    return tuple(sorted(substrings | mutated | {"q" * length}))


def test_adaptive_short_query_differential_lengths_one_to_six() -> None:
    """Hard gate: adaptive multi-q must equal Naive for every length 1-6."""
    for length in range(1, 7):
        queries = _short_query_lengths(length)
        assert queries, length
        _assert_queries_match(
            SHORT_QUERY_CORPUS,
            queries,
            q=3,
            q_values=(1, 2, 3),
        )


def test_exhaustive_short_alphabet_differential_with_multi_q() -> None:
    alphabet = "ab "
    corpus = tuple(
        "".join(characters)
        for length in range(5)
        for characters in product(alphabet, repeat=length)
    )
    queries = tuple(
        "".join(characters)
        for length in range(1, 7)
        for characters in product(alphabet, repeat=length)
    )

    assert len(queries) == 1092
    _assert_queries_match(corpus, queries, q=3, q_values=(1, 2, 3))
