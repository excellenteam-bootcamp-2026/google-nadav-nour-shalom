"""
Q-GRAM + TRIE hybrid implementation of SearchAlgorithm.

Offline build phase:
  - Insert every word from every PreparedSentence into a character-level Trie.
  - For each unique word, index its Q-grams (trigrams by default) mapping each
    trigram to the Trie leaf node where that word ends.

Online search phase:
  1. Extract all Q-grams from the normalized query.
  2. Look up each Q-gram in the index to retrieve candidate word leaf nodes.
  3. Fuzzy-compare the query against each candidate word (at most 1 edit).
  4. For every matching (word, sentence) pair, emit a MatchCandidate.

Key difference from NaiveSearchAlgorithm:
  The naive algorithm is a full substring matcher (queries may match across word
  boundaries). This implementation matches queries against word prefixes only.
  For typical autocomplete usage (user types the start of a word), results are
  equivalent. Cross-word-boundary matches are not supported.
"""
from collections.abc import Iterable

from src.algorithms.trie_node import TrieNode
from src.contracts.search_algorithm import SearchAlgorithm
from src.models.edit_type import EditType
from src.models.match_candidate import MatchCandidate
from src.models.prepared_sentence import PreparedSentence


class QGramTrieSearchAlgorithm(SearchAlgorithm):
    """Q-GRAM + TRIE hybrid search: fast online lookup via offline index.

    Trades a one-time build cost for near-instant per-query response times,
    making it suitable for large corpora where the naive approach is too slow.
    """

    Q: int = 3                   # Q-gram (trigram) length
    SHORT_WORD_THRESHOLD: int = 4  # words this length or shorter go into the short-word index

    def __init__(self) -> None:
        self._root: TrieNode = TrieNode()
        # trigram string → list of Trie leaf nodes whose word contains that trigram
        self._qgrams: dict[str, list[TrieNode]] = {}
        # Dedicated index for short words (length <= SHORT_WORD_THRESHOLD).
        # Key: the exact word string. Value: its Trie leaf node.
        self._short_word_index: dict[str, TrieNode] = {}

    # ------------------------------------------------------------------
    # Build phase (offline, called once at startup)
    # ------------------------------------------------------------------

    def build(self, sentences: Iterable[PreparedSentence]) -> None:
        """Insert every word of every sentence into the Trie and Q-gram index.

        Each unique word is inserted into the Trie exactly once.
        Duplicate occurrences of the same word (in different sentences) simply
        append a new entry to the existing leaf node's occurrences list.
        """
        for sentence in sentences:
            words = sentence.normalized_text.split()
            char_pos = 0
            for word in words:
                leaf = self._insert_word(word)
                leaf.occurrences.append((sentence, char_pos))
                char_pos += len(word) + 1  # +1 for the separating space

    def _insert_word(self, word: str) -> TrieNode:
        """Walk (or create) the Trie path for *word* and return its leaf node.

        Q-grams are registered the first time a word is encountered.
        """
        node = self._root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]

        if node.word is None:
            node.word = word
            if len(word) <= self.SHORT_WORD_THRESHOLD:
                # Short word: store directly by key for O(1) lookup later.
                self._short_word_index[word] = node
            else:
                # Normal word: register every Q-gram -> this leaf node.
                for i in range(len(word) - self.Q + 1):
                    qgram = word[i : i + self.Q]
                    self._qgrams.setdefault(qgram, []).append(node)

        return node

    # ------------------------------------------------------------------
    # Search phase (online, called for every user query)
    # ------------------------------------------------------------------

    def search(self, normalized_query: str) -> list[MatchCandidate]:
        """Return all fuzzy matches for an already-normalized query.

        Uses Q-gram filtering to restrict the candidate set, then performs
        character-level fuzzy comparison. To prevent hanging on common words
        or short queries, we cap the results and prioritize EXACT matches.
        """
        if not normalized_query:
            return []

        candidates = self._get_candidates(normalized_query)
        
        # 1. Find all valid edits for the candidate words.
        valid_edits = []
        for word_node in candidates:
            for edit_type, edit_index, correct_chars in self._fuzzy_compare(
                normalized_query, word_node.word
            ):
                valid_edits.append((edit_type, word_node, edit_index, correct_chars))

        # 2. Sort by edit type priority so we process EXACT matches first.
        priority = {
            EditType.EXACT: 0,
            EditType.REPLACEMENT: 1,
            EditType.INSERTION: 2,
            EditType.DELETION: 3
        }
        valid_edits.sort(key=lambda x: priority.get(x[0], 99))

        # 3. Generate MatchCandidate objects up to a safe limit.
        results: list[MatchCandidate] = []
        MAX_RESULTS = 2000
        
        for edit_type, word_node, edit_index, correct_chars in valid_edits:
            for sentence, word_start in word_node.occurrences:
                results.append(
                    MatchCandidate(
                        sentence=sentence,
                        match_start=word_start,
                        edit_type=edit_type,
                        edit_index=edit_index,
                        correct_characters=correct_chars,
                    )
                )
                if len(results) >= MAX_RESULTS:
                    return results

        return results

    def _get_candidates(self, query: str) -> list[TrieNode]:
        """Return Trie leaf nodes that are candidates to match *query*.

        Short queries (length <= SHORT_WORD_THRESHOLD) are routed to the
        dedicated short-word index, avoiding a full Trie traversal.
        Longer queries use the standard Q-gram filtering path.
        """
        if len(query) <= self.SHORT_WORD_THRESHOLD:
            return self._get_short_candidates(query)

        seen_ids: set[int] = set()
        candidates: list[TrieNode] = []
        for i in range(len(query) - self.Q + 1):
            qgram = query[i : i + self.Q]
            for node in self._qgrams.get(qgram, []):
                node_id = id(node)
                if node_id not in seen_ids:
                    seen_ids.add(node_id)
                    candidates.append(node)
        return candidates

    def _get_short_candidates(self, query: str) -> list[TrieNode]:
        """Return candidates from the short-word index only.

        Restricts the candidate set to words whose length is within 1 of
        the query length, since we allow at most 1 edit per search.
        For example, query "pi" (length 2) will only consider words of
        length 1, 2, or 3 — never long words like "programming".
        """
        target_lengths = {len(query) - 1, len(query), len(query) + 1}
        return [
            node
            for word, node in self._short_word_index.items()
            if len(word) in target_lengths
        ]

    # ------------------------------------------------------------------
    # Fuzzy comparison helpers
    # ------------------------------------------------------------------

    def _fuzzy_compare(
        self,
        query: str,
        word: str,
    ) -> list[tuple[EditType, int | None, int]]:
        """Compare *query* against the beginning of *word*, allowing at most 1 edit.

        Mirrors the comparison logic of NaiveSearchAlgorithm applied to word
        prefixes. Multiple results are possible when more than one edit
        interpretation produces a valid match for the same (query, word) pair.

        Returns:
            A list of (edit_type, edit_index, correct_characters) tuples.
        """
        m, n = len(query), len(word)
        results: list[tuple[EditType, int | None, int]] = []

        # Equal-length prefix comparison (EXACT or REPLACEMENT).
        if n >= m:
            r = self._check_equal_length(query, word[:m])
            if r is not None:
                results.append(r)

        # INSERTION: query is missing one character → compare vs word[:m+1].
        if n >= m + 1:
            r = self._check_insertion(query, word[: m + 1])
            if r is not None:
                results.append(r)

        # DELETION: query has one extra character → compare vs word[:m-1].
        if m >= 2 and n >= m - 1:
            r = self._check_deletion(query, word[: m - 1])
            if r is not None:
                results.append(r)

        return results

    @staticmethod
    def _check_equal_length(
        query: str,
        target: str,
    ) -> tuple[EditType, int | None, int] | None:
        """Return EXACT or REPLACEMENT, or None when there are 2+ mismatches."""
        mismatches = [i for i, (q, t) in enumerate(zip(query, target)) if q != t]
        if not mismatches:
            return (EditType.EXACT, None, len(query))
        if len(mismatches) == 1:
            return (EditType.REPLACEMENT, mismatches[0], len(query) - 1)
        return None

    @staticmethod
    def _check_insertion(
        query: str,
        target: str,
    ) -> tuple[EditType, int, int] | None:
        """Return INSERTION if removing exactly one char from *target* yields *query*."""
        for slot in range(len(target)):
            if query == target[:slot] + target[slot + 1 :]:
                return (EditType.INSERTION, slot, len(query))
        return None

    @staticmethod
    def _check_deletion(
        query: str,
        target: str,
    ) -> tuple[EditType, int, int] | None:
        """Return DELETION if removing exactly one char from *query* yields *target*."""
        for idx in range(len(query)):
            if query[:idx] + query[idx + 1 :] == target:
                return (EditType.DELETION, idx, len(query) - 1)
        return None
