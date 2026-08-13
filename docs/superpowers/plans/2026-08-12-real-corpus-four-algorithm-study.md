# Real-Corpus Four-Algorithm Study Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and run a reproducible, semantics-preserving full-production-corpus comparison of every actual search implementation in the repository.

**Architecture:** A new benchmark module owns workload generation, adapters/instrumentation, measurements, analysis, and artifact serialization while importing the four algorithms unchanged. It records unsupported/broken states as results and emits both machine-readable artifacts and a consolidated Markdown report.

**Tech Stack:** Python 3.14 standard library (`argparse`, `csv`, `cProfile`, `pstats`, `statistics`, `time`, `tracemalloc`) and pytest.

## Global Constraints

- Use `data/Archive3.zip`, selected by `src/main.py`, in full for the primary corpus.
- Do not change algorithm matching semantics, normalization, candidate semantics, scoring, ranking, or top-five behavior.
- All runnable algorithms receive the exact same normalized query text.
- Naive raw candidates are the oracle; correctness is a hard gate.
- Keep build and online timing separate and label censored/unavailable data honestly.

---

### Task 1: Benchmark primitives and workload

**Files:**
- Create: `benchmark/code/real_corpus_benchmark.py`
- Create: `tests/test_real_corpus_benchmark.py`

**Interfaces:**
- Produces: `RealQuery`, `canonicalize`, `percentile`, `summarize`, `build_real_workload`, and `group_query_tags`.

- [ ] Write literal fixture tests proving canonicalization includes source identity and multiplicity, percentile values are nearest-rank, and workload generation is deterministic with required tags.
- [ ] Run `python -m pytest tests/test_real_corpus_benchmark.py -q` and confirm the import fails because the module is absent.
- [ ] Implement only the tested data models, statistics helpers, and deterministic source-stratified workload generator.
- [ ] Re-run the focused tests and refactor with the tests green.

### Task 2: Algorithm discovery, builds, and work instrumentation

**Files:**
- Modify: `benchmark/code/real_corpus_benchmark.py`
- Modify: `tests/test_real_corpus_benchmark.py`

**Interfaces:**
- Produces: `discover_algorithms`, `measure_build`, `run_search_observation`, and serializable algorithm/build status records.

- [ ] Add tests showing all four actual class/module mappings are reported and the legacy positional Q-gram incompatibility is represented as an explicit error.
- [ ] Run the focused test and observe the expected failure.
- [ ] Add benchmark-only wrappers/counters for Naive, Q-Gram Trie, and Bi-Anchor; inspect the legacy positional implementation without changing it.
- [ ] Run focused tests and the pre-existing algorithm tests.

### Task 3: Correctness, timing, categories, wins, speedups, and extremes

**Files:**
- Modify: `benchmark/code/real_corpus_benchmark.py`
- Modify: `tests/test_real_corpus_benchmark.py`

**Interfaces:**
- Produces: `evaluate_queries` and summaries for correctness, overall/category latency, work, fastest-correct wins, speedups, worst cases, and best cases.

- [ ] Add small real-component tests with hand-checked candidate differences and winner/category summaries.
- [ ] Run them red.
- [ ] Implement interleaved observations, full candidate comparison, mismatch classification, and summary aggregation.
- [ ] Run focused and full tests green.

### Task 4: Parameter, scaling, CPU, memory, and serialization

**Files:**
- Modify: `benchmark/code/real_corpus_benchmark.py`
- Modify: `tests/test_real_corpus_benchmark.py`

**Interfaces:**
- Produces: `run_parameter_study`, `run_scaling_study`, `profile_scenarios`, `write_artifacts`, and CLI `main`.

- [ ] Add tests for q=2/3/4 configuration enumeration, stable scaling slices, JSON/CSV round trips, and report sections.
- [ ] Run them red.
- [ ] Implement the studies and writers with configurable practical budgets/timeouts.
- [ ] Run focused and full tests green; run compileall.

### Task 5: Execute and report the real study

**Files:**
- Create: `benchmark/output/real-corpus/real-corpus-four-algorithm-results.json`
- Create: `benchmark/output/real-corpus/real-corpus-query-results.csv`
- Create: `benchmark/output/real-corpus/real-corpus-profile-summary.json`
- Create: `benchmark/output/real-corpus/real-corpus-four-algorithm-report.md`

- [ ] Run the benchmark on the complete `data/Archive3.zip` corpus.
- [ ] Inspect slow/censored observations and rerun only when needed to distinguish noise from a real limitation.
- [ ] Parse all output artifacts and reconcile headline counts/tables.
- [ ] Run `python -m pytest`, `python -m compileall -q src`, and the artifact consistency command before reporting completion.
