# Reusable Four-Algorithm Benchmark Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build one source-configurable runner under `benchmark/code` for trustworthy QUICK, STANDARD, and DEEP comparisons of all four existing search algorithms.

**Architecture:** `benchmark/code/benchmark_all_algorithms.py` owns benchmark orchestration and stored-data analysis while importing production preparation/build/search code and the existing deterministic workload generator. Pure build timing, memory measurement, and final online builds are separate; timed results supply correctness and work observations without duplicate searches.

**Tech Stack:** Python 3.14 standard library, argparse, dataclasses, `perf_counter_ns`, `tracemalloc`, `cProfile`, JSON/CSV, pytest.

## Global Constraints

- STANDARD and DEEP prepare 100% of `--source` once.
- The registry must contain Naive, Q-Gram + Verifier, Q-Gram + Tree Hybrid, and Selective Bi-Anchor or fail before benchmarking.
- Do not modify core algorithm semantics or parallelize primary latency calls.
- STANDARD defaults: 700 queries, 3 timing repetitions, 3 build repetitions, seed 42.
- Reports and analyses must use stored observations without search reruns.

---

### Task 1: Configuration, modes, registry, and output paths

**Files:**
- Create: `benchmark/code/benchmark_all_algorithms.py`
- Create: `tests/test_benchmark_all_algorithms.py`

**Interfaces:**
- Produces: `parse_args(argv)`, `resolve_config(namespace) -> BenchmarkConfig`, `algorithm_specs()`, and `create_run_directory(config, now)`.

- [ ] Write tests asserting STANDARD defaults, QUICK/DEEP defaults, mutually exclusive flags, source/parameter overrides, timestamped paths, and all four required IDs.
- [ ] Run `python -m pytest tests/test_benchmark_all_algorithms.py -q -p no:cacheprovider` and confirm imports/functions are missing.
- [ ] Implement immutable mode/config/spec dataclasses, argparse parsing, registry validation, and path creation.
- [ ] Re-run the focused tests to green.

### Task 2: Separate build timing, memory, and final runtime construction

**Files:**
- Modify: `benchmark/code/benchmark_all_algorithms.py`
- Modify: `tests/test_benchmark_all_algorithms.py`

**Interfaces:**
- Consumes: `AlgorithmSpec`, shared `tuple[PreparedSentence, ...]`.
- Produces: `measure_builds(specs, sentences, repetitions)` returning build samples, one separate memory observation, structure metrics, and one final reusable runtime.

- [ ] Add failing tests with counting builders proving `repetitions + 2` independent constructions, no `tracemalloc` around pure samples, and a final reusable instance.
- [ ] Implement independent pure timing, dedicated memory construction, final online construction, and public-contract-aware structure metrics.
- [ ] Run focused tests and preserve the full baseline.

### Task 3: One-pass online observations and correctness reuse

**Files:**
- Modify: `benchmark/code/benchmark_all_algorithms.py`
- Modify: `tests/test_benchmark_all_algorithms.py`

**Interfaces:**
- Produces: `run_search_phase(config, queries, runtimes, progress) -> SearchDataset` with timing rows, correctness rows, work rows, and captured errors.

- [ ] Add failing tests proving exactly `queries * algorithms * repetitions + warmups` search calls, deterministic rotation, raw samples, and reuse of a timed Naive result as oracle.
- [ ] Add failing tests proving one algorithm exception is captured and the remaining matrix continues.
- [ ] Implement first-result canonicalization outside timing, cumulative-counter deltas, tree observation wrappers, correctness comparison, exception capture, progress/ETA, and sequential execution.
- [ ] Run focused tests to green.

### Task 4: Stored-data analysis, artifacts, report, and validity gate

**Files:**
- Modify: `benchmark/code/benchmark_all_algorithms.py`
- Modify: `tests/test_benchmark_all_algorithms.py`

**Interfaces:**
- Produces: `analyze_dataset(...)`, `write_run_artifacts(...)`, `render_report(stored_payload)`, and `validity_reasons(...)`.

- [ ] Add failing tests for overall distributions, independent 1–6 rows, categories/result buckets, wins/ties, speedups, break-even, and required summary keys.
- [ ] Add a failing test whose runtime raises if report generation attempts a search.
- [ ] Implement CSV/JSON writers, stored-data-only tables, conclusions, QUICK warning, DEEP-only section markers, and complete/incomplete validation.
- [ ] Re-run focused tests to green.

### Task 5: Orchestration, DEEP gates, documentation, and verification

**Files:**
- Modify: `benchmark/code/benchmark_all_algorithms.py`
- Modify: `tests/test_benchmark_all_algorithms.py`
- Modify: `README.md`

**Interfaces:**
- Produces: `main(argv=None) -> int` and the documented command `python benchmark/code/benchmark_all_algorithms.py --source data/Archive3.zip`.

- [ ] Add failing orchestration tests for QUICK, default STANDARD, query-file reuse, q-study gating, and startup execution-count reporting.
- [ ] Implement prepare-once orchestration, workload selection, warmup, DEEP-only profiling/scaling/repeatability hooks, output writing, and terminal completion status.
- [ ] Document normal, QUICK, explicit STANDARD, DEEP, and custom commands plus all supported arguments.
- [ ] Run `python -m pytest -p no:cacheprovider` and require zero failures.
- [ ] Run `python -m compileall -q .` and require exit code 0.
- [ ] Audit the attached validity checklist against generated fixture artifacts and `--help` output.
