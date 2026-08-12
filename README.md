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
oracle and the fallback for queries shorter than two configured seeds.
Scoring, sentence-level deduplication, ranking, alphabetical tie-breaking, and
top-5 selection belong to the online completion module and are not implemented
inside search.

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
statistics. Use `--q 2` or `--q 4` for configuration comparisons; the runtime
default remains `q=3`.
