# Trustworthy Archive3 Benchmark Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a reproducible, per-query, repeated-timing comparison of all four actual algorithms on 100% of `Archive3.zip`, including a runnable Q-Gram+Verifier implementation and substantial short-query coverage.

**Architecture:** Restore the existing positional Q-Gram implementation to the frozen raw-search contract by using its postings only for correctness-safe candidate generation and the shared `OneEditVerifier` for semantics. A dedicated `archive3_benchmark` runner persists one stratified real workload, independently measures builds, rotates algorithm timing order, saves every raw sample and work counter, and derives all report tables from detailed results.

**Tech Stack:** Python 3.14 standard library, pytest, `perf_counter_ns`, `tracemalloc`, `cProfile`, CSV/JSON, SHA-256.

## Global Constraints

- Primary corpus is the complete production `data/Archive3.zip` prepared once through `DataPreparer`.
- All four algorithms consume the identical tuple of `PreparedSentence` objects and identical stored query workload.
- Naive raw candidates are the correctness oracle; incorrect algorithms remain visible but cannot win.
- Search timing excludes corpus loading, index build, output serialization, and benchmark bookkeeping.
- Core edit, candidate, normalization, completion, scoring, and ranking semantics remain unchanged.
- The existing user edit in `src/main.py` remains untouched.

---

### Task 1: Restore Q-Gram + Verifier integration

**Files:**
- Create: `tests/test_qgram_search.py`
- Modify: `src/structures/qgram_search_structure.py`
- Modify: `src/algorithms/qgram_search_algorithm.py`
- Create: `src/algorithms/qgram_search_stats.py`

**Interfaces:**
- `QGramSearchAlgorithm(stats: QGramSearchStats | None = None).search(normalized_query, structure) -> list[MatchCandidate]`
- `QGramStructureBuilder(q=3).build(PreparedSentence[]) -> QGramSearchStructure`

- [ ] Write differential tests covering exact internal/cross-word substrings, all edit types, repeated ambiguity, length 1 fallback, empty queries, and wrong structure types.
- [ ] Run the tests and confirm failures arise from the obsolete model/verifier contract.
- [ ] Change the structure to index `normalized_text` and expose posting statistics.
- [ ] Generate candidate `(sentence, start, target_length)` contexts from q-gram occurrence alignment shifts `-1/0/+1`; deduplicate, then call `OneEditVerifier.compare`.
- [ ] Use exhaustive Naive fallback only where no q-gram survival guarantee exists.
- [ ] Re-run focused differential and full tests.

### Task 2: Persisted Archive3 workload and reproducibility metadata

**Files:**
- Create: `benchmark/code/archive3_benchmark.py`
- Create: `tests/test_archive3_benchmark.py`
- Create: `benchmark/output/Archive3/`

**Interfaces:**
- `generate_workload(sentences, seed, target_count) -> tuple[Archive3Query, ...]`
- `save_queries` / `load_queries` preserve identical normalized queries and metadata.

- [ ] Write tests for unique IDs/text, deterministic output, 1–6 exact length buckets, 7–8/9–12/13–20/21+ buckets, all required categories, and frequency percentile labels.
- [ ] Run red, implement production-corpus-derived stratification and mutation generation, then run green.
- [ ] Add environment metadata: Python/platform/architecture/CPU/timestamp/git/archive SHA-256 and corpus preparation time/memory/statistics.

### Task 3: Reliable builds and online observations

**Files:**
- Modify: `benchmark/code/archive3_benchmark.py`
- Modify: `tests/test_archive3_benchmark.py`

**Interfaces:**
- Independent build repetitions return min/median/mean/max, peak/retained memory, and algorithm-specific structure metrics.
- Per-query observations retain raw samples plus min/median/mean/p95/max, correctness, result counts, speedup, and internal work.

- [ ] Test build repetition summaries and structure metrics on hand-checked corpora.
- [ ] Test deterministic rotated timing order and dynamic repetition metadata.
- [ ] Test canonical raw-result comparison includes every meaningful candidate field and multiplicity.
- [ ] Implement uniform warmups, GC policy, per-query medians, raw samples, and algorithm-specific counters.

### Task 4: Derived analysis and output suite

**Files:**
- Modify: `benchmark/code/archive3_benchmark.py`
- Modify: `tests/test_archive3_benchmark.py`

**Interfaces:**
- Writes `environment.json`, `corpus_summary.json`, `queries.json`, `build_results.json`, `per_query_results.csv`, `raw_timings.json`, `correctness_results.json`, `internal_work_metrics.json`, `summary.json`, and `benchmark_report.md`.

- [ ] Test per-length/category/result-count tables, fastest-correct wins/ties, speedups, worst/best cases, break-even, scaling, repeatability, and q-study serialization.
- [ ] Test the report has all 22 required self-contained sections and documented rerun command.
- [ ] Implement writers and a consistency validator that fails on a missing algorithm/query/sample.

### Task 5: Full Archive3 execution and verification

**Files:**
- Create/update: `benchmark/output/Archive3/*` benchmark artifacts.

- [ ] Calibrate length-1 raw-result memory/time and record safe repetition/query limits explicitly.
- [ ] Generate and persist the largest feasible stratified workload with substantial 1–6 coverage.
- [ ] Run all four algorithms on the same complete corpus/workload with warmup and at least three Naive repetitions; use 10 repetitions for cheap algorithms.
- [ ] Run three indexed build repetitions, repeatability subset, 10/25/50/75/100% scaling, and q=2/3/4 secondary study.
- [ ] Run artifact validation, `python -m pytest -p no:cacheprovider`, and `python -m compileall -q src` before final reporting.
