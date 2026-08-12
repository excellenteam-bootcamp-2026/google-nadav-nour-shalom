import random
from dataclasses import dataclass
from statistics import median
from time import perf_counter
from typing import Callable

from models.prepared_sentence import PreparedSentence


@dataclass
class BenchmarkResult:
    query_type: str
    query: str
    time_ms: float
    results_count: int


class SearchBenchmark:
    def __init__(
        self,
        search_function: Callable[[str], list],
        sample_size: int = 100,
        seed: int = 42,
    ) -> None:
        self.search_function = search_function
        self.sample_size = sample_size
        self.random = random.Random(seed)
        self.results: list[BenchmarkResult] = []

    def _make_query(self, text: str) -> str:
        words = text.split()

        if not words:
            return ""

        # Use up to the first 4 words as an autocomplete query
        return " ".join(words[:4])

    def _non_space_positions(self, text: str) -> list[int]:
        return [
            i
            for i, char in enumerate(text)
            if not char.isspace()
        ]

    def _replace_char(self, text: str) -> str:
        positions = self._non_space_positions(text)

        if not positions:
            return text

        position = self.random.choice(positions)

        new_char = "x"

        if text[position].lower() == "x":
            new_char = "z"

        return (
            text[:position]
            + new_char
            + text[position + 1:]
        )

    def _delete_char(self, text: str) -> str:
        positions = self._non_space_positions(text)

        if not positions:
            return text

        position = self.random.choice(positions)

        return text[:position] + text[position + 1:]

    def _insert_char(self, text: str) -> str:
        if not text:
            return "x"

        position = self.random.randrange(len(text) + 1)

        return text[:position] + "x" + text[position:]

    def _measure(
        self,
        query: str,
        query_type: str,
    ) -> None:
        start = perf_counter()

        results = self.search_function(query)

        end = perf_counter()

        elapsed_ms = (end - start) * 1000

        self.results.append(
            BenchmarkResult(
                query_type=query_type,
                query=query,
                time_ms=elapsed_ms,
                results_count=len(results),
            )
        )

    def run(
        self,
        sentences: list[PreparedSentence],
    ) -> None:
        self.results.clear()

        if not sentences:
            print("No sentences available for benchmark.")
            return

        amount = min(
            self.sample_size,
            len(sentences),
        )

        sample = self.random.sample(
            sentences,
            amount,
        )

        for sentence in sample:
            query = self._make_query(
                sentence.normalized_text
            )

            if not query:
                continue

            # Correct query
            self._measure(
                query,
                "exact",
            )

            # One replaced character
            self._measure(
                self._replace_char(query),
                "replace",
            )

            # One deleted character
            self._measure(
                self._delete_char(query),
                "delete",
            )

            # One extra character
            self._measure(
                self._insert_char(query),
                "insert",
            )

    def _average(
        self,
        query_type: str,
    ) -> float:
        times = [
            result.time_ms
            for result in self.results
            if result.query_type == query_type
        ]

        if not times:
            return 0.0

        return sum(times) / len(times)

    def print_report(self) -> None:
        if not self.results:
            print("No benchmark results.")
            return

        times = [
            result.time_ms
            for result in self.results
        ]

        print()
        print("========== SEARCH BENCHMARK ==========")

        print(f"Queries tested: {len(self.results)}")

        print(
            f"Average time: "
            f"{sum(times) / len(times):.3f} ms"
        )

        print(
            f"Median time: "
            f"{median(times):.3f} ms"
        )

        print(
            f"Fastest query: "
            f"{min(times):.3f} ms"
        )

        print(
            f"Slowest query: "
            f"{max(times):.3f} ms"
        )

        print()
        print("Average by query type:")

        print(
            f"Exact:   "
            f"{self._average('exact'):.3f} ms"
        )

        print(
            f"Replace: "
            f"{self._average('replace'):.3f} ms"
        )

        print(
            f"Delete:  "
            f"{self._average('delete'):.3f} ms"
        )

        print(
            f"Insert:  "
            f"{self._average('insert'):.3f} ms"
        )

        print("======================================")