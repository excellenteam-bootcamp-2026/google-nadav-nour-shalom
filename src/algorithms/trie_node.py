"""Trie node used by the Q-GRAM + TRIE hybrid search algorithm."""
from __future__ import annotations

from src.models.prepared_sentence import PreparedSentence


class TrieNode:
    """A single node in the character-level prefix Trie.

    Each node represents one character in the path from the root.
    A node becomes a word-end node when ``word`` is set to a non-None string,
    meaning the path from root to this node spells out a complete word.

    ``occurrences`` is populated only at word-end nodes and stores every
    (PreparedSentence, word_start_position) pair in the corpus that contains
    that specific word.
    """

    __slots__ = ("children", "word", "occurrences")

    def __init__(self) -> None:
        self.children: dict[str, TrieNode] = {}
        self.word: str | None = None
        self.occurrences: list[tuple[PreparedSentence, int]] = []
