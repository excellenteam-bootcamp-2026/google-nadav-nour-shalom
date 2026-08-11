"""
Tests for the autocomplete engine input loop (Step 1: Receive User Query).
"""
import pytest
from unittest.mock import patch
from src.autocomplete.engine import run


def test_empty_input_is_skipped(capsys):
    """Empty string input must not produce any output and must not crash."""
    inputs = ["", "hello", KeyboardInterrupt]

    def side_effect(*args):
        value = inputs.pop(0)
        if isinstance(value, type) and issubclass(value, BaseException):
            raise value()
        return value

    with patch("builtins.input", side_effect=side_effect):
        run([])

    captured = capsys.readouterr()
    # The debug line should only appear for "hello", not for the empty string.
    assert captured.out.count("[DEBUG] Received query:") == 1
    assert "hello" in captured.out


def test_whitespace_only_input_is_skipped(capsys):
    """Input containing only spaces must be treated the same as empty input."""
    inputs = ["   ", "\t", "hi", KeyboardInterrupt]

    def side_effect(*args):
        value = inputs.pop(0)
        if isinstance(value, type) and issubclass(value, BaseException):
            raise value()
        return value

    with patch("builtins.input", side_effect=side_effect):
        run([])

    captured = capsys.readouterr()
    assert captured.out.count("[DEBUG] Received query:") == 1
    assert "hi" in captured.out


def test_keyboard_interrupt_exits_gracefully(capsys):
    """Ctrl+C (KeyboardInterrupt) must print 'Goodbye!' and exit cleanly."""
    with patch("builtins.input", side_effect=KeyboardInterrupt):
        run([])

    captured = capsys.readouterr()
    assert "Goodbye!" in captured.out
