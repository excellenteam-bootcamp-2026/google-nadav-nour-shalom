"""
Tests for the autocomplete engine input loop (Steps 1-3: Receive, Normalize, Search).
"""
from unittest.mock import MagicMock, patch

from src.autocomplete.engine import run
from src.models.edit_type import EditType
from src.models.match_candidate import MatchCandidate
from src.models.prepared_sentence import PreparedSentence


def _make_candidate(index: int) -> MatchCandidate:
    """Build a real, scoreable candidate.

    A bare MagicMock cannot be used here: calculate_score looks its
    edit_type up in the penalty table and would raise KeyError.
    """
    sentence = PreparedSentence(
        sentence_id=index,
        original_text=f"sentence {index}",
        normalized_text=f"sentence {index}",
        source_path="file.txt",
        offset=index + 1,
    )
    return MatchCandidate(
        sentence=sentence,
        match_start=0,
        edit_type=EditType.EXACT,
        edit_index=None,
        correct_characters=5,
    )


def _make_engine(candidate_count: int = 0) -> MagicMock:
    """Return a mock search engine that returns a fixed number of candidates."""
    engine = MagicMock()
    engine.search.return_value = [
        _make_candidate(index) for index in range(candidate_count)
    ]
    return engine


def _scripted_input(inputs: list):
    """Return an input side effect that replays inputs, raising exceptions."""

    def side_effect(*args):
        value = inputs.pop(0)
        if isinstance(value, type) and issubclass(value, BaseException):
            raise value()
        return value

    return side_effect


def test_empty_input_is_skipped(capsys):
    """Empty string input must be ignored — search must not be called."""
    engine = _make_engine()
    with patch("builtins.input", side_effect=_scripted_input(["", "hello", KeyboardInterrupt])):
        run(engine)

    # search() must be called exactly once — only for "hello", not for "".
    assert engine.search.call_count == 1


def test_whitespace_only_input_is_skipped(capsys):
    """Whitespace-only input must be treated the same as empty input."""
    engine = _make_engine()
    with patch("builtins.input", side_effect=_scripted_input(["   ", "\t", "hi", KeyboardInterrupt])):
        run(engine)

    # search() must be called exactly once — only for "hi".
    assert engine.search.call_count == 1


def test_keyboard_interrupt_exits_gracefully(capsys):
    """Ctrl+C (KeyboardInterrupt) must print 'Goodbye!' and exit cleanly."""
    engine = _make_engine()
    with patch("builtins.input", side_effect=KeyboardInterrupt):
        run(engine)

    captured = capsys.readouterr()
    assert "Goodbye!" in captured.out


def test_valid_query_triggers_search(capsys):
    """A valid query must be normalized and passed to the search engine."""
    engine = _make_engine(candidate_count=3)
    with patch("builtins.input", side_effect=_scripted_input(["Hello, World!", KeyboardInterrupt])):
        run(engine)

    # search() must have been called once with the normalized form.
    engine.search.assert_called_once_with("hello world")
    captured = capsys.readouterr()
    # All three distinct sentences must be listed back to the user.
    for index in range(3):
        assert f"sentence {index}" in captured.out


def test_prefix_accumulates_across_inputs():
    """Each typed line extends the sentence built so far."""
    engine = _make_engine()
    with patch("builtins.input", side_effect=_scripted_input(["to be", "or not", KeyboardInterrupt])):
        run(engine)

    assert [call.args[0] for call in engine.search.call_args_list] == [
        "to be",
        "to be or not",
    ]


def test_hash_resets_to_a_fresh_prefix():
    """'#' must discard the accumulated prefix and start a new sentence."""
    engine = _make_engine()
    inputs = ["to be", "#", "or not", KeyboardInterrupt]
    with patch("builtins.input", side_effect=_scripted_input(inputs)):
        run(engine)

    # After '#', "or not" must be searched on its own — not appended.
    assert [call.args[0] for call in engine.search.call_args_list] == [
        "to be",
        "or not",
    ]


def test_hash_does_not_trigger_a_search(capsys):
    """'#' is a command, not a query: it must never reach the search engine."""
    engine = _make_engine()
    with patch("builtins.input", side_effect=_scripted_input(["#", KeyboardInterrupt])):
        run(engine)

    assert engine.search.call_count == 0
    assert "Starting a new sentence." in capsys.readouterr().out


def test_hash_is_recognised_despite_surrounding_whitespace():
    """A '#' line with stray spaces still resets."""
    engine = _make_engine()
    inputs = ["to be", "  #  ", "or not", KeyboardInterrupt]
    with patch("builtins.input", side_effect=_scripted_input(inputs)):
        run(engine)

    assert [call.args[0] for call in engine.search.call_args_list] == [
        "to be",
        "or not",
    ]

