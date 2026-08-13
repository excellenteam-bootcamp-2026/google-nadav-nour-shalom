# AutoComplete Project Foundation

This repository contains the shared contracts for parallel development of the
offline preparation, search, and online completion modules.

## Stable boundaries

- `DataPreparer` reads source files and produces shared `PreparedSentence`
  objects without depending on a search implementation.
- `SearchStructureBuilder` converts prepared sentences into search data.
- `SearchStructure` represents data/state only.
- `SearchAlgorithm` searches an already-built structure and returns raw
  `MatchCandidate` objects.
- `SearchEngine` is the public facade used to build and search without exposing
  the configured builder, structure, or algorithm.
- `ProjectTextNormalizer` is shared by offline preparation and online query
  processing.

The default runtime search uses `BiAnchorStructureBuilder` and
`BiAnchorSearchAlgorithm`. It selects two non-overlapping exact query seeds,
deduplicates bounded candidate slices, and delegates verification to the same
`OneEditVerifier` used by `NaiveSearchAlgorithm`. Naive remains the correctness
oracle and the fallback for queries too short to hold two anchors.
Scoring, sentence-level deduplication, ranking, alphabetical tie-breaking, and
top-5 selection belong to the online completion module and are not implemented
inside search.

### Adaptive multi-q anchoring

`BiAnchorStructureBuilder` can index several seed lengths at once
(`q_values`), and `BiAnchorSearchAlgorithm` picks one per query.

- **Correctness.** The Bi-Anchor proof needs only two non-overlapping query
  seed *occurrences*, not a particular q. Every q with `2 * q <= len(query)`
  admits such a pair, and one edit can damage at most one of two disjoint
  ranges, so the surviving anchor is still exact. Adaptive q therefore does
  not touch the one-edit proof, `OneEditVerifier`, or `MatchCandidate`.
- **Performance.** Which valid q is used is chosen per query by estimated
  retrieval cost, `frequency(seed_a) + frequency(seed_b)` for that q's
  cheapest non-overlapping pair. Shorter seeds offer more disjoint placements
  but have longer posting lists, so neither direction wins in general.
  Equal cost keeps the larger q.
- **Routing floor.** `minimum_anchor_length` sends still-shorter queries to
  Naive. It is a measured performance decision, never a correctness one.

`HashSeedLookup` holds one shared word-occurrence table plus one seed index
per q, and infers q from `len(seed)`, so the `SeedLookup` contract is
unchanged. Intra-word seed frequencies are precomputed: adaptive selection
prices several seeds before expanding any, and summing a posting list per
price quote costs tens of milliseconds for a common short seed.

## Run data preparation

Place the assignment archive at `data/Archive.zip`, then run:

```powershell
python src/main.py
```

## Run tests

The test suite uses Python's standard library:

```powershell
python -m unittest discover -s tests -v
```

Pytest is also supported:

```powershell
python -m pytest
```

## Run search evaluation

### Permanent four-algorithm benchmark

The normal trustworthy benchmark has one entrypoint under `benchmark/code` and uses 100% of the
selected source:

```powershell
python benchmark/code/benchmark_all_algorithms.py --source data/Archive3.zip
```

Changing only `--source` is enough to benchmark another archive or source
accepted by the production `DataPreparer`; no Python edit is required.

Modes:

- **QUICK** — development sanity check: 125 deterministic queries, one timing
  repetition, one build repetition, full source, correctness, all four
  algorithms. It is explicitly not final performance evidence.
- **STANDARD** (default) — normal trustworthy comparison: 700 deterministic
  queries, three timing repetitions, three pure build repetitions, full
  source, separate memory builds, raw per-query results, and correctness.
- **DEEP** — research diagnostics: 2,000 queries, seven timing repetitions,
  five build repetitions, with scaling/profiling/repeatability and q-study
  gates kept out of normal runs.

```powershell
# Quick
python benchmark/code/benchmark_all_algorithms.py --source data/Archive3.zip --quick

# Explicit standard
python benchmark/code/benchmark_all_algorithms.py --source data/Archive3.zip --standard

# Deep
python benchmark/code/benchmark_all_algorithms.py --source data/Archive3.zip --deep

# Custom standard
python benchmark/code/benchmark_all_algorithms.py --source data/Archive3.zip --standard --queries 900 --repetitions 3 --build-repetitions 3 --seed 42
```

Supported options are `--source`, `--output`, `--queries`, `--repetitions`,
`--build-repetitions`, `--seed`, `--query-file`, `--q-study`, `--overwrite`,
and the mutually exclusive `--quick` / `--standard` / `--deep` flags. With no
mode and no source arguments, STANDARD and `data/Archive3.zip` are used.

Every timestamped run is stored under
`benchmark/output/<source-name>/<UTC timestamp>/` by default and contains:

- `environment.json`
- `corpus_summary.json`
- `queries.json`
- `build_results.json`
- `correctness_results.json`
- `per_query_results.csv`
- `raw_timings.json`
- `internal_work_metrics.json`
- `summary.json`
- `benchmark_report.md`

The runner always registers Naive, Q-Gram + Verifier, Q-Gram + Tree Hybrid,
and Selective Bi-Anchor, and fails loudly if that registry is incomplete. The
result retained from a timed Naive repetition is the raw correctness oracle;
there is no duplicate Naive correctness pass. All report tables are derived
from stored observations, memory collection uses separate builds, and STANDARD
does not run cProfile, scaling, q studies, or a second repeatability run.

Default STANDARD performs `700 × 4 × 3 = 8,400` timed searches. Compared with
the previous FULL example of `1,500 × 4 × 10 = 60,000`, that is an 86% timed
execution reduction, plus the removed duplicate correctness searches.

### Legacy focused evaluations

Compare Naive and Selective Bi-Anchor on a sample of the real Archive corpus
plus deterministic synthetic, repetitive, high-frequency, and cross-word
datasets:

```powershell
python -m benchmark.code.legacy_benchmark --dataset all --q 3 --repeats 5 --output benchmark/output/legacy/benchmark-results.json
```

The console and JSON reports separate raw-candidate correctness from latency,
speedup, candidate/verifier reductions, fallback rate, and index build/memory
statistics. Use `--q 2` or `--q 4` for configuration comparisons.

## Run the short-query study

Compare Naive, forced `q=1`/`q=2`/`q=3`, and adaptive selection for query
lengths 1-6 on the real Archive corpus:

```powershell
python -m benchmark.code.short_query_benchmark --archive data/Archive3.zip --per-length 16 --expansion-guard 100000 --output-dir benchmark/output/short-query
```

Naive costs tens of seconds per query on the full corpus, so the study is
tiered: correctness is gated against Naive on a stratified slice
(`--correctness-fraction`) with the complete workload, latency is measured on
the corpus given by `--latency-fraction`, and the full-corpus Naive baseline is
sampled per length. `--expansion-guard` skips executing a configuration whose
planned anchor pair predicts more occurrences than the budget and reports the
prediction instead, so a configuration too expensive to run stays visible.
