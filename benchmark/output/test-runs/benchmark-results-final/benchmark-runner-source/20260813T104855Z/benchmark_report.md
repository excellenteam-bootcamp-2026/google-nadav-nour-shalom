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
  "timestamp_utc": "2026-08-13T10:48:55.045343+00:00",
  "python_version": "3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]",
  "platform": "Windows-11-10.0.26200-SP0",
  "cpu": "Intel64 Family 6 Model 140 Stepping 1, GenuineIntel",
  "process_architecture": "64bit",
  "git_branch": "adaptive-multi-q-bi-anchor",
  "git_commit_sha": "c95961417ecf0f6a14fc0516ed509da56b8f3486",
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
  "preparation_time_ns": 3137400,
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
| Q-Gram + Verifier | 0.550 | 0.550 | 0.550 | 0.550 |
| Q-Gram + Tree Hybrid | 0.331 | 0.331 | 0.331 | 0.331 |
| Selective Bi-Anchor | 0.493 | 0.493 | 0.493 | 0.493 |

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
| Naive | 1.554 | 1.683 | 2.396 | 4.085 | 4.085 |
| Q-Gram + Verifier | 0.179 | 0.453 | 1.345 | 1.395 | 1.395 |
| Q-Gram + Tree Hybrid | 0.040 | 0.098 | 0.307 | 0.335 | 0.335 |
| Selective Bi-Anchor | 1.233 | 1.671 | 4.184 | 5.127 | 5.127 |

# Query Length 1–6

| Length | N | Naive med/p95 | QG+V med/p95 | Tree med/p95 | Bi med/p95 | Fastest correct | Winner % | Correct N/Q/T/B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 4 | 1.250 / 4.085 | 1.280 / 1.395 | 0.270 / 0.335 | 1.223 / 1.247 | bi_anchor | 50.00% | 4/4/0/4 |
| 2 | 4 | 1.061 / 1.202 | 0.507 / 0.708 | 0.189 / 0.200 | 1.155 / 1.233 | qgram_verifier | 100.00% | 4/4/0/4 |
| 3 | 4 | 1.563 / 2.135 | 0.592 / 0.962 | 0.027 / 0.046 | 1.262 / 1.895 | qgram_verifier | 100.00% | 4/4/0/4 |
| 4 | 4 | 1.472 / 2.074 | 0.143 / 0.145 | 0.030 / 0.037 | 3.254 / 5.127 | qgram_verifier | 100.00% | 4/4/0/4 |
| 5 | 4 | 1.715 / 2.396 | 0.169 / 0.334 | 0.040 / 0.046 | 3.007 / 3.877 | qgram_verifier | 100.00% | 4/4/0/4 |
| 6 | 4 | 2.157 / 2.325 | 0.077 / 0.089 | 0.028 / 0.044 | 0.146 / 0.162 | qgram_verifier | 100.00% | 4/4/0/4 |

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
| exact | 24 | 1.554 / 2.396 | 0.179 / 1.345 | 0.040 / 0.307 | 1.233 / 4.184 | qgram_verifier | 83.33% | 24/24/0/24 |
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
| 1-5 | 13 | 1.653 | 0.105 | 0.032 | 1.578 |
| 6-20 | 3 | 1.566 | 0.806 | 0.046 | 1.399 |
| 21-100 | 4 | 1.151 | 0.507 | 0.189 | 1.175 |
| 101-1000 | 4 | 1.250 | 1.280 | 0.270 | 1.223 |
| 1000+ | 0 | 0.000 | 0.000 | 0.000 | 0.000 |

# Win Rates

| Algorithm | Wins | Percent |
| --- | --- | --- |
| Naive | 1 | 4.17% |
| Q-Gram + Verifier | 20 | 83.33% |
| Q-Gram + Tree Hybrid | 0 | 0.00% |
| Selective Bi-Anchor | 2 | 8.33% |
| Ties | 1 | 4.17% |

# Speedup vs Naive

```json
{
  "qgram_verifier": {
    "median": 7.0138000826616675,
    "mean": 10.01915462755399,
    "p75": 14.607042253521128,
    "p90": 23.123180291153414,
    "best": 30.2,
    "worst": 0.900126422250316
  },
  "qgram_tree_hybrid": {
    "median": 47.02082084653367,
    "mean": 41.17923816650715,
    "p75": 56.05945945945946,
    "p90": 69.35326086956522,
    "best": 105.35204081632654,
    "worst": 3.851553166069295
  },
  "bi_anchor": {
    "median": 0.9986569929682076,
    "mean": 3.2096333766811296,
    "p75": 1.1263585522844781,
    "p90": 13.920173267326733,
    "best": 15.722785665990534,
    "worst": 0.28305897955999376
  }
}
```

# Worst Queries

```json
{
  "naive": [
    {
      "query_id": "q000004",
      "query": "i",
      "length": 1,
      "categories": [
        "exact"
      ],
      "result_count": 240,
      "median_ns": 4085400.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 429
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
      "median_ns": 2395700.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 612
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
      "median_ns": 2325400.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 603
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
      "median_ns": 2249500.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 603
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
      "median_ns": 2134900.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 630
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
      "median_ns": 2074200.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 621
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
      "median_ns": 2064900.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 603
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
      "median_ns": 1872900.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 612
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
      "median_ns": 1653500.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 603
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
      "median_ns": 1566200.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 630
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
      "median_ns": 1560400.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 630
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
      "median_ns": 1557300.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 612
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
      "median_ns": 1551700.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 612
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
      "median_ns": 1493600.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 621
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
      "median_ns": 1451300.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 621
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
      "median_ns": 1289500.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 429
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
      "median_ns": 1276100.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 621
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
      "median_ns": 1210400.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 429
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
      "median_ns": 1201800.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 639
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
      "median_ns": 1145600.0,
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
      "median_ns": 1117500.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 630
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
      "median_ns": 1100000.0,
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
      "median_ns": 1021800.0,
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
      "median_ns": 985600.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 639
      }
    }
  ],
  "qgram_verifier": [
    {
      "query_id": "q000002",
      "query": "n",
      "length": 1,
      "categories": [
        "exact"
      ],
      "result_count": 254,
      "median_ns": 1395000.0,
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
      "median_ns": 1344700.0,
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
      "median_ns": 1216100.0,
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
      "query_id": "q000004",
      "query": "i",
      "length": 1,
      "categories": [
        "exact"
      ],
      "result_count": 240,
      "median_ns": 1186100.0,
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
      "query_id": "q000012",
      "query": "for",
      "length": 3,
      "categories": [
        "exact"
      ],
      "result_count": 9,
      "median_ns": 961900.0,
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
      "median_ns": 806000.0,
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
      "query_id": "q000006",
      "query": "te",
      "length": 2,
      "categories": [
        "exact"
      ],
      "result_count": 80,
      "median_ns": 708100.0,
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
      "query_id": "q000007",
      "query": "cr",
      "length": 2,
      "categories": [
        "exact"
      ],
      "result_count": 50,
      "median_ns": 535100.0,
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
      "query_id": "q000008",
      "query": "lt",
      "length": 2,
      "categories": [
        "exact"
      ],
      "result_count": 42,
      "median_ns": 478600.0,
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
      "query_id": "q000010",
      "query": "aaa",
      "length": 3,
      "categories": [
        "exact"
      ],
      "result_count": 25,
      "median_ns": 378400.0,
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
      "query_id": "q000018",
      "query": "s cro",
      "length": 5,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 333900.0,
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
      "query_id": "q000020",
      "query": "undar",
      "length": 5,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 199100.0,
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
      "median_ns": 158100.0,
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
      "median_ns": 145000.0,
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
      "median_ns": 144200.0,
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
      "length": 4,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 142000.0,
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
      "query_id": "q000017",
      "query": "pqrst",
      "length": 5,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 138700.0,
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
      "length": 4,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 104700.0,
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
      "query_id": "q000022",
      "query": "ulti w",
      "length": 6,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 89300.0,
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
      "query_id": "q000009",
      "query": "xyz",
      "length": 3,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 88300.0,
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
      "query_id": "q000019",
      "query": "jklmn",
      "length": 5,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 88200.0,
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
      "median_ns": 77000.0,
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
      "median_ns": 76300.0,
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
      "median_ns": 72300.0,
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
      "query_id": "q000002",
      "query": "n",
      "length": 1,
      "categories": [
        "exact"
      ],
      "result_count": 29,
      "median_ns": 334800.0,
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
      "median_ns": 307200.0,
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
      "query_id": "q000004",
      "query": "i",
      "length": 1,
      "categories": [
        "exact"
      ],
      "result_count": 26,
      "median_ns": 232600.0,
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
      "median_ns": 222700.0,
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
      "median_ns": 199800.0,
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
      "median_ns": 199400.0,
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
      "median_ns": 177600.0,
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
      "median_ns": 169800.0,
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
      "query_id": "q000018",
      "query": "s cro",
      "length": 5,
      "categories": [
        "exact"
      ],
      "result_count": 0,
      "median_ns": 46000.0,
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
      "query_id": "q000012",
      "query": "for",
      "length": 3,
      "categories": [
        "exact"
      ],
      "result_count": 2,
      "median_ns": 45800.0,
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
      "length": 6,
      "categories": [
        "exact"
      ],
      "result_count": 3,
      "median_ns": 43900.0,
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
      "query_id": "q000019",
      "query": "jklmn",
      "length": 5,
      "categories": [
        "exact"
      ],
      "result_count": 0,
      "median_ns": 42400.0,
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
      "query_id": "q000015",
      "query": "icie",
      "length": 4,
      "categories": [
        "exact"
      ],
      "result_count": 0,
      "median_ns": 37000.0,
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
      "query_id": "q000017",
      "query": "pqrst",
      "length": 5,
      "categories": [
        "exact"
      ],
      "result_count": 0,
      "median_ns": 36900.0,
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
      "median_ns": 34900.0,
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
      "query_id": "q000021",
      "query": "eplace",
      "length": 6,
      "categories": [
        "exact"
      ],
      "result_count": 1,
      "median_ns": 31500.0,
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
      "query_id": "q000014",
      "query": "hmar",
      "length": 4,
      "categories": [
        "exact"
      ],
      "result_count": 0,
      "median_ns": 30600.0,
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
      "median_ns": 29900.0,
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
      "median_ns": 29700.0,
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
      "query_id": "q000023",
      "query": "are mu",
      "length": 6,
      "categories": [
        "exact"
      ],
      "result_count": 0,
      "median_ns": 24600.0,
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
      "length": 3,
      "categories": [
        "exact"
      ],
      "result_count": 3,
      "median_ns": 24000.0,
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
      "query_id": "q000009",
      "query": "xyz",
      "length": 3,
      "categories": [
        "exact"
      ],
      "result_count": 0,
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
      "query_id": "q000022",
      "query": "ulti w",
      "length": 6,
      "categories": [
        "exact"
      ],
      "result_count": 0,
      "median_ns": 19600.0,
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
      "median_ns": 18400.0,
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
      "query_id": "q000014",
      "query": "hmar",
      "length": 4,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 5127200.0,
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
      "query_id": "q000013",
      "query": "c be",
      "length": 4,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 4183800.0,
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
      "length": 5,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 3876500.0,
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
      "median_ns": 3023500.0,
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
      "median_ns": 2989700.0,
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
      "query_id": "q000015",
      "query": "icie",
      "length": 4,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 2323700.0,
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
      "median_ns": 1895400.0,
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
      "query_id": "q000020",
      "query": "undar",
      "length": 5,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 1577900.0,
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
      "query_id": "q000016",
      "query": "mark",
      "length": 4,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 1563800.0,
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
      "median_ns": 1399400.0,
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
      "query_id": "q000003",
      "query": "y",
      "length": 1,
      "categories": [
        "exact"
      ],
      "result_count": 222,
      "median_ns": 1246600.0,
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
      "median_ns": 1234200.0,
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
      "query_id": "q000007",
      "query": "cr",
      "length": 2,
      "categories": [
        "exact"
      ],
      "result_count": 50,
      "median_ns": 1232600.0,
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
      "median_ns": 1225800.0,
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
      "query_id": "q000002",
      "query": "n",
      "length": 1,
      "categories": [
        "exact"
      ],
      "result_count": 254,
      "median_ns": 1211500.0,
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
      "query_id": "q000004",
      "query": "i",
      "length": 1,
      "categories": [
        "exact"
      ],
      "result_count": 240,
      "median_ns": 1149500.0,
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
      "median_ns": 1124100.0,
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
      "query_id": "q000009",
      "query": "xyz",
      "length": 3,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 1086400.0,
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
      "median_ns": 1084900.0,
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
      "length": 2,
      "categories": [
        "exact"
      ],
      "result_count": 14,
      "median_ns": 962900.0,
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
      "query_id": "q000024",
      "query": "bounda",
      "length": 6,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 161600.0,
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
      "length": 6,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 147900.0,
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
      "length": 6,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 143500.0,
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
      "query_id": "q000022",
      "query": "ulti w",
      "length": 6,
      "categories": [
        "exact"
      ],
      "result_count": 5,
      "median_ns": 132200.0,
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
      "speedup_vs_naive": 30.2,
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
      "speedup_vs_naive": 29.482306684141548,
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
      "speedup_vs_naive": 23.123180291153414,
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
      "speedup_vs_naive": 22.869986168741356,
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
      "speedup_vs_naive": 17.656462585034014,
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
      "speedup_vs_naive": 17.272530641672674,
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
      "query_id": "q000015",
      "query": "icie",
      "speedup_vs_naive": 14.607042253521128,
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
      "query_id": "q000009",
      "query": "xyz",
      "speedup_vs_naive": 12.655719139297847,
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
      "speedup_vs_naive": 12.188156638013371,
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
      "speedup_vs_naive": 10.300689655172414,
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
      "speedup_vs_naive": 10.064493758668515,
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
      "speedup_vs_naive": 7.793571069814163,
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
      "speedup_vs_naive": 6.234029095509172,
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
      "speedup_vs_naive": 5.609164420485175,
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
      "query_id": "q000010",
      "query": "aaa",
      "speedup_vs_naive": 4.123678646934461,
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
      "query_id": "q000004",
      "query": "i",
      "speedup_vs_naive": 3.444397605598179,
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
      "query_id": "q000008",
      "query": "lt",
      "speedup_vs_naive": 2.2983702465524445,
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
      "speedup_vs_naive": 2.2194614824825867,
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
      "speedup_vs_naive": 1.9431761786600497,
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
      "speedup_vs_naive": 1.9095496168940385,
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
    }
  ],
  "qgram_tree_hybrid": [
    {
      "query_id": "q000022",
      "query": "ulti w",
      "speedup_vs_naive": 105.35204081632654,
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
      "speedup_vs_naive": 94.52845528455285,
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
      "speedup_vs_naive": 69.35326086956522,
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
      "query_id": "q000010",
      "query": "aaa",
      "speedup_vs_naive": 65.01666666666667,
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
      "speedup_vs_naive": 64.92411924119241,
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
      "query_id": "q000009",
      "query": "xyz",
      "speedup_vs_naive": 57.015306122448976,
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
      "speedup_vs_naive": 56.05945945945946,
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
      "speedup_vs_naive": 52.492063492063494,
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
      "query_id": "q000011",
      "query": "dar",
      "speedup_vs_naive": 52.381270903010034,
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
      "speedup_vs_naive": 51.241457858769934,
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
      "speedup_vs_naive": 50.28956228956229,
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
      "query_id": "q000014",
      "query": "hmar",
      "speedup_vs_naive": 47.428104575163395,
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
      "query_id": "q000012",
      "query": "for",
      "speedup_vs_naive": 46.61353711790393,
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
      "speedup_vs_naive": 44.46131805157593,
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
      "query_id": "q000018",
      "query": "s cro",
      "speedup_vs_naive": 40.71521739130435,
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
      "speedup_vs_naive": 36.72877358490566,
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
      "query_id": "q000004",
      "query": "i",
      "speedup_vs_naive": 17.564058469475494,
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
      "speedup_vs_naive": 6.766891891891892,
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
      "speedup_vs_naive": 5.804475853945819,
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
      "speedup_vs_naive": 5.505505505505505,
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
      "query_id": "q000023",
      "query": "are mu",
      "speedup_vs_naive": 15.722785665990534,
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
      "speedup_vs_naive": 15.619515885022693,
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
      "speedup_vs_naive": 13.920173267326733,
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
      "query_id": "q000021",
      "query": "eplace",
      "speedup_vs_naive": 11.522648083623693,
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
      "query_id": "q000004",
      "query": "i",
      "speedup_vs_naive": 3.554066985645933,
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
      "speedup_vs_naive": 1.3881327284049463,
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
      "query_id": "q000012",
      "query": "for",
      "speedup_vs_naive": 1.1263585522844781,
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
      "query_id": "q000011",
      "query": "dar",
      "speedup_vs_naive": 1.1191939402601114,
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
      "query_id": "q000002",
      "query": "n",
      "speedup_vs_naive": 1.0643829962855964,
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
      "query_id": "q000009",
      "query": "xyz",
      "speedup_vs_naive": 1.0286266568483062,
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
      "speedup_vs_naive": 1.02357461834043,
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
      "query_id": "q000008",
      "query": "lt",
      "speedup_vs_naive": 1.0139183334869573,
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
      "query_id": "q000020",
      "query": "undar",
      "speedup_vs_naive": 0.9833956524494581,
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
      "query_id": "q000001",
      "query": "u",
      "speedup_vs_naive": 0.9807162534435262,
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
      "query_id": "q000006",
      "query": "te",
      "speedup_vs_naive": 0.9804209495839452,
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
      "query_id": "q000016",
      "query": "mark",
      "speedup_vs_naive": 0.955109349021614,
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
      "speedup_vs_naive": 0.9189796245788545,
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
      "query_id": "q000015",
      "query": "icie",
      "speedup_vs_naive": 0.8926281361621552,
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
      "query_id": "q000007",
      "query": "cr",
      "speedup_vs_naive": 0.8289793931526854,
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
      "query_id": "q000017",
      "query": "pqrst",
      "speedup_vs_naive": 0.8013178579790614,
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
  "bi_anchor": 41
}
```

# Conclusions

Fastest overall correct algorithm: `qgram_verifier`.
Best for length 1: `bi_anchor`.
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
Largest measured latency bottleneck: `bi_anchor` on query `hmar` at 5.127 ms; its stored work counters are `{"query_count": 1, "anchored_query_count": 0, "fallback_count": 1, "zero_frequency_returns": 0, "seed_occurrences_expanded": 0, "candidate_contexts_generated": 621, "candidate_contexts_after_dedup": 621, "verifier_calls": 621, "selected_seed_frequency_sum": 0, "q_candidates_evaluated": 0}`.
Correctness is based on the retained timed Naive result; no separate Naive oracle search was run.
Next experiment: target the largest counter in the worst stored correct-algorithm case, then rerun the saved `queries.json` without changing match semantics.

Algorithm redesign is outside this benchmark run.
