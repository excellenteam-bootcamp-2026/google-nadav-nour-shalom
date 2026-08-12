from src.algorithms.one_edit_verifier import OneEditVerifier
from src.models.edit_type import EditType
from src.models.prepared_sentence import PreparedSentence


def _sentence(text: str) -> PreparedSentence:
    return PreparedSentence(
        sentence_id=7,
        original_text=text,
        normalized_text=text,
        source_path="archive/example.txt",
        offset=3,
    )


def _interpretations(query: str, target: str):
    sentence = _sentence(target)
    return OneEditVerifier.compare(query, target, sentence, 11)


def test_equal_text_is_exact() -> None:
    matches = _interpretations("python", "python")

    assert [
        (match.edit_type, match.edit_index, match.correct_characters)
        for match in matches
    ] == [(EditType.EXACT, None, 6)]
    assert matches[0].match_start == 11


def test_one_equal_length_mismatch_is_replacement() -> None:
    matches = _interpretations("pythom", "python")

    assert [
        (match.edit_type, match.edit_index, match.correct_characters)
        for match in matches
    ] == [(EditType.REPLACEMENT, 5, 5)]


def test_longer_target_is_query_insertion() -> None:
    matches = _interpretations("pyton", "python")

    assert [
        (match.edit_type, match.edit_index, match.correct_characters)
        for match in matches
    ] == [(EditType.INSERTION, 3, 5)]


def test_longer_query_is_query_deletion_with_repeated_ambiguity() -> None:
    matches = _interpretations("pythhon", "python")

    assert [
        (match.edit_type, match.edit_index, match.correct_characters)
        for match in matches
    ] == [
        (EditType.DELETION, 3, 6),
        (EditType.DELETION, 4, 6),
    ]


def test_repeated_target_character_preserves_every_insertion_slot() -> None:
    matches = _interpretations("aa", "aaa")

    assert [match.edit_index for match in matches] == [0, 1, 2]
