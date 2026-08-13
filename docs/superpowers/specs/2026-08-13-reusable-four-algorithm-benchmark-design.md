# Reusable Four-Algorithm Benchmark Design

## Objective

Provide one permanent command, `python benchmark/code/benchmark_all_algorithms.py`, that benchmarks any source accepted by the production `DataPreparer`. STANDARD is the default and consumes 100% of the selected source. QUICK and DEEP change workload depth, never the required four-algorithm registry.

## Architecture

The runner in `benchmark/code` is the only user-facing runner. It orchestrates existing production preparation, builders, structures, search algorithms, and instrumentation; it does not copy matching logic. Older specialized benchmark modules remain available as historical studies in the same code directory but are not invoked by the permanent command.

The runner has five explicit stages:

1. Resolve CLI mode/configuration and create a timestamped source-specific run directory.
2. Prepare the selected source exactly once and generate or load one deterministic query workload.
3. Measure pure build latency, then build once under `tracemalloc` for memory, then build one final online runtime per algorithm.
4. Warm each runtime and execute controlled sequential search calls. One retained timed result supplies both latency and correctness data; Naive is never rerun as a separate oracle. Lightweight counters are captured from the same timed call.
5. Serialize the observations once, derive all tables from stored observations, validate completeness, and render the report without calling a search implementation.

## Modes

- QUICK: 125 queries, one timing repetition, one build repetition, correctness and all four algorithms; explicitly not final evidence.
- STANDARD: 700 queries, three timing repetitions, three build repetitions, seed 42, full selected corpus, no scaling/q study/cProfile/repeatability.
- DEEP: 2000 queries, seven timing repetitions, five build repetitions, plus profiling, scaling, repeatability, and optional/default q study support.

CLI values override mode defaults. `--quick`, `--standard`, and `--deep` are mutually exclusive; absent a flag, STANDARD is selected.

## Correctness and instrumentation

Every first successful timed result is canonicalized outside the timing boundary. The Naive signature is the oracle. Optimized signatures are compared using every meaningful `MatchCandidate` field and multiplicity. Small mismatches retain exact compact counters for FN/FP details; large equality is decided by count plus independent order-insensitive hash accumulators. Exceptions are stored with tracebacks and make the validity gate incomplete.

Production counters are attached when supported. The tree hybrid is observed through benchmark-owned wrappers around its existing candidate/fuzzy helper calls; this measures the existing algorithm without rewriting it. All instrumentation is uniform across repetitions and no algorithm is executed again merely to obtain work metrics.

## Outputs and validity

Runs live under `benchmark/output/<source-stem>/<UTC timestamp>/` unless `--output` changes the base. Each run writes the ten requested JSON/CSV/Markdown artifacts plus `errors.json` when necessary. The report generator consumes serialized observation records only.

STANDARD prints `BENCHMARK COMPLETE` only when the full selected corpus, all four algorithms, all queries, correctness, separate build/memory data, raw samples, per-query CSV, lengths 1–6, and report are present. Otherwise it prints `BENCHMARK INCOMPLETE` with exact reasons.

## Testing

Tests use small real `PreparedSentence` fixtures and injected fake runtimes where full-corpus cost is irrelevant. They cover CLI modes/overrides, registry validation, deterministic workload generation, timed-oracle reuse, rotated order, exception capture, aggregation, length rows, timestamped artifacts, QUICK/STANDARD behavior, and report generation that cannot invoke searches. No test asserts hardware-specific timings.
