"""Tests for the short-query (length 1-6) adaptive Bi-Anchor benchmark."""

import pytest

from src.autocomplete.short_query_benchmark import (
    LENGTHS,
    REQUIRED_TAGS,
    anchor_runtimes,
    build_short_query_workload,
    measure_index_configurations,
    per_length_table,
    render_report,
    run_correctness_gate,
    run_length_study,
)
from src.builders.bi_anchor_structure_builder import BiAnchorStructureBuilder
from src.models.prepared_sentence import PreparedSentence


def _corpus() -> tuple[PreparedSentence, ...]:
    texts = [
        "the fastest test of the tested system",
        "testing a short query path for banana bread",
        "a test of the emergency broadcast system",
        "unrelated content here about hello world",
        "banana split and banana bread again",
        "quick brown foxes jump over lazy dogs",
        "the system tested every short query path",
        "hello world of testing and retesting",
    ]
    return tuple(
        PreparedSentence(
            sentence_id=sentence_id,
            original_text=text,
            normalized_text=text,
            source_path=f"archive/file{sentence_id % 3}.txt",
            offset=sentence_id + 1,
        )
        for sentence_id, text in enumerate(texts)
    )


CORPUS = _corpus()


def test_workload_covers_every_short_length() -> None:
    workload = build_short_query_workload(CORPUS, per_length=12)

    by_length = {length: 0 for length in LENGTHS}
    for item in workload:
        by_length[len(item.query)] += 1

    assert set(by_length) == set(LENGTHS)
    assert all(count > 0 for count in by_length.values())


def test_workload_covers_every_required_query_class() -> None:
    workload = build_short_query_workload(CORPUS, per_length=12)

    covered = {tag for item in workload for tag in item.tags}

    assert REQUIRED_TAGS <= covered


def test_workload_is_deterministic_for_one_seed() -> None:
    first = build_short_query_workload(CORPUS, per_length=10, seed=7)
    second = build_short_query_workload(CORPUS, per_length=10, seed=7)

    assert [item.query for item in first] == [item.query for item in second]


def test_forced_q_runtimes_reuse_one_shared_index() -> None:
    structure = BiAnchorStructureBuilder(q=3, q_values=(1, 2, 3)).build(CORPUS)

    runtimes = anchor_runtimes(structure)

    assert set(runtimes) == {"adaptive", "q1", "q2", "q3"}
    assert runtimes["q2"].structure.q_values == (2,)
    assert runtimes["adaptive"].structure.q_values == (1, 2, 3)
    for runtime in runtimes.values():
        assert runtime.structure.seed_lookup is structure.seed_lookup


def test_forced_q_runtime_never_anchors_below_its_own_q() -> None:
    structure = BiAnchorStructureBuilder(q=3, q_values=(1, 2, 3)).build(CORPUS)
    runtime = anchor_runtimes(structure)["q3"]

    runtime.search("test")

    assert runtime.stats.fallback_count == 1
    assert runtime.stats.last_selected_q is None


def test_correctness_gate_reports_zero_mismatches_for_every_runtime() -> None:
    workload = build_short_query_workload(CORPUS, per_length=8)

    gate = run_correctness_gate(CORPUS, workload)

    assert set(gate["runtimes"]) == {"adaptive", "q1", "q2", "q3"}
    for name, metrics in gate["runtimes"].items():
        assert metrics["mismatches"] == 0, name
        assert metrics["false_negatives"] == 0, name
        assert metrics["false_positives"] == 0, name
    assert gate["queries"] == len(workload)


def test_length_study_reports_each_configuration_and_marks_invalid_q() -> None:
    workload = build_short_query_workload(CORPUS, per_length=6)

    study = run_length_study(CORPUS, workload, repeats=1, naive_per_length=1)

    assert set(study["by_length"]) == {str(length) for length in LENGTHS}
    length_one = study["by_length"]["1"]
    assert length_one["q1"]["valid"] is False
    assert length_one["adaptive"]["fallback_rate"] == 1.0
    length_four = study["by_length"]["4"]
    assert length_four["q2"]["valid"] is True
    assert length_four["q3"]["valid"] is False
    assert length_four["adaptive"]["latency"]["count"] > 0
    assert "selected_q_counts" in length_four["adaptive"]


def test_expansion_guard_skips_execution_but_still_reports_the_prediction() -> None:
    workload = build_short_query_workload(CORPUS, per_length=6)

    study = run_length_study(
        CORPUS,
        workload,
        repeats=1,
        naive_per_length=0,
        include_naive=False,
        expansion_guard=0,
    )

    for length in ("2", "4", "6"):
        adaptive = study["by_length"][length]["adaptive"]
        assert adaptive["executed"] == 0, length
        assert adaptive["guarded"] > 0, length
        assert adaptive["predicted_expansion"]["count"] > 0, length


def test_length_table_renders_one_row_per_length() -> None:
    workload = build_short_query_workload(CORPUS, per_length=6)
    study = run_length_study(CORPUS, workload, repeats=1, naive_per_length=1)

    table = per_length_table(study)

    assert table.count("\n") == len(LENGTHS) + 1
    assert "| 1 |" in table
    assert "| 6 |" in table


def test_index_configurations_measure_build_and_memory_per_q_set() -> None:
    measured = measure_index_configurations(CORPUS, ((3,), (2, 3), (1, 2, 3)))

    assert set(measured) == {"q={3}", "q={2,3}", "q={1,2,3}"}
    for name, metrics in measured.items():
        assert metrics["build_ns"] > 0, name
        assert metrics["retained_memory_bytes"] > 0, name
        assert metrics["unique_words"] == 34, name
    assert (
        measured["q={1,2,3}"]["retained_memory_bytes"]
        > measured["q={3}"]["retained_memory_bytes"]
    )


def test_report_contains_every_required_section() -> None:
    workload = build_short_query_workload(CORPUS, per_length=6)
    payload = {
        "corpus": {"prepared_sentences": len(CORPUS)},
        "workload": {"queries": len(workload)},
        "correctness": run_correctness_gate(CORPUS, workload),
        "length_study": run_length_study(
            CORPUS, workload, repeats=1, naive_per_length=1
        ),
        "index_configurations": measure_index_configurations(
            CORPUS, ((3,), (2, 3), (1, 2, 3))
        ),
    }

    report = render_report(payload)

    for heading in (
        "Corpus",
        "Correctness gate",
        "Per-length results",
        "Index configurations",
    ):
        assert heading in report


def test_workload_rejects_a_corpus_without_text() -> None:
    with pytest.raises(ValueError, match="corpus"):
        build_short_query_workload((), per_length=4)
