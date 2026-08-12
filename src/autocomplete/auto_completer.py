"""Public entry point for the online autocomplete system.

The specification names one public operation:

    get_best_k_completions(prefix: str) -> list[AutoCompleteData]

It takes the raw prefix the user typed, not the internal candidate list,
so this module owns the composition:

    normalize(prefix) -> engine.search(...) -> rank -> AutoCompleteData

``completion.get_best_k_completions`` keeps its candidate-based signature
and is reused here, unchanged, as the ranking step.

The search engine is built once offline, so the module-level function
reads it from a singleton installed by an explicit ``init_completions``
call. ``AutoCompleter`` is the same pipeline with the engine passed in
explicitly; tests and any caller holding several corpora should use it
rather than the global.
"""

from collections.abc import Callable

from src.autocomplete.auto_complete_data import AutoCompleteData
from src.autocomplete.completion import get_best_k_completions as rank_candidates
from src.autocomplete.normalizer import normalize_text
from src.models.match_candidate import MatchCandidate


class AutoCompleter:
    """Turn a raw user prefix into ranked AutoCompleteData results."""

    def __init__(
        self,
        search_engine,
        on_candidates: Callable[[list[MatchCandidate]], None] | None = None,
    ) -> None:
        """Bind the pipeline to an already-built search engine.

        Args:
            search_engine: A built SearchEngine ready to accept normalized
                           queries and return MatchCandidate lists.
            on_candidates: Optional diagnostic hook invoked with the raw,
                           unranked candidates before scoring.
        """
        self._search_engine = search_engine
        self._on_candidates = on_candidates

    def get_best_k_completions(
        self,
        prefix: str,
        k: int = 5,
    ) -> list[AutoCompleteData]:
        """Return the best k completions for a raw (non-normalized) prefix.

        Args:
            prefix: Text as the user typed it, punctuation and casing
                    included; neither is required to match.
            k: Maximum number of results to return (default 5).

        Returns:
            Up to k AutoCompleteData objects ordered best-first. Each one
            carries the original sentence text, its source file, the
            one-based line offset in that file, and the score.
        """
        normalized = normalize_text(prefix)

        if not normalized:
            return []

        candidates = self._search_engine.search(normalized)

        if self._on_candidates is not None:
            self._on_candidates(candidates)

        return rank_candidates(candidates, k=k)


_default_completer: AutoCompleter | None = None


def init_completions(
    search_engine,
    on_candidates: Callable[[list[MatchCandidate]], None] | None = None,
) -> AutoCompleter:
    """Install the engine that the module-level function will query.

    Args:
        search_engine: A built SearchEngine.
        on_candidates: Optional diagnostic hook, as for AutoCompleter.

    Returns:
        The AutoCompleter now backing the module-level function.
    """
    global _default_completer
    _default_completer = AutoCompleter(search_engine, on_candidates=on_candidates)
    return _default_completer


def get_best_k_completions(prefix: str, k: int = 5) -> list[AutoCompleteData]:
    """Return the best k completions for a raw prefix (spec entry point).

    Args:
        prefix: Text as the user typed it, punctuation and casing
                included; neither is required to match.
        k: Maximum number of results to return (default 5).

    Returns:
        Up to k AutoCompleteData objects ordered best-first.

    Raises:
        RuntimeError: If init_completions has not been called yet.
    """
    if _default_completer is None:
        raise RuntimeError(
            "init_completions(search_engine) must be called before "
            "get_best_k_completions()."
        )

    return _default_completer.get_best_k_completions(prefix, k=k)
