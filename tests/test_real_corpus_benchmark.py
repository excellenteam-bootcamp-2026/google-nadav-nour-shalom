from __future__ import annotations

import csv
import json
from pathlib import Path
import subprocess
import sys

from benchmark.code.real_corpus_benchmark import (
    REQUIRED_QUERY_TAGS,
    RealQuery,
    build_algorithms,
    build_real_workload,
    canonicalize,
    corpus_statistics,
    discover_algorithms,
    evaluate_queries,
    percentile,
    profile_scenarios,
    run_parameter_study,
    run_scaling_study,
    summarize_evaluation_rows,
    summarize,
    stable_corpus_slices,
    write_artifacts,
)
from src.models.edit_type import EditType
from src.models.match_candidate import MatchCandidate
from src.models.prepared_sentence import PreparedSentence


def _sentence(
    sentence_id: int,
    text: str,
    source: str = "fixture.txt",
) -> PreparedSentence:
    return PreparedSentence(
        sentence_id=sentence_id,
        original_text=text,
        normalized_text=text,
        source_path=source,
        offset=sentence_id + 10,
    )


def test_canonicalize_preserves_source_identity_and_multiplicity() -> None:
    first = _sentence(7, "aaaa", "one.txt")
    second = _sentence(7, "aaaa", "two.txt")
    matches = [
        MatchCandidate(first, 0, EditType.INSERTION, 0, 3),
        MatchCandidate(first, 0, EditType.INSERTION, 0, 3),
        MatchCandidate(second, 0, EditType.INSERTION, 0, 3),
    ]

    result = canonicalize(matches)

    assert len(result) == 2
    assert result[(7, "one.txt", 17, 0, "insertion", 0, 3)] == 2
    assert result[(7, "two.txt", 17, 0, "insertion", 0, 3)] == 1


def test_percentile_and_summary_use_nearest_rank() -> None:
    samples = [40, 10, 30, 20]

    assert percentile(samples, 50) == 20
    assert percentile(samples, 75) == 30
    assert percentile(samples, 95) == 40
    assert summarize(samples) == {
        "count": 4,
        "mean_ns": 25.0,
        "median_ns": 25.0,
        "p50_ns": 20.0,
        "p75_ns": 30.0,
        "p90_ns": 40.0,
        "p95_ns": 40.0,
        "p99_ns": 40.0,
        "max_ns": 40.0,
    }


def test_real_workload_is_deterministic_and_covers_required_tags() -> None:
    sentences = tuple(
        _sentence(index, text, f"source-{index % 4}.txt")
        for index, text in enumerate(
            [
                "aaaaa repeated pattern near boundary",
                "python configuration supports multiple values",
                "cross word substring example",
                "rarelyobservedtoken lives here",
                "the common text and the common value",
                "replacement insertion deletion candidates",
                "ending boundary marker",
                "short words a an the",
            ]
            * 4
        )
    )

    first = build_real_workload(sentences, target_count=32, seed=20260812)
    second = build_real_workload(sentences, target_count=32, seed=20260812)

    assert first == second
    assert len(first) == 32
    assert all(isinstance(item, RealQuery) for item in first)
    assert all(item.query for item in first)
    observed = {tag for item in first for tag in item.tags}
    assert REQUIRED_QUERY_TAGS <= observed
    assert len({item.source_file for item in first if item.source_file}) >= 4
    assert all(
        len(item.query) >= 6
        for item in first
        if any(
            tag in item.tags
            for tag in ("common_qgram", "medium_qgram", "rare_qgram")
        )
    )


def test_discovery_maps_all_four_actual_implementations() -> None:
    discovered = discover_algorithms()

    assert [item["id"] for item in discovered] == [
        "naive",
        "qgram_positional",
        "qgram_tree_hybrid",
        "bi_anchor",
    ]
    assert [item["class"] for item in discovered] == [
        "NaiveSearchAlgorithm",
        "QGramSearchAlgorithm",
        "QGramTrieSearchAlgorithm",
        "BiAnchorSearchAlgorithm",
    ]
    positional = discovered[1]
    assert positional["contract_compatible"] is True
    assert positional["verifier"].startswith("OneEditVerifier.compare")


def test_builds_report_structure_metrics_and_broken_qgram_explicitly() -> None:
    sentences = (
        _sentence(0, "python programming"),
        _sentence(1, "python search"),
    )

    builds, runtimes = build_algorithms(sentences, q=3, measure_memory=True)

    assert set(builds) == {
        "naive",
        "qgram_positional",
        "qgram_tree_hybrid",
        "bi_anchor",
    }
    assert set(runtimes) == {
        "naive",
        "qgram_positional",
        "qgram_tree_hybrid",
        "bi_anchor",
    }
    assert builds["naive"]["status"] == "ok"
    assert builds["naive"]["stats"]["sentences"] == 2
    assert builds["qgram_positional"]["status"] == "ok"
    assert builds["qgram_positional"]["stats"]["qgram_keys"] > 0
    assert builds["qgram_positional"]["stats"]["posting_references"] > 0
    assert builds["qgram_tree_hybrid"]["stats"] == {
        "tree_nodes": 23,
        "tree_edges": 22,
        "terminals": 3,
        "word_occurrences": 4,
        "qgram_keys": 17,
        "qgram_references": 17,
    }
    assert builds["bi_anchor"]["stats"]["unique_words"] == 3
    assert all(builds[name]["build_ns"] >= 0 for name in builds)


def test_evaluation_compares_complete_raw_results_and_groups_tags() -> None:
    sentences = (
        _sentence(0, "hello world"),
        _sentence(1, "hello there"),
    )
    _builds, runtimes = build_algorithms(sentences, q=3, measure_memory=False)
    queries = (
        RealQuery(
            query="hello",
            tags=("medium_exact", "inside_word", "multiple_matches"),
            source_sentence_id=0,
            source_file="fixture.txt",
            source_offset=10,
            expected_start=0,
            mutation="exact",
        ),
        RealQuery(
            query="lo wo",
            tags=("cross_word", "medium_exact"),
            source_sentence_id=0,
            source_file="fixture.txt",
            source_offset=10,
            expected_start=3,
            mutation="exact",
        ),
    )

    report, rows = evaluate_queries(runtimes, queries, repeats=1, warmups=0)

    assert len(rows) == 8
    assert report["correctness"]["naive"] == {
        "queries": 2,
        "matching_result_sets": 2,
        "mismatches": 0,
        "false_negatives": 0,
        "false_positives": 0,
    }
    assert report["correctness"]["bi_anchor"]["mismatches"] == 0
    assert report["correctness"]["qgram_positional"]["mismatches"] == 0
    assert report["correctness"]["qgram_tree_hybrid"]["mismatches"] == 2
    assert report["correctness"]["qgram_tree_hybrid"]["false_negatives"] > 0
    assert set(report["by_category"]) >= {
        "cross_word",
        "inside_word",
        "length_3_5",
        "medium_exact",
        "multiple_matches",
    }
    assert report["head_to_head"]["eligible_queries"] == 2
    naive_row = next(
        row
        for row in rows
        if row["algorithm"] == "naive" and row["query"] == "hello"
    )
    assert naive_row["work"]["sentence_positions_examined"] == 22
    assert naive_row["work"]["verifier_calls"] == 42
    reconstructed = summarize_evaluation_rows(rows)
    assert reconstructed["correctness"] == report["correctness"]
    assert reconstructed["overall_latency"] == report["overall_latency"]
    assert reconstructed["head_to_head"] == report["head_to_head"]


def test_corpus_statistics_and_scaling_slices_are_stable() -> None:
    sentences = tuple(
        _sentence(index, "one two" if index else "abc", f"s{index}.txt")
        for index in range(10)
    )

    stats = corpus_statistics(sentences, files_loaded=10)
    slices = stable_corpus_slices(sentences)

    assert stats == {
        "files_loaded": 10,
        "prepared_sentences": 10,
        "total_original_characters": 66,
        "total_normalized_characters": 66,
        "total_word_occurrences": 19,
        "unique_words": 3,
        "average_sentence_length": 6.6,
        "median_sentence_length": 7.0,
        "p95_sentence_length": 7.0,
        "maximum_sentence_length": 7,
    }
    assert [(fraction, len(items)) for fraction, items in slices] == [
        (10, 1),
        (25, 3),
        (50, 5),
        (75, 8),
        (100, 10),
    ]


def test_artifact_writer_round_trips_json_csv_and_twenty_section_report() -> None:
    payload = {
        "algorithms": discover_algorithms(),
        "baseline": {"collected": 137, "passed": 137, "failed": 0, "skipped": 0, "compileall": "passed"},
        "corpus": {"prepared_sentences": 2, "files_loaded": 1},
        "workload": {"generated_queries": 1, "executed_queries": 1},
        "builds": {},
        "evaluation": {"correctness": {}, "overall_latency": {}, "speedup_vs_naive": {}, "by_category": {}, "head_to_head": {}, "worst_cases": {}, "best_cases": {}},
        "parameter_study": {},
        "scaling_study": {},
        "profiles": {},
        "limitations": ["fixture"],
        "recommendations": {},
    }
    rows = [
        {
            "query": "hello",
            "tags": ("inside_word",),
            "algorithm": "naive",
            "latency_ns": 10.0,
            "result_count": 1,
            "correct": True,
            "false_negatives": 0,
            "false_positives": 0,
            "mismatch_classification": None,
            "work": {"verifier_calls": 3},
        }
    ]

    output_dir = Path("benchmark/output/test-runs/real-corpus")
    paths = write_artifacts(payload, rows, output_dir=output_dir)
    try:
        assert json.loads(paths["results"].read_text(encoding="utf-8"))["baseline"]["passed"] == 137
        assert json.loads(paths["profiles"].read_text(encoding="utf-8")) == {}
        with paths["queries"].open(encoding="utf-8", newline="") as handle:
            written = list(csv.DictReader(handle))
        assert written[0]["query"] == "hello"
        report = paths["report"].read_text(encoding="utf-8")
        assert "# 1. Algorithms found" in report
        assert "# 20. Recommended next step" in report
    finally:
        for path in paths.values():
            path.unlink(missing_ok=True)


def test_parameter_scaling_and_profile_studies_use_real_implementations() -> None:
    sentences = tuple(
        _sentence(index, f"python search value {index}") for index in range(8)
    )
    queries = (
        RealQuery("python", ("medium_exact", "inside_word"), 0, "fixture.txt", 10, 0, "exact"),
    )

    parameters = run_parameter_study(sentences, queries)
    scaling = run_scaling_study(sentences, queries, fractions=(50, 100))
    profiles = profile_scenarios(sentences, queries, fraction=0.5, top_count=3)

    assert set(parameters) == {"q=2", "q=3", "q=4"}
    assert parameters["q=3"]["qgram_positional"]["status"] == "ok"
    assert parameters["q=3"]["bi_anchor"]["status"] == "ok"
    assert list(scaling) == ["50%", "100%"]
    assert scaling["100%"]["sentences"] == 8
    assert profiles["corpus_fraction"] == 0.5
    assert set(profiles["algorithms"]) == {
        "naive",
        "qgram_positional",
        "qgram_tree_hybrid",
        "bi_anchor",
    }
    assert profiles["algorithms"]["naive"]["build"]["status"] == "ok"


def test_module_cli_defines_helpers_before_calling_main() -> None:
    output_dir = Path("benchmark/output/test-runs/real-corpus-cli")
    source = Path("benchmark/output/test-runs/cli-corpus.txt")
    source.write_text(
        "python configuration supports real search\n"
        "cross word matching example here\n",
        encoding="utf-8",
    )
    try:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "benchmark.code.real_corpus_benchmark",
                "--archive",
                str(source),
                "--generated-queries",
                "16",
                "--executed-queries",
                "1",
                "--profile-fraction",
                "1",
                "--output-dir",
                str(output_dir),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert completed.returncode == 0, completed.stderr
        assert (output_dir / "real-corpus-four-algorithm-results.json").exists()
    finally:
        source.unlink(missing_ok=True)
        for name in (
            "real-corpus-four-algorithm-results.json",
            "real-corpus-query-results.csv",
            "real-corpus-profile-summary.json",
            "real-corpus-four-algorithm-report.md",
        ):
            (output_dir / name).unlink(missing_ok=True)
