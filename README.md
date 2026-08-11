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

The current search pair is intentionally brute-force:
`NaiveStructureBuilder`, `NaiveSearchStructure`, and `NaiveSearchAlgorithm`.
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
