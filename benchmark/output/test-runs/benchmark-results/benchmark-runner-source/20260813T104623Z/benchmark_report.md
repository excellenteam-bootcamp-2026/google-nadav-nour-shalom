# Benchmark Configuration

> **QUICK BENCHMARK — NOT FINAL PERFORMANCE EVIDENCE**

Mode: **QUICK**  
Queries: 24  
Timing repetitions: 1  
Build repetitions: 1  
Expected timed search executions: 96

# Environment

```json
{
  "timestamp_utc": "2026-08-13T10:46:23.912057+00:00",
  "python_version": "3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]",
  "platform": "Windows-11-10.0.26200-SP0",
  "cpu": "Intel64 Family 6 Model 140 Stepping 1, GenuineIntel",
  "process_architecture": "64bit",
  "git_branch": "adaptive-multi-q-bi-anchor",
  "git_commit_sha": "b3603f0323d71d4e13c35fa3b0d1e06df726f61b",
  "source_path": "C:\\Users\\nours\\Desktop\\google-nadav-nour-shalom\\tests\\artifact-output\\benchmark-runner-source.txt",
  "source_size_bytes": 219,
  "source_sha256": "e0e80b9d13c0f40234af536613c91cec849d747137ba178a887f7b7960d6c7ed",
  "benchmark_mode": "QUICK",
  "benchmark_arguments": {
    "queries": 24,
    "repetitions": 1,
    "build_repetitions": 1,
    "seed": 42,
    "query_file": null,
    "q_study": false
  }
}
```

# Corpus Summary

```json
{
  "corpus_fraction": 1.0,
  "source_files": 1,
  "prepared_sentences": 3,
  "total_original_characters": 216,
  "total_normalized_characters": 216,
  "word_occurrences": 25,
  "unique_normalized_words": 25,
  "preparation_time_ns": 4078000,
  "sentence_length": {
    "min": 69,
    "mean": 72.0,
    "median": 70.0,
    "p75": 77,
    "p90": 77,
    "p95": 77,
    "p99": 77,
    "max": 77
  }
}
```

# Algorithm Mapping

| Concept | Implementation | Builder / structure |
| --- | --- | --- |
| Naive | NaiveSearchAlgorithm | NaiveStructureBuilder / NaiveSearchStructure |
| Q-Gram + Verifier | QGramSearchAlgorithm | QGramStructureBuilder / QGramSearchStructure |
| Q-Gram + Tree Hybrid | QGramTrieSearchAlgorithm | internal TrieNode + q-gram map |
| Selective Bi-Anchor | BiAnchorSearchAlgorithm | BiAnchorStructureBuilder / BiAnchorSearchStructure |

# Correctness

| Algorithm | Queries | Mismatches | FN | FP |
| --- | --- | --- | --- | --- |
| Naive | 24 | 0 | 0 | 0 |
| Q-Gram + Verifier | 24 | 0 | 0 | 0 |
| Q-Gram + Tree Hybrid | 24 | 24 | 1102 | 0 |
| Selective Bi-Anchor | 24 | 0 | 0 | 0 |

# Build Time

| Algorithm | Min ms | Median ms | Mean ms | Max ms |
| --- | --- | --- | --- | --- |
| Naive | 0.018 | 0.018 | 0.018 | 0.018 |
| Q-Gram + Verifier | 0.549 | 0.549 | 0.549 | 0.549 |
| Q-Gram + Tree Hybrid | 0.189 | 0.189 | 0.189 | 0.189 |
| Selective Bi-Anchor | 0.301 | 0.301 | 0.301 | 0.301 |

# Memory

| Algorithm | Peak build B | Retained B | Method |
| --- | --- | --- | --- |
| Naive | 1368 | 1104 | tracemalloc dedicated build |
| Q-Gram + Verifier | 68541 | 68033 | tracemalloc dedicated build |
| Q-Gram + Tree Hybrid | 75379 | 75323 | tracemalloc dedicated build |
| Selective Bi-Anchor | 73176 | 52656 | tracemalloc dedicated build |

# Overall Search Performance

| Algorithm | Median ms | Mean ms | P95 ms | P99 ms | Max ms |
| --- | --- | --- | --- | --- | --- |
| Naive | 1.433 | 1.314 | 1.764 | 1.813 | 1.813 |
| Q-Gram + Verifier | 0.187 | 0.397 | 1.068 | 1.230 | 1.230 |
| Q-Gram + Tree Hybrid | 0.031 | 0.083 | 0.232 | 0.258 | 0.258 |
| Selective Bi-Anchor | 1.153 | 1.088 | 1.662 | 3.069 | 3.069 |

# Query Length 1–6

| Length | N | Naive med/p95 | QG+V med/p95 | Tree med/p95 | Bi med/p95 | Fastest correct |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 4 | 0.889 / 1.071 | 0.981 / 1.230 | 0.212 / 0.258 | 0.905 / 1.171 | naive |
| 2 | 4 | 1.012 / 1.813 | 0.575 / 0.973 | 0.167 / 0.232 | 1.216 / 1.360 | qgram_verifier |
| 3 | 4 | 1.491 / 1.511 | 0.533 / 0.655 | 0.030 / 0.036 | 1.490 / 1.599 | qgram_verifier |
| 4 | 4 | 1.489 / 1.637 | 0.093 / 0.148 | 0.018 / 0.030 | 1.194 / 1.662 | qgram_verifier |
| 5 | 4 | 1.334 / 1.512 | 0.131 / 0.208 | 0.024 / 0.026 | 1.209 / 3.069 | qgram_verifier |
| 6 | 4 | 1.739 / 1.764 | 0.070 / 0.074 | 0.027 / 0.038 | 0.122 / 0.145 | qgram_verifier |

# Longer Query Length Groups

| Length | N | Naive med/p95 | QG+V med/p95 | Tree med/p95 | Bi med/p95 | Fastest correct |
| --- | --- | --- | --- | --- | --- | --- |
| 7-8 | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data |
| 9-12 | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data |
| 13-20 | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data |
| 21+ | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data |

# Query Categories

| Category | N | Naive | QG+V | Tree | Bi | Fastest correct |
| --- | --- | --- | --- | --- | --- | --- |
| exact | 24 | 1.433 | 0.187 | 0.031 | 1.153 | qgram_verifier |
| whole_word | 0 | 0.000 | 0.000 | 0.000 | 0.000 | insufficient correct data |
| inside_word | 0 | 0.000 | 0.000 | 0.000 | 0.000 | insufficient correct data |
| cross_word | 0 | 0.000 | 0.000 | 0.000 | 0.000 | insufficient correct data |
| replacement | 0 | 0.000 | 0.000 | 0.000 | 0.000 | insufficient correct data |
| insertion | 0 | 0.000 | 0.000 | 0.000 | 0.000 | insufficient correct data |
| deletion | 0 | 0.000 | 0.000 | 0.000 | 0.000 | insufficient correct data |
| repeated | 0 | 0.000 | 0.000 | 0.000 | 0.000 | insufficient correct data |
| common | 0 | 0.000 | 0.000 | 0.000 | 0.000 | insufficient correct data |
| rare | 0 | 0.000 | 0.000 | 0.000 | 0.000 | insufficient correct data |
| high_result_count | 0 | 0.000 | 0.000 | 0.000 | 0.000 | insufficient correct data |
| low_result_count | 0 | 0.000 | 0.000 | 0.000 | 0.000 | insufficient correct data |
| no_match | 0 | 0.000 | 0.000 | 0.000 | 0.000 | insufficient correct data |
| near_miss | 0 | 0.000 | 0.000 | 0.000 | 0.000 | insufficient correct data |
| multi_word | 0 | 0.000 | 0.000 | 0.000 | 0.000 | insufficient correct data |
| near_boundary | 0 | 0.000 | 0.000 | 0.000 | 0.000 | insufficient correct data |
| repeated_pattern | 0 | 0.000 | 0.000 | 0.000 | 0.000 | insufficient correct data |
| boundary_near_start | 0 | 0.000 | 0.000 | 0.000 | 0.000 | insufficient correct data |
| boundary_near_end | 0 | 0.000 | 0.000 | 0.000 | 0.000 | insufficient correct data |

# Match Count Analysis

| Raw matches | N | Naive | QG+V | Tree | Bi |
| --- | --- | --- | --- | --- | --- |
| 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1-5 | 13 | 1.511 | 0.092 | 0.023 | 1.156 |
| 6-20 | 3 | 1.493 | 0.536 | 0.036 | 1.143 |
| 21-100 | 4 | 1.012 | 0.630 | 0.158 | 1.325 |
| 101-1000 | 4 | 0.889 | 0.981 | 0.212 | 0.905 |
| 1000+ | 0 | 0.000 | 0.000 | 0.000 | 0.000 |

# Win Rates

| Algorithm | Wins | Percent |
| --- | --- | --- |
| Naive | 2 | 8.33% |
| Q-Gram + Verifier | 20 | 83.33% |
| Q-Gram + Tree Hybrid | 0 | 0.00% |
| Selective Bi-Anchor | 0 | 0.00% |
| Ties | 2 | 8.33% |

# Speedup vs Naive

```json
{
  "qgram_verifier": {
    "median": 7.466339051916277,
    "mean": 9.996413005909012,
    "p75": 16.853944562899787,
    "p90": 23.800269905533064,
    "best": 25.69357249626308,
    "worst": 0.6608391608391608
  },
  "qgram_tree_hybrid": {
    "median": 47.32879063611547,
    "mean": 45.860604159113116,
    "p75": 60.19672131147541,
    "p90": 101.99354838709678,
    "best": 147.02105263157895,
    "worst": 3.1512214036448234
  },
  "bi_anchor": {
    "median": 1.011035531742602,
    "mean": 3.1085891981805958,
    "p75": 1.3739787936728662,
    "p90": 13.355866355866356,
    "best": 15.130696474634565,
    "worst": 0.4927167856095415
  }
}
```

# Worst Queries

See `summary.json` (`worst_cases`) for the stored-data top 25 per algorithm.

# Best Queries

See `summary.json` (`best_cases`) for the stored-data top 20 speedups.

# Internal Work Metrics

Per-query counters are stored in `internal_work_metrics.json`; no search was rerun to create this report.

# Build/Search Break-Even

```json
{
  "qgram_verifier": 1,
  "qgram_tree_hybrid": 1,
  "bi_anchor": 2
}
```

# Conclusions

Fastest overall correct algorithm: `qgram_verifier`.
Best for length 1: `naive`.
Best for length 2: `qgram_verifier`.
Best for length 3: `qgram_verifier`.
Best for length 4: `qgram_verifier`.
Best for length 5: `qgram_verifier`.
Best for length 6: `qgram_verifier`.
Best for medium queries (9–12): `insufficient correct data`.
Best for long queries (21+): `insufficient correct data`.
Best inside-word: `insufficient correct data`.
Best cross-word: `insufficient correct data`.
Best common: `insufficient correct data`.
Best rare: `insufficient correct data`.
Best no-match: `insufficient correct data`.
Correctness is based on the retained timed Naive result; no separate Naive oracle search was run.

Largest bottlenecks and the next optimization experiment must be selected from the stored worst-case and internal-work evidence; algorithm redesign is outside this run.
