"""
Tests for the autocomplete engine input loop (Steps 1-3: Receive, Normalize, Search).
"""
from unittest.mock import MagicMock, patch

from src.autocomplete.engine import run


def _make_engine(candidate_count: int = 0) -> MagicMock:
    """Return a mock search engine that returns a fixed number of candidates."""
    engine = MagicMock()
    engine.search.return_value = [MagicMock()] * candidate_count
    return engine


def test_empty_input_is_skipped(capsys):
    """Empty string input must be ignored — search must not be called."""
    inputs = ["", "hello", KeyboardInterrupt]

    def side_effect(*args):
        value = inputs.pop(0)
        if isinstance(value, type) and issubclass(value, BaseException):
            raise value()
        return value

    engine = _make_engine()
    with patch("builtins.input", side_effect=side_effect):
        run(engine)

    # search() must be called exactly once — only for "hello", not for "".
    assert engine.search.call_count == 1


def test_whitespace_only_input_is_skipped(capsys):
    """Whitespace-only input must be treated the same as empty input."""
    inputs = ["   ", "\t", "hi", KeyboardInterrupt]

    def side_effect(*args):
        value = inputs.pop(0)
        if isinstance(value, type) and issubclass(value, BaseException):
            raise value()
        return value

    engine = _make_engine()
    with patch("builtins.input", side_effect=side_effect):
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
    inputs = ["Hello, World!", KeyboardInterrupt]

    def side_effect(*args):
        value = inputs.pop(0)
        if isinstance(value, type) and issubclass(value, BaseException):
            raise value()
        return value

    engine = _make_engine(candidate_count=3)
    with patch("builtins.input", side_effect=side_effect):
        run(engine)

    # search() must have been called once with the normalized form.
    engine.search.assert_called_once_with("hello world")
    captured = capsys.readouterr()
    assert "3" in captured.out

