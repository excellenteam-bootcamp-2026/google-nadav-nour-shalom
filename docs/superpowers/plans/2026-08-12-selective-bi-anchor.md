# Selective Bi-Anchor Search Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add hash-indexed Selective Bi-Anchor candidate generation that shares the existing one-edit verifier with Naive, prove raw-result equivalence, benchmark it, and make it the runtime default.

**Architecture:** `BiAnchorStructureBuilder` converts prepared sentences into immutable sentence access plus `HashSeedLookup`. `BiAnchorSearchAlgorithm` selects two non-overlapping query seed occurrences, generates and deduplicates bounded target contexts, then delegates all fuzzy semantics to the same `OneEditVerifier` used by Naive.

**Tech Stack:** Python 3.14, standard-library dataclasses/ABC/statistics/time/tracemalloc/json, pytest/unittest-compatible tests.

## Global Constraints

- Configurable `q`, default 3; no scattered seed-length literals.
- No Trie, Huffman, generic index framework, alternate normalization, dynamic programming, scoring, or ranking.
- Preserve all existing `MatchCandidate` semantics and repeated-character multiplicity.
- Treat frequency and best-pair choice as performance concerns only.
- Switch `src/main.py` only after zero differential and fuzz mismatches.

---

### Task 1: Extract Shared One-Edit Verification

**Files:**
- Create: `src/algorithms/one_edit_verifier.py`
- Modify: `src/algorithms/naive_search_algorithm.py`
- Test: `tests/test_one_edit_verifier.py`

**Interfaces:**
- Produces: `OneEditVerifier.compare(query, target, sentence, match_start) -> list[MatchCandidate]`

- [ ] Add direct characterization tests for exact, replacement, insertion/deletion direction, and repeated-character interpretations.
- [ ] Run `python -m pytest tests/test_one_edit_verifier.py` and confirm import failure before production code exists.
- [ ] Move the four existing comparison helpers unchanged into static verifier methods and delegate Naive slices to `compare`.
- [ ] Run `python -m pytest tests/test_one_edit_verifier.py tests/test_naive.py` and the full `python -m pytest` suite.
- [ ] Commit only verifier extraction and its tests.

### Task 2: Add Candidate and Seed-Lookup Models

**Files:**
- Create: `src/models/seed_candidate.py`
- Create: `src/models/candidate_context.py`
- Create: `src/models/seed_occurrence.py`
- Create: `src/contracts/seed_lookup.py`
- Test: `tests/test_bi_anchor_models.py`

**Interfaces:**
- Produces immutable `SeedCandidate(text, query_start, query_end, frequency)`, `CandidateContext(sentence_id, start, target_length)`, `SeedOccurrence(sentence_id, position)`, and abstract `SeedLookup.frequency/occurrences`.

- [ ] Add tests proving frozen identity includes query ranges and context identity excludes alignment shifts.
- [ ] Run the focused test and observe missing-module failure.
- [ ] Add minimal frozen/slotted dataclasses and the two-method abstract lookup contract.
- [ ] Run focused and full suites, then commit.

### Task 3: Implement Hash Seed Lookup

**Files:**
- Create: `src/structures/hash_seed_lookup.py`
- Test: `tests/test_hash_seed_lookup.py`

**Interfaces:**
- Consumes: `PreparedSentence`, `SeedLookup`, `SeedOccurrence`.
- Produces: `HashSeedLookup.build(sentences, q)`, unified `frequency/occurrences`, and immutable `HashSeedIndexStats`.

- [ ] Add tests with literal expectations for unique vocabulary, weighted repeated-word frequency, both `banana`/`ana` offsets, absolute occurrence resolution, q-length boundary windows, and sentences lacking prepared word positions.
- [ ] Run focused tests and observe missing implementation failure.
- [ ] Implement unique word/occurrence tables, intra-word references, boundary occurrences, private backend dispatch, validation, and build statistics.
- [ ] Run focused and full suites, then commit.

### Task 4: Add Bi-Anchor Structure and Builder

**Files:**
- Create: `src/structures/bi_anchor_search_structure.py`
- Create: `src/builders/bi_anchor_structure_builder.py`
- Test: `tests/test_bi_anchor_structure.py`

**Interfaces:**
- Produces: immutable `BiAnchorSearchStructure(sentences, sentences_by_id, seed_lookup, q, build_stats)` and `BiAnchorStructureBuilder(q=3)`.

- [ ] Add tests for default/configured q, immutable prepared data, lookup construction, duplicate sentence-ID rejection, and invalid q.
- [ ] Run focused tests and observe missing implementation failure.
- [ ] Implement the minimal structure/builder without another sentence-table abstraction.
- [ ] Run focused and full suites, then commit.

### Task 5: Implement Selective Bi-Anchor Candidate Generation

**Files:**
- Create: `src/algorithms/bi_anchor_search_algorithm.py`
- Create: `src/algorithms/bi_anchor_search_stats.py`
- Test: `tests/test_bi_anchor.py`

**Interfaces:**
- Consumes: `BiAnchorSearchStructure`, `SeedCandidate`, `CandidateContext`, `OneEditVerifier`, and Naive fallback.
- Produces: `BiAnchorSearchAlgorithm.search(...) -> list[MatchCandidate]`, deterministic minimum-frequency non-overlapping pair selection, and optional per-query stats.

- [ ] Add focused tests for exact, replacement, query insertion/deletion, `gramm`, boundary `lo wo`, repeated ambiguity above fallback length, identical seed strings at non-overlapping ranges, both-zero early return, strict beginning/end bounds, context deduplication, complete match deduplication, and fallback.
- [ ] Run focused tests and observe missing implementation failure.
- [ ] Implement seed occurrence generation, O(n²) pair selection, ±1 starts crossed with m-1/m/m+1 lengths, pre-slice bounds, context dedup, shared verification, complete semantic match dedup, and optional stats.
- [ ] Run focused and full suites, then commit.

### Task 6: Prove Differential Correctness and Pass the Runtime Gate

**Files:**
- Create: `tests/test_bi_anchor_differential.py`
- Modify after the gate: `src/main.py`

**Interfaces:**
- Canonical candidate key: `(sentence_id, match_start, edit_type, edit_index, correct_characters)`.

- [ ] Add curated differential matrices for all edit positions, overlaps, word boundaries, repeated text, common/rare seeds, short fallback, and sentence edges.
- [ ] Add deterministic fixed-seed fuzz and tractable exhaustive generation over `"ab "`, reporting exact query counts.
- [ ] Run differential tests and confirm any candidate-generation defect is caught; fix implementation defects test-first.
- [ ] Run the complete suite and require zero differential/fuzz mismatches.
- [ ] Only after that evidence, replace Naive imports/composition in `src/main.py` with default-q Bi-Anchor while retaining Naive modules.
- [ ] Run full tests again and commit differential tests plus gated runtime wiring.

### Task 7: Extend Benchmark and Evaluate

**Files:**
- Modify: `src/autocomplete/benchmark.py`
- Create: `tests/test_benchmark.py`
- Create at runtime: `benchmark-results.json`
- Modify: `README.md`

**Interfaces:**
- Produces repeatable correctness/performance reports for identical corpora/queries, optional JSON serialization, and metrics for both online queries and offline indexes.

- [ ] Add tests for percentile calculation, full semantic canonicalization, mismatch accounting, result serialization, and instrument aggregation without timing-ratio assertions.
- [ ] Run focused tests and observe failures against the old single-algorithm benchmark.
- [ ] Extend the existing benchmark with `perf_counter_ns()` repeated samples; mean/median/p95/category speedup; mismatch/false-negative/false-positive counts; verifier/candidate/fallback statistics; build/index/memory statistics; and labeled datasets.
- [ ] Document exact benchmark invocation and runtime Bi-Anchor composition.
- [ ] Run focused/full suites, then run Archive and synthetic benchmark datasets and save real JSON measurements.
- [ ] Commit benchmark, tests, documentation, and measured report.

### Task 8: Final Verification

**Files:** all changed files.

- [ ] Run `python -m pytest` fresh and record collected/passed/failed/skipped.
- [ ] Run the differential/fuzz tests separately and record exact workloads and zero-mismatch counts.
- [ ] Run the benchmark/evaluation command fresh and record measured latency, reduction, fallback, build, and memory values.
- [ ] Inspect `git diff`, `git status`, verifier references, prohibited backend names, and search/completion ownership.
- [ ] Use completion-verification and branch-finishing workflows, then report only evidence-backed results.
