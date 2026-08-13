# Benchmark Configuration

> **QUICK BENCHMARK — NOT FINAL PERFORMANCE EVIDENCE**

Mode: **QUICK**  
Queries: 37  
Timing repetitions: 1  
Build repetitions: 1  
Expected timed search executions: 148
Query source: **SAVED**  
Query file: `C:\Users\nours\Desktop\google-nadav-nour-shalom\tests\fixtures\search_correctness_queries.json`  
Query count: 37  
Query file SHA-256: `5c4ceaff28cdc5a77aa0b8c3c23d82aac9aa77b20f6b97e4aec527b136a51558`

# Environment

```json
{
  "timestamp_utc": "2026-08-13T11:36:18.586733+00:00",
  "python_version": "3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]",
  "platform": "Windows-11-10.0.26200-SP0",
  "cpu": "Intel64 Family 6 Model 140 Stepping 1, GenuineIntel",
  "process_architecture": "64bit",
  "git_branch": "main",
  "git_commit_sha": "16abbb94ccb1517377b6101286a6ea65ea8f1846",
  "source_path": "C:\\Users\\nours\\Desktop\\google-nadav-nour-shalom\\tests\\fixtures\\benchmark-runner-source.txt",
  "source_size_bytes": 222,
  "source_sha256": "34e75a13bb48d50d5d4b75fc2195c7a263df05bb405f1b2b50f1bb6c2ed36891",
  "benchmark_mode": "QUICK",
  "benchmark_arguments": {
    "queries": 37,
    "repetitions": 1,
    "build_repetitions": 1,
    "seed": 999,
    "query_file": "tests\\fixtures\\search_correctness_queries.json",
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
  "preparation_time_ns": 14324300,
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
| Naive | 37 | 0 | 0 | 0 |
| Q-Gram + Verifier | 37 | 0 | 0 | 0 |
| Q-Gram + Tree Hybrid | 37 | 7 | 580 | 0 |
| Selective Bi-Anchor | 37 | 0 | 0 | 0 |

# Build Time

| Algorithm | Min ms | Median ms | Mean ms | Max ms |
| --- | --- | --- | --- | --- |
| Naive | 0.015 | 0.015 | 0.015 | 0.015 |
| Q-Gram + Verifier | 0.406 | 0.406 | 0.406 | 0.406 |
| Q-Gram + Tree Hybrid | 0.234 | 0.234 | 0.234 | 0.234 |
| Selective Bi-Anchor | 0.295 | 0.295 | 0.295 | 0.295 |

# Memory

| Algorithm | Peak build B | Retained B | Method |
| --- | --- | --- | --- |
| Naive | 1368 | 1104 | tracemalloc dedicated build |
| Q-Gram + Verifier | 68541 | 68033 | tracemalloc dedicated build |
| Q-Gram + Tree Hybrid | 74947 | 74891 | tracemalloc dedicated build |
| Selective Bi-Anchor | 73176 | 52656 | tracemalloc dedicated build |

# Overall Search Performance

| Algorithm | Median ms | Mean ms | P95 ms | P99 ms | Max ms |
| --- | --- | --- | --- | --- | --- |
| Naive | 1.551 | 1.607 | 2.780 | 2.885 | 2.885 |
| Q-Gram + Verifier | 0.099 | 0.169 | 1.116 | 1.216 | 1.216 |
| Q-Gram + Tree Hybrid | 0.017 | 0.019 | 0.036 | 0.056 | 0.056 |
| Selective Bi-Anchor | 0.076 | 0.625 | 1.898 | 2.263 | 2.263 |

# Query Length 1–6

| Length | N | Naive med/p95 | QG+V med/p95 | Tree med/p95 | Bi med/p95 | Fastest correct | Winner % | Correct N/Q/T/B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2 | 0.959 / 1.131 | 1.166 / 1.216 | 0.022 / 0.025 | 0.984 / 1.198 | naive | 50.00% | 2/2/0/2 |
| 2 | 3 | 0.823 / 1.032 | 0.325 / 0.364 | 0.023 / 0.031 | 0.811 / 1.061 | qgram_verifier | 100.00% | 3/3/0/3 |
| 3 | 2 | 0.894 / 0.899 | 0.458 / 0.575 | 0.025 / 0.026 | 0.905 / 0.930 | qgram_verifier | 50.00% | 2/2/1/2 |
| 4 | 2 | 1.602 / 1.747 | 0.080 / 0.149 | 0.032 / 0.033 | 1.659 / 1.756 | qgram_verifier | 100.00% | 2/2/1/2 |
| 5 | 7 | 1.848 / 1.910 | 0.091 / 0.171 | 0.010 / 0.056 | 1.856 / 2.263 | qgram_tree_hybrid | 85.71% | 7/7/7/7 |
| 6 | 4 | 1.229 / 1.980 | 0.010 / 0.043 | 0.013 / 0.028 | 0.035 / 0.070 | qgram_verifier | 75.00% | 4/4/4/4 |

# Longer Query Length Groups

| Length | N | Naive med/p95 | QG+V med/p95 | Tree med/p95 | Bi med/p95 | Fastest correct | Winner % | Correct N/Q/T/B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 7-8 | 6 | 1.369 / 2.209 | 0.069 / 0.153 | 0.013 / 0.030 | 0.024 / 0.131 | qgram_tree_hybrid | 83.33% | 6/6/6/6 |
| 9-12 | 8 | 2.704 / 2.885 | 0.105 / 0.137 | 0.017 / 0.036 | 0.042 / 0.049 | qgram_tree_hybrid | 100.00% | 8/8/8/8 |
| 13-20 | 2 | 2.199 / 2.389 | 0.136 / 0.147 | 0.016 / 0.018 | 0.065 / 0.076 | qgram_tree_hybrid | 100.00% | 2/2/2/2 |
| 21+ | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |

# Query Categories

| Category | N | Naive med/p95 | QG+V med/p95 | Tree med/p95 | Bi med/p95 | Fastest correct | Winner % | Correct N/Q/T/B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| exact | 25 | 1.574 / 2.646 | 0.099 / 1.116 | 0.017 / 0.036 | 0.758 / 1.898 | qgram_tree_hybrid | 60.00% | 25/25/20/25 |
| whole_word | 12 | 1.718 / 2.885 | 0.099 / 1.216 | 0.024 / 0.056 | 0.414 / 2.263 | qgram_tree_hybrid | 58.33% | 12/12/9/12 |
| inside_word | 5 | 1.551 / 2.189 | 0.083 / 0.128 | 0.010 / 0.015 | 0.027 / 1.898 | qgram_tree_hybrid | 80.00% | 5/5/5/5 |
| cross_word | 12 | 1.945 / 2.646 | 0.091 / 0.171 | 0.015 / 0.030 | 0.042 / 1.861 | qgram_tree_hybrid | 91.67% | 12/12/12/12 |
| replacement | 3 | 1.869 / 2.771 | 0.111 / 0.575 | 0.026 / 0.029 | 0.930 / 1.856 | qgram_tree_hybrid | 66.67% | 3/3/2/3 |
| insertion | 3 | 1.359 / 2.763 | 0.112 / 0.364 | 0.020 / 0.028 | 0.037 / 1.061 | qgram_tree_hybrid | 66.67% | 3/3/2/3 |
| deletion | 3 | 1.522 / 2.885 | 0.063 / 0.109 | 0.017 / 0.018 | 0.049 / 0.099 | qgram_tree_hybrid | 100.00% | 3/3/3/3 |
| repeated | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| common | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| rare | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| high_result_count | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| low_result_count | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| no_match | 3 | 1.319 / 2.389 | 0.008 / 0.147 | 0.011 / 0.018 | 0.021 / 0.076 | qgram_tree_hybrid | 66.67% | 3/3/3/3 |
| near_miss | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| multi_word | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| near_boundary | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| repeated_pattern | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| boundary_near_start | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |
| boundary_near_end | 0 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | insufficient correct data | 0.00% | 0/0/0/0 |

# Match Count Analysis

| Raw matches | N | Naive | QG+V | Tree | Bi |
| --- | --- | --- | --- | --- | --- |
| 0 | 29 | 1.807 | 0.087 | 0.015 | 0.049 |
| 1-5 | 3 | 0.888 | 0.043 | 0.026 | 0.758 |
| 6-20 | 0 | 0.000 | 0.000 | 0.000 | 0.000 |
| 21-100 | 3 | 1.032 | 0.325 | 0.031 | 1.061 |
| 101-1000 | 2 | 0.959 | 1.166 | 0.022 | 0.984 |
| 1000+ | 0 | 0.000 | 0.000 | 0.000 | 0.000 |

# Win Rates

| Algorithm | Wins | Percent |
| --- | --- | --- |
| Naive | 1 | 2.70% |
| Q-Gram + Verifier | 11 | 29.73% |
| Q-Gram + Tree Hybrid | 24 | 64.86% |
| Selective Bi-Anchor | 1 | 2.70% |
| Ties | 0 | 0.00% |

# Speedup vs Naive

```json
{
  "qgram_verifier": {
    "median": 19.536269430051814,
    "mean": 47.55638385190902,
    "p75": 31.991701244813278,
    "p90": 165.70526315789473,
    "best": 205.49180327868854,
    "worst": 0.7056820218677182
  },
  "qgram_tree_hybrid": {
    "median": 113.76436781609195,
    "mean": 108.26079646567545,
    "p75": 156.66666666666666,
    "p90": 187.4047619047619,
    "best": 212.22222222222223,
    "worst": 1.5384615384615385
  },
  "bi_anchor": {
    "median": 16.810502283105023,
    "mean": 28.10313032730058,
    "p75": 58.199074074074076,
    "p90": 64.88992974238876,
    "best": 77.68387096774194,
    "worst": 0.5988349514563107
  }
}
```

# Worst Queries

```json
{
  "naive": [
    {
      "query_id": "deletion",
      "query": "programmking",
      "length": 12,
      "categories": [
        "deletion",
        "whole_word"
      ],
      "result_count": 0,
      "median_ns": 2885300.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 549
      }
    },
    {
      "query_id": "long-exact",
      "query": "programming",
      "length": 11,
      "categories": [
        "exact",
        "whole_word",
        "query_beginning"
      ],
      "result_count": 0,
      "median_ns": 2780500.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 558
      }
    },
    {
      "query_id": "replacement",
      "query": "prograxming",
      "length": 11,
      "categories": [
        "replacement",
        "whole_word"
      ],
      "result_count": 0,
      "median_ns": 2770800.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 558
      }
    },
    {
      "query_id": "insertion",
      "query": "programing",
      "length": 10,
      "categories": [
        "insertion",
        "whole_word"
      ],
      "result_count": 0,
      "median_ns": 2763200.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 567
      }
    },
    {
      "query_id": "hello-cross",
      "query": "hello world",
      "length": 11,
      "categories": [
        "exact",
        "cross_word",
        "many_match"
      ],
      "result_count": 0,
      "median_ns": 2645500.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 558
      }
    },
    {
      "query_id": "between-sentences",
      "query": "gamma programming",
      "length": 17,
      "categories": [
        "no_match",
        "sentence_boundary",
        "cross_word"
      ],
      "result_count": 0,
      "median_ns": 2388600.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 504
      }
    },
    {
      "query_id": "cross-word",
      "query": "ming in",
      "length": 7,
      "categories": [
        "exact",
        "cross_word"
      ],
      "result_count": 0,
      "median_ns": 2208900.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 594
      }
    },
    {
      "query_id": "world-hello",
      "query": "world hello",
      "length": 11,
      "categories": [
        "exact",
        "cross_word",
        "inside_word"
      ],
      "result_count": 0,
      "median_ns": 2188900.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 558
      }
    },
    {
      "query_id": "repeated-words",
      "query": "repeated repeated",
      "length": 17,
      "categories": [
        "exact",
        "cross_word",
        "repeated_qgrams",
        "query_end",
        "sentence_boundary"
      ],
      "result_count": 0,
      "median_ns": 2010100.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 504
      }
    },
    {
      "query_id": "length-6-cross",
      "query": "alpha ",
      "length": 6,
      "categories": [
        "exact",
        "cross_word",
        "query_beginning",
        "sentence_boundary"
      ],
      "result_count": 0,
      "median_ns": 1979500.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 603
      }
    },
    {
      "query_id": "leading-space-cross",
      "query": " beta",
      "length": 5,
      "categories": [
        "exact",
        "cross_word"
      ],
      "result_count": 0,
      "median_ns": 1910000.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 612
      }
    },
    {
      "query_id": "inside-word",
      "query": "gramm",
      "length": 5,
      "categories": [
        "exact",
        "inside_word"
      ],
      "result_count": 0,
      "median_ns": 1874800.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 612
      }
    },
    {
      "query_id": "query-end-replacement",
      "query": "gammx",
      "length": 5,
      "categories": [
        "replacement",
        "query_end",
        "sentence_boundary"
      ],
      "result_count": 0,
      "median_ns": 1868700.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 612
      }
    },
    {
      "query_id": "query-end",
      "query": "gamma",
      "length": 5,
      "categories": [
        "exact",
        "whole_word",
        "query_end",
        "sentence_boundary"
      ],
      "result_count": 0,
      "median_ns": 1847900.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 612
      }
    },
    {
      "query_id": "length-5-whole",
      "query": "alpha",
      "length": 5,
      "categories": [
        "exact",
        "whole_word",
        "query_beginning",
        "sentence_boundary"
      ],
      "result_count": 0,
      "median_ns": 1807000.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 612
      }
    },
    {
      "query_id": "repeated-characters",
      "query": "aaaa",
      "length": 4,
      "categories": [
        "exact",
        "repeated_characters",
        "many_match"
      ],
      "result_count": 21,
      "median_ns": 1747100.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 621
      }
    },
    {
      "query_id": "hello-many",
      "query": "hello",
      "length": 5,
      "categories": [
        "exact",
        "whole_word",
        "many_match"
      ],
      "result_count": 0,
      "median_ns": 1628800.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 612
      }
    },
    {
      "query_id": "beta-gamma",
      "query": "beta gamma",
      "length": 10,
      "categories": [
        "exact",
        "cross_word",
        "query_end",
        "sentence_boundary"
      ],
      "result_count": 0,
      "median_ns": 1574200.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 567
      }
    },
    {
      "query_id": "inside-cross",
      "query": "ello wor",
      "length": 8,
      "categories": [
        "exact",
        "inside_word",
        "cross_word"
      ],
      "result_count": 0,
      "median_ns": 1551000.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 585
      }
    },
    {
      "query_id": "ends-deletion",
      "query": "ends herre",
      "length": 10,
      "categories": [
        "deletion",
        "cross_word",
        "query_end",
        "sentence_boundary",
        "ambiguous_edit"
      ],
      "result_count": 0,
      "median_ns": 1522400.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 567
      }
    },
    {
      "query_id": "length-4",
      "query": "alph",
      "length": 4,
      "categories": [
        "exact",
        "query_beginning"
      ],
      "result_count": 0,
      "median_ns": 1456000.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 621
      }
    },
    {
      "query_id": "ambiguous-deletion",
      "query": "aaaaaaa",
      "length": 7,
      "categories": [
        "deletion",
        "repeated_characters",
        "ambiguous_edit"
      ],
      "result_count": 0,
      "median_ns": 1379100.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 594
      }
    },
    {
      "query_id": "ends-insertion",
      "query": "ends her",
      "length": 8,
      "categories": [
        "insertion",
        "cross_word",
        "query_end",
        "sentence_boundary"
      ],
      "result_count": 0,
      "median_ns": 1359500.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 585
      }
    },
    {
      "query_id": "no-match",
      "query": "qqqqqqqq",
      "length": 8,
      "categories": [
        "no_match",
        "repeated_characters",
        "repeated_qgrams"
      ],
      "result_count": 0,
      "median_ns": 1319100.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 585
      }
    },
    {
      "query_id": "prefix-inside-cross",
      "query": "refix s",
      "length": 7,
      "categories": [
        "exact",
        "inside_word",
        "cross_word"
      ],
      "result_count": 0,
      "median_ns": 1257100.0,
      "internal_work": {
        "query_count": 1,
        "verifier_calls": 594
      }
    }
  ],
  "qgram_verifier": [
    {
      "query_id": "single-word-x",
      "query": "x",
      "length": 1,
      "categories": [
        "exact",
        "whole_word",
        "query_beginning",
        "query_end",
        "sentence_boundary"
      ],
      "result_count": 218,
      "median_ns": 1215600.0,
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
      "query_id": "length-1-many",
      "query": "a",
      "length": 1,
      "categories": [
        "exact",
        "many_match",
        "repeated_characters"
      ],
      "result_count": 239,
      "median_ns": 1115800.0,
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
      "query_id": "replacement-no-shared-qgram",
      "query": "cat",
      "length": 3,
      "categories": [
        "replacement",
        "whole_word"
      ],
      "result_count": 4,
      "median_ns": 575200.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "posting_lists_accessed": 3,
        "posting_entries_scanned": 35,
        "candidate_starts_before_dedup": 105,
        "candidate_starts_after_dedup": 81,
        "target_contexts": 237,
        "verifier_calls": 237,
        "fallback_count": 0
      }
    },
    {
      "query_id": "ambiguous-insertion",
      "query": "aa",
      "length": 2,
      "categories": [
        "insertion",
        "repeated_characters",
        "ambiguous_edit",
        "many_match"
      ],
      "result_count": 55,
      "median_ns": 363700.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 2,
        "posting_lists_accessed": 2,
        "posting_entries_scanned": 26,
        "candidate_starts_before_dedup": 78,
        "candidate_starts_after_dedup": 35,
        "target_contexts": 102,
        "verifier_calls": 102,
        "fallback_count": 0
      }
    },
    {
      "query_id": "length-3",
      "query": "alp",
      "length": 3,
      "categories": [
        "exact",
        "query_beginning"
      ],
      "result_count": 0,
      "median_ns": 341400.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "posting_lists_accessed": 3,
        "posting_entries_scanned": 24,
        "candidate_starts_before_dedup": 72,
        "candidate_starts_after_dedup": 57,
        "target_contexts": 165,
        "verifier_calls": 165,
        "fallback_count": 0
      }
    },
    {
      "query_id": "length-2",
      "query": "al",
      "length": 2,
      "categories": [
        "exact",
        "query_beginning"
      ],
      "result_count": 39,
      "median_ns": 324500.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 2,
        "posting_lists_accessed": 2,
        "posting_entries_scanned": 20,
        "candidate_starts_before_dedup": 60,
        "candidate_starts_after_dedup": 48,
        "target_contexts": 141,
        "verifier_calls": 141,
        "fallback_count": 0
      }
    },
    {
      "query_id": "leading-space-cross",
      "query": " beta",
      "length": 5,
      "categories": [
        "exact",
        "cross_word"
      ],
      "result_count": 0,
      "median_ns": 170600.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "posting_lists_accessed": 4,
        "posting_entries_scanned": 5,
        "candidate_starts_before_dedup": 15,
        "candidate_starts_after_dedup": 12,
        "target_contexts": 36,
        "verifier_calls": 36,
        "fallback_count": 0
      }
    },
    {
      "query_id": "cross-word",
      "query": "ming in",
      "length": 7,
      "categories": [
        "exact",
        "cross_word"
      ],
      "result_count": 0,
      "median_ns": 152600.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 5,
        "posting_lists_accessed": 5,
        "posting_entries_scanned": 4,
        "candidate_starts_before_dedup": 12,
        "candidate_starts_after_dedup": 12,
        "target_contexts": 27,
        "verifier_calls": 27,
        "fallback_count": 0
      }
    },
    {
      "query_id": "repeated-characters",
      "query": "aaaa",
      "length": 4,
      "categories": [
        "exact",
        "repeated_characters",
        "many_match"
      ],
      "result_count": 21,
      "median_ns": 149100.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "posting_lists_accessed": 3,
        "posting_entries_scanned": 12,
        "candidate_starts_before_dedup": 36,
        "candidate_starts_after_dedup": 8,
        "target_contexts": 15,
        "verifier_calls": 15,
        "fallback_count": 0
      }
    },
    {
      "query_id": "between-sentences",
      "query": "gamma programming",
      "length": 17,
      "categories": [
        "no_match",
        "sentence_boundary",
        "cross_word"
      ],
      "result_count": 0,
      "median_ns": 147400.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 15,
        "posting_lists_accessed": 15,
        "posting_entries_scanned": 2,
        "candidate_starts_before_dedup": 6,
        "candidate_starts_after_dedup": 6,
        "target_contexts": 15,
        "verifier_calls": 15,
        "fallback_count": 0
      }
    },
    {
      "query_id": "hello-cross",
      "query": "hello world",
      "length": 11,
      "categories": [
        "exact",
        "cross_word",
        "many_match"
      ],
      "result_count": 0,
      "median_ns": 137300.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 9,
        "posting_lists_accessed": 9,
        "posting_entries_scanned": 4,
        "candidate_starts_before_dedup": 12,
        "candidate_starts_after_dedup": 6,
        "target_contexts": 18,
        "verifier_calls": 18,
        "fallback_count": 0
      }
    },
    {
      "query_id": "query-end",
      "query": "gamma",
      "length": 5,
      "categories": [
        "exact",
        "whole_word",
        "query_end",
        "sentence_boundary"
      ],
      "result_count": 0,
      "median_ns": 131700.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "posting_lists_accessed": 4,
        "posting_entries_scanned": 3,
        "candidate_starts_before_dedup": 9,
        "candidate_starts_after_dedup": 9,
        "target_contexts": 27,
        "verifier_calls": 27,
        "fallback_count": 0
      }
    },
    {
      "query_id": "inside-word",
      "query": "gramm",
      "length": 5,
      "categories": [
        "exact",
        "inside_word"
      ],
      "result_count": 0,
      "median_ns": 127600.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "posting_lists_accessed": 4,
        "posting_entries_scanned": 3,
        "candidate_starts_before_dedup": 9,
        "candidate_starts_after_dedup": 9,
        "target_contexts": 27,
        "verifier_calls": 27,
        "fallback_count": 0
      }
    },
    {
      "query_id": "long-exact",
      "query": "programming",
      "length": 11,
      "categories": [
        "exact",
        "whole_word",
        "query_beginning"
      ],
      "result_count": 0,
      "median_ns": 124700.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 9,
        "posting_lists_accessed": 9,
        "posting_entries_scanned": 2,
        "candidate_starts_before_dedup": 6,
        "candidate_starts_after_dedup": 6,
        "target_contexts": 15,
        "verifier_calls": 15,
        "fallback_count": 0
      }
    },
    {
      "query_id": "repeated-words",
      "query": "repeated repeated",
      "length": 17,
      "categories": [
        "exact",
        "cross_word",
        "repeated_qgrams",
        "query_end",
        "sentence_boundary"
      ],
      "result_count": 0,
      "median_ns": 124600.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 15,
        "posting_lists_accessed": 15,
        "posting_entries_scanned": 16,
        "candidate_starts_before_dedup": 48,
        "candidate_starts_after_dedup": 8,
        "target_contexts": 15,
        "verifier_calls": 15,
        "fallback_count": 0
      }
    },
    {
      "query_id": "insertion",
      "query": "programing",
      "length": 10,
      "categories": [
        "insertion",
        "whole_word"
      ],
      "result_count": 0,
      "median_ns": 111500.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 8,
        "posting_lists_accessed": 8,
        "posting_entries_scanned": 2,
        "candidate_starts_before_dedup": 6,
        "candidate_starts_after_dedup": 6,
        "target_contexts": 15,
        "verifier_calls": 15,
        "fallback_count": 0
      }
    },
    {
      "query_id": "replacement",
      "query": "prograxming",
      "length": 11,
      "categories": [
        "replacement",
        "whole_word"
      ],
      "result_count": 0,
      "median_ns": 111200.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 9,
        "posting_lists_accessed": 9,
        "posting_entries_scanned": 2,
        "candidate_starts_before_dedup": 6,
        "candidate_starts_after_dedup": 6,
        "target_contexts": 15,
        "verifier_calls": 15,
        "fallback_count": 0
      }
    },
    {
      "query_id": "ambiguous-deletion",
      "query": "aaaaaaa",
      "length": 7,
      "categories": [
        "deletion",
        "repeated_characters",
        "ambiguous_edit"
      ],
      "result_count": 0,
      "median_ns": 108900.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 5,
        "posting_lists_accessed": 5,
        "posting_entries_scanned": 15,
        "candidate_starts_before_dedup": 45,
        "candidate_starts_after_dedup": 9,
        "target_contexts": 12,
        "verifier_calls": 12,
        "fallback_count": 0
      }
    },
    {
      "query_id": "world-hello",
      "query": "world hello",
      "length": 11,
      "categories": [
        "exact",
        "cross_word",
        "inside_word"
      ],
      "result_count": 0,
      "median_ns": 99200.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 9,
        "posting_lists_accessed": 9,
        "posting_entries_scanned": 2,
        "candidate_starts_before_dedup": 6,
        "candidate_starts_after_dedup": 6,
        "target_contexts": 15,
        "verifier_calls": 15,
        "fallback_count": 0
      }
    },
    {
      "query_id": "query-end-replacement",
      "query": "gammx",
      "length": 5,
      "categories": [
        "replacement",
        "query_end",
        "sentence_boundary"
      ],
      "result_count": 0,
      "median_ns": 91100.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "posting_lists_accessed": 4,
        "posting_entries_scanned": 2,
        "candidate_starts_before_dedup": 6,
        "candidate_starts_after_dedup": 6,
        "target_contexts": 18,
        "verifier_calls": 18,
        "fallback_count": 0
      }
    },
    {
      "query_id": "hello-many",
      "query": "hello",
      "length": 5,
      "categories": [
        "exact",
        "whole_word",
        "many_match"
      ],
      "result_count": 0,
      "median_ns": 87100.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "posting_lists_accessed": 4,
        "posting_entries_scanned": 3,
        "candidate_starts_before_dedup": 9,
        "candidate_starts_after_dedup": 9,
        "target_contexts": 27,
        "verifier_calls": 27,
        "fallback_count": 0
      }
    },
    {
      "query_id": "inside-cross",
      "query": "ello wor",
      "length": 8,
      "categories": [
        "exact",
        "inside_word",
        "cross_word"
      ],
      "result_count": 0,
      "median_ns": 82600.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 6,
        "posting_lists_accessed": 6,
        "posting_entries_scanned": 4,
        "candidate_starts_before_dedup": 12,
        "candidate_starts_after_dedup": 6,
        "target_contexts": 18,
        "verifier_calls": 18,
        "fallback_count": 0
      }
    },
    {
      "query_id": "deletion",
      "query": "programmking",
      "length": 12,
      "categories": [
        "deletion",
        "whole_word"
      ],
      "result_count": 0,
      "median_ns": 62700.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 10,
        "posting_lists_accessed": 10,
        "posting_entries_scanned": 1,
        "candidate_starts_before_dedup": 3,
        "candidate_starts_after_dedup": 3,
        "target_contexts": 6,
        "verifier_calls": 6,
        "fallback_count": 0
      }
    },
    {
      "query_id": "ends-deletion",
      "query": "ends herre",
      "length": 10,
      "categories": [
        "deletion",
        "cross_word",
        "query_end",
        "sentence_boundary",
        "ambiguous_edit"
      ],
      "result_count": 0,
      "median_ns": 57000.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 8,
        "posting_lists_accessed": 8,
        "posting_entries_scanned": 3,
        "candidate_starts_before_dedup": 9,
        "candidate_starts_after_dedup": 7,
        "target_contexts": 12,
        "verifier_calls": 12,
        "fallback_count": 0
      }
    },
    {
      "query_id": "ends-insertion",
      "query": "ends her",
      "length": 8,
      "categories": [
        "insertion",
        "cross_word",
        "query_end",
        "sentence_boundary"
      ],
      "result_count": 0,
      "median_ns": 54900.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 6,
        "posting_lists_accessed": 6,
        "posting_entries_scanned": 3,
        "candidate_starts_before_dedup": 9,
        "candidate_starts_after_dedup": 7,
        "target_contexts": 13,
        "verifier_calls": 13,
        "fallback_count": 0
      }
    }
  ],
  "qgram_tree_hybrid": [
    {
      "query_id": "length-5-whole",
      "query": "alpha",
      "length": 5,
      "categories": [
        "exact",
        "whole_word",
        "query_beginning",
        "sentence_boundary"
      ],
      "result_count": 0,
      "median_ns": 56000.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "tree_lookups": 1,
        "candidate_words": 0,
        "candidate_occurrences": 0,
        "verifier_calls": 0
      }
    },
    {
      "query_id": "long-exact",
      "query": "programming",
      "length": 11,
      "categories": [
        "exact",
        "whole_word",
        "query_beginning"
      ],
      "result_count": 0,
      "median_ns": 36300.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 9,
        "tree_lookups": 1,
        "candidate_words": 2,
        "candidate_occurrences": 2,
        "verifier_calls": 2
      }
    },
    {
      "query_id": "repeated-characters",
      "query": "aaaa",
      "length": 4,
      "categories": [
        "exact",
        "repeated_characters",
        "many_match"
      ],
      "result_count": 0,
      "median_ns": 32900.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 2,
        "tree_lookups": 1,
        "candidate_words": 4,
        "candidate_occurrences": 4,
        "verifier_calls": 4
      }
    },
    {
      "query_id": "length-4",
      "query": "alph",
      "length": 4,
      "categories": [
        "exact",
        "query_beginning"
      ],
      "result_count": 0,
      "median_ns": 31500.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 2,
        "tree_lookups": 1,
        "candidate_words": 4,
        "candidate_occurrences": 4,
        "verifier_calls": 4
      }
    },
    {
      "query_id": "length-2",
      "query": "al",
      "length": 2,
      "categories": [
        "exact",
        "query_beginning"
      ],
      "result_count": 0,
      "median_ns": 31000.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 0,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "cross-word",
      "query": "ming in",
      "length": 7,
      "categories": [
        "exact",
        "cross_word"
      ],
      "result_count": 0,
      "median_ns": 30300.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 5,
        "tree_lookups": 1,
        "candidate_words": 2,
        "candidate_occurrences": 2,
        "verifier_calls": 2
      }
    },
    {
      "query_id": "replacement",
      "query": "prograxming",
      "length": 11,
      "categories": [
        "replacement",
        "whole_word"
      ],
      "result_count": 0,
      "median_ns": 29500.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 9,
        "tree_lookups": 1,
        "candidate_words": 2,
        "candidate_occurrences": 2,
        "verifier_calls": 2
      }
    },
    {
      "query_id": "insertion",
      "query": "programing",
      "length": 10,
      "categories": [
        "insertion",
        "whole_word"
      ],
      "result_count": 0,
      "median_ns": 28100.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 8,
        "tree_lookups": 1,
        "candidate_words": 2,
        "candidate_occurrences": 2,
        "verifier_calls": 2
      }
    },
    {
      "query_id": "suffix",
      "query": "suffix",
      "length": 6,
      "categories": [
        "exact",
        "whole_word",
        "query_end",
        "sentence_boundary"
      ],
      "result_count": 2,
      "median_ns": 27700.0,
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
      "query_id": "replacement-no-shared-qgram",
      "query": "cat",
      "length": 3,
      "categories": [
        "replacement",
        "whole_word"
      ],
      "result_count": 0,
      "median_ns": 25800.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 1,
        "tree_lookups": 1,
        "candidate_words": 4,
        "candidate_occurrences": 4,
        "verifier_calls": 4
      }
    },
    {
      "query_id": "length-1-many",
      "query": "a",
      "length": 1,
      "categories": [
        "exact",
        "many_match",
        "repeated_characters"
      ],
      "result_count": 0,
      "median_ns": 24600.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 0,
        "tree_lookups": 1,
        "candidate_words": 0,
        "candidate_occurrences": 0,
        "verifier_calls": 0
      }
    },
    {
      "query_id": "length-3",
      "query": "alp",
      "length": 3,
      "categories": [
        "exact",
        "query_beginning"
      ],
      "result_count": 0,
      "median_ns": 24100.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 1,
        "tree_lookups": 1,
        "candidate_words": 4,
        "candidate_occurrences": 4,
        "verifier_calls": 4
      }
    },
    {
      "query_id": "single-word-zz",
      "query": "zz",
      "length": 2,
      "categories": [
        "exact",
        "whole_word",
        "query_beginning",
        "query_end",
        "sentence_boundary",
        "repeated_characters"
      ],
      "result_count": 0,
      "median_ns": 22700.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 0,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "ambiguous-insertion",
      "query": "aa",
      "length": 2,
      "categories": [
        "insertion",
        "repeated_characters",
        "ambiguous_edit",
        "many_match"
      ],
      "result_count": 0,
      "median_ns": 19900.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 0,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "single-word-x",
      "query": "x",
      "length": 1,
      "categories": [
        "exact",
        "whole_word",
        "query_beginning",
        "query_end",
        "sentence_boundary"
      ],
      "result_count": 0,
      "median_ns": 19900.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 0,
        "tree_lookups": 1,
        "candidate_words": 0,
        "candidate_occurrences": 0,
        "verifier_calls": 0
      }
    },
    {
      "query_id": "ambiguous-deletion",
      "query": "aaaaaaa",
      "length": 7,
      "categories": [
        "deletion",
        "repeated_characters",
        "ambiguous_edit"
      ],
      "result_count": 0,
      "median_ns": 18400.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 5,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "between-sentences",
      "query": "gamma programming",
      "length": 17,
      "categories": [
        "no_match",
        "sentence_boundary",
        "cross_word"
      ],
      "result_count": 0,
      "median_ns": 18000.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 15,
        "tree_lookups": 1,
        "candidate_words": 2,
        "candidate_occurrences": 2,
        "verifier_calls": 2
      }
    },
    {
      "query_id": "length-6-cross",
      "query": "alpha ",
      "length": 6,
      "categories": [
        "exact",
        "cross_word",
        "query_beginning",
        "sentence_boundary"
      ],
      "result_count": 0,
      "median_ns": 17400.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "tree_lookups": 1,
        "candidate_words": 0,
        "candidate_occurrences": 0,
        "verifier_calls": 0
      }
    },
    {
      "query_id": "hello-cross",
      "query": "hello world",
      "length": 11,
      "categories": [
        "exact",
        "cross_word",
        "many_match"
      ],
      "result_count": 0,
      "median_ns": 17200.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 9,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "deletion",
      "query": "programmking",
      "length": 12,
      "categories": [
        "deletion",
        "whole_word"
      ],
      "result_count": 0,
      "median_ns": 16600.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 10,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "ends-insertion",
      "query": "ends her",
      "length": 8,
      "categories": [
        "insertion",
        "cross_word",
        "query_end",
        "sentence_boundary"
      ],
      "result_count": 0,
      "median_ns": 15800.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 6,
        "tree_lookups": 1,
        "candidate_words": 2,
        "candidate_occurrences": 2,
        "verifier_calls": 2
      }
    },
    {
      "query_id": "world-hello",
      "query": "world hello",
      "length": 11,
      "categories": [
        "exact",
        "cross_word",
        "inside_word"
      ],
      "result_count": 0,
      "median_ns": 14600.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 9,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "repeated-words",
      "query": "repeated repeated",
      "length": 17,
      "categories": [
        "exact",
        "cross_word",
        "repeated_qgrams",
        "query_end",
        "sentence_boundary"
      ],
      "result_count": 0,
      "median_ns": 14500.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 15,
        "tree_lookups": 1,
        "candidate_words": 2,
        "candidate_occurrences": 2,
        "verifier_calls": 2
      }
    },
    {
      "query_id": "query-end-replacement",
      "query": "gammx",
      "length": 5,
      "categories": [
        "replacement",
        "query_end",
        "sentence_boundary"
      ],
      "result_count": 0,
      "median_ns": 12500.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "tree_lookups": 1,
        "candidate_words": 0,
        "candidate_occurrences": 0,
        "verifier_calls": 0
      }
    },
    {
      "query_id": "query-end",
      "query": "gamma",
      "length": 5,
      "categories": [
        "exact",
        "whole_word",
        "query_end",
        "sentence_boundary"
      ],
      "result_count": 0,
      "median_ns": 10700.0,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "tree_lookups": 1,
        "candidate_words": 0,
        "candidate_occurrences": 0,
        "verifier_calls": 0
      }
    }
  ],
  "bi_anchor": [
    {
      "query_id": "length-5-whole",
      "query": "alpha",
      "length": 5,
      "categories": [
        "exact",
        "whole_word",
        "query_beginning",
        "sentence_boundary"
      ],
      "result_count": 0,
      "median_ns": 2263300.0,
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
      "query_id": "inside-word",
      "query": "gramm",
      "length": 5,
      "categories": [
        "exact",
        "inside_word"
      ],
      "result_count": 0,
      "median_ns": 1898100.0,
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
        "last_selected_q": null,
        "last_pair_cost_by_q": {},
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "leading-space-cross",
      "query": " beta",
      "length": 5,
      "categories": [
        "exact",
        "cross_word"
      ],
      "result_count": 0,
      "median_ns": 1861300.0,
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
        "last_selected_q": null,
        "last_pair_cost_by_q": {},
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "query-end-replacement",
      "query": "gammx",
      "length": 5,
      "categories": [
        "replacement",
        "query_end",
        "sentence_boundary"
      ],
      "result_count": 0,
      "median_ns": 1855600.0,
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
      "query_id": "query-end",
      "query": "gamma",
      "length": 5,
      "categories": [
        "exact",
        "whole_word",
        "query_end",
        "sentence_boundary"
      ],
      "result_count": 0,
      "median_ns": 1848100.0,
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
      "query_id": "repeated-characters",
      "query": "aaaa",
      "length": 4,
      "categories": [
        "exact",
        "repeated_characters",
        "many_match"
      ],
      "result_count": 21,
      "median_ns": 1756400.0,
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
      "query_id": "length-4",
      "query": "alph",
      "length": 4,
      "categories": [
        "exact",
        "query_beginning"
      ],
      "result_count": 0,
      "median_ns": 1561300.0,
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
      "query_id": "hello-many",
      "query": "hello",
      "length": 5,
      "categories": [
        "exact",
        "whole_word",
        "many_match"
      ],
      "result_count": 0,
      "median_ns": 1477900.0,
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
        "last_selected_q": null,
        "last_pair_cost_by_q": {},
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "repeated-qgrams-short",
      "query": "ababa",
      "length": 5,
      "categories": [
        "exact",
        "repeated_qgrams",
        "many_match"
      ],
      "result_count": 0,
      "median_ns": 1287500.0,
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
        "last_selected_q": null,
        "last_pair_cost_by_q": {},
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "single-word-x",
      "query": "x",
      "length": 1,
      "categories": [
        "exact",
        "whole_word",
        "query_beginning",
        "query_end",
        "sentence_boundary"
      ],
      "result_count": 218,
      "median_ns": 1197800.0,
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
      "query_id": "ambiguous-insertion",
      "query": "aa",
      "length": 2,
      "categories": [
        "insertion",
        "repeated_characters",
        "ambiguous_edit",
        "many_match"
      ],
      "result_count": 55,
      "median_ns": 1061100.0,
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
      "query_id": "replacement-no-shared-qgram",
      "query": "cat",
      "length": 3,
      "categories": [
        "replacement",
        "whole_word"
      ],
      "result_count": 4,
      "median_ns": 929600.0,
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
        "last_selected_q": null,
        "last_pair_cost_by_q": {},
        "q_candidates_evaluated": 0
      }
    },
    {
      "query_id": "length-3",
      "query": "alp",
      "length": 3,
      "categories": [
        "exact",
        "query_beginning"
      ],
      "result_count": 0,
      "median_ns": 879500.0,
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
      "query_id": "length-2",
      "query": "al",
      "length": 2,
      "categories": [
        "exact",
        "query_beginning"
      ],
      "result_count": 39,
      "median_ns": 811100.0,
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
      "query_id": "length-1-many",
      "query": "a",
      "length": 1,
      "categories": [
        "exact",
        "many_match",
        "repeated_characters"
      ],
      "result_count": 239,
      "median_ns": 770200.0,
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
      "query_id": "single-word-zz",
      "query": "zz",
      "length": 2,
      "categories": [
        "exact",
        "whole_word",
        "query_beginning",
        "query_end",
        "sentence_boundary",
        "repeated_characters"
      ],
      "result_count": 4,
      "median_ns": 758200.0,
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
      "query_id": "cross-word",
      "query": "ming in",
      "length": 7,
      "categories": [
        "exact",
        "cross_word"
      ],
      "result_count": 0,
      "median_ns": 131400.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 1,
        "candidate_contexts_generated": 9,
        "candidate_contexts_after_dedup": 9,
        "verifier_calls": 9,
        "selected_seed_frequency_sum": 1,
        "last_selected_seeds": [
          {
            "text": "min",
            "query_start": 0,
            "query_end": 3,
            "frequency": 1
          },
          {
            "text": "g i",
            "query_start": 3,
            "query_end": 6,
            "frequency": 0
          }
        ],
        "last_selected_q": 3,
        "last_pair_cost_by_q": {
          "3": 1
        },
        "selected_q_counts": {
          "3": 7
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "ambiguous-deletion",
      "query": "aaaaaaa",
      "length": 7,
      "categories": [
        "deletion",
        "repeated_characters",
        "ambiguous_edit"
      ],
      "result_count": 0,
      "median_ns": 98800.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 6,
        "candidate_contexts_generated": 18,
        "candidate_contexts_after_dedup": 9,
        "verifier_calls": 9,
        "selected_seed_frequency_sum": 6,
        "last_selected_seeds": [
          {
            "text": "aaa",
            "query_start": 0,
            "query_end": 3,
            "frequency": 3
          },
          {
            "text": "aaa",
            "query_start": 3,
            "query_end": 6,
            "frequency": 3
          }
        ],
        "last_selected_q": 3,
        "last_pair_cost_by_q": {
          "3": 6
        },
        "selected_q_counts": {
          "3": 8
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "between-sentences",
      "query": "gamma programming",
      "length": 17,
      "categories": [
        "no_match",
        "sentence_boundary",
        "cross_word"
      ],
      "result_count": 0,
      "median_ns": 75600.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 1,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 0,
        "candidate_contexts_after_dedup": 0,
        "verifier_calls": 0,
        "selected_seed_frequency_sum": 0,
        "last_selected_seeds": [
          {
            "text": "gam",
            "query_start": 0,
            "query_end": 3,
            "frequency": 0
          },
          {
            "text": "ma ",
            "query_start": 3,
            "query_end": 6,
            "frequency": 0
          }
        ],
        "last_selected_q": 0,
        "selected_q_counts": {
          "3": 19
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "suffix",
      "query": "suffix",
      "length": 6,
      "categories": [
        "exact",
        "whole_word",
        "query_end",
        "sentence_boundary"
      ],
      "result_count": 2,
      "median_ns": 69500.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 1,
        "candidate_contexts_generated": 9,
        "candidate_contexts_after_dedup": 9,
        "verifier_calls": 9,
        "selected_seed_frequency_sum": 1,
        "last_selected_seeds": [
          {
            "text": "suf",
            "query_start": 0,
            "query_end": 3,
            "frequency": 1
          },
          {
            "text": "fix",
            "query_start": 3,
            "query_end": 6,
            "frequency": 0
          }
        ],
        "last_selected_q": 0,
        "last_pair_cost_by_q": {
          "3": 1
        },
        "selected_q_counts": {
          "3": 15
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "repeated-words",
      "query": "repeated repeated",
      "length": 17,
      "categories": [
        "exact",
        "cross_word",
        "repeated_qgrams",
        "query_end",
        "sentence_boundary"
      ],
      "result_count": 0,
      "median_ns": 54900.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 1,
        "candidate_contexts_generated": 0,
        "candidate_contexts_after_dedup": 0,
        "verifier_calls": 0,
        "selected_seed_frequency_sum": 1,
        "last_selected_seeds": [
          {
            "text": "epe",
            "query_start": 1,
            "query_end": 4,
            "frequency": 1
          },
          {
            "text": "d r",
            "query_start": 7,
            "query_end": 10,
            "frequency": 0
          }
        ],
        "last_selected_q": 0,
        "last_pair_cost_by_q": {
          "3": 1
        },
        "selected_q_counts": {
          "3": 21
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "hello-cross",
      "query": "hello world",
      "length": 11,
      "categories": [
        "exact",
        "cross_word",
        "many_match"
      ],
      "result_count": 0,
      "median_ns": 49000.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 1,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 0,
        "candidate_contexts_after_dedup": 0,
        "verifier_calls": 0,
        "selected_seed_frequency_sum": 0,
        "last_selected_seeds": [
          {
            "text": "hel",
            "query_start": 0,
            "query_end": 3,
            "frequency": 0
          },
          {
            "text": "lo ",
            "query_start": 3,
            "query_end": 6,
            "frequency": 0
          }
        ],
        "last_selected_q": 3,
        "last_pair_cost_by_q": {
          "3": 0
        },
        "selected_q_counts": {
          "3": 10
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "deletion",
      "query": "programmking",
      "length": 12,
      "categories": [
        "deletion",
        "whole_word"
      ],
      "result_count": 0,
      "median_ns": 48700.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 1,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 0,
        "candidate_contexts_after_dedup": 0,
        "verifier_calls": 0,
        "selected_seed_frequency_sum": 0,
        "last_selected_q": 0,
        "selected_q_counts": {
          "3": 6
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "long-exact",
      "query": "programming",
      "length": 11,
      "categories": [
        "exact",
        "whole_word",
        "query_beginning"
      ],
      "result_count": 0,
      "median_ns": 43100.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 1,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 0,
        "candidate_contexts_after_dedup": 0,
        "verifier_calls": 0,
        "selected_seed_frequency_sum": 0,
        "last_selected_seeds": [
          {
            "text": "pro",
            "query_start": 0,
            "query_end": 3,
            "frequency": 0
          },
          {
            "text": "gra",
            "query_start": 3,
            "query_end": 6,
            "frequency": 0
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
      "query_id": "replacement",
      "query": "prograxming",
      "length": 11,
      "categories": [
        "replacement",
        "whole_word"
      ],
      "result_count": 0,
      "median_ns": 42700.0,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 1,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 0,
        "candidate_contexts_after_dedup": 0,
        "verifier_calls": 0,
        "selected_seed_frequency_sum": 0,
        "last_selected_q": 0,
        "selected_q_counts": {
          "3": 4
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
      "query_id": "repeated-qgrams",
      "query": "ababab",
      "speedup_vs_naive": 205.49180327868854,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "posting_lists_accessed": 4,
        "posting_entries_scanned": 0,
        "candidate_starts_before_dedup": 0,
        "candidate_starts_after_dedup": 0,
        "target_contexts": 0,
        "verifier_calls": 0,
        "fallback_count": 0
      }
    },
    {
      "query_id": "prefix",
      "query": "prefix",
      "speedup_vs_naive": 177.0735294117647,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "posting_lists_accessed": 4,
        "posting_entries_scanned": 0,
        "candidate_starts_before_dedup": 0,
        "candidate_starts_after_dedup": 0,
        "target_contexts": 0,
        "verifier_calls": 0,
        "fallback_count": 0
      }
    },
    {
      "query_id": "no-match",
      "query": "qqqqqqqq",
      "speedup_vs_naive": 171.3116883116883,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 6,
        "posting_lists_accessed": 6,
        "posting_entries_scanned": 0,
        "candidate_starts_before_dedup": 0,
        "candidate_starts_after_dedup": 0,
        "target_contexts": 0,
        "verifier_calls": 0,
        "fallback_count": 0
      }
    },
    {
      "query_id": "beta-gamma",
      "query": "beta gamma",
      "speedup_vs_naive": 165.70526315789473,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 8,
        "posting_lists_accessed": 8,
        "posting_entries_scanned": 0,
        "candidate_starts_before_dedup": 0,
        "candidate_starts_after_dedup": 0,
        "target_contexts": 0,
        "verifier_calls": 0,
        "fallback_count": 0
      }
    },
    {
      "query_id": "prefix-inside-cross",
      "query": "refix s",
      "speedup_vs_naive": 153.3048780487805,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 5,
        "posting_lists_accessed": 5,
        "posting_entries_scanned": 0,
        "candidate_starts_before_dedup": 0,
        "candidate_starts_after_dedup": 0,
        "target_contexts": 0,
        "verifier_calls": 0,
        "fallback_count": 0
      }
    },
    {
      "query_id": "length-6-cross",
      "query": "alpha ",
      "speedup_vs_naive": 146.62962962962962,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "posting_lists_accessed": 4,
        "posting_entries_scanned": 0,
        "candidate_starts_before_dedup": 0,
        "candidate_starts_after_dedup": 0,
        "target_contexts": 0,
        "verifier_calls": 0,
        "fallback_count": 0
      }
    },
    {
      "query_id": "length-5-whole",
      "query": "alpha",
      "speedup_vs_naive": 142.28346456692913,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "posting_lists_accessed": 4,
        "posting_entries_scanned": 0,
        "candidate_starts_before_dedup": 0,
        "candidate_starts_after_dedup": 0,
        "target_contexts": 0,
        "verifier_calls": 0,
        "fallback_count": 0
      }
    },
    {
      "query_id": "length-4",
      "query": "alph",
      "speedup_vs_naive": 126.6086956521739,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "posting_lists_accessed": 3,
        "posting_entries_scanned": 0,
        "candidate_starts_before_dedup": 0,
        "candidate_starts_after_dedup": 0,
        "target_contexts": 0,
        "verifier_calls": 0,
        "fallback_count": 0
      }
    },
    {
      "query_id": "deletion",
      "query": "programmking",
      "speedup_vs_naive": 46.01754385964912,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 10,
        "posting_lists_accessed": 10,
        "posting_entries_scanned": 1,
        "candidate_starts_before_dedup": 3,
        "candidate_starts_after_dedup": 3,
        "target_contexts": 6,
        "verifier_calls": 6,
        "fallback_count": 0
      }
    },
    {
      "query_id": "repeated-qgrams-short",
      "query": "ababa",
      "speedup_vs_naive": 31.991701244813278,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "posting_lists_accessed": 4,
        "posting_entries_scanned": 2,
        "candidate_starts_before_dedup": 6,
        "candidate_starts_after_dedup": 2,
        "target_contexts": 6,
        "verifier_calls": 6,
        "fallback_count": 0
      }
    },
    {
      "query_id": "suffix",
      "query": "suffix",
      "speedup_vs_naive": 27.666666666666668,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "posting_lists_accessed": 4,
        "posting_entries_scanned": 3,
        "candidate_starts_before_dedup": 9,
        "candidate_starts_after_dedup": 3,
        "target_contexts": 9,
        "verifier_calls": 9,
        "fallback_count": 0
      }
    },
    {
      "query_id": "ends-deletion",
      "query": "ends herre",
      "speedup_vs_naive": 26.70877192982456,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 8,
        "posting_lists_accessed": 8,
        "posting_entries_scanned": 3,
        "candidate_starts_before_dedup": 9,
        "candidate_starts_after_dedup": 7,
        "target_contexts": 12,
        "verifier_calls": 12,
        "fallback_count": 0
      }
    },
    {
      "query_id": "replacement",
      "query": "prograxming",
      "speedup_vs_naive": 24.91726618705036,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 9,
        "posting_lists_accessed": 9,
        "posting_entries_scanned": 2,
        "candidate_starts_before_dedup": 6,
        "candidate_starts_after_dedup": 6,
        "target_contexts": 15,
        "verifier_calls": 15,
        "fallback_count": 0
      }
    },
    {
      "query_id": "insertion",
      "query": "programing",
      "speedup_vs_naive": 24.782062780269058,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 8,
        "posting_lists_accessed": 8,
        "posting_entries_scanned": 2,
        "candidate_starts_before_dedup": 6,
        "candidate_starts_after_dedup": 6,
        "target_contexts": 15,
        "verifier_calls": 15,
        "fallback_count": 0
      }
    },
    {
      "query_id": "ends-insertion",
      "query": "ends her",
      "speedup_vs_naive": 24.7632058287796,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 6,
        "posting_lists_accessed": 6,
        "posting_entries_scanned": 3,
        "candidate_starts_before_dedup": 9,
        "candidate_starts_after_dedup": 7,
        "target_contexts": 13,
        "verifier_calls": 13,
        "fallback_count": 0
      }
    },
    {
      "query_id": "long-exact",
      "query": "programming",
      "speedup_vs_naive": 22.297514033680834,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 9,
        "posting_lists_accessed": 9,
        "posting_entries_scanned": 2,
        "candidate_starts_before_dedup": 6,
        "candidate_starts_after_dedup": 6,
        "target_contexts": 15,
        "verifier_calls": 15,
        "fallback_count": 0
      }
    },
    {
      "query_id": "world-hello",
      "query": "world hello",
      "speedup_vs_naive": 22.065524193548388,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 9,
        "posting_lists_accessed": 9,
        "posting_entries_scanned": 2,
        "candidate_starts_before_dedup": 6,
        "candidate_starts_after_dedup": 6,
        "target_contexts": 15,
        "verifier_calls": 15,
        "fallback_count": 0
      }
    },
    {
      "query_id": "query-end-replacement",
      "query": "gammx",
      "speedup_vs_naive": 20.512623490669593,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "posting_lists_accessed": 4,
        "posting_entries_scanned": 2,
        "candidate_starts_before_dedup": 6,
        "candidate_starts_after_dedup": 6,
        "target_contexts": 18,
        "verifier_calls": 18,
        "fallback_count": 0
      }
    },
    {
      "query_id": "single-word-zz",
      "query": "zz",
      "speedup_vs_naive": 19.536269430051814,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 2,
        "posting_lists_accessed": 2,
        "posting_entries_scanned": 2,
        "candidate_starts_before_dedup": 6,
        "candidate_starts_after_dedup": 4,
        "target_contexts": 12,
        "verifier_calls": 12,
        "fallback_count": 0
      }
    },
    {
      "query_id": "hello-cross",
      "query": "hello world",
      "speedup_vs_naive": 19.2680262199563,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 9,
        "posting_lists_accessed": 9,
        "posting_entries_scanned": 4,
        "candidate_starts_before_dedup": 12,
        "candidate_starts_after_dedup": 6,
        "target_contexts": 18,
        "verifier_calls": 18,
        "fallback_count": 0
      }
    }
  ],
  "qgram_tree_hybrid": [
    {
      "query_id": "leading-space-cross",
      "query": " beta",
      "speedup_vs_naive": 212.22222222222223,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "tree_lookups": 1,
        "candidate_words": 0,
        "candidate_occurrences": 0,
        "verifier_calls": 0
      }
    },
    {
      "query_id": "hello-many",
      "query": "hello",
      "speedup_vs_naive": 193.9047619047619,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "tree_lookups": 1,
        "candidate_words": 0,
        "candidate_occurrences": 0,
        "verifier_calls": 0
      }
    },
    {
      "query_id": "prefix-inside-cross",
      "query": "refix s",
      "speedup_vs_naive": 190.46969696969697,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 5,
        "tree_lookups": 1,
        "candidate_words": 0,
        "candidate_occurrences": 0,
        "verifier_calls": 0
      }
    },
    {
      "query_id": "beta-gamma",
      "query": "beta gamma",
      "speedup_vs_naive": 187.4047619047619,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 8,
        "tree_lookups": 1,
        "candidate_words": 0,
        "candidate_occurrences": 0,
        "verifier_calls": 0
      }
    },
    {
      "query_id": "inside-word",
      "query": "gramm",
      "speedup_vs_naive": 180.26923076923077,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "tree_lookups": 1,
        "candidate_words": 0,
        "candidate_occurrences": 0,
        "verifier_calls": 0
      }
    },
    {
      "query_id": "deletion",
      "query": "programmking",
      "speedup_vs_naive": 173.8132530120482,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 10,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "query-end",
      "query": "gamma",
      "speedup_vs_naive": 172.70093457943926,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "tree_lookups": 1,
        "candidate_words": 0,
        "candidate_occurrences": 0,
        "verifier_calls": 0
      }
    },
    {
      "query_id": "prefix",
      "query": "prefix",
      "speedup_vs_naive": 167.23611111111111,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "tree_lookups": 1,
        "candidate_words": 0,
        "candidate_occurrences": 0,
        "verifier_calls": 0
      }
    },
    {
      "query_id": "repeated-qgrams",
      "query": "ababab",
      "speedup_vs_naive": 162.7922077922078,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "tree_lookups": 1,
        "candidate_words": 0,
        "candidate_occurrences": 0,
        "verifier_calls": 0
      }
    },
    {
      "query_id": "inside-cross",
      "query": "ello wor",
      "speedup_vs_naive": 156.66666666666666,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 6,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "hello-cross",
      "query": "hello world",
      "speedup_vs_naive": 153.8081395348837,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 9,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "world-hello",
      "query": "world hello",
      "speedup_vs_naive": 149.92465753424656,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 9,
        "tree_lookups": 1,
        "candidate_words": 1,
        "candidate_occurrences": 1,
        "verifier_calls": 1
      }
    },
    {
      "query_id": "query-end-replacement",
      "query": "gammx",
      "speedup_vs_naive": 149.496,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "tree_lookups": 1,
        "candidate_words": 0,
        "candidate_occurrences": 0,
        "verifier_calls": 0
      }
    },
    {
      "query_id": "ends-deletion",
      "query": "ends herre",
      "speedup_vs_naive": 149.2549019607843,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 8,
        "tree_lookups": 1,
        "candidate_words": 2,
        "candidate_occurrences": 2,
        "verifier_calls": 2
      }
    },
    {
      "query_id": "repeated-qgrams-short",
      "query": "ababa",
      "speedup_vs_naive": 145.47169811320754,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 3,
        "tree_lookups": 1,
        "candidate_words": 0,
        "candidate_occurrences": 0,
        "verifier_calls": 0
      }
    },
    {
      "query_id": "repeated-words",
      "query": "repeated repeated",
      "speedup_vs_naive": 138.62758620689655,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 15,
        "tree_lookups": 1,
        "candidate_words": 2,
        "candidate_occurrences": 2,
        "verifier_calls": 2
      }
    },
    {
      "query_id": "between-sentences",
      "query": "gamma programming",
      "speedup_vs_naive": 132.7,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 15,
        "tree_lookups": 1,
        "candidate_words": 2,
        "candidate_occurrences": 2,
        "verifier_calls": 2
      }
    },
    {
      "query_id": "no-match",
      "query": "qqqqqqqq",
      "speedup_vs_naive": 124.44339622641509,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 6,
        "tree_lookups": 1,
        "candidate_words": 0,
        "candidate_occurrences": 0,
        "verifier_calls": 0
      }
    },
    {
      "query_id": "length-6-cross",
      "query": "alpha ",
      "speedup_vs_naive": 113.76436781609195,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 4,
        "tree_lookups": 1,
        "candidate_words": 0,
        "candidate_occurrences": 0,
        "verifier_calls": 0
      }
    },
    {
      "query_id": "insertion",
      "query": "programing",
      "speedup_vs_naive": 98.33451957295374,
      "internal_work": {
        "query_count": 1,
        "query_qgrams": 8,
        "tree_lookups": 1,
        "candidate_words": 2,
        "candidate_occurrences": 2,
        "verifier_calls": 2
      }
    }
  ],
  "bi_anchor": [
    {
      "query_id": "prefix",
      "query": "prefix",
      "speedup_vs_naive": 77.68387096774194,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 1,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 0,
        "candidate_contexts_after_dedup": 0,
        "verifier_calls": 0,
        "selected_seed_frequency_sum": 0,
        "last_selected_seeds": [
          {
            "text": "pre",
            "query_start": 0,
            "query_end": 3,
            "frequency": 0
          },
          {
            "text": "fix",
            "query_start": 3,
            "query_end": 6,
            "frequency": 0
          }
        ],
        "last_selected_q": 0,
        "selected_q_counts": {
          "3": 14
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "insertion",
      "query": "programing",
      "speedup_vs_naive": 75.49726775956285,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 1,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 0,
        "candidate_contexts_after_dedup": 0,
        "verifier_calls": 0,
        "selected_seed_frequency_sum": 0,
        "last_selected_q": 0,
        "selected_q_counts": {
          "3": 5
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "ends-insertion",
      "query": "ends her",
      "speedup_vs_naive": 68.66161616161617,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 1,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 0,
        "candidate_contexts_after_dedup": 0,
        "verifier_calls": 0,
        "selected_seed_frequency_sum": 0,
        "last_selected_seeds": [
          {
            "text": "nds",
            "query_start": 1,
            "query_end": 4,
            "frequency": 0
          },
          {
            "text": " he",
            "query_start": 4,
            "query_end": 7,
            "frequency": 0
          }
        ],
        "last_selected_q": 0,
        "selected_q_counts": {
          "3": 17
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "replacement",
      "query": "prograxming",
      "speedup_vs_naive": 64.88992974238876,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 1,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 0,
        "candidate_contexts_after_dedup": 0,
        "verifier_calls": 0,
        "selected_seed_frequency_sum": 0,
        "last_selected_q": 0,
        "selected_q_counts": {
          "3": 4
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "long-exact",
      "query": "programming",
      "speedup_vs_naive": 64.51276102088167,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 1,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 0,
        "candidate_contexts_after_dedup": 0,
        "verifier_calls": 0,
        "selected_seed_frequency_sum": 0,
        "last_selected_seeds": [
          {
            "text": "pro",
            "query_start": 0,
            "query_end": 3,
            "frequency": 0
          },
          {
            "text": "gra",
            "query_start": 3,
            "query_end": 6,
            "frequency": 0
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
      "query_id": "no-match",
      "query": "qqqqqqqq",
      "speedup_vs_naive": 63.41826923076923,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 1,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 0,
        "candidate_contexts_after_dedup": 0,
        "verifier_calls": 0,
        "selected_seed_frequency_sum": 0,
        "last_selected_seeds": [
          {
            "text": "qqq",
            "query_start": 0,
            "query_end": 3,
            "frequency": 0
          },
          {
            "text": "qqq",
            "query_start": 3,
            "query_end": 6,
            "frequency": 0
          }
        ],
        "last_selected_q": 3,
        "last_pair_cost_by_q": {
          "3": 0
        },
        "selected_q_counts": {
          "3": 13
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "deletion",
      "query": "programmking",
      "speedup_vs_naive": 59.24640657084189,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 1,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 0,
        "candidate_contexts_after_dedup": 0,
        "verifier_calls": 0,
        "selected_seed_frequency_sum": 0,
        "last_selected_q": 0,
        "selected_q_counts": {
          "3": 6
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "ends-deletion",
      "query": "ends herre",
      "speedup_vs_naive": 59.007751937984494,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 1,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 0,
        "candidate_contexts_after_dedup": 0,
        "verifier_calls": 0,
        "selected_seed_frequency_sum": 0,
        "last_selected_q": 0,
        "selected_q_counts": {
          "3": 18
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "beta-gamma",
      "query": "beta gamma",
      "speedup_vs_naive": 58.520446096654275,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 1,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 0,
        "candidate_contexts_after_dedup": 0,
        "verifier_calls": 0,
        "selected_seed_frequency_sum": 0,
        "last_selected_seeds": [
          {
            "text": "bet",
            "query_start": 0,
            "query_end": 3,
            "frequency": 0
          },
          {
            "text": "a g",
            "query_start": 3,
            "query_end": 6,
            "frequency": 0
          }
        ],
        "last_selected_q": 3,
        "last_pair_cost_by_q": {
          "3": 0
        },
        "selected_q_counts": {
          "3": 20
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "prefix-inside-cross",
      "query": "refix s",
      "speedup_vs_naive": 58.199074074074076,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 1,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 0,
        "candidate_contexts_after_dedup": 0,
        "verifier_calls": 0,
        "selected_seed_frequency_sum": 0,
        "last_selected_seeds": [
          {
            "text": "ref",
            "query_start": 0,
            "query_end": 3,
            "frequency": 0
          },
          {
            "text": "ix ",
            "query_start": 3,
            "query_end": 6,
            "frequency": 0
          }
        ],
        "last_selected_q": 0,
        "last_pair_cost_by_q": {
          "3": 0
        },
        "selected_q_counts": {
          "3": 16
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "inside-cross",
      "query": "ello wor",
      "speedup_vs_naive": 57.44444444444444,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 1,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 0,
        "candidate_contexts_after_dedup": 0,
        "verifier_calls": 0,
        "selected_seed_frequency_sum": 0,
        "last_selected_seeds": [
          {
            "text": "ell",
            "query_start": 0,
            "query_end": 3,
            "frequency": 0
          },
          {
            "text": "o w",
            "query_start": 3,
            "query_end": 6,
            "frequency": 0
          }
        ],
        "last_selected_q": 3,
        "last_pair_cost_by_q": {
          "3": 0
        },
        "selected_q_counts": {
          "3": 12
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "hello-cross",
      "query": "hello world",
      "speedup_vs_naive": 53.98979591836735,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 1,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 0,
        "candidate_contexts_after_dedup": 0,
        "verifier_calls": 0,
        "selected_seed_frequency_sum": 0,
        "last_selected_seeds": [
          {
            "text": "hel",
            "query_start": 0,
            "query_end": 3,
            "frequency": 0
          },
          {
            "text": "lo ",
            "query_start": 3,
            "query_end": 6,
            "frequency": 0
          }
        ],
        "last_selected_q": 3,
        "last_pair_cost_by_q": {
          "3": 0
        },
        "selected_q_counts": {
          "3": 10
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "world-hello",
      "query": "world hello",
      "speedup_vs_naive": 52.744578313253015,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 1,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 0,
        "candidate_contexts_after_dedup": 0,
        "verifier_calls": 0,
        "selected_seed_frequency_sum": 0,
        "last_selected_seeds": [
          {
            "text": "orl",
            "query_start": 1,
            "query_end": 4,
            "frequency": 0
          },
          {
            "text": "d h",
            "query_start": 4,
            "query_end": 7,
            "frequency": 0
          }
        ],
        "last_selected_q": 0,
        "selected_q_counts": {
          "3": 11
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "repeated-qgrams",
      "query": "ababab",
      "speedup_vs_naive": 47.48106060606061,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 1,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 0,
        "candidate_contexts_after_dedup": 0,
        "verifier_calls": 0,
        "selected_seed_frequency_sum": 0,
        "last_selected_seeds": [
          {
            "text": "aba",
            "query_start": 0,
            "query_end": 3,
            "frequency": 0
          },
          {
            "text": "bab",
            "query_start": 3,
            "query_end": 6,
            "frequency": 0
          }
        ],
        "last_selected_q": 0,
        "last_pair_cost_by_q": {
          "3": 0
        },
        "selected_q_counts": {
          "3": 9
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "length-6-cross",
      "query": "alpha ",
      "speedup_vs_naive": 46.467136150234744,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 1,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 0,
        "candidate_contexts_after_dedup": 0,
        "verifier_calls": 0,
        "selected_seed_frequency_sum": 0,
        "last_selected_seeds": [
          {
            "text": "alp",
            "query_start": 0,
            "query_end": 3,
            "frequency": 0
          },
          {
            "text": "ha ",
            "query_start": 3,
            "query_end": 6,
            "frequency": 0
          }
        ],
        "last_selected_q": 3,
        "last_pair_cost_by_q": {
          "3": 0
        },
        "selected_q_counts": {
          "3": 2
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "repeated-words",
      "query": "repeated repeated",
      "speedup_vs_naive": 36.61384335154827,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 1,
        "candidate_contexts_generated": 0,
        "candidate_contexts_after_dedup": 0,
        "verifier_calls": 0,
        "selected_seed_frequency_sum": 1,
        "last_selected_seeds": [
          {
            "text": "epe",
            "query_start": 1,
            "query_end": 4,
            "frequency": 1
          },
          {
            "text": "d r",
            "query_start": 7,
            "query_end": 10,
            "frequency": 0
          }
        ],
        "last_selected_q": 0,
        "last_pair_cost_by_q": {
          "3": 1
        },
        "selected_q_counts": {
          "3": 21
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "between-sentences",
      "query": "gamma programming",
      "speedup_vs_naive": 31.595238095238095,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 1,
        "seed_occurrences_expanded": 0,
        "candidate_contexts_generated": 0,
        "candidate_contexts_after_dedup": 0,
        "verifier_calls": 0,
        "selected_seed_frequency_sum": 0,
        "last_selected_seeds": [
          {
            "text": "gam",
            "query_start": 0,
            "query_end": 3,
            "frequency": 0
          },
          {
            "text": "ma ",
            "query_start": 3,
            "query_end": 6,
            "frequency": 0
          }
        ],
        "last_selected_q": 0,
        "selected_q_counts": {
          "3": 19
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "suffix",
      "query": "suffix",
      "speedup_vs_naive": 16.958273381294966,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 1,
        "candidate_contexts_generated": 9,
        "candidate_contexts_after_dedup": 9,
        "verifier_calls": 9,
        "selected_seed_frequency_sum": 1,
        "last_selected_seeds": [
          {
            "text": "suf",
            "query_start": 0,
            "query_end": 3,
            "frequency": 1
          },
          {
            "text": "fix",
            "query_start": 3,
            "query_end": 6,
            "frequency": 0
          }
        ],
        "last_selected_q": 0,
        "last_pair_cost_by_q": {
          "3": 1
        },
        "selected_q_counts": {
          "3": 15
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "cross-word",
      "query": "ming in",
      "speedup_vs_naive": 16.810502283105023,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 1,
        "candidate_contexts_generated": 9,
        "candidate_contexts_after_dedup": 9,
        "verifier_calls": 9,
        "selected_seed_frequency_sum": 1,
        "last_selected_seeds": [
          {
            "text": "min",
            "query_start": 0,
            "query_end": 3,
            "frequency": 1
          },
          {
            "text": "g i",
            "query_start": 3,
            "query_end": 6,
            "frequency": 0
          }
        ],
        "last_selected_q": 3,
        "last_pair_cost_by_q": {
          "3": 1
        },
        "selected_q_counts": {
          "3": 7
        },
        "q_candidates_evaluated": 1
      }
    },
    {
      "query_id": "ambiguous-deletion",
      "query": "aaaaaaa",
      "speedup_vs_naive": 13.958502024291498,
      "internal_work": {
        "query_count": 1,
        "anchored_query_count": 1,
        "fallback_count": 0,
        "zero_frequency_returns": 0,
        "seed_occurrences_expanded": 6,
        "candidate_contexts_generated": 18,
        "candidate_contexts_after_dedup": 9,
        "verifier_calls": 9,
        "selected_seed_frequency_sum": 6,
        "last_selected_seeds": [
          {
            "text": "aaa",
            "query_start": 0,
            "query_end": 3,
            "frequency": 3
          },
          {
            "text": "aaa",
            "query_start": 3,
            "query_end": 6,
            "frequency": 3
          }
        ],
        "last_selected_q": 3,
        "last_pair_cost_by_q": {
          "3": 6
        },
        "selected_q_counts": {
          "3": 8
        },
        "q_candidates_evaluated": 1
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
  "bi_anchor": 1
}
```

# Conclusions

Fastest overall correct algorithm: `bi_anchor`.
Best for length 1: `naive`.
Best for length 2: `qgram_verifier`.
Best for length 3: `qgram_verifier`.
Best for length 4: `qgram_verifier`.
Best for length 5: `qgram_tree_hybrid`.
Best for length 6: `qgram_verifier`.
Best for medium queries (9–12): `qgram_tree_hybrid`.
Best for long queries (21+): `insufficient correct data`.
Best inside-word: `qgram_tree_hybrid`.
Best cross-word: `qgram_tree_hybrid`.
Best common: `insufficient correct data`.
Best rare: `insufficient correct data`.
Best no-match: `qgram_tree_hybrid`.
Cheapest measured build: `naive`.
Least approximate retained/index memory: `naive`.
Q-Gram + Verifier correctness: all checked raw result sets matched Naive.
Q-Gram + Tree Hybrid correctness: INCORRECT on 7 queries; FN=580, FP=0.
Selective Bi-Anchor correctness: all checked raw result sets matched Naive.
Optimized algorithms that lost or added raw matches: qgram_tree_hybrid.
Algorithms with zero per-query wins in this workload: none; this is the measured dominance indicator, not a proof for every workload.
Largest measured latency bottleneck: `naive` on query `programmking` at 2.885 ms; its stored work counters are `{"query_count": 1, "verifier_calls": 549}`.
Correctness is based on the retained timed Naive result; no separate Naive oracle search was run.
Next experiment: target the largest counter in the worst stored correct-algorithm case, then rerun the saved `queries.json` without changing match semantics.

Algorithm redesign is outside this benchmark run.
