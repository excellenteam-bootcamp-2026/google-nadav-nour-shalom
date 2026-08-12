# Selective Bi-Anchor Search Design

## Goal

Implement Selective Bi-Anchor candidate generation backed by hash indexes while preserving the existing Naive one-edit semantics exactly. Both search algorithms delegate verification to one shared `OneEditVerifier`; Bi-Anchor changes only how candidate target slices are found.

## Existing Architecture and Baseline

The repository already separates preparation, structure construction, searching, and completion:

- `DataPreparer` produces immutable `PreparedSentence` values containing normalized full sentences and word positions.
- `SearchStructureBuilder` builds immutable data-only search structures.
- `SearchAlgorithm` consumes an already-normalized query and a built structure, returning raw `MatchCandidate` values.
- `SearchEngine` coordinates building and searching.
- The completion layer owns scoring, sentence consolidation, ranking, and top-five selection.

The pre-change baseline command is `python -m pytest`. It collected 89 tests and reported 89 passed, 0 failed, and 0 skipped. Pytest emitted one cache-path warning unrelated to test behavior.

`NaiveSearchAlgorithm` currently generates every in-bounds target slice of length `m`, `m + 1`, and `m - 1` at every sentence position. Its private comparison helpers implement exact matching, one replacement, a character missing from the query (`INSERTION`), a character extra in the query (`DELETION`), and multiple valid edit interpretations for repeated characters.

## Shared Verification

The first isolated implementation phase extracts the current comparison behavior into `src/algorithms/one_edit_verifier.py`. The public operation is conceptually:

```python
OneEditVerifier.compare(
    query: str,
    target: str,
    sentence: PreparedSentence,
    match_start: int,
) -> list[MatchCandidate]
```

The existing `_compare`, `_check_equal_length`, `_check_missing_character`, and `_check_extra_character` logic moves as literally as practical. No semantics, ordering, multiplicity, edit indices, or correct-character counts change. `NaiveSearchAlgorithm` continues exhaustive target generation and calls this verifier for every valid slice.

The full pre-existing suite is run immediately after extraction. This phase is kept logically isolated from all indexing and Bi-Anchor changes.

## Models and Lookup Contract

Two immutable, slotted dataclasses support candidate generation:

- `SeedCandidate(text, query_start, query_end, frequency)` identifies one seed occurrence within the query. Its half-open query range is part of its identity, so identical text at different positions remains distinct.
- `CandidateContext(sentence_id, start, target_length)` identifies exactly one target slice to verify. It does not retain an alignment shift after `start` has been calculated.

The `SeedLookup` abstraction exposes only:

```python
frequency(seed: str) -> int
occurrences(seed: str) -> tuple[SeedOccurrence, ...]
```

Each occurrence provides only a sentence ID and absolute normalized-sentence position. Index type and storage details remain hidden from `BiAnchorSearchAlgorithm`.

## Hash Seed Index

`HashSeedLookup` is the only backend in this implementation. The configured seed length `q` defaults to 3 and must be positive.

For intra-word seeds, the builder creates:

- a unique normalized-word table with stable integer word IDs;
- a word-occurrence table mapping each word ID to `(sentence_id, word_start)` occurrences;
- an intra-word seed index mapping a seed to every `(word_id, seed_offset)` reference.

All offsets of repeated seeds within a word are retained. Lookup expands each reference through every corpus occurrence of that word and returns absolute sentence positions. Frequency is the actual expansion count: each seed offset contributes the number of corpus occurrences for its word.

For boundary seeds, every q-length normalized-sentence window spanning at least one normalized word-space boundary is indexed as `(sentence_id, absolute_position)`. Boundary frequency is the length of that occurrence list. Dispatch between intra-word and boundary storage happens only inside `HashSeedLookup`.

The implementation reuses `PreparedSentence.word_positions` when present and derives equivalent non-whitespace word ranges from `normalized_text` when callers construct sentences without preparation metadata, as existing unit tests do.

No Trie, Huffman storage, generic indexing framework, or duplicate sentence-table domain abstraction is introduced.

## Structure and Builder

`BiAnchorSearchStructure` is an immutable `SearchStructure` containing:

- prepared sentences with efficient lookup by `sentence_id`;
- the `HashSeedLookup` through its `SeedLookup` contract;
- the configured positive seed length `q`.

`BiAnchorStructureBuilder(q=3)` builds this structure from the same `PreparedSentence` input accepted by the Naive builder. Duplicate sentence IDs are rejected because candidate identity and lookup resolution require unambiguous IDs.

## Selective Bi-Anchor Search

For a normalized query of length `m`, `BiAnchorSearchAlgorithm` performs the following:

1. Return no matches for an empty query.
2. If `m < 2 * q`, use `NaiveSearchAlgorithm` against the same structure's sentences. Any inability to form a non-overlapping seed pair also falls back to Naive.
3. Generate every q-length query seed occurrence, including identical seed text at different query positions, and attach its lookup frequency.
4. Examine all seed pairs and choose a non-overlapping pair minimizing the sum of frequencies. Selection rarity affects performance only.
5. If both selected frequencies are zero, return no matches.
6. Expand corpus occurrences for both selected seed texts.
7. For an occurrence at `source_position` and query seed beginning at `query_start`, calculate `base_start = source_position - query_start`. Generate starts `base_start - 1`, `base_start`, and `base_start + 1` independently with target lengths `m - 1`, `m`, and `m + 1`.
8. Apply strict bounds checks before slicing: target length positive, start non-negative, and end no greater than the sentence length.
9. Deduplicate `CandidateContext` values by `(sentence_id, start, target_length)` before verification.
10. Slice each valid target and call the shared `OneEditVerifier.compare`.
11. Remove only completely identical final `MatchCandidate` values using sentence ID, match start, edit type, edit index, and correct-character count. Distinct repeated-character interpretations remain.

The correctness invariant is that one edit cannot destroy both non-overlapping query seed ranges. Replacement and query deletion affect one query character; query insertion affects one insertion slot. At least one selected seed therefore survives as an exact target substring in every valid one-edit match. An insertion or deletion before that surviving seed changes its alignment by at most one character, so the three candidate starts cover the possible positions. Target lengths describe edit semantics and remain independent from alignment shifts.

## Instrumentation

Production search remains usable without instrumentation. An optional stats object supplied to or created by the Bi-Anchor algorithm records:

- selected seed text, query ranges, and frequencies;
- expanded seed-occurrence count;
- candidate contexts before and after deduplication;
- verifier calls;
- Naive fallback count.

Index build statistics record build time, unique words, word occurrences, intra-word keys and references, boundary keys and occurrences, and optional `tracemalloc` memory measurements. Instrumentation does not alter search results or the stable `SearchAlgorithm.search` interface.

## Testing Strategy

Implementation follows isolated red-green-refactor cycles:

1. Characterize the existing verifier semantics, extract the verifier, and rerun all existing tests.
2. Add model and hash-lookup unit tests for occurrence identity, repeated word offsets, weighted frequency, boundary seeds, and word-position fallback.
3. Add builder and algorithm tests for exact, replacement, insertion, deletion, middle-of-word, cross-word, repeated-character ambiguity, zero-frequency early return, explicit bounds, candidate-context deduplication, identical seed text at distinct query positions, and short-query fallback.
4. Add deterministic differential tests comparing complete semantic `MatchCandidate` identities from Naive and Bi-Anchor. Cases cover overlap, boundary positions, repeated characters, every edit position, common and rare seeds, and short fallback.
5. Add fixed-seed fuzz or small exhaustive corpus/query comparisons. The required gate is zero mismatches, zero false negatives, and zero false positives.

The production entry point in `src/main.py` remains configured for Naive until the complete focused, differential, and fuzz suite passes with zero mismatches. Only then is it switched to `BiAnchorStructureBuilder(q=3)` and `BiAnchorSearchAlgorithm`, whose short-query path still delegates to Naive.

## Benchmark and Evaluation

The existing `src/autocomplete/benchmark.py` is extended instead of adding a competing framework. It compares Naive and Bi-Anchor using the same prepared corpus, normalized queries, shared verifier, and full candidate canonicalization.

Correctness is reported independently from performance: total queries, matching sets, mismatches, false negatives, and false positives. Timing uses repeated `perf_counter_ns()` samples and reports mean, median, p95, category speedups, and overall speedup. Candidate metrics include verifier calls, expanded occurrences, candidate contexts before and after deduplication, fallback rate, average selected-seed frequency, and reduction ratios. Offline metrics include index build time, index cardinalities, and practical `tracemalloc` memory.

Datasets include the available `data/Archive.zip` corpus, deterministic random data, repetitive text, high-frequency vocabulary, cross-word queries, and short/medium/long query groups. Console output is accompanied by JSON output. Synthetic and Archive results are labeled separately, and no speed threshold is asserted in unit tests.

## Scope Boundaries

Search continues to return raw `list[MatchCandidate]`. It does not score, consolidate by sentence, rank, alphabetically tie-break, select the top five, alter normalization, or change the UI/CLI completion contract. The only entry-point integration is replacing the production search builder and algorithm after differential correctness is proven.

## Acceptance Gate

The work is complete only if the pre-existing baseline remains green, Naive and Bi-Anchor share exactly one verifier implementation, all focused and deterministic differential tests pass with zero mismatches, the benchmark executes and reports real measurements, `src/main.py` switches only after the correctness gate, and no prohibited indexing or compression backend is added.
