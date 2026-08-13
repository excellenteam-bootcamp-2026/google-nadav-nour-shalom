# Real-Corpus Four-Algorithm Study Design

## Scope

Measure the repository's four actual search implementations against the complete production corpus, `data/Archive3.zip`, without changing their matching behavior. Naive raw `MatchCandidate` output is the correctness oracle. Implementations that cannot consume the shared `PreparedSentence` contract or cannot return raw `MatchCandidate` values are recorded as broken rather than repaired into a different algorithm.

## Architecture

Add a separate `benchmark.code.real_corpus_benchmark` module so the existing two-algorithm benchmark and its public data classes remain stable. The new runner will:

1. prepare the full archive through `DataPreparer`;
2. generate one deterministic, source-stratified workload with rich query metadata;
3. build and measure each actual implementation independently;
4. run correctness before comparative timing, preserving complete candidate semantics;
5. collect implementation-specific work, latency, scaling, parameter, CPU, and memory data;
6. write JSON, CSV, profile JSON, and a Markdown report.

Instrumentation lives in the benchmark module. It may subclass or inspect an implementation to count existing operations, but it does not alter search results, ranking, normalization, or runtime defaults.

## Runtime feasibility

The production corpus has 194,392 sentences and 8,158,666 normalized characters. A pilot call to `NaiveSearchAlgorithm.search("python")` did not complete within 120 seconds. Therefore the runner uses an explicit practical full-corpus query budget and records timeout-censored/unavailable observations rather than risking unbounded execution or claiming statistically meaningful repeated Naive timing where none is practical. The deterministic workload still covers every requested query family, with tags allowed to overlap.

## Correctness and failure handling

Canonical keys include sentence ID, source path, source offset, match start, edit type, edit index, and correct-character count, including multiplicity. Each optimized result is compared independently with Naive. Exact differences and a reason classification are saved. A result cap, prefix-only behavior, missing verifier API, cross-word limitation, timeout, or exception is reported explicitly and never treated as a match.

## Outputs

- `benchmark/output/real-corpus/real-corpus-four-algorithm-results.json`: complete machine-readable study
- `benchmark/output/real-corpus/real-corpus-query-results.csv`: per-query latency, correctness, result count, and work
- `benchmark/output/real-corpus/real-corpus-profile-summary.json`: cProfile summaries
- `benchmark/output/real-corpus/real-corpus-four-algorithm-report.md`: consolidated human-readable report

## Verification

Unit tests cover deterministic workload construction, complete canonicalization, percentile/speedup summaries, overlapping category grouping, and explicit unavailable-algorithm reporting. Final verification reruns the complete pytest suite, compileall, artifact JSON parsing, and benchmark report consistency checks.
