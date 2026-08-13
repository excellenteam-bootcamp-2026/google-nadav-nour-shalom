from __future__ import annotations

from datetime import datetime, timezone
from dataclasses import dataclass, replace
import hashlib
import inspect
import json
from pathlib import Path
import shutil
import tracemalloc

import pytest

from benchmark.code import benchmark_all_algorithms as benchmark
from benchmark.code.archive3_benchmark import Archive3Query
from benchmark.code.archive3_benchmark import save_queries
from src.models.edit_type import EditType
from src.models.match_candidate import MatchCandidate
from src.models.prepared_sentence import PreparedSentence


SAVED_QUERY_FIXTURE = Path("tests/fixtures/search_correctness_queries.json")


def test_default_mode_is_standard_with_trustworthy_defaults() -> None:
    config = benchmark.resolve_config(benchmark.parse_args([]))

    assert config.mode == "standard"
    assert config.source == Path("data/Archive2.zip")
    assert config.output_base == Path("benchmark/output")
    assert config.query_count == 700
    assert config.repetitions == 3
    assert config.build_repetitions == 3
    assert config.seed == 42
    assert config.full_corpus is True
    assert config.expected_timed_searches == 700 * 4 * 3


@pytest.mark.parametrize(
    ("flag", "mode", "queries", "repetitions", "build_repetitions"),
    (
        ("--quick", "quick", 125, 1, 1),
        ("--standard", "standard", 700, 3, 3),
        ("--deep", "deep", 2000, 7, 5),
    ),
)
def test_mode_defaults(
    flag: str,
    mode: str,
    queries: int,
    repetitions: int,
    build_repetitions: int,
) -> None:
    config = benchmark.resolve_config(benchmark.parse_args([flag]))

    assert config.mode == mode
    assert config.query_count == queries
    assert config.repetitions == repetitions
    assert config.build_repetitions == build_repetitions


def test_mode_flags_are_mutually_exclusive() -> None:
    with pytest.raises(SystemExit):
        benchmark.parse_args(["--quick", "--deep"])


def test_source_and_numeric_cli_values_override_defaults() -> None:
    config = benchmark.resolve_config(
        benchmark.parse_args(
            [
                "--source",
                "data/Archive4.zip",
                "--queries",
                "900",
                "--repetitions",
                "4",
                "--build-repetitions",
                "2",
                "--seed",
                "99",
                "--output",
                "custom-results",
            ]
        )
    )

    assert config.source == Path("data/Archive4.zip")
    assert config.query_count == 900
    assert config.repetitions == 4
    assert config.build_repetitions == 2
    assert config.seed == 99
    assert config.output_base == Path("custom-results")


def test_registry_contains_exactly_all_four_required_algorithms() -> None:
    specs = benchmark.algorithm_specs()

    assert tuple(spec.algorithm_id for spec in specs) == (
        "naive",
        "qgram_verifier",
        "qgram_tree_hybrid",
        "bi_anchor",
    )
    benchmark.validate_algorithm_specs(specs)


def test_registry_validation_fails_loudly_when_qgram_verifier_is_missing() -> None:
    specs = tuple(
        spec
        for spec in benchmark.algorithm_specs()
        if spec.algorithm_id != "qgram_verifier"
    )

    with pytest.raises(RuntimeError, match="qgram_verifier"):
        benchmark.validate_algorithm_specs(specs)


def test_run_directory_is_source_specific_and_timestamped() -> None:
    config = benchmark.resolve_config(
        benchmark.parse_args(["--source", "data/Archive4.zip"])
    )

    result = benchmark.run_directory(
        config,
        datetime(2026, 8, 13, 12, 34, 56, tzinfo=timezone.utc),
    )

    assert result == Path("benchmark/output/Archive4/20260813T123456Z")


@dataclass
class _FakeRuntime:
    serial: int

    def search(self, query: str):
        return []

    def structure_metrics(self) -> dict[str, int]:
        return {"serial": self.serial}


def test_build_measurement_separates_timing_memory_and_final_runtime() -> None:
    trace_states: list[bool] = []
    instrument_states: list[bool] = []

    def factory(_sentences, *, instrument: bool):
        instrument_states.append(instrument)
        trace_states.append(tracemalloc.is_tracing())
        return _FakeRuntime(len(trace_states))

    spec = benchmark.AlgorithmSpec(
        "fake", "Fake", "FakeRuntime", "FakeBuilder", factory
    )

    results, runtimes = benchmark.measure_builds(
        (spec,), (), repetitions=3
    )

    assert trace_states == [False, False, False, True, False]
    assert instrument_states == [False, False, False, False, True]
    assert results["fake"]["build_repetitions"] == 3
    assert len(results["fake"]["build_time_ns"]["samples"]) == 3
    assert results["fake"]["memory_method"] == "tracemalloc dedicated build"
    assert results["fake"]["peak_build_memory_bytes"] >= 0
    assert results["fake"]["approx_retained_memory_bytes"] >= 0
    assert results["fake"]["structure_metrics"] == {"serial": 4}
    assert runtimes["fake"].serial == 5


def test_build_measurement_rejects_missing_factory() -> None:
    spec = benchmark.AlgorithmSpec("fake", "Fake", "Missing", "Missing")

    with pytest.raises(RuntimeError, match="cannot be instantiated"):
        benchmark.measure_builds((spec,), (), repetitions=1)


def _query(query_id: str, text: str) -> Archive3Query:
    return Archive3Query(
        query_id=query_id,
        query_text=text,
        normalized_query=text,
        query_length=len(text),
        length_bucket=str(len(text)) if len(text) <= 6 else "7-8",
        primary_category="exact",
        categories=("exact", "inside_word"),
        source_sentence_id=1,
        source_path="fixture.txt",
        source_start=0,
        mutation_type=None,
        frequency_band=None,
        qgram_frequency=None,
    )


def _match(text: str) -> MatchCandidate:
    sentence = PreparedSentence(
        sentence_id=1,
        original_text=text,
        normalized_text=text,
        source_path="fixture.txt",
        offset=1,
    )
    return MatchCandidate(sentence, 0, EditType.EXACT, None, len(text))


def _real_corpus() -> tuple[PreparedSentence, ...]:
    return tuple(
        PreparedSentence(
            sentence_id=index,
            original_text=text,
            normalized_text=text,
            source_path="fixture.txt",
            offset=index + 1,
        )
        for index, text in enumerate(
            ("python search works", "cross word matching", "rare token")
        )
    )


class _CountingRuntime:
    def __init__(self, algorithm_id: str, *, fail_query: str | None = None):
        self.algorithm_id = algorithm_id
        self.calls: list[str] = []
        self.fail_query = fail_query

    def search(self, query: str):
        self.calls.append(query)
        if query == self.fail_query:
            raise RuntimeError(f"failed {query}")
        return [_match(query)]

    def work_snapshot(self) -> dict[str, int]:
        return {"search_calls": len(self.calls), "verifier_calls": len(self.calls)}


def _tiny_standard_config(query_count: int = 2) -> benchmark.BenchmarkConfig:
    base = benchmark.resolve_config(benchmark.parse_args(["--standard"]))
    return replace(
        base,
        query_count=query_count,
        repetitions=3,
        build_repetitions=1,
        short_queries_per_length=1,
    )


def test_search_phase_reuses_timed_naive_result_and_never_reruns_for_correctness() -> None:
    queries = (_query("q1", "a"), _query("q2", "python"))
    runtimes = {
        algorithm_id: _CountingRuntime(algorithm_id)
        for algorithm_id in benchmark.REQUIRED_ALGORITHM_IDS
    }

    dataset = benchmark.run_search_phase(
        _tiny_standard_config(), queries, runtimes
    )

    expected_calls_per_runtime = 1 + len(queries) * 3  # one warmup + timed calls
    assert all(
        len(runtime.calls) == expected_calls_per_runtime
        for runtime in runtimes.values()
    )
    assert dataset["expected_timed_searches"] == 2 * 4 * 3
    assert dataset["actual_timed_searches"] == 2 * 4 * 3
    assert len(dataset["timing_rows"]) == 2 * 4
    assert len(dataset["correctness_rows"]) == 2 * 4
    assert len(dataset["work_rows"]) == 2 * 4
    assert dataset["errors"] == []
    for row in dataset["timing_rows"]:
        assert len(row["raw_samples_ns"]) == 3
        assert row["timing"]["p95_ns"] is None
    optimized = [
        row for row in dataset["correctness_rows"]
        if row["algorithm_id"] != "naive"
    ]
    assert all(row["correct"] for row in optimized)
    assert all(row["oracle_source"] == "timed_naive_result" for row in optimized)


def test_search_phase_rotates_order_deterministically() -> None:
    queries = (_query("q1", "abc"), _query("q2", "def"))
    runtimes = {
        algorithm_id: _CountingRuntime(algorithm_id)
        for algorithm_id in benchmark.REQUIRED_ALGORITHM_IDS
    }

    dataset = benchmark.run_search_phase(
        _tiny_standard_config(), queries, runtimes
    )
    rows = {
        (row["query_id"], row["algorithm_id"]): row
        for row in dataset["timing_rows"]
    }

    assert rows[("q1", "naive")]["order_positions"] == [0, 3, 2]
    assert rows[("q2", "naive")]["order_positions"] == [3, 2, 1]


def test_search_phase_captures_exception_and_continues_other_queries() -> None:
    queries = (_query("q1", "bad"), _query("q2", "good"))
    runtimes = {
        algorithm_id: _CountingRuntime(
            algorithm_id,
            fail_query="bad" if algorithm_id == "qgram_verifier" else None,
        )
        for algorithm_id in benchmark.REQUIRED_ALGORITHM_IDS
    }

    dataset = benchmark.run_search_phase(
        _tiny_standard_config(), queries, runtimes
    )

    assert len(dataset["errors"]) == 1
    error = dataset["errors"][0]
    assert error["algorithm_id"] == "qgram_verifier"
    assert error["query_id"] == "q1"
    assert "RuntimeError: failed bad" in error["traceback"]
    assert any(
        row["query_id"] == "q2" and row["algorithm_id"] == "qgram_verifier"
        for row in dataset["timing_rows"]
    )


def test_actual_registry_builds_all_four_runtimes_and_exposes_metrics() -> None:
    specs = benchmark.algorithm_specs()

    builds, runtimes = benchmark.measure_builds(
        specs, _real_corpus(), repetitions=1
    )

    assert tuple(builds) == benchmark.REQUIRED_ALGORITHM_IDS
    assert tuple(runtimes) == benchmark.REQUIRED_ALGORITHM_IDS
    assert builds["naive"]["structure_metrics"]["sentence_count"] == 3
    assert builds["qgram_verifier"]["structure_metrics"]["posting_entries"] > 0
    assert builds["qgram_tree_hybrid"]["structure_metrics"]["tree_nodes"] > 0
    assert builds["bi_anchor"]["structure_metrics"]["word_occurrences"] > 0
    assert all(runtime.search("python") is not None for runtime in runtimes.values())


def test_registry_classes_load_from_this_repository() -> None:
    root = Path.cwd().resolve()
    expected = {
        "naive": benchmark.NaiveSearchAlgorithm,
        "qgram_verifier": benchmark.QGramSearchAlgorithm,
        "qgram_tree_hybrid": benchmark.QGramTrieSearchAlgorithm,
        "bi_anchor": benchmark.BiAnchorSearchAlgorithm,
    }

    for spec in benchmark.algorithm_specs():
        implementation = expected[spec.algorithm_id]
        source = Path(inspect.getsourcefile(implementation)).resolve()
        assert source.is_relative_to(root)
        assert source == root / Path(*implementation.__module__.split(".")).with_suffix(".py")


def test_tree_benchmark_adapter_preserves_raw_search_semantics() -> None:
    corpus = _real_corpus()
    plain = benchmark._make_tree(corpus, instrument=False)
    observed = benchmark._make_tree(corpus, instrument=True)

    for query in ("python", "pyton", "cross", "ra", ""):
        assert benchmark.canonical_signature(observed.search(query)) == (
            benchmark.canonical_signature(plain.search(query))
        )


def _stored_dataset(queries: tuple[Archive3Query, ...]) -> dict[str, object]:
    timing_rows = []
    correctness_rows = []
    work_rows = []
    for query_index, query in enumerate(queries):
        for algorithm_index, algorithm_id in enumerate(
            benchmark.REQUIRED_ALGORITHM_IDS
        ):
            value = (query_index + 1) * 1_000_000 + algorithm_index * 10_000
            count = (0, 3, 12, 50, 500, 1500)[query_index % 6]
            timing_rows.append({
                **benchmark._query_metadata(query),
                "algorithm_id": algorithm_id,
                "repetitions_requested": 3,
                "repetitions_completed": 3,
                "raw_samples_ns": [value - 1000, value, value + 1000],
                "order_positions": [0, 1, 2],
                "timing": benchmark.summarize_ns(
                    [value - 1000, value, value + 1000]
                ),
                "result_count": count,
            })
            correctness_rows.append({
                "query_id": query.query_id,
                "algorithm_id": algorithm_id,
                "oracle_source": "timed_naive_result",
                "correct": True,
                "status": "oracle" if algorithm_id == "naive" else "raw_results_match",
                "false_negatives": 0,
                "false_positives": 0,
            })
            work_rows.append({
                "query_id": query.query_id,
                "algorithm_id": algorithm_id,
                "metrics": {"verifier_calls": query_index + 1},
            })
    return {
        "expected_timed_searches": len(queries) * 4 * 3,
        "actual_timed_searches": len(queries) * 4 * 3,
        "warmup_calls": 4,
        "clock": "time.perf_counter_ns",
        "gc_disabled_uniformly_during_timed_calls": True,
        "timing_rows": timing_rows,
        "correctness_rows": correctness_rows,
        "work_rows": work_rows,
        "errors": [],
    }


def _six_lengths() -> tuple[Archive3Query, ...]:
    return tuple(_query(f"q{length}", "x" * length) for length in range(1, 7))


def _stored_builds() -> dict[str, dict[str, object]]:
    return {
        algorithm_id: {
            "algorithm_id": algorithm_id,
            "build_repetitions": 3,
            "build_time_ns": benchmark.summarize_ns(
                [1_000_000, 1_100_000, 1_200_000]
            ),
            "memory_method": "tracemalloc dedicated build",
            "peak_build_memory_bytes": 1000,
            "approx_retained_memory_bytes": 500,
            "structure_metrics": {},
            "final_online_build_separate": True,
        }
        for algorithm_id in benchmark.REQUIRED_ALGORITHM_IDS
    }


def test_analysis_has_required_summary_shape_and_independent_lengths_1_to_6() -> None:
    queries = _six_lengths()
    config = _tiny_standard_config(query_count=6)

    summary = benchmark.analyze_dataset(
        config, queries, _stored_builds(), _stored_dataset(queries)
    )

    assert set(summary) >= {
        "benchmark_mode",
        "source",
        "environment",
        "corpus",
        "algorithms",
        "correctness",
        "build",
        "memory",
        "overall_latency",
        "by_length",
        "by_category",
        "by_result_count",
        "win_rates",
        "speedup_vs_naive",
        "break_even",
    }
    assert tuple(summary["by_length"])[0:6] == ("1", "2", "3", "4", "5", "6")
    assert all(summary["by_length"][str(length)]["query_count"] == 1 for length in range(1, 7))
    assert set(summary["by_result_count"]) == {
        "0", "1-5", "6-20", "21-100", "101-1000", "1000+"
    }
    assert summary["execution_counts"]["timed_searches"] == 6 * 4 * 3
    assert summary["execution_counts"]["separate_naive_oracle_searches"] == 0


def test_report_is_generated_from_stored_summary_without_runtimes() -> None:
    queries = _six_lengths()
    summary = benchmark.analyze_dataset(
        _tiny_standard_config(query_count=6),
        queries,
        _stored_builds(),
        _stored_dataset(queries),
    )

    report = benchmark.render_report(summary)

    assert "# Benchmark Configuration" in report
    assert "STANDARD" in report
    assert "# Query Length 1–6" in report
    assert "Q-Gram + Verifier" in report
    assert "timed Naive result" in report


def test_artifact_writer_creates_complete_output_suite() -> None:
    output = Path("benchmark/output/test-runs/reusable-runner")
    shutil.rmtree(output, ignore_errors=True)
    queries = _six_lengths()
    config = _tiny_standard_config(query_count=6)
    dataset = _stored_dataset(queries)
    builds = _stored_builds()
    summary = benchmark.analyze_dataset(config, queries, builds, dataset)

    try:
        benchmark.write_run_artifacts(
            output,
            config=config,
            environment={"python_version": "test"},
            corpus={"prepared_sentences": 6, "corpus_fraction": 1.0},
            queries=queries,
            builds=builds,
            dataset=dataset,
            summary=summary,
        )

        assert {path.name for path in output.iterdir()} >= {
            "environment.json",
            "corpus_summary.json",
            "queries.json",
            "build_results.json",
            "correctness_results.json",
            "per_query_results.csv",
            "raw_timings.json",
            "internal_work_metrics.json",
            "summary.json",
            "benchmark_report.md",
        }
    finally:
        shutil.rmtree(output, ignore_errors=True)


def _workload_corpus() -> tuple[PreparedSentence, ...]:
    texts = (
        "abcdefghijklmnopqrstuvwxyz whole words cross boundary patterns",
        "another sufficiently long sentence for deterministic benchmark queries",
        "repeated aaaaa common common uncommon replacement insertion deletion",
    ) * 5
    return tuple(
        PreparedSentence(
            sentence_id=index,
            original_text=text,
            normalized_text=text,
            source_path=f"fixture-{index % 2}.txt",
            offset=index + 1,
        )
        for index, text in enumerate(texts)
    )


def test_prepare_queries_is_deterministic_and_honors_query_file() -> None:
    config = replace(
        _tiny_standard_config(query_count=24),
        seed=42,
        short_queries_per_length=2,
    )

    first = benchmark.prepare_queries(_workload_corpus(), config)
    second = benchmark.prepare_queries(_workload_corpus(), config)

    assert first == second
    assert len(first) == 24
    categories = {category for query in first for category in query.categories}
    assert {"boundary_near_start", "boundary_near_end", "repeated_pattern"} <= categories
    query_file = Path("benchmark/output/test-runs/reusable-queries.json")
    try:
        save_queries(query_file, first, seed=42)
        loaded = benchmark.prepare_queries(
            _workload_corpus(), replace(config, query_file=query_file, seed=999)
        )
        assert loaded == first
    finally:
        query_file.unlink(missing_ok=True)


def test_saved_query_file_is_loaded_without_generation_and_has_identity(
    monkeypatch,
) -> None:
    payload = json.loads(SAVED_QUERY_FIXTURE.read_text(encoding="utf-8"))
    config = replace(
        _tiny_standard_config(query_count=999),
        query_file=SAVED_QUERY_FIXTURE,
        seed=999,
    )

    def forbidden_generation(*_args, **_kwargs):
        raise AssertionError("saved queries must not invoke generation")

    monkeypatch.setattr(benchmark, "generate_workload", forbidden_generation)
    loaded = benchmark.prepare_queries((), config)
    metadata = benchmark.query_workload_metadata(config, loaded)

    assert [query.query_id for query in loaded] == [
        item["query_id"] for item in payload["queries"]
    ]
    assert [query.normalized_query for query in loaded] == [
        item["normalized_query"] for item in payload["queries"]
    ]
    assert metadata == {
        "source": "SAVED",
        "file": str(SAVED_QUERY_FIXTURE.resolve()),
        "query_count": payload["query_count"],
        "sha256": hashlib.sha256(SAVED_QUERY_FIXTURE.read_bytes()).hexdigest(),
        "seed": payload["random_seed_used_to_create_it"],
    }


def test_report_records_saved_query_source_file_count_and_hash() -> None:
    config = replace(
        _tiny_standard_config(),
        query_file=SAVED_QUERY_FIXTURE,
    )
    queries = benchmark.prepare_queries((), config)
    config = replace(config, query_count=len(queries))
    summary = benchmark.analyze_dataset(
        config,
        queries,
        _stored_builds(),
        _stored_dataset(queries),
    )

    report = benchmark.render_report(summary)

    assert "Query source: **SAVED**" in report
    assert f"Query file: `{SAVED_QUERY_FIXTURE.resolve()}`" in report
    assert f"Query count: {len(queries)}" in report
    assert hashlib.sha256(SAVED_QUERY_FIXTURE.read_bytes()).hexdigest() in report


def test_validity_gate_reports_complete_standard_and_exact_failures() -> None:
    queries = _six_lengths()
    config = _tiny_standard_config(query_count=6)
    dataset = _stored_dataset(queries)
    builds = _stored_builds()
    corpus = {"corpus_fraction": 1.0, "prepared_sentences": 6}

    assert benchmark.validity_reasons(
        config, queries, builds, dataset, corpus
    ) == []

    broken = {**dataset, "errors": [{"algorithm_id": "qgram_verifier"}]}
    reasons = benchmark.validity_reasons(
        config, queries[:-1], builds, broken, corpus
    )
    assert any("length 6" in reason for reason in reasons)
    assert any("failed" in reason for reason in reasons)

    incorrect = {
        **dataset,
        "correctness_rows": [dict(row) for row in dataset["correctness_rows"]],
    }
    tree_row = next(
        row
        for row in incorrect["correctness_rows"]
        if row["algorithm_id"] == "qgram_tree_hybrid"
    )
    tree_row.update(
        correct=False,
        status="raw_result_mismatch",
        false_negatives=1,
        false_positives=0,
    )

    reasons = benchmark.validity_reasons(
        config, queries, builds, incorrect, corpus
    )

    assert any(
        "qgram_tree_hybrid" in reason and "correctness" in reason
        for reason in reasons
    )


def test_secondary_study_plan_keeps_standard_lean_and_honors_explicit_q_study() -> None:
    standard = benchmark.resolve_config(benchmark.parse_args(["--standard"]))
    explicit_q = benchmark.resolve_config(
        benchmark.parse_args(["--standard", "--q-study"])
    )
    deep = benchmark.resolve_config(benchmark.parse_args(["--deep"]))

    assert benchmark.secondary_study_plan(standard) == {
        "profiling": False,
        "scaling": False,
        "q_study": False,
        "repeatability": False,
    }
    assert benchmark.secondary_study_plan(explicit_q)["q_study"] is True
    assert benchmark.secondary_study_plan(deep) == {
        "profiling": True,
        "scaling": True,
        "q_study": True,
        "repeatability": True,
    }


def test_even_corpus_slice_uses_requested_fraction_without_truncating_primary() -> None:
    corpus = _workload_corpus()

    quarter = benchmark.even_corpus_slice(corpus, 0.25)

    assert len(quarter) == 4
    assert quarter[0] == corpus[0]
    assert quarter[-1] != corpus[3]
    assert benchmark.even_corpus_slice(corpus, 1.0) == corpus
