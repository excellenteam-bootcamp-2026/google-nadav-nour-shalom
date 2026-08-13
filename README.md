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

Compare Naive and Selective Bi-Anchor on a sample of the real Archive corpus
plus deterministic synthetic, repetitive, high-frequency, and cross-word
datasets:

```powershell
python -m src.autocomplete.benchmark --dataset all --q 3 --repeats 5 --output benchmark-results.json
```

The console and JSON reports separate raw-candidate correctness from latency,
speedup, candidate/verifier reductions, fallback rate, and index build/memory
statistics. Use `--q 2` or `--q 4` for configuration comparisons.

## Run the short-query study

Compare Naive, forced `q=1`/`q=2`/`q=3`, and adaptive selection for query
lengths 1-6 on the real Archive corpus:

```powershell
python -m src.autocomplete.short_query_benchmark --archive data/Archive3.zip --per-length 16 --expansion-guard 100000 --output-dir benchmark/short-query
```

Naive costs tens of seconds per query on the full corpus, so the study is
tiered: correctness is gated against Naive on a stratified slice
(`--correctness-fraction`) with the complete workload, latency is measured on
the corpus given by `--latency-fraction`, and the full-corpus Naive baseline is
sampled per length. `--expansion-guard` skips executing a configuration whose
planned anchor pair predicts more occurrences than the budget and reports the
prediction instead, so a configuration too expensive to run stays visible.
