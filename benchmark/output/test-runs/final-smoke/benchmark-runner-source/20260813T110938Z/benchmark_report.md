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
  "timestamp_utc": "2026-08-13T11:09:38.317556+00:00",
  "python_version": "3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]",
  "platform": "Windows-11-10.0.26200-SP0",
  "cpu": "Intel64 Family 6 Model 140 Stepping 1, GenuineIntel",
  "process_architecture": "64bit",
  "git_branch": "adaptive-multi-q-bi-anchor",
  "git_commit_sha": "c95961417ecf0f6a14fc0516ed509da56b8f3486",
  "source_path": "C:\\Users\\nours\\Desktop\\google-nadav-nour-shalom\\tests\\fixtures\\benchmark-runner-source.txt",
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
  "preparation_time_ns": 29499900,
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
| Naive | 0.016 | 0.016 | 0.016 | 0.016 |
| Q-Gram + Verifier | 0.569 | 0.569 | 0.569 | 0.569 |
| Q-Gram + Tree Hybrid | 0.137 | 0.137 | 0.137 | 0.137 |
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
| Naive | 1.048 | 1.057 | 1.482 | 1.633 | 1.633 |
| Q-Gram + Verifier | 0.129 | 0.313 | 1.006 | 1.058 | 1.058 |
| Q-Gram + Tree Hybrid | 0.022 | 0.059 | 0.165 | 0.174 | 0.174 |
| Selective Bi-Anchor | 0.955 | 0.847 | 1.485 | 1.506 | 1.506 |

# Query Length 1–6

| Length | N | Naive med/p95 | QG+V med/p95 | Tree med/p95 | Bi med/p95 | Fastest correct | Winner % | Correct N/Q/T/B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 4 | 0.786 / 0.884 | 0.881 / 1.058 | 0.159 / 0.174 | 0.679 / 0.954 | naive | 25.00% | 4/4/0/4 |
| 2 | 4 | 0.837 / 0.854 | 0.394 / 0.609 | 0.130 / 0.141 | 0.876 / 1.004 | qgram_verifier | 100.00% | 4/4/0/4 |
| 3 | 4 | 1.066 / 1.482 | 0.456 / 0.573 | 0.020 / 0.022 | 0.985 / 1.485 | qgram_verifier | 100.00% | 4/4/0/4 |
| 4 | 4 | 1.121 / 1.633 | 0.085 / 0.130 | 0.018 / 0.022 | 1.129 / 1.506 | qgram_verifier | 100.00% | 4/4/0/4 |
| 5 | 4 | 1.115 / 1.166 | 0.099 / 0.158 | 0.020 / 0.028 | 1.078 / 1.128 | qgram_verifier | 100.00% | 4/4/0/4 |
| 6 | 4 | 1.313 / 1.379 | 0.049 / 0.051 | 0.016 / 0.025 | 0.088 / 0.099 | qgram_verifier | 100.00% | 4/4/0/4 |

# Longer Query Length Groups

| Length | N | Naive med/p95 | QG+V med/p95 | Tree med/p95 | Bi med/p95 | Fastest correct | Winner % | Correct N/Q/T/B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 7-8 | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| 9-12 | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| 13-20 | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| 21+ | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |

# Query Categories

| Category | N | Naive med/p95 | QG+V med/p95 | Tree med/p95 | Bi med/p95 | Fastest correct | Winner % | Correct N/Q/T/B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| exact | 24 | 1.048 / 1.482 | 0.129 / 1.006 | 0.022 / 0.165 | 0.955 / 1.485 | qgram_verifier | 83.33% | 24/24/0/24 |
| whole_word | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| inside_word | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| cross_word | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| replacement | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| insertion | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| deletion | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| repeated | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| common | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| rare | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| high_result_count | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| low_result_count | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| no_match | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| near_miss | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| multi_word | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| near_boundary | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| repeated_pattern | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| boundary_near_start | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| boundary_near_end | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |

# Match Count Analysis

| Raw matches | N | Naive | QG+V | Tree | Bi |
| --- | --- | --- | --- | --- | --- |
| 0 | 0 | 0.000 | 0.000 | 0.000 | 0.000 |
| 1-5 | 13 | 1.163 | 0.071 | 0.017 | 1.034 |
| 6-20 | 3 | 1.115 | 0.514 | 0.021 | 0.957 |
| 21-100 | 4 | 0.845 | 0.426 | 0.130 | 0.892 |
| 101-1000 | 4 | 0.786 | 0.881 | 0.159 | 0.679 |
| 1000+ | 0 | 0.000 | 0.000 | 0.000 | 0.000 |

# Win Rates

| Algorithm | Wins | Percent |
| --- | --- | --- |
| Naive | 1 | 4.17% |
| Q-Gram + Verifier | 20 | 83.33% |
| Q-Gram + Tree Hybrid | 0 | 0.00% |
| Selective Bi-Anchor | 1 | 4.17% |
| Ties | 2 | 8.33% |

# Speedup vs Naive

```json
{
  "qgram_verifier": {
    "median": 7.7406795790416485,
    "mean": 10.410954768048114,
    "p75": 14.56638418079096,
    "p90": 25.162337662337663,
    "best": 28.64033264033264,
    "worst": 0.7376181474480151
  },
  "qgram_tree_hybrid": {
    "median": 52.15816326530612,
    "mean": 49.60215662195487,
    "p75": 65.66666666666667,
    "p90": 114.91666666666667,
    "best": 137.50666666666666,
    "worst": 4.4876365727429555
  },
  "bi_anchor": {
    "median": 1.0031265163444179,
    "mean": 3.298153820345442,
    "p75": 1.1785809549213124,
    "p90": 14.59322033898305,
    "best": 16.776155717761558,
    "worst": 0.8040244388364989
  }
}
```

# Worst Queries

```json
{
  "naive": [
    {
      "query_id": "q000015",
      "query": "icie",
      "length": 4,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 1633400.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 621
      }
    },
    {
      "query_id": "q000011",
      "query": "dar",
      "length": 3,
      "categories": [
        "exact"
      ],
      "result_count": 9,
      "median_ns": 1481700.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 630
      }
    },
    {
      "query_id": "q000022",
      "query": "ulti w",
      "length": 6,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 1379000.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 603
      }
    },
    {
      "query_id": "q000023",
      "query": "are mu",
      "length": 6,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 1377600.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 603
      }
    },
    {
      "query_id": "q000021",
      "query": "eplace",
      "length": 6,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 1247500.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 603
      }
    },
    {
      "query_id": "q000016",
      "query": "mark",
      "length": 4,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 1210700.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 621
      }
    },
    {
      "query_id": "q000019",
      "query": "jklmn",
      "length": 5,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 1166200.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 612
      }
    },
    {
      "query_id": "q000024",
      "query": "bounda",
      "length": 6,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 1162500.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 603
      }
    },
    {
      "query_id": "q000017",
      "query": "pqrst",
      "length": 5,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 1122900.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 612
      }
    },
    {
      "query_id": "q000012",
      "query": "for",
      "length": 3,
      "categories": [
        "exact"
      ],
      "result_count": 9,
      "median_ns": 1114600.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 630
      }
    },
    {
      "query_id": "q000020",
      "query": "undar",
      "length": 5,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 1107700.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 612
      }
    },
    {
      "query_id": "q000018",
      "query": "s cro",
      "length": 5,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 1065400.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 612
      }
    },
    {
      "query_id": "q000013",
      "query": "c be",
      "length": 4,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 1031300.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 621
      }
    },
    {
      "query_id": "q000010",
      "query": "aaa",
      "length": 3,
      "categories": [
        "exact"
      ],
      "result_count": 25,
      "median_ns": 1017000.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 630
      }
    },
    {
      "query_id": "q000014",
      "query": "hmar",
      "length": 4,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 983000.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 621
      }
    },
    {
      "query_id": "q000003",
      "query": "y",
      "length": 1,
      "categories": [
        "exact"
      ],
      "result_count": 222,
      "median_ns": 883700.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 429
      }
    },
    {
      "query_id": "q000009",
      "query": "xyz",
      "length": 3,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 882300.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 630
      }
    },
    {
      "query_id": "q000006",
      "query": "te",
      "length": 2,
      "categories": [
        "exact"
      ],
      "result_count": 80,
      "median_ns": 853700.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 639
      }
    },
    {
      "query_id": "q000005",
      "query": "gh",
      "length": 2,
      "categories": [
        "exact"
      ],
      "result_count": 14,
      "median_ns": 837800.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 639
      }
    },
    {
      "query_id": "q000008",
      "query": "lt",
      "length": 2,
      "categories": [
        "exact"
      ],
      "result_count": 42,
      "median_ns": 836300.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 639
      }
    },
    {
      "query_id": "q000007",
      "query": "cr",
      "length": 2,
      "categories": [
        "exact"
      ],
      "result_count": 50,
      "median_ns": 815200.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 639
      }
    },
    {
      "query_id": "q000001",
      "query": "u",
      "length": 1,
      "categories": [
        "exact"
      ],
      "result_count": 228,
      "median_ns": 792500.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 429
      }
    },
    {
      "query_id": "q000004",
      "query": "i",
      "length": 1,
      "categories": [
        "exact"
      ],
      "result_count": 240,
      "median_ns": 780400.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 429
      }
    },
    {
      "query_id": "q000002",
      "query": "n",
      "length": 1,
      "categories": [
        "exact"
      ],
      "result_count": 254,
      "median_ns": 597400.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 429
      }
    }
  ],
  "qgram_verifier": [
    {
      "query_id": "q000004",
      "query": "i",
      "length": 1,
      "categories": [
        "exact"
      ],
      "result_count": 240,
      "median_ns": 1058000.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 0,
        "posting_lists_accessed": 0,
        "posting_entries_scanned": 0,
        "candidate_starts_before_dedup": 216,
        "candidate_starts_after_dedup": 216,
        "target_contexts": 429,
        "verifier_calls": 429,
        "fallback_count": 1
      }
    },
    {
      "query_id": "q000001",
      "query": "u",
      "length": 1,
      "categories": [
        "exact"
      ],
      "result_count": 228,
      "median_ns": 1006500.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 0,
        "posting_lists_accessed": 0,
        "posting_entries_scanned": 0,
        "candidate_starts_before_dedup": 216,
        "candidate_starts_after_dedup": 216,
        "target_contexts": 429,
        "verifier_calls": 429,
        "fallback_count": 1
      }
    },
    {
      "query_id": "q000003",
      "query": "y",
      "length": 1,
      "categories": [
        "exact"
      ],
      "result_count": 222,
      "median_ns": 754600.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 0,
        "posting_lists_accessed": 0,
        "posting_entries_scanned": 0,
        "candidate_starts_before_dedup": 216,
        "candidate_starts_after_dedup": 216,
        "target_contexts": 429,
        "verifier_calls": 429,
        "fallback_count": 1
      }
    },
    {
      "query_id": "q000002",
      "query": "n",
      "length": 1,
      "categories": [
        "exact"
      ],
      "result_count": 254,
      "median_ns": 632300.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 0,
        "posting_lists_accessed": 0,
        "posting_entries_scanned": 0,
        "candidate_starts_before_dedup": 216,
        "candidate_starts_after_dedup": 216,
        "target_contexts": 429,
        "verifier_calls": 429,
        "fallback_count": 1
      }
    },
    {
      "query_id": "q000006",
      "query": "te",
      "length": 2,
      "categories": [
        "exact"
      ],
      "result_count": 80,
      "median_ns": 609000.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 2,
        "posting_lists_accessed": 2,
        "posting_entries_scanned": 37,
        "candidate_starts_before_dedup": 111,
        "candidate_starts_after_dedup": 89,
        "target_contexts": 266,
        "verifier_calls": 266,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000012",
      "query": "for",
      "length": 3,
      "categories": [
        "exact"
      ],
      "result_count": 9,
      "median_ns": 572700.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "posting_lists_accessed": 3,
        "posting_entries_scanned": 35,
        "candidate_starts_before_dedup": 105,
        "candidate_starts_after_dedup": 84,
        "target_contexts": 252,
        "verifier_calls": 252,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000011",
      "query": "dar",
      "length": 3,
      "categories": [
        "exact"
      ],
      "result_count": 9,
      "median_ns": 513800.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "posting_lists_accessed": 3,
        "posting_entries_scanned": 37,
        "candidate_starts_before_dedup": 111,
        "candidate_starts_after_dedup": 79,
        "target_contexts": 230,
        "verifier_calls": 230,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000007",
      "query": "cr",
      "length": 2,
      "categories": [
        "exact"
      ],
      "result_count": 50,
      "median_ns": 453800.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 2,
        "posting_lists_accessed": 2,
        "posting_entries_scanned": 25,
        "candidate_starts_before_dedup": 75,
        "candidate_starts_after_dedup": 69,
        "target_contexts": 207,
        "verifier_calls": 207,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000010",
      "query": "aaa",
      "length": 3,
      "categories": [
        "exact"
      ],
      "result_count": 25,
      "median_ns": 398300.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "posting_lists_accessed": 3,
        "posting_entries_scanned": 39,
        "candidate_starts_before_dedup": 117,
        "candidate_starts_after_dedup": 42,
        "target_contexts": 120,
        "verifier_calls": 120,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000008",
      "query": "lt",
      "length": 2,
      "categories": [
        "exact"
      ],
      "result_count": 42,
      "median_ns": 334300.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 2,
        "posting_lists_accessed": 2,
        "posting_entries_scanned": 20,
        "candidate_starts_before_dedup": 60,
        "candidate_starts_after_dedup": 52,
        "target_contexts": 156,
        "verifier_calls": 156,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000018",
      "query": "s cro",
      "length": 5,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 158200.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "posting_lists_accessed": 4,
        "posting_entries_scanned": 7,
        "candidate_starts_before_dedup": 21,
        "candidate_starts_after_dedup": 12,
        "target_contexts": 36,
        "verifier_calls": 36,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000015",
      "query": "icie",
      "length": 4,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 130300.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "posting_lists_accessed": 3,
        "posting_entries_scanned": 5,
        "candidate_starts_before_dedup": 15,
        "candidate_starts_after_dedup": 9,
        "target_contexts": 26,
        "verifier_calls": 26,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000020",
      "query": "undar",
      "length": 5,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 127600.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "posting_lists_accessed": 4,
        "posting_entries_scanned": 8,
        "candidate_starts_before_dedup": 24,
        "candidate_starts_after_dedup": 15,
        "target_contexts": 44,
        "verifier_calls": 44,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000005",
      "query": "gh",
      "length": 2,
      "categories": [
        "exact"
      ],
      "result_count": 14,
      "median_ns": 123200.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 2,
        "posting_lists_accessed": 2,
        "posting_entries_scanned": 7,
        "candidate_starts_before_dedup": 21,
        "candidate_starts_after_dedup": 17,
        "target_contexts": 48,
        "verifier_calls": 48,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000016",
      "query": "mark",
      "length": 4,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 88600.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "posting_lists_accessed": 3,
        "posting_entries_scanned": 5,
        "candidate_starts_before_dedup": 15,
        "candidate_starts_after_dedup": 9,
        "target_contexts": 27,
        "verifier_calls": 27,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000014",
      "query": "hmar",
      "length": 4,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 82200.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "posting_lists_accessed": 3,
        "posting_entries_scanned": 5,
        "candidate_starts_before_dedup": 15,
        "candidate_starts_after_dedup": 9,
        "target_contexts": 27,
        "verifier_calls": 27,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000009",
      "query": "xyz",
      "length": 3,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 74000.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "posting_lists_accessed": 3,
        "posting_entries_scanned": 5,
        "candidate_starts_before_dedup": 15,
        "candidate_starts_after_dedup": 9,
        "target_contexts": 27,
        "verifier_calls": 27,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000013",
      "query": "c be",
      "length": 4,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 70800.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "posting_lists_accessed": 3,
        "posting_entries_scanned": 4,
        "candidate_starts_before_dedup": 12,
        "candidate_starts_after_dedup": 6,
        "target_contexts": 18,
        "verifier_calls": 18,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000017",
      "query": "pqrst",
      "length": 5,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 70300.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "posting_lists_accessed": 4,
        "posting_entries_scanned": 5,
        "candidate_starts_before_dedup": 15,
        "candidate_starts_after_dedup": 6,
        "target_contexts": 18,
        "verifier_calls": 18,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000022",
      "query": "ulti w",
      "length": 6,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 51000.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "posting_lists_accessed": 4,
        "posting_entries_scanned": 4,
        "candidate_starts_before_dedup": 12,
        "candidate_starts_after_dedup": 3,
        "target_contexts": 9,
        "verifier_calls": 9,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000021",
      "query": "eplace",
      "length": 6,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 50400.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "posting_lists_accessed": 4,
        "posting_entries_scanned": 4,
        "candidate_starts_before_dedup": 12,
        "candidate_starts_after_dedup": 3,
        "target_contexts": 9,
        "verifier_calls": 9,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000023",
      "query": "are mu",
      "length": 6,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 48100.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "posting_lists_accessed": 4,
        "posting_entries_scanned": 4,
        "candidate_starts_before_dedup": 12,
        "candidate_starts_after_dedup": 3,
        "target_contexts": 9,
        "verifier_calls": 9,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000019",
      "query": "jklmn",
      "length": 5,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 47200.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "posting_lists_accessed": 4,
        "posting_entries_scanned": 4,
        "candidate_starts_before_dedup": 12,
        "candidate_starts_after_dedup": 3,
        "target_contexts": 9,
        "verifier_calls": 9,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000024",
      "query": "bounda",
      "length": 6,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 46200.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "posting_lists_accessed": 4,
        "posting_entries_scanned": 4,
        "candidate_starts_before_dedup": 12,
        "candidate_starts_after_dedup": 3,
        "target_contexts": 9,
        "verifier_calls": 9,
        "fallback_count": 0
      }
    }
  ],
  "qgram_tree_hybrid": [
    {
      "query_id": "q000004",
      "query": "i",
      "length": 1,
      "categories": [
        "exact"
      ],
      "result_count": 26,
      "median_ns": 173900.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 0,
        "tree_lookups": 1,
        "candidate_words": 25,
        "candidate_occurrences": 25,
        "verifier_calls": 25
      }
    },
    {
      "query_id": "q000003",
      "query": "y",
      "length": 1,
      "categories": [
        "exact"
      ],
      "result_count": 25,
      "median_ns": 165200.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 0,
        "tree_lookups": 1,
        "candidate_words": 25,
        "candidate_occurrences": 25,
        "verifier_calls": 25
      }
    },
    {
      "query_id": "q000001",
      "query": "u",
      "length": 1,
      "categories": [
        "exact"
      ],
      "result_count": 29,
      "median_ns": 152400.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 0,
        "tree_lookups": 1,
        "candidate_words": 25,
        "candidate_occurrences": 25,
        "verifier_calls": 25
      }
    },
    {
      "query_id": "q000006",
      "query": "te",
      "length": 2,
      "categories": [
        "exact"
      ],
      "result_count": 7,
      "median_ns": 140900.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 0,
        "tree_lookups": 1,
        "candidate_words": 25,
        "candidate_occurrences": 25,
        "verifier_calls": 25
      }
    },
    {
      "query_id": "q000007",
      "query": "cr",
      "length": 2,
      "categories": [
        "exact"
      ],
      "result_count": 8,
      "median_ns": 135800.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 0,
        "tree_lookups": 1,
        "candidate_words": 25,
        "candidate_occurrences": 25,
        "verifier_calls": 25
      }
    },
    {
      "query_id": "q000008",
      "query": "lt",
      "length": 2,
      "categories": [
        "exact"
      ],
      "result_count": 2,
      "median_ns": 123800.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 0,
        "tree_lookups": 1,
        "candidate_words": 25,
        "candidate_occurrences": 25,
        "verifier_calls": 25
      }
    },
    {
      "query_id": "q000005",
      "query": "gh",
      "length": 2,
      "categories": [
        "exact"
      ],
      "result_count": 1,
      "median_ns": 119800.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 0,
        "tree_lookups": 1,
        "candidate_words": 25,
        "candidate_occurrences": 25,
        "verifier_calls": 25
      }
    },
    {
      "query_id": "q000002",
      "query": "n",
      "length": 1,
      "categories": [
        "exact"
      ],
      "result_count": 29,
      "median_ns": 113900.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 0,
        "tree_lookups": 1,
        "candidate_words": 25,
        "candidate_occurrences": 25,
        "verifier_calls": 25
      }
    },
    {
      "query_id": "q000019",
      "query": "jklmn",
      "length": 5,
      "categories": [
        "exact"
      ],
      "result_count": 0,
      "median_ns": 27500.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000024",
      "query": "bounda",
      "length": 6,
      "categories": [
        "exact"
      ],
      "result_count": 3,
      "median_ns": 24500.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000018",
      "query": "s cro",
      "length": 5,
      "categories": [
        "exact"
      ],
      "result_count": 0,
      "median_ns": 23300.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000010",
      "query": "aaa",
      "length": 3,
      "categories": [
        "exact"
      ],
      "result_count": 3,
      "median_ns": 22000.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 1,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000015",
      "query": "icie",
      "length": 4,
      "categories": [
        "exact"
      ],
      "result_count": 0,
      "median_ns": 22000.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 2,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000011",
      "query": "dar",
      "length": 3,
      "categories": [
        "exact"
      ],
      "result_count": 0,
      "median_ns": 21300.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 1,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000016",
      "query": "mark",
      "length": 4,
      "categories": [
        "exact"
      ],
      "result_count": 0,
      "median_ns": 20000.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 2,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000021",
      "query": "eplace",
      "length": 6,
      "categories": [
        "exact"
      ],
      "result_count": 1,
      "median_ns": 19900.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000012",
      "query": "for",
      "length": 3,
      "categories": [
        "exact"
      ],
      "result_count": 2,
      "median_ns": 19600.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 1,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000017",
      "query": "pqrst",
      "length": 5,
      "categories": [
        "exact"
      ],
      "result_count": 0,
      "median_ns": 17100.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000020",
      "query": "undar",
      "length": 5,
      "categories": [
        "exact"
      ],
      "result_count": 0,
      "median_ns": 16500.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000014",
      "query": "hmar",
      "length": 4,
      "categories": [
        "exact"
      ],
      "result_count": 0,
      "median_ns": 15300.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 2,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000009",
      "query": "xyz",
      "length": 3,
      "categories": [
        "exact"
      ],
      "result_count": 0,
      "median_ns": 14600.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 1,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000022",
      "query": "ulti w",
      "length": 6,
      "categories": [
        "exact"
      ],
      "result_count": 0,
      "median_ns": 12000.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000023",
      "query": "are mu",
      "length": 6,
      "categories": [
        "exact"
      ],
      "result_count": 0,
      "median_ns": 10700.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000013",
      "query": "c be",
      "length": 4,
      "categories": [
        "exact"
      ],
      "result_count": 0,
      "median_ns": 7500.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 2,
        "tree_lookups": 1,
        "candidate_words": 0,
        "candidate_occurrences": 0,
        "verifier_calls": 0
      }
    }
  ],
  "bi_anchor": [
    {
      "query_id": "q000016",
      "query": "mark",
      "length": 4,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 1505800.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 621,
        "candidate_contexts_after_dedup": 621,
        "verifier_calls": 621,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000011",
      "query": "dar",
      "length": 3,
      "categories": [
        "exact"
      ],
      "result_count": 9,
      "median_ns": 1485400.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 630,
        "candidate_contexts_after_dedup": 630,
        "verifier_calls": 630,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000015",
      "query": "icie",
      "length": 4,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 1224400.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 621,
        "candidate_contexts_after_dedup": 621,
        "verifier_calls": 621,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000020",
      "query": "undar",
      "length": 5,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 1127700.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 612,
        "candidate_contexts_after_dedup": 612,
        "verifier_calls": 612,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000017",
      "query": "pqrst",
      "length": 5,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 1082700.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 612,
        "candidate_contexts_after_dedup": 612,
        "verifier_calls": 612,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000018",
      "query": "s cro",
      "length": 5,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 1073700.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 612,
        "candidate_contexts_after_dedup": 612,
        "verifier_calls": 612,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000019",
      "query": "jklmn",
      "length": 5,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 1071600.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 612,
        "candidate_contexts_after_dedup": 612,
        "verifier_calls": 612,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000013",
      "query": "c be",
      "length": 4,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 1033900.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 621,
        "candidate_contexts_after_dedup": 621,
        "verifier_calls": 621,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000009",
      "query": "xyz",
      "length": 3,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 1013000.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 630,
        "candidate_contexts_after_dedup": 630,
        "verifier_calls": 630,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000008",
      "query": "lt",
      "length": 2,
      "categories": [
        "exact"
      ],
      "result_count": 42,
      "median_ns": 1004400.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 639,
        "candidate_contexts_after_dedup": 639,
        "verifier_calls": 639,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000014",
      "query": "hmar",
      "length": 4,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 989700.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 621,
        "candidate_contexts_after_dedup": 621,
        "verifier_calls": 621,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000012",
      "query": "for",
      "length": 3,
      "categories": [
        "exact"
      ],
      "result_count": 9,
      "median_ns": 956900.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 630,
        "candidate_contexts_after_dedup": 630,
        "verifier_calls": 630,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000004",
      "query": "i",
      "length": 1,
      "categories": [
        "exact"
      ],
      "result_count": 240,
      "median_ns": 953900.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 429,
        "candidate_contexts_after_dedup": 429,
        "verifier_calls": 429,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000010",
      "query": "aaa",
      "length": 3,
      "categories": [
        "exact"
      ],
      "result_count": 25,
      "median_ns": 923300.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 630,
        "candidate_contexts_after_dedup": 630,
        "verifier_calls": 630,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000005",
      "query": "gh",
      "length": 2,
      "categories": [
        "exact"
      ],
      "result_count": 14,
      "median_ns": 891700.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 639,
        "candidate_contexts_after_dedup": 639,
        "verifier_calls": 639,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000007",
      "query": "cr",
      "length": 2,
      "categories": [
        "exact"
      ],
      "result_count": 50,
      "median_ns": 860600.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 639,
        "candidate_contexts_after_dedup": 639,
        "verifier_calls": 639,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000006",
      "query": "te",
      "length": 2,
      "categories": [
        "exact"
      ],
      "result_count": 80,
      "median_ns": 846300.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 639,
        "candidate_contexts_after_dedup": 639,
        "verifier_calls": 639,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000003",
      "query": "y",
      "length": 1,
      "categories": [
        "exact"
      ],
      "result_count": 222,
      "median_ns": 749800.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 429,
        "candidate_contexts_after_dedup": 429,
        "verifier_calls": 429,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000002",
      "query": "n",
      "length": 1,
      "categories": [
        "exact"
      ],
      "result_count": 254,
      "median_ns": 607800.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 429,
        "candidate_contexts_after_dedup": 429,
        "verifier_calls": 429,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000001",
      "query": "u",
      "length": 1,
      "categories": [
        "exact"
      ],
      "result_count": 228,
      "median_ns": 576500.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 429,
        "candidate_contexts_after_dedup": 429,
        "verifier_calls": 429,
        "selected_seed_frequency_sum": 0,
        "last_selected_q": null,
        "last_pair_cost_by_q": {},
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000021",
      "query": "eplace",
      "length": 6,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 99400.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 2,
        "candidate_contexts_generated": 18,
        "candidate_contexts_after_dedup": 9,
        "verifier_calls": 9,
        "selected_seed_frequency_sum": 2,
        "last_selected_q": 3,
        "last_pair_cost_by_q": {
          "3": 2
        },
        "selected_q_counts": {
          "3": 2
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "q000023",
      "query": "are mu",
      "length": 6,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 94400.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 2,
        "candidate_contexts_generated": 18,
        "candidate_contexts_after_dedup": 9,
        "verifier_calls": 9,
        "selected_seed_frequency_sum": 2,
        "last_selected_seeds": [
          {
            "text": "are",
            "query_start": 0,
            "query_end": 3,
            "frequency": 1
          },
          {
            "text": " mu",
            "query_start": 3,
            "query_end": 6,
            "frequency": 1
          }
        ],
        "last_selected_q": 0,
        "selected_q_counts": {
          "3": 4
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "q000022",
      "query": "ulti w",
      "length": 6,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 82200.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 2,
        "candidate_contexts_generated": 18,
        "candidate_contexts_after_dedup": 9,
        "verifier_calls": 9,
        "selected_seed_frequency_sum": 2,
        "last_selected_seeds": [
          {
            "text": "ult",
            "query_start": 0,
            "query_end": 3,
            "frequency": 1
          },
          {
            "text": "i w",
            "query_start": 3,
            "query_end": 6,
            "frequency": 1
          }
        ],
        "last_selected_q": 0,
        "selected_q_counts": {
          "3": 3
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "q000024",
      "query": "bounda",
      "length": 6,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 78600.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 2,
        "candidate_contexts_generated": 18,
        "candidate_contexts_after_dedup": 9,
        "verifier_calls": 9,
        "selected_seed_frequency_sum": 2,
        "last_selected_seeds": [
          {
            "text": "bou",
            "query_start": 0,
            "query_end": 3,
            "frequency": 1
          },
          {
            "text": "nda",
            "query_start": 3,
            "query_end": 6,
            "frequency": 1
          }
        ],
        "last_selected_q": 0,
        "selected_q_counts": {
          "3": 5
        },
        "q_candidates_evaluated": 1
      }
    }
  ]
}
```

# Best Queries

```json
{
  "qgram_verifier": [
    {
      "query_id": "q000023",
      "query": "are mu",
      "speedup_vs_naive": 28.64033264033264,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "posting_lists_accessed": 4,
        "posting_entries_scanned": 4,
        "candidate_starts_before_dedup": 12,
        "candidate_starts_after_dedup": 3,
        "target_contexts": 9,
        "verifier_calls": 9,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000022",
      "query": "ulti w",
      "speedup_vs_naive": 27.03921568627451,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "posting_lists_accessed": 4,
        "posting_entries_scanned": 4,
        "candidate_starts_before_dedup": 12,
        "candidate_starts_after_dedup": 3,
        "target_contexts": 9,
        "verifier_calls": 9,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000024",
      "query": "bounda",
      "speedup_vs_naive": 25.162337662337663,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "posting_lists_accessed": 4,
        "posting_entries_scanned": 4,
        "candidate_starts_before_dedup": 12,
        "candidate_starts_after_dedup": 3,
        "target_contexts": 9,
        "verifier_calls": 9,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000021",
      "query": "eplace",
      "speedup_vs_naive": 24.751984126984127,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "posting_lists_accessed": 4,
        "posting_entries_scanned": 4,
        "candidate_starts_before_dedup": 12,
        "candidate_starts_after_dedup": 3,
        "target_contexts": 9,
        "verifier_calls": 9,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000019",
      "query": "jklmn",
      "speedup_vs_naive": 24.70762711864407,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "posting_lists_accessed": 4,
        "posting_entries_scanned": 4,
        "candidate_starts_before_dedup": 12,
        "candidate_starts_after_dedup": 3,
        "target_contexts": 9,
        "verifier_calls": 9,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000017",
      "query": "pqrst",
      "speedup_vs_naive": 15.972972972972974,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "posting_lists_accessed": 4,
        "posting_entries_scanned": 5,
        "candidate_starts_before_dedup": 15,
        "candidate_starts_after_dedup": 6,
        "target_contexts": 18,
        "verifier_calls": 18,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000013",
      "query": "c be",
      "speedup_vs_naive": 14.56638418079096,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "posting_lists_accessed": 3,
        "posting_entries_scanned": 4,
        "candidate_starts_before_dedup": 12,
        "candidate_starts_after_dedup": 6,
        "target_contexts": 18,
        "verifier_calls": 18,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000016",
      "query": "mark",
      "speedup_vs_naive": 13.664785553047404,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "posting_lists_accessed": 3,
        "posting_entries_scanned": 5,
        "candidate_starts_before_dedup": 15,
        "candidate_starts_after_dedup": 9,
        "target_contexts": 27,
        "verifier_calls": 27,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000015",
      "query": "icie",
      "speedup_vs_naive": 12.535686876438987,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "posting_lists_accessed": 3,
        "posting_entries_scanned": 5,
        "candidate_starts_before_dedup": 15,
        "candidate_starts_after_dedup": 9,
        "target_contexts": 26,
        "verifier_calls": 26,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000014",
      "query": "hmar",
      "speedup_vs_naive": 11.958637469586375,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "posting_lists_accessed": 3,
        "posting_entries_scanned": 5,
        "candidate_starts_before_dedup": 15,
        "candidate_starts_after_dedup": 9,
        "target_contexts": 27,
        "verifier_calls": 27,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000009",
      "query": "xyz",
      "speedup_vs_naive": 11.922972972972973,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "posting_lists_accessed": 3,
        "posting_entries_scanned": 5,
        "candidate_starts_before_dedup": 15,
        "candidate_starts_after_dedup": 9,
        "target_contexts": 27,
        "verifier_calls": 27,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000020",
      "query": "undar",
      "speedup_vs_naive": 8.681034482758621,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "posting_lists_accessed": 4,
        "posting_entries_scanned": 8,
        "candidate_starts_before_dedup": 24,
        "candidate_starts_after_dedup": 15,
        "target_contexts": 44,
        "verifier_calls": 44,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000005",
      "query": "gh",
      "speedup_vs_naive": 6.800324675324675,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 2,
        "posting_lists_accessed": 2,
        "posting_entries_scanned": 7,
        "candidate_starts_before_dedup": 21,
        "candidate_starts_after_dedup": 17,
        "target_contexts": 48,
        "verifier_calls": 48,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000018",
      "query": "s cro",
      "speedup_vs_naive": 6.734513274336283,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "posting_lists_accessed": 4,
        "posting_entries_scanned": 7,
        "candidate_starts_before_dedup": 21,
        "candidate_starts_after_dedup": 12,
        "target_contexts": 36,
        "verifier_calls": 36,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000011",
      "query": "dar",
      "speedup_vs_naive": 2.883806928766057,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "posting_lists_accessed": 3,
        "posting_entries_scanned": 37,
        "candidate_starts_before_dedup": 111,
        "candidate_starts_after_dedup": 79,
        "target_contexts": 230,
        "verifier_calls": 230,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000010",
      "query": "aaa",
      "speedup_vs_naive": 2.5533517449158927,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "posting_lists_accessed": 3,
        "posting_entries_scanned": 39,
        "candidate_starts_before_dedup": 117,
        "candidate_starts_after_dedup": 42,
        "target_contexts": 120,
        "verifier_calls": 120,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000008",
      "query": "lt",
      "speedup_vs_naive": 2.5016452288363746,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 2,
        "posting_lists_accessed": 2,
        "posting_entries_scanned": 20,
        "candidate_starts_before_dedup": 60,
        "candidate_starts_after_dedup": 52,
        "target_contexts": 156,
        "verifier_calls": 156,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000012",
      "query": "for",
      "speedup_vs_naive": 1.9462196612537106,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "posting_lists_accessed": 3,
        "posting_entries_scanned": 35,
        "candidate_starts_before_dedup": 105,
        "candidate_starts_after_dedup": 84,
        "target_contexts": 252,
        "verifier_calls": 252,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000007",
      "query": "cr",
      "speedup_vs_naive": 1.7963860731599823,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 2,
        "posting_lists_accessed": 2,
        "posting_entries_scanned": 25,
        "candidate_starts_before_dedup": 75,
        "candidate_starts_after_dedup": 69,
        "target_contexts": 207,
        "verifier_calls": 207,
        "fallback_count": 0
      }
    },
    {
      "query_id": "q000006",
      "query": "te",
      "speedup_vs_naive": 1.4018062397372741,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 2,
        "posting_lists_accessed": 2,
        "posting_entries_scanned": 37,
        "candidate_starts_before_dedup": 111,
        "candidate_starts_after_dedup": 89,
        "target_contexts": 266,
        "verifier_calls": 266,
        "fallback_count": 0
      }
    }
  ],
  "qgram_tree_hybrid": [
    {
      "query_id": "q000013",
      "query": "c be",
      "speedup_vs_naive": 137.50666666666666,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 2,
        "tree_lookups": 1,
        "candidate_words": 0,
        "candidate_occurrences": 0,
        "verifier_calls": 0
      }
    },
    {
      "query_id": "q000023",
      "query": "are mu",
      "speedup_vs_naive": 128.74766355140187,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000022",
      "query": "ulti w",
      "speedup_vs_naive": 114.91666666666667,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000015",
      "query": "icie",
      "speedup_vs_naive": 74.24545454545455,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 2,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000011",
      "query": "dar",
      "speedup_vs_naive": 69.56338028169014,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 1,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000020",
      "query": "undar",
      "speedup_vs_naive": 67.13333333333334,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000017",
      "query": "pqrst",
      "speedup_vs_naive": 65.66666666666667,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000014",
      "query": "hmar",
      "speedup_vs_naive": 64.2483660130719,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 2,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000021",
      "query": "eplace",
      "speedup_vs_naive": 62.688442211055275,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000016",
      "query": "mark",
      "speedup_vs_naive": 60.535,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 2,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000009",
      "query": "xyz",
      "speedup_vs_naive": 60.43150684931507,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 1,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000012",
      "query": "for",
      "speedup_vs_naive": 56.86734693877551,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 1,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000024",
      "query": "bounda",
      "speedup_vs_naive": 47.44897959183673,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000010",
      "query": "aaa",
      "speedup_vs_naive": 46.22727272727273,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 1,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000018",
      "query": "s cro",
      "speedup_vs_naive": 45.72532188841202,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000019",
      "query": "jklmn",
      "speedup_vs_naive": 42.407272727272726,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "q000005",
      "query": "gh",
      "speedup_vs_naive": 6.993322203672788,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 0,
        "tree_lookups": 1,
        "candidate_words": 25,
        "candidate_occurrences": 25,
        "verifier_calls": 25
      }
    },
    {
      "query_id": "q000008",
      "query": "lt",
      "speedup_vs_naive": 6.755250403877222,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 0,
        "tree_lookups": 1,
        "candidate_words": 25,
        "candidate_occurrences": 25,
        "verifier_calls": 25
      }
    },
    {
      "query_id": "q000006",
      "query": "te",
      "speedup_vs_naive": 6.058907026259758,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 0,
        "tree_lookups": 1,
        "candidate_words": 25,
        "candidate_occurrences": 25,
        "verifier_calls": 25
      }
    },
    {
      "query_id": "q000007",
      "query": "cr",
      "speedup_vs_naive": 6.002945508100147,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 0,
        "tree_lookups": 1,
        "candidate_words": 25,
        "candidate_occurrences": 25,
        "verifier_calls": 25
      }
    }
  ],
  "bi_anchor": [
    {
      "query_id": "q000022",
      "query": "ulti w",
      "speedup_vs_naive": 16.776155717761558,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 2,
        "candidate_contexts_generated": 18,
        "candidate_contexts_after_dedup": 9,
        "verifier_calls": 9,
        "selected_seed_frequency_sum": 2,
        "last_selected_seeds": [
          {
            "text": "ult",
            "query_start": 0,
            "query_end": 3,
            "frequency": 1
          },
          {
            "text": "i w",
            "query_start": 3,
            "query_end": 6,
            "frequency": 1
          }
        ],
        "last_selected_q": 0,
        "selected_q_counts": {
          "3": 3
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "q000024",
      "query": "bounda",
      "speedup_vs_naive": 14.790076335877863,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 2,
        "candidate_contexts_generated": 18,
        "candidate_contexts_after_dedup": 9,
        "verifier_calls": 9,
        "selected_seed_frequency_sum": 2,
        "last_selected_seeds": [
          {
            "text": "bou",
            "query_start": 0,
            "query_end": 3,
            "frequency": 1
          },
          {
            "text": "nda",
            "query_start": 3,
            "query_end": 6,
            "frequency": 1
          }
        ],
        "last_selected_q": 0,
        "selected_q_counts": {
          "3": 5
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "q000023",
      "query": "are mu",
      "speedup_vs_naive": 14.59322033898305,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 2,
        "candidate_contexts_generated": 18,
        "candidate_contexts_after_dedup": 9,
        "verifier_calls": 9,
        "selected_seed_frequency_sum": 2,
        "last_selected_seeds": [
          {
            "text": "are",
            "query_start": 0,
            "query_end": 3,
            "frequency": 1
          },
          {
            "text": " mu",
            "query_start": 3,
            "query_end": 6,
            "frequency": 1
          }
        ],
        "last_selected_q": 0,
        "selected_q_counts": {
          "3": 4
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "q000021",
      "query": "eplace",
      "speedup_vs_naive": 12.550301810865191,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 2,
        "candidate_contexts_generated": 18,
        "candidate_contexts_after_dedup": 9,
        "verifier_calls": 9,
        "selected_seed_frequency_sum": 2,
        "last_selected_q": 3,
        "last_pair_cost_by_q": {
          "3": 2
        },
        "selected_q_counts": {
          "3": 2
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "q000001",
      "query": "u",
      "speedup_vs_naive": 1.3746747614917607,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 429,
        "candidate_contexts_after_dedup": 429,
        "verifier_calls": 429,
        "selected_seed_frequency_sum": 0,
        "last_selected_q": null,
        "last_pair_cost_by_q": {},
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000015",
      "query": "icie",
      "speedup_vs_naive": 1.3340411630186213,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 621,
        "candidate_contexts_after_dedup": 621,
        "verifier_calls": 621,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000003",
      "query": "y",
      "speedup_vs_naive": 1.1785809549213124,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 429,
        "candidate_contexts_after_dedup": 429,
        "verifier_calls": 429,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000012",
      "query": "for",
      "speedup_vs_naive": 1.164803009718884,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 630,
        "candidate_contexts_after_dedup": 630,
        "verifier_calls": 630,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000010",
      "query": "aaa",
      "speedup_vs_naive": 1.101483808079714,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 630,
        "candidate_contexts_after_dedup": 630,
        "verifier_calls": 630,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000019",
      "query": "jklmn",
      "speedup_vs_naive": 1.0882792086599478,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 612,
        "candidate_contexts_after_dedup": 612,
        "verifier_calls": 612,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000017",
      "query": "pqrst",
      "speedup_vs_naive": 1.0371293987254087,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 612,
        "candidate_contexts_after_dedup": 612,
        "verifier_calls": 612,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000006",
      "query": "te",
      "speedup_vs_naive": 1.0087439442278152,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 639,
        "candidate_contexts_after_dedup": 639,
        "verifier_calls": 639,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000011",
      "query": "dar",
      "speedup_vs_naive": 0.9975090884610206,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 630,
        "candidate_contexts_after_dedup": 630,
        "verifier_calls": 630,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000013",
      "query": "c be",
      "speedup_vs_naive": 0.9974852500241803,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 621,
        "candidate_contexts_after_dedup": 621,
        "verifier_calls": 621,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000014",
      "query": "hmar",
      "speedup_vs_naive": 0.9932302717995352,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 621,
        "candidate_contexts_after_dedup": 621,
        "verifier_calls": 621,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000018",
      "query": "s cro",
      "speedup_vs_naive": 0.9922697215237031,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 612,
        "candidate_contexts_after_dedup": 612,
        "verifier_calls": 612,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000002",
      "query": "n",
      "speedup_vs_naive": 0.9828891082592959,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 429,
        "candidate_contexts_after_dedup": 429,
        "verifier_calls": 429,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000020",
      "query": "undar",
      "speedup_vs_naive": 0.9822647867340605,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 612,
        "candidate_contexts_after_dedup": 612,
        "verifier_calls": 612,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000007",
      "query": "cr",
      "speedup_vs_naive": 0.9472461073669532,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 639,
        "candidate_contexts_after_dedup": 639,
        "verifier_calls": 639,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "q000005",
      "query": "gh",
      "speedup_vs_naive": 0.9395536615453628,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 0,
        "fallback_count": 1,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 639,
        "candidate_contexts_after_dedup": 639,
        "verifier_calls": 639,
        "selected_seed_frequency_sum": 0,
        "q_candidates_evaluated": 0
      }
    }
  ]
}
```

# Internal Work Metrics

Worst/best entries above include their stored counters. The complete per-query data is in `internal_work_metrics.json`; no search was rerun to create this report.

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
Cheapest measured build: `naive`.
Least approximate retained/index memory: `naive`.
Q-Gram + Verifier correctness: all checked raw result sets matched Naive.
Q-Gram + Tree Hybrid correctness: INCORRECT on 24 queries; FN=1102, FP=0.
Selective Bi-Anchor correctness: all checked raw result sets matched Naive.
Optimized algorithms that lost or added raw matches: qgram_tree_hybrid.
Algorithms with zero per-query wins in this workload: qgram_tree_hybrid; this is the measured dominance indicator, not a proof for every workload.
Largest measured latency bottleneck: `naive` on query `icie` at 1.633 ms; its stored work counters are `{"query_count": 1, "verifier_calls": 621}`.
Correctness is based on the retained timed Naive result; no separate Naive oracle search was run.
Next experiment: target the largest counter in the worst stored correct-algorithm case, then rerun the saved `queries.json` without changing match semantics.

Algorithm redesign is outside this benchmark run.
