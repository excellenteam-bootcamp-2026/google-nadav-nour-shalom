# Real-Corpus Four-Algorithm Comparative Study

# 1. Algorithms found

| Conceptual | Actual class/module | Builder | Verifier | Runnable |
| --- | --- | --- | --- | --- |
| Naive Search | NaiveSearchAlgorithm / `src.algorithms.naive_search_algorithm` | NaiveStructureBuilder | OneEditVerifier.compare | True |
| Q-Gram Positional Search + One-Edit Verifier | QGramSearchAlgorithm / `src.algorithms.qgram_search_algorithm` | QGramStructureBuilder | missing OneEditVerifier.verify API | False |
| Q-Gram + Tree Hybrid Search | QGramTrieSearchAlgorithm / `src.algorithms.qgram_trie_search_algorithm` | QGramTrieSearchAlgorithm.build | private _fuzzy_compare helpers | True |
| Selective Bi-Anchor + Shared OneEditVerifier | BiAnchorSearchAlgorithm / `src.algorithms.bi_anchor_search_algorithm` | BiAnchorStructureBuilder | OneEditVerifier.compare (Naive fallback for short queries) | True |

# 2. Test baseline

collected: 137, passed: 137, failed: 0, skipped: 0, compileall: passed, note: Untouched Phase 1 baseline before benchmark-only files were added., algorithm_specific_tests: ['tests/test_naive.py', 'tests/test_qgram_trie.py', 'tests/test_bi_anchor.py', 'tests/test_bi_anchor_differential.py', 'tests/test_bi_anchor_structure.py', 'tests/test_hash_seed_lookup.py', 'tests/test_one_edit_verifier.py']

# 3. Real corpus

- files_loaded: 480
- prepared_sentences: 194392
- total_original_characters: 9715672
- total_normalized_characters: 8158666
- total_word_occurrences: 1307893
- unique_words: 63457
- average_sentence_length: 41.97017366969834
- median_sentence_length: 50.0
- p95_sentence_length: 66.0
- maximum_sentence_length: 337
- source_archive: data\Archive3.zip
- skipped_duplicate_files: 0
- skipped_invalid_files: 0
- source file names: retained in the machine-readable JSON

# 4. Query workload

- random_seed: 20260812
- selection: deterministic source-stratified real substrings and one-edit mutations
- generated_queries: 64
- executed_queries: 23
- generated_tag_counts: {'inside_word': 60, 'short_exact': 27, 'medium_exact': 23, 'long_exact': 1, 'cross_word': 1, 'replacement': 1, 'insertion': 1, 'deletion': 1, 'repeated': 1, 'common_qgram': 1, 'medium_qgram': 1, 'rare_qgram': 1, 'no_match': 1, 'near_boundary': 2, 'high_frequency': 1, 'multiple_matches': 1}
- executed_tag_counts: {'no_match': 1, 'inside_word': 19, 'long_exact': 1, 'deletion': 1, 'repeated': 1, 'cross_word': 1, 'insertion': 1, 'replacement': 1, 'near_boundary': 2, 'medium_exact': 10, 'high_frequency': 1, 'multiple_matches': 1, 'common_qgram': 1, 'rare_qgram': 1, 'medium_qgram': 1}
- executed_length_counts: {'length_16_plus': 3, 'length_9_15': 9, 'length_6_8': 11}
- executed_source_files: 15
- resource_guard: Length 1-5 queries remain in the generated workload but are not run against the full raw-candidate Naive/Bi-Anchor paths: length-1 one-replacement semantics can emit a candidate at almost every corpus character and risk memory exhaustion.
- supplemental_note: Three full-corpus rare/medium/common q-gram queries were added after coverage reconciliation; all summaries were recomputed from 23 per-query observations.
- complete workload metadata: retained in JSON; per-observation data: CSV

# 5. Correctness

| Algorithm | Queries | Matching | Mismatches | FN | FP |
| --- | --- | --- | --- | --- | --- |
| naive | 23 | 23 | 0 | 0 | 0 |
| qgram_tree_hybrid | 23 | 1 | 22 | 259869 | 0 |
| bi_anchor | 23 | 23 | 0 | 0 | 0 |

# 6. Offline build

| Algorithm | Status | Build ms | Retained MiB | Peak MiB | Index statistics/error |
| --- | --- | --- | --- | --- | --- |
| naive | ok | 0.043 | 0.00 | 0.00 | {'sentences': 194392} |
| qgram_positional | error | 0.100 | 0.00 | 0.00 | AttributeError: 'PreparedSentence' object has no attribute 'normalized_sentence' |
| qgram_tree_hybrid | ok | 6823.954 | 187.49 | 187.49 | {'tree_nodes': 323120, 'tree_edges': 323119, 'terminals': 63457, 'word_occurrences': 1307893, 'qgram_keys': 16060, 'qgram_references': 640187} |
| bi_anchor | ok | 32516.096 | 330.63 | 384.42 | {'unique_words': 63457, 'word_occurrences': 1307893, 'intra_word_seed_keys': 16060, 'intra_word_seed_references': 640187, 'boundary_seed_keys': 3416, 'boundary_occurrences': 3284984} |

# 7. Overall online performance

| Algorithm | Median ms | Mean ms | P95 ms | P99 ms | Max ms |
| --- | --- | --- | --- | --- | --- |
| naive | 50072.678 | 51060.274 | 70201.101 | 74719.571 | 74719.571 |
| qgram_tree_hybrid | 20.552 | 23.187 | 57.320 | 82.674 | 82.674 |
| bi_anchor | 229.182 | 384.682 | 851.151 | 2694.172 | 2694.172 |

# 8. Speedup vs Naive

| Algorithm | Samples | Median | Mean | P90 | Worst | Best |
| --- | --- | --- | --- | --- | --- | --- |
| qgram_tree_hybrid | 1 | 5790.063494588101 | 5790.063494588101 | 5790.063494588101 | 5790.063494588101 | 5790.063494588101 |
| bi_anchor | 23 | 198.9322624503887 | 5009.970655141364 | 22329.678740063355 | 21.411237819171323 | 39849.92769487815 |

# 9. Results by query category

| Category | Fastest correct | Naive ms | Tree Hybrid ms (incorrect) | Bi-Anchor ms |
| --- | --- | --- | --- | --- |
| common_qgram | bi_anchor | 54437.901 | 26.406 | 167.658 |
| cross_word | bi_anchor | 57685.562 | 20.552 | 2694.172 |
| deletion | bi_anchor | 61446.133 | 37.463 | 85.015 |
| few_matches | bi_anchor | 70201.101 | 11.946 | 1.767 |
| high_frequency | bi_anchor | 38267.167 | 9.560 | 445.707 |
| insertion | bi_anchor | 52469.433 | 57.320 | 72.963 |
| inside_word | bi_anchor | 48786.044 | 18.256 | 229.182 |
| length_16_plus | bi_anchor | 69167.519 | 11.946 | 3.346 |
| length_6_8 | bi_anchor | 40697.640 | 15.810 | 445.707 |
| length_9_15 | bi_anchor | 52469.433 | 30.709 | 108.163 |
| long_exact | bi_anchor | 62169.834 | 10.227 | 7.362 |
| many_matches | bi_anchor | 48411.354 | 20.654 | 284.532 |
| medium_exact | bi_anchor | 42048.481 | 15.251 | 456.244 |
| medium_qgram | bi_anchor | 70201.101 | 10.324 | 1.767 |
| multiple_matches | bi_anchor | 38267.167 | 9.560 | 445.707 |
| near_boundary | bi_anchor | 46639.488 | 21.015 | 229.311 |
| no_match | bi_anchor | 69167.519 | 11.946 | 1.736 |
| rare_qgram | bi_anchor | 74719.571 | 22.416 | 3.346 |
| repeated | bi_anchor | 59352.668 | 41.517 | 327.779 |
| replacement | bi_anchor | 51028.842 | 30.709 | 61.453 |

# 10. Internal work

Algorithm-specific counters are stored per query in the CSV and JSON.

```json
{
  "bi_anchor": {
    "fallback_to_naive": {
      "mean": 0.0,
      "median": 0,
      "p95": 0.0,
      "max": 0
    },
    "frequency_a": {
      "mean": 6131.173913043478,
      "median": 2544,
      "p95": 13169.0,
      "max": 36319
    },
    "frequency_b": {
      "mean": 4782.434782608696,
      "median": 2499,
      "p95": 12523.0,
      "max": 23044
    },
    "seed_occurrences_expanded": {
      "mean": 10913.608695652174,
      "median": 8759,
      "p95": 36213.0,
      "max": 39535
    },
    "candidate_contexts_before_dedup": {
      "mean": 86771.08695652174,
      "median": 68531,
      "p95": 303884.0,
      "max": 342282
    },
    "candidate_contexts_after_dedup": {
      "mean": 66142.21739130435,
      "median": 54064,
      "p95": 200223.0,
      "max": 341973
    },
    "verifier_calls": {
      "mean": 66142.21739130435,
      "median": 54064,
      "p95": 200223.0,
      "max": 341973
    }
  },
  "naive": {
    "sentence_positions_examined": {
      "mean": 8158666.0,
      "median": 8158666,
      "p95": 8158666.0,
      "max": 8158666
    },
    "candidate_slices_checked": {
      "mean": 19319466.47826087,
      "median": 19917037,
      "p95": 21586538.0,
      "max": 21586538
    },
    "verifier_calls": {
      "mean": 19319466.47826087,
      "median": 19917037,
      "p95": 21586538.0,
      "max": 21586538
    }
  },
  "qgram_tree_hybrid": {
    "query_qgrams": {
      "mean": 8.347826086956522,
      "median": 7,
      "p95": 22.0,
      "max": 25
    },
    "qgram_lookups": {
      "mean": 8.347826086956522,
      "median": 7,
      "p95": 22.0,
      "max": 25
    },
    "posting_entries_loaded": {
      "mean": 5413.0,
      "median": 5112,
      "p95": 9459.0,
      "max": 15716
    },
    "tree_nodes_traversed": {
      "mean": 0.0,
      "median": 0,
      "p95": 0.0,
      "max": 0
    },
    "branches_explored": {
      "mean": 8.347826086956522,
      "median": 7,
      "p95": 22.0,
      "max": 25
    },
    "candidate_words_before_dedup": {
      "mean": 5413.0,
      "median": 5112,
      "p95": 9459.0,
      "max": 15716
    },
    "candidate_words_after_dedup": {
      "mean": 3456.8695652173915,
      "median": 2877,
      "p95": 7678.0,
      "max": 7678
    },
    "verifier_calls": {
      "mean": 3456.8695652173915,
      "median": 2877,
      "p95": 7678.0,
      "max": 7678
    }
  }
}
```

# 11. Head-to-head win rates

```json
{
  "eligible_queries": 23,
  "wins": {
    "naive": 0,
    "qgram_tree_hybrid": 0,
    "bi_anchor": 23
  },
  "ties_within_2_percent": 0,
  "by_category": {
    "common_qgram": {
      "queries": 1,
      "wins": {
        "naive": 0,
        "qgram_tree_hybrid": 0,
        "bi_anchor": 1
      },
      "ties_within_2_percent": 0
    },
    "cross_word": {
      "queries": 1,
      "wins": {
        "naive": 0,
        "qgram_tree_hybrid": 0,
        "bi_anchor": 1
      },
      "ties_within_2_percent": 0
    },
    "deletion": {
      "queries": 1,
      "wins": {
        "naive": 0,
        "qgram_tree_hybrid": 0,
        "bi_anchor": 1
      },
      "ties_within_2_percent": 0
    },
    "few_matches": {
      "queries": 3,
      "wins": {
        "naive": 0,
        "qgram_tree_hybrid": 0,
        "bi_anchor": 3
      },
      "ties_within_2_percent": 0
    },
    "high_frequency": {
      "queries": 1,
      "wins": {
        "naive": 0,
        "qgram_tree_hybrid": 0,
        "bi_anchor": 1
      },
      "ties_within_2_percent": 0
    },
    "insertion": {
      "queries": 1,
      "wins": {
        "naive": 0,
        "qgram_tree_hybrid": 0,
        "bi_anchor": 1
      },
      "ties_within_2_percent": 0
    },
    "inside_word": {
      "queries": 19,
      "wins": {
        "naive": 0,
        "qgram_tree_hybrid": 0,
        "bi_anchor": 19
      },
      "ties_within_2_percent": 0
    },
    "length_16_plus": {
      "queries": 3,
      "wins": {
        "naive": 0,
        "qgram_tree_hybrid": 0,
        "bi_anchor": 3
      },
      "ties_within_2_percent": 0
    },
    "length_6_8": {
      "queries": 11,
      "wins": {
        "naive": 0,
        "qgram_tree_hybrid": 0,
        "bi_anchor": 11
      },
      "ties_within_2_percent": 0
    },
    "length_9_15": {
      "queries": 9,
      "wins": {
        "naive": 0,
        "qgram_tree_hybrid": 0,
        "bi_anchor": 9
      },
      "ties_within_2_percent": 0
    },
    "long_exact": {
      "queries": 1,
      "wins": {
        "naive": 0,
        "qgram_tree_hybrid": 0,
        "bi_anchor": 1
      },
      "ties_within_2_percent": 0
    },
    "many_matches": {
      "queries": 20,
      "wins": {
        "naive": 0,
        "qgram_tree_hybrid": 0,
        "bi_anchor": 20
      },
      "ties_within_2_percent": 0
    },
    "medium_exact": {
      "queries": 10,
      "wins": {
        "naive": 0,
        "qgram_tree_hybrid": 0,
        "bi_anchor": 10
      },
      "ties_within_2_percent": 0
    },
    "medium_qgram": {
      "queries": 1,
      "wins": {
        "naive": 0,
        "qgram_tree_hybrid": 0,
        "bi_anchor": 1
      },
      "ties_within_2_percent": 0
    },
    "multiple_matches": {
      "queries": 1,
      "wins": {
        "naive": 0,
        "qgram_tree_hybrid": 0,
        "bi_anchor": 1
      },
      "ties_within_2_percent": 0
    },
    "near_boundary": {
      "queries": 2,
      "wins": {
        "naive": 0,
        "qgram_tree_hybrid": 0,
        "bi_anchor": 2
      },
      "ties_within_2_percent": 0
    },
    "no_match": {
      "queries": 1,
      "wins": {
        "naive": 0,
        "qgram_tree_hybrid": 0,
        "bi_anchor": 1
      },
      "ties_within_2_percent": 0
    },
    "rare_qgram": {
      "queries": 1,
      "wins": {
        "naive": 0,
        "qgram_tree_hybrid": 0,
        "bi_anchor": 1
      },
      "ties_within_2_percent": 0
    },
    "repeated": {
      "queries": 1,
      "wins": {
        "naive": 0,
        "qgram_tree_hybrid": 0,
        "bi_anchor": 1
      },
      "ties_within_2_percent": 0
    },
    "replacement": {
      "queries": 1,
      "wins": {
        "naive": 0,
        "qgram_tree_hybrid": 0,
        "bi_anchor": 1
      },
      "ties_within_2_percent": 0
    }
  }
}
```

# 12. Worst cases

## naive

| Query | Length | Tags | Latency ms | Results | Work |
| --- | --- | --- | --- | --- | --- |
| pythondev2001january | 20 | few_matches, inside_word, length_16_plus, rare_qgram | 74719.571 | 3 | {'sentence_positions_examined': 8158666, 'candidate_slices_checked': 14427753, 'verifier_calls': 14427753} |
| gdbmnextkeykey | 14 | few_matches, inside_word, length_9_15, medium_qgram | 70201.101 | 3 | {'sentence_positions_examined': 8158666, 'candidate_slices_checked': 17299110, 'verifier_calls': 17299110} |
| zzzzzzbenchmarknear miss | 24 | few_matches, length_16_plus, no_match | 69167.519 | 0 | {'sentence_positions_examined': 8158666, 'candidate_slices_checked': 12671279, 'verifier_calls': 12671279} |
| ipaddressipv6addressaddress | 27 | inside_word, length_16_plus, long_exact, many_matches | 62169.834 | 6 | {'sentence_positions_examined': 8158666, 'candidate_slices_checked': 11422465, 'verifier_calls': 11422465} |
| insxtalling | 11 | deletion, inside_word, length_9_15, many_matches | 61446.133 | 145 | {'sentence_positions_examined': 8158666, 'candidate_slices_checked': 18845545, 'verifier_calls': 18845545} |
| installing | 10 | inside_word, length_9_15, many_matches, repeated | 59352.668 | 677 | {'sentence_positions_examined': 8158666, 'candidate_slices_checked': 19377093, 'verifier_calls': 19377093} |
| ing col | 7 | cross_word, length_6_8, many_matches | 57685.562 | 2587 | {'sentence_positions_examined': 8158666, 'candidate_slices_checked': 21022678, 'verifier_calls': 21022678} |
| extensions | 10 | common_qgram, inside_word, length_9_15, many_matches | 54437.901 | 3038 | {'sentence_positions_examined': 8158666, 'candidate_slices_checked': 19377093, 'verifier_calls': 19377093} |
| insalling | 9 | insertion, inside_word, length_9_15, many_matches | 52469.433 | 145 | {'sentence_positions_examined': 8158666, 'candidate_slices_checked': 19917037, 'verifier_calls': 19917037} |
| inxtalling | 10 | inside_word, length_9_15, many_matches, replacement | 51028.842 | 145 | {'sentence_positions_examined': 8158666, 'candidate_slices_checked': 19377093, 'verifier_calls': 19377093} |
| installi | 8 | length_6_8, many_matches, near_boundary | 50692.710 | 3179 | {'sentence_positions_examined': 8158666, 'candidate_slices_checked': 20465818, 'verifier_calls': 20465818} |
| return | 6 | inside_word, length_6_8, many_matches, medium_exact | 50072.678 | 43987 | {'sentence_positions_examined': 8158666, 'candidate_slices_checked': 21586538, 'verifier_calls': 21586538} |
| installing | 10 | inside_word, length_9_15, many_matches, medium_exact | 48786.044 | 677 | {'sentence_positions_examined': 8158666, 'candidate_slices_checked': 19377093, 'verifier_calls': 19377093} |
| descriptor | 10 | inside_word, length_9_15, many_matches, medium_exact | 48036.664 | 3748 | {'sentence_positions_examined': 8158666, 'candidate_slices_checked': 19377093, 'verifier_calls': 19377093} |
| reference | 9 | inside_word, length_9_15, many_matches, medium_exact | 45591.614 | 8295 | {'sentence_positions_examined': 8158666, 'candidate_slices_checked': 19917037, 'verifier_calls': 19917037} |
| pyobject | 8 | inside_word, length_6_8, many_matches, medium_exact | 43399.322 | 9790 | {'sentence_positions_examined': 8158666, 'candidate_slices_checked': 20465818, 'verifier_calls': 20465818} |
| requests | 8 | length_6_8, many_matches, near_boundary | 42586.267 | 2966 | {'sentence_positions_examined': 8158666, 'candidate_slices_checked': 20465818, 'verifier_calls': 20465818} |
| convert | 7 | inside_word, length_6_8, many_matches, medium_exact | 40697.640 | 6049 | {'sentence_positions_examined': 8158666, 'candidate_slices_checked': 21022678, 'verifier_calls': 21022678} |
| return | 6 | inside_word, length_6_8, many_matches, medium_exact | 40431.389 | 43987 | {'sentence_positions_examined': 8158666, 'candidate_slices_checked': 21586538, 'verifier_calls': 21586538} |
| python | 6 | high_frequency, inside_word, length_6_8, many_matches, multiple_matches | 38267.167 | 44685 | {'sentence_positions_examined': 8158666, 'candidate_slices_checked': 21586538, 'verifier_calls': 21586538} |

## qgram_tree_hybrid

| Query | Length | Tags | Latency ms | Results | Work |
| --- | --- | --- | --- | --- | --- |
| installing | 10 | inside_word, length_9_15, many_matches, medium_exact | 82.674 | 278 | {'query_qgrams': 8, 'qgram_lookups': 8, 'posting_entries_loaded': 9459, 'tree_nodes_traversed': 0, 'branches_explored': 8, 'candidate_words_before_dedup': 9459, 'candidate_words_after_dedup': 7678, 'verifier_calls': 7678} |
| insalling | 9 | insertion, inside_word, length_9_15, many_matches | 57.320 | 139 | {'query_qgrams': 7, 'qgram_lookups': 7, 'posting_entries_loaded': 7005, 'tree_nodes_traversed': 0, 'branches_explored': 7, 'candidate_words_before_dedup': 7005, 'candidate_words_after_dedup': 6220, 'verifier_calls': 6220} |
| installing | 10 | inside_word, length_9_15, many_matches, repeated | 41.517 | 278 | {'query_qgrams': 8, 'qgram_lookups': 8, 'posting_entries_loaded': 9459, 'tree_nodes_traversed': 0, 'branches_explored': 8, 'candidate_words_before_dedup': 9459, 'candidate_words_after_dedup': 7678, 'verifier_calls': 7678} |
| insxtalling | 11 | deletion, inside_word, length_9_15, many_matches | 37.463 | 139 | {'query_qgrams': 9, 'qgram_lookups': 9, 'posting_entries_loaded': 7177, 'tree_nodes_traversed': 0, 'branches_explored': 9, 'candidate_words_before_dedup': 7177, 'candidate_words_after_dedup': 6258, 'verifier_calls': 6258} |
| inxtalling | 10 | inside_word, length_9_15, many_matches, replacement | 30.709 | 139 | {'query_qgrams': 8, 'qgram_lookups': 8, 'posting_entries_loaded': 6498, 'tree_nodes_traversed': 0, 'branches_explored': 8, 'candidate_words_before_dedup': 6498, 'candidate_words_after_dedup': 5732, 'verifier_calls': 5732} |
| extensions | 10 | common_qgram, inside_word, length_9_15, many_matches | 26.406 | 1407 | {'query_qgrams': 8, 'qgram_lookups': 8, 'posting_entries_loaded': 7068, 'tree_nodes_traversed': 0, 'branches_explored': 8, 'candidate_words_before_dedup': 7068, 'candidate_words_after_dedup': 4944, 'verifier_calls': 4944} |
| pythondev2001january | 20 | few_matches, inside_word, length_16_plus, rare_qgram | 22.416 | 2 | {'query_qgrams': 18, 'qgram_lookups': 18, 'posting_entries_loaded': 5737, 'tree_nodes_traversed': 0, 'branches_explored': 18, 'candidate_words_before_dedup': 5737, 'candidate_words_after_dedup': 3193, 'verifier_calls': 3193} |
| pyobject | 8 | inside_word, length_6_8, many_matches, medium_exact | 21.801 | 2000 | {'query_qgrams': 6, 'qgram_lookups': 6, 'posting_entries_loaded': 8623, 'tree_nodes_traversed': 0, 'branches_explored': 6, 'candidate_words_before_dedup': 8623, 'candidate_words_after_dedup': 2728, 'verifier_calls': 2728} |
| convert | 7 | inside_word, length_6_8, many_matches, medium_exact | 21.690 | 2000 | {'query_qgrams': 5, 'qgram_lookups': 5, 'posting_entries_loaded': 4554, 'tree_nodes_traversed': 0, 'branches_explored': 5, 'candidate_words_before_dedup': 4554, 'candidate_words_after_dedup': 3860, 'verifier_calls': 3860} |
| installi | 8 | length_6_8, many_matches, near_boundary | 21.275 | 2000 | {'query_qgrams': 6, 'qgram_lookups': 6, 'posting_entries_loaded': 5112, 'tree_nodes_traversed': 0, 'branches_explored': 6, 'candidate_words_before_dedup': 5112, 'candidate_words_after_dedup': 3938, 'verifier_calls': 3938} |
| requests | 8 | length_6_8, many_matches, near_boundary | 20.756 | 1241 | {'query_qgrams': 6, 'qgram_lookups': 6, 'posting_entries_loaded': 5167, 'tree_nodes_traversed': 0, 'branches_explored': 6, 'candidate_words_before_dedup': 5167, 'candidate_words_after_dedup': 2877, 'verifier_calls': 2877} |
| ing col | 7 | cross_word, length_6_8, many_matches | 20.552 | 0 | {'query_qgrams': 5, 'qgram_lookups': 5, 'posting_entries_loaded': 3970, 'tree_nodes_traversed': 0, 'branches_explored': 5, 'candidate_words_before_dedup': 3970, 'candidate_words_after_dedup': 3756, 'verifier_calls': 3756} |
| reference | 9 | inside_word, length_9_15, many_matches, medium_exact | 18.256 | 2000 | {'query_qgrams': 7, 'qgram_lookups': 7, 'posting_entries_loaded': 3803, 'tree_nodes_traversed': 0, 'branches_explored': 7, 'candidate_words_before_dedup': 3803, 'candidate_words_after_dedup': 2822, 'verifier_calls': 2822} |
| return | 6 | inside_word, length_6_8, many_matches, medium_exact | 15.810 | 2000 | {'query_qgrams': 4, 'qgram_lookups': 4, 'posting_entries_loaded': 1576, 'tree_nodes_traversed': 0, 'branches_explored': 4, 'candidate_words_before_dedup': 1576, 'candidate_words_after_dedup': 1118, 'verifier_calls': 1118} |
| return | 6 | inside_word, length_6_8, many_matches, medium_exact | 14.691 | 2000 | {'query_qgrams': 4, 'qgram_lookups': 4, 'posting_entries_loaded': 1576, 'tree_nodes_traversed': 0, 'branches_explored': 4, 'candidate_words_before_dedup': 1576, 'candidate_words_after_dedup': 1118, 'verifier_calls': 1118} |
| object | 6 | inside_word, length_6_8, many_matches, medium_exact | 12.931 | 2000 | {'query_qgrams': 4, 'qgram_lookups': 4, 'posting_entries_loaded': 7049, 'tree_nodes_traversed': 0, 'branches_explored': 4, 'candidate_words_before_dedup': 7049, 'candidate_words_after_dedup': 2683, 'verifier_calls': 2683} |
| descriptor | 10 | inside_word, length_9_15, many_matches, medium_exact | 12.208 | 1741 | {'query_qgrams': 8, 'qgram_lookups': 8, 'posting_entries_loaded': 3145, 'tree_nodes_traversed': 0, 'branches_explored': 8, 'candidate_words_before_dedup': 3145, 'candidate_words_after_dedup': 2059, 'verifier_calls': 2059} |
| zzzzzzbenchmarknear miss | 24 | few_matches, length_16_plus, no_match | 11.946 | 0 | {'query_qgrams': 22, 'qgram_lookups': 22, 'posting_entries_loaded': 2453, 'tree_nodes_traversed': 0, 'branches_explored': 22, 'candidate_words_before_dedup': 2453, 'candidate_words_after_dedup': 2147, 'verifier_calls': 2147} |
| gdbmnextkeykey | 14 | few_matches, inside_word, length_9_15, medium_qgram | 10.324 | 2 | {'query_qgrams': 12, 'qgram_lookups': 12, 'posting_entries_loaded': 2918, 'tree_nodes_traversed': 0, 'branches_explored': 12, 'candidate_words_before_dedup': 2918, 'candidate_words_after_dedup': 1845, 'verifier_calls': 1845} |
| ipaddressipv6addressaddress | 27 | inside_word, length_16_plus, long_exact, many_matches | 10.227 | 3 | {'query_qgrams': 25, 'qgram_lookups': 25, 'posting_entries_loaded': 15716, 'tree_nodes_traversed': 0, 'branches_explored': 25, 'candidate_words_before_dedup': 15716, 'candidate_words_after_dedup': 3481, 'verifier_calls': 3481} |

## bi_anchor

| Query | Length | Tags | Latency ms | Results | Work |
| --- | --- | --- | --- | --- | --- |
| ing col | 7 | cross_word, length_6_8, many_matches | 2694.172 | 2587 | {'fallback_to_naive': 0, 'selected_seed_a': 'ng ', 'selected_seed_b': 'col', 'frequency_a': 36319, 'frequency_b': 3216, 'seed_occurrences_expanded': 39535, 'candidate_contexts_before_dedup': 342282, 'candidate_contexts_after_dedup': 341973, 'verifier_calls': 341973} |
| return | 6 | inside_word, length_6_8, many_matches, medium_exact | 851.151 | 43987 | {'fallback_to_naive': 0, 'selected_seed_a': 'ret', 'selected_seed_b': 'urn', 'frequency_a': 11971, 'frequency_b': 9887, 'seed_occurrences_expanded': 21858, 'candidate_contexts_before_dedup': 168325, 'candidate_contexts_after_dedup': 94559, 'verifier_calls': 94559} |
| object | 6 | inside_word, length_6_8, many_matches, medium_exact | 839.738 | 60322 | {'fallback_to_naive': 0, 'selected_seed_a': 'obj', 'selected_seed_b': 'ect', 'frequency_a': 13169, 'frequency_b': 23044, 'seed_occurrences_expanded': 36213, 'candidate_contexts_before_dedup': 303884, 'candidate_contexts_after_dedup': 200223, 'verifier_calls': 200223} |
| return | 6 | inside_word, length_6_8, many_matches, medium_exact | 668.535 | 43987 | {'fallback_to_naive': 0, 'selected_seed_a': 'ret', 'selected_seed_b': 'urn', 'frequency_a': 11971, 'frequency_b': 9887, 'seed_occurrences_expanded': 21858, 'candidate_contexts_before_dedup': 168325, 'candidate_contexts_after_dedup': 94559, 'verifier_calls': 94559} |
| installing | 10 | inside_word, length_9_15, many_matches, medium_exact | 517.388 | 677 | {'fallback_to_naive': 0, 'selected_seed_a': 'ins', 'selected_seed_b': 'lli', 'frequency_a': 8582, 'frequency_b': 1922, 'seed_occurrences_expanded': 10504, 'candidate_contexts_before_dedup': 75613, 'candidate_contexts_after_dedup': 74422, 'verifier_calls': 74422} |
| return | 6 | inside_word, length_6_8, many_matches, medium_exact | 473.083 | 43987 | {'fallback_to_naive': 0, 'selected_seed_a': 'ret', 'selected_seed_b': 'urn', 'frequency_a': 11971, 'frequency_b': 9887, 'seed_occurrences_expanded': 21858, 'candidate_contexts_before_dedup': 168325, 'candidate_contexts_after_dedup': 94559, 'verifier_calls': 94559} |
| python | 6 | high_frequency, inside_word, length_6_8, many_matches, multiple_matches | 445.707 | 44685 | {'fallback_to_naive': 0, 'selected_seed_a': 'pyt', 'selected_seed_b': 'hon', 'frequency_a': 10127, 'frequency_b': 9573, 'seed_occurrences_expanded': 19700, 'candidate_contexts_before_dedup': 161436, 'candidate_contexts_after_dedup': 84328, 'verifier_calls': 84328} |
| pyobject | 8 | inside_word, length_6_8, many_matches, medium_exact | 439.405 | 9790 | {'fallback_to_naive': 0, 'selected_seed_a': 'pyo', 'selected_seed_b': 'bje', 'frequency_a': 2153, 'frequency_b': 12523, 'seed_occurrences_expanded': 14676, 'candidate_contexts_before_dedup': 114383, 'candidate_contexts_after_dedup': 98278, 'verifier_calls': 98278} |
| installi | 8 | length_6_8, many_matches, near_boundary | 329.890 | 3179 | {'fallback_to_naive': 0, 'selected_seed_a': 'ins', 'selected_seed_b': 'lli', 'frequency_a': 8582, 'frequency_b': 1922, 'seed_occurrences_expanded': 10504, 'candidate_contexts_before_dedup': 81218, 'candidate_contexts_after_dedup': 79976, 'verifier_calls': 79976} |
| installing | 10 | inside_word, length_9_15, many_matches, repeated | 327.779 | 677 | {'fallback_to_naive': 0, 'selected_seed_a': 'ins', 'selected_seed_b': 'lli', 'frequency_a': 8582, 'frequency_b': 1922, 'seed_occurrences_expanded': 10504, 'candidate_contexts_before_dedup': 75613, 'candidate_contexts_after_dedup': 74422, 'verifier_calls': 74422} |
| output | 6 | inside_word, length_6_8, many_matches, medium_exact | 241.286 | 6817 | {'fallback_to_naive': 0, 'selected_seed_a': 'out', 'selected_seed_b': 'put', 'frequency_a': 5917, 'frequency_b': 3348, 'seed_occurrences_expanded': 9265, 'candidate_contexts_before_dedup': 73524, 'candidate_contexts_after_dedup': 61797, 'verifier_calls': 61797} |
| reference | 9 | inside_word, length_9_15, many_matches, medium_exact | 229.182 | 8295 | {'fallback_to_naive': 0, 'selected_seed_a': 'efe', 'selected_seed_b': 'ren', 'frequency_a': 2544, 'frequency_b': 6215, 'seed_occurrences_expanded': 8759, 'candidate_contexts_before_dedup': 68531, 'candidate_contexts_after_dedup': 54064, 'verifier_calls': 54064} |
| extensions | 10 | common_qgram, inside_word, length_9_15, many_matches | 167.658 | 3038 | {'fallback_to_naive': 0, 'selected_seed_a': 'xte', 'selected_seed_b': 'nsi', 'frequency_a': 1778, 'frequency_b': 2989, 'seed_occurrences_expanded': 4767, 'candidate_contexts_before_dedup': 36946, 'candidate_contexts_after_dedup': 27756, 'verifier_calls': 27756} |
| convert | 7 | inside_word, length_6_8, many_matches, medium_exact | 152.177 | 6049 | {'fallback_to_naive': 0, 'selected_seed_a': 'onv', 'selected_seed_b': 'ert', 'frequency_a': 1950, 'frequency_b': 4279, 'seed_occurrences_expanded': 6229, 'candidate_contexts_before_dedup': 48213, 'candidate_contexts_after_dedup': 39156, 'verifier_calls': 39156} |
| requests | 8 | length_6_8, many_matches, near_boundary | 128.732 | 2966 | {'fallback_to_naive': 0, 'selected_seed_a': 'req', 'selected_seed_b': 'sts', 'frequency_a': 2492, 'frequency_b': 2499, 'seed_occurrences_expanded': 4991, 'candidate_contexts_before_dedup': 37329, 'candidate_contexts_after_dedup': 35857, 'verifier_calls': 35857} |
| descriptor | 10 | inside_word, length_9_15, many_matches, medium_exact | 108.163 | 3748 | {'fallback_to_naive': 0, 'selected_seed_a': 'esc', 'selected_seed_b': 'pto', 'frequency_a': 2603, 'frequency_b': 994, 'seed_occurrences_expanded': 3597, 'candidate_contexts_before_dedup': 28633, 'candidate_contexts_after_dedup': 22199, 'verifier_calls': 22199} |
| insxtalling | 11 | deletion, inside_word, length_9_15, many_matches | 85.015 | 145 | {'fallback_to_naive': 0, 'selected_seed_a': 'sxt', 'selected_seed_b': 'lli', 'frequency_a': 0, 'frequency_b': 1922, 'seed_occurrences_expanded': 1922, 'candidate_contexts_before_dedup': 13111, 'candidate_contexts_after_dedup': 13111, 'verifier_calls': 13111} |
| insalling | 9 | insertion, inside_word, length_9_15, many_matches | 72.963 | 145 | {'fallback_to_naive': 0, 'selected_seed_a': 'nsa', 'selected_seed_b': 'lli', 'frequency_a': 256, 'frequency_b': 1922, 'seed_occurrences_expanded': 2178, 'candidate_contexts_before_dedup': 15911, 'candidate_contexts_after_dedup': 15911, 'verifier_calls': 15911} |
| inxtalling | 10 | inside_word, length_9_15, many_matches, replacement | 61.453 | 145 | {'fallback_to_naive': 0, 'selected_seed_a': 'nxt', 'selected_seed_b': 'lli', 'frequency_a': 1, 'frequency_b': 1922, 'seed_occurrences_expanded': 1923, 'candidate_contexts_before_dedup': 13531, 'candidate_contexts_after_dedup': 13531, 'verifier_calls': 13531} |
| ipaddressipv6addressaddress | 27 | inside_word, length_16_plus, long_exact, many_matches | 7.362 | 6 | {'fallback_to_naive': 0, 'selected_seed_a': 'v6a', 'selected_seed_b': 'sad', 'frequency_a': 23, 'frequency_b': 111, 'seed_occurrences_expanded': 134, 'candidate_contexts_before_dedup': 465, 'candidate_contexts_after_dedup': 459, 'verifier_calls': 459} |

# 13. Best cases

## qgram_tree_hybrid

| Query | Tags | Speedup | Why/work |
| --- | --- | --- | --- |
| zzzzzzbenchmarknear miss | few_matches, length_16_plus, no_match | 5790.063494588101 | {'query_qgrams': 22, 'qgram_lookups': 22, 'posting_entries_loaded': 2453, 'tree_nodes_traversed': 0, 'branches_explored': 22, 'candidate_words_before_dedup': 2453, 'candidate_words_after_dedup': 2147, 'verifier_calls': 2147} |

## bi_anchor

| Query | Tags | Speedup | Why/work |
| --- | --- | --- | --- |
| zzzzzzbenchmarknear miss | few_matches, length_16_plus, no_match | 39849.92769487815 | {'fallback_to_naive': 0, 'selected_seed_a': 'zzb', 'selected_seed_b': 'rkn', 'frequency_a': 0, 'frequency_b': 1, 'seed_occurrences_expanded': 1, 'candidate_contexts_before_dedup': 0, 'candidate_contexts_after_dedup': 0, 'verifier_calls': 0} |
| gdbmnextkeykey | few_matches, inside_word, length_9_15, medium_qgram | 39731.22451751655 | {'fallback_to_naive': 0, 'selected_seed_a': 'bmn', 'selected_seed_b': 'xtk', 'frequency_a': 23, 'frequency_b': 10, 'seed_occurrences_expanded': 33, 'candidate_contexts_before_dedup': 125, 'candidate_contexts_after_dedup': 122, 'verifier_calls': 122} |
| pythondev2001january | few_matches, inside_word, length_16_plus, rare_qgram | 22329.678740063355 | {'fallback_to_naive': 0, 'selected_seed_a': 'v20', 'selected_seed_b': '1ja', 'frequency_a': 3, 'frequency_b': 1, 'seed_occurrences_expanded': 4, 'candidate_contexts_before_dedup': 12, 'candidate_contexts_after_dedup': 9, 'verifier_calls': 9} |
| ipaddressipv6addressaddress | inside_word, length_16_plus, long_exact, many_matches | 8444.693534365662 | {'fallback_to_naive': 0, 'selected_seed_a': 'v6a', 'selected_seed_b': 'sad', 'frequency_a': 23, 'frequency_b': 111, 'seed_occurrences_expanded': 134, 'candidate_contexts_before_dedup': 465, 'candidate_contexts_after_dedup': 459, 'verifier_calls': 459} |
| inxtalling | inside_word, length_9_15, many_matches, replacement | 830.365102069044 | {'fallback_to_naive': 0, 'selected_seed_a': 'nxt', 'selected_seed_b': 'lli', 'frequency_a': 1, 'frequency_b': 1922, 'seed_occurrences_expanded': 1923, 'candidate_contexts_before_dedup': 13531, 'candidate_contexts_after_dedup': 13531, 'verifier_calls': 13531} |
| insxtalling | deletion, inside_word, length_9_15, many_matches | 722.770683187731 | {'fallback_to_naive': 0, 'selected_seed_a': 'sxt', 'selected_seed_b': 'lli', 'frequency_a': 0, 'frequency_b': 1922, 'seed_occurrences_expanded': 1922, 'candidate_contexts_before_dedup': 13111, 'candidate_contexts_after_dedup': 13111, 'verifier_calls': 13111} |
| insalling | insertion, inside_word, length_9_15, many_matches | 719.1218655431779 | {'fallback_to_naive': 0, 'selected_seed_a': 'nsa', 'selected_seed_b': 'lli', 'frequency_a': 256, 'frequency_b': 1922, 'seed_occurrences_expanded': 2178, 'candidate_contexts_before_dedup': 15911, 'candidate_contexts_after_dedup': 15911, 'verifier_calls': 15911} |
| descriptor | inside_word, length_9_15, many_matches, medium_exact | 444.11405019650914 | {'fallback_to_naive': 0, 'selected_seed_a': 'esc', 'selected_seed_b': 'pto', 'frequency_a': 2603, 'frequency_b': 994, 'seed_occurrences_expanded': 3597, 'candidate_contexts_before_dedup': 28633, 'candidate_contexts_after_dedup': 22199, 'verifier_calls': 22199} |
| requests | length_6_8, many_matches, near_boundary | 330.81208785660186 | {'fallback_to_naive': 0, 'selected_seed_a': 'req', 'selected_seed_b': 'sts', 'frequency_a': 2492, 'frequency_b': 2499, 'seed_occurrences_expanded': 4991, 'candidate_contexts_before_dedup': 37329, 'candidate_contexts_after_dedup': 35857, 'verifier_calls': 35857} |
| extensions | common_qgram, inside_word, length_9_15, many_matches | 324.69631016492514 | {'fallback_to_naive': 0, 'selected_seed_a': 'xte', 'selected_seed_b': 'nsi', 'frequency_a': 1778, 'frequency_b': 2989, 'seed_occurrences_expanded': 4767, 'candidate_contexts_before_dedup': 36946, 'candidate_contexts_after_dedup': 27756, 'verifier_calls': 27756} |
| convert | inside_word, length_6_8, many_matches, medium_exact | 267.4360347253299 | {'fallback_to_naive': 0, 'selected_seed_a': 'onv', 'selected_seed_b': 'ert', 'frequency_a': 1950, 'frequency_b': 4279, 'seed_occurrences_expanded': 6229, 'candidate_contexts_before_dedup': 48213, 'candidate_contexts_after_dedup': 39156, 'verifier_calls': 39156} |
| reference | inside_word, length_9_15, many_matches, medium_exact | 198.9322624503887 | {'fallback_to_naive': 0, 'selected_seed_a': 'efe', 'selected_seed_b': 'ren', 'frequency_a': 2544, 'frequency_b': 6215, 'seed_occurrences_expanded': 8759, 'candidate_contexts_before_dedup': 68531, 'candidate_contexts_after_dedup': 54064, 'verifier_calls': 54064} |
| installing | inside_word, length_9_15, many_matches, repeated | 181.07548296319527 | {'fallback_to_naive': 0, 'selected_seed_a': 'ins', 'selected_seed_b': 'lli', 'frequency_a': 8582, 'frequency_b': 1922, 'seed_occurrences_expanded': 10504, 'candidate_contexts_before_dedup': 75613, 'candidate_contexts_after_dedup': 74422, 'verifier_calls': 74422} |
| output | inside_word, length_6_8, many_matches, medium_exact | 156.67606285826304 | {'fallback_to_naive': 0, 'selected_seed_a': 'out', 'selected_seed_b': 'put', 'frequency_a': 5917, 'frequency_b': 3348, 'seed_occurrences_expanded': 9265, 'candidate_contexts_before_dedup': 73524, 'candidate_contexts_after_dedup': 61797, 'verifier_calls': 61797} |
| installi | length_6_8, many_matches, near_boundary | 153.6653542101723 | {'fallback_to_naive': 0, 'selected_seed_a': 'ins', 'selected_seed_b': 'lli', 'frequency_a': 8582, 'frequency_b': 1922, 'seed_occurrences_expanded': 10504, 'candidate_contexts_before_dedup': 81218, 'candidate_contexts_after_dedup': 79976, 'verifier_calls': 79976} |
| pyobject | inside_word, length_6_8, many_matches, medium_exact | 98.76829415387249 | {'fallback_to_naive': 0, 'selected_seed_a': 'pyo', 'selected_seed_b': 'bje', 'frequency_a': 2153, 'frequency_b': 12523, 'seed_occurrences_expanded': 14676, 'candidate_contexts_before_dedup': 114383, 'candidate_contexts_after_dedup': 98278, 'verifier_calls': 98278} |
| installing | inside_word, length_9_15, many_matches, medium_exact | 94.29301025130671 | {'fallback_to_naive': 0, 'selected_seed_a': 'ins', 'selected_seed_b': 'lli', 'frequency_a': 8582, 'frequency_b': 1922, 'seed_occurrences_expanded': 10504, 'candidate_contexts_before_dedup': 75613, 'candidate_contexts_after_dedup': 74422, 'verifier_calls': 74422} |
| python | high_frequency, inside_word, length_6_8, many_matches, multiple_matches | 85.85716859472574 | {'fallback_to_naive': 0, 'selected_seed_a': 'pyt', 'selected_seed_b': 'hon', 'frequency_a': 10127, 'frequency_b': 9573, 'seed_occurrences_expanded': 19700, 'candidate_contexts_before_dedup': 161436, 'candidate_contexts_after_dedup': 84328, 'verifier_calls': 84328} |
| return | inside_word, length_6_8, many_matches, medium_exact | 79.64893109710934 | {'fallback_to_naive': 0, 'selected_seed_a': 'ret', 'selected_seed_b': 'urn', 'frequency_a': 11971, 'frequency_b': 9887, 'seed_occurrences_expanded': 21858, 'candidate_contexts_before_dedup': 168325, 'candidate_contexts_after_dedup': 94559, 'verifier_calls': 94559} |
| return | inside_word, length_6_8, many_matches, medium_exact | 60.47758554487266 | {'fallback_to_naive': 0, 'selected_seed_a': 'ret', 'selected_seed_b': 'urn', 'frequency_a': 11971, 'frequency_b': 9887, 'seed_occurrences_expanded': 21858, 'candidate_contexts_before_dedup': 168325, 'candidate_contexts_after_dedup': 94559, 'verifier_calls': 94559} |

# 14. Parameter comparison

The parameter panel uses the same three full-corpus queries per configuration. It does not override the q=3 production default, and faster Tree Hybrid values do not pass the correctness gate.

| q | Algorithm | Status | Build ms | Retained MiB | Fallback | Median ms | P95 ms | Median candidates | Median verifier calls |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| q=2 | qgram_positional | error | 0.134 | 0.00 | n/a | n/a | n/a | n/a | n/a |
| q=2 | qgram_tree_hybrid | ok | 7458.449 | 186.05 | 0.0 | 162.863 | 219.735 | 21902.0 | 21902.0 |
| q=2 | bi_anchor | ok | 29308.112 | 276.51 | 0.0 | 1324.195 | 2295.502 | 247085.0 | 247085.0 |
| q=3 | qgram_positional | error | 0.116 | 0.00 | n/a | n/a | n/a | n/a | n/a |
| q=3 | qgram_tree_hybrid | ok | 10539.057 | 187.49 | 0.0 | 33.848 | 45.634 | 5732.0 | 5732.0 |
| q=3 | bi_anchor | ok | 30751.907 | 330.63 | 0.0 | 60.010 | 330.205 | 13531.0 | 13531.0 |
| q=4 | qgram_positional | error | 0.098 | 0.00 | n/a | n/a | n/a | n/a | n/a |
| q=4 | qgram_tree_hybrid | ok | 8617.555 | 193.33 | 0.0 | 4.460 | 4.857 | 620.0 | 620.0 |
| q=4 | bi_anchor | ok | 43960.655 | 380.86 | 0.0 | 41.489 | 203.619 | 7620.0 | 7620.0 |

# 15. Scaling with corpus size

Stable production-order prefixes and one shared no-match query were used. With one observation per point, median and p95 are identical.

| Corpus | Sentences | Algorithm | Status | Build ms | Retained MiB | Median ms | P95 ms |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 10% | 19440 | naive | ok | 0.047 | 0.00 | 6608.792 | 6608.792 |
| 10% | 19440 | qgram_positional | error | 0.120 | 0.00 | n/a | n/a |
| 10% | 19440 | qgram_tree_hybrid | ok | 2196.538 | 21.96 | 1.909 | 1.909 |
| 10% | 19440 | bi_anchor | ok | 4399.152 | 31.97 | 0.305 | 0.305 |
| 25% | 48598 | naive | ok | 0.054 | 0.00 | 17746.304 | 17746.304 |
| 25% | 48598 | qgram_positional | error | 0.140 | 0.00 | n/a | n/a |
| 25% | 48598 | qgram_tree_hybrid | ok | 3316.209 | 51.54 | 3.620 | 3.620 |
| 25% | 48598 | bi_anchor | ok | 9447.478 | 82.20 | 0.668 | 0.668 |
| 50% | 97196 | naive | ok | 0.037 | 0.00 | 31245.691 | 31245.691 |
| 50% | 97196 | qgram_positional | error | 0.073 | 0.00 | n/a | n/a |
| 50% | 97196 | qgram_tree_hybrid | ok | 4951.438 | 98.44 | 3.941 | 3.941 |
| 50% | 97196 | bi_anchor | ok | 15373.596 | 162.74 | 1.254 | 1.254 |
| 75% | 145794 | naive | ok | 0.219 | 0.00 | 54436.311 | 54436.311 |
| 75% | 145794 | qgram_positional | error | 0.083 | 0.00 | n/a | n/a |
| 75% | 145794 | qgram_tree_hybrid | ok | 5731.648 | 146.36 | 8.623 | 8.623 |
| 75% | 145794 | bi_anchor | ok | 21744.507 | 242.87 | 2.477 | 2.477 |
| 100% | 194392 | naive | ok | 0.071 | 0.00 | 76765.238 | 76765.238 |
| 100% | 194392 | qgram_positional | error | 0.080 | 0.00 | n/a | n/a |
| 100% | 194392 | qgram_tree_hybrid | ok | 7746.088 | 187.49 | 23.720 | 23.720 |
| 100% | 194392 | bi_anchor | ok | 31685.871 | 330.63 | 2.700 | 2.700 |

# 16. CPU profiles

Profiles use a stable 10% corpus prefix. The profile JSON contains the top 15 functions for each scenario.

| Algorithm | Scenario | Status | Elapsed ms | Hottest cumulative function | Cumulative s | Self s | Calls |
| --- | --- | --- | --- | --- | --- | --- | --- |
| naive | build | ok | 3.033 | real_corpus_benchmark.py:199(_construct_algorithm) | 0.0001474 | 1.8900000000000002e-05 | 1 |
| naive | typical_fast | ok | 8471.254 | real_corpus_benchmark.py:84(search) | 8.4711367 | 3.2000000000000003e-06 | 1 |
| naive | typical_medium | ok | 8344.182 | real_corpus_benchmark.py:84(search) | 8.3440869 | 2.0000000000000003e-06 | 1 |
| naive | representative_worst | ok | 8838.888 | real_corpus_benchmark.py:84(search) | 8.8387656 | 2.9e-06 | 1 |
| qgram_positional | build | error | 0.515 | real_corpus_benchmark.py:199(_construct_algorithm) | 0.00041180000000000003 | 9.600000000000001e-06 | 1 |
| qgram_tree_hybrid | build | ok | 1727.885 | real_corpus_benchmark.py:199(_construct_algorithm) | 1.7277736000000001 | 1.4700000000000002e-05 | 1 |
| qgram_tree_hybrid | typical_fast | ok | 3.626 | real_corpus_benchmark.py:84(search) | 0.0035065 | 2.16e-05 | 1 |
| qgram_tree_hybrid | typical_medium | ok | 23.221 | real_corpus_benchmark.py:84(search) | 0.0230846 | 4.92e-05 | 1 |
| qgram_tree_hybrid | representative_worst | ok | 14.619 | real_corpus_benchmark.py:84(search) | 0.014505500000000001 | 5.66e-05 | 1 |
| bi_anchor | build | ok | 859.888 | real_corpus_benchmark.py:199(_construct_algorithm) | 0.8597207 | 1.9e-05 | 1 |
| bi_anchor | typical_fast | ok | 0.784 | real_corpus_benchmark.py:84(search) | 0.0006945 | 8.1e-06 | 1 |
| bi_anchor | typical_medium | ok | 305.140 | real_corpus_benchmark.py:84(search) | 0.305027 | 0.0021497 | 1 |
| bi_anchor | representative_worst | ok | 53.308 | real_corpus_benchmark.py:84(search) | 0.053209900000000004 | 0.0004334 | 1 |

Confirmed bottlenecks: Naive spends cumulative time in the full `_search_sentence`/`_check_from_position` scan and shared verifier; Tree Hybrid build time is dominated by `_insert_word` and query time by `_fuzzy_compare` plus result emission; Bi-Anchor build time is in `HashSeedLookup.build`, while common-query time is dominated by `_candidate_contexts` and `OneEditVerifier.compare`. Positional Q-Gram fails immediately in `QGramSearchStructure.add_sentence`.

# 17. Memory profiles

Retained and peak values use tracemalloc started after corpus preparation; they are allocation estimates, not exact recursive object sizes. See the offline-build table.

# 18. Final comparison table

| Algorithm | Correct | FN | Build ms | Memory MiB | Median ms | P95 ms | P99 ms | Median speedup | Worst speedup | Strength | Weakness |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| naive | True | 0 | 0.043 | 0.00 | 50072.678 | 70201.101 | 74719.571 | None | None | near-zero build/index memory | full-corpus exhaustive scan |
| qgram_positional | False | None | 0.100 | 0.00 | n/a | n/a | n/a | None | None | compact packed postings (design intent) | not runnable on shared corpus/result contract |
| qgram_tree_hybrid | False | 259869 | 6823.954 | 187.49 | 20.552 | 57.320 | 82.674 | 5790.063494588101 | 5790.063494588101 | very low measured lookup latency | prefix-only/capped semantics; incorrect raw results |
| bi_anchor | True | 0 | 32516.096 | 330.63 | 229.182 | 851.151 | 2694.172 | 198.9322624503887 | 21.411237819171323 | no_match | cross_word |

# 19. Improvement opportunities

| Algorithm | Expected benefit | Complexity | Correctness risk | Memory impact | Measured evidence |
| --- | --- | --- | --- | --- | --- |
| naive | High | High | High | Worse | Full-corpus pilot exceeded 120 seconds; exhaustive verifier-call counts are recorded per query. |
| qgram_positional | Unknown until runnable | Medium | High | Worse | AttributeError: 'PreparedSentence' object has no attribute 'normalized_sentence' |
| qgram_tree_hybrid | Low as a direct replacement | High | High | Worse | 22 raw-result mismatches in the executed workload. |
| bi_anchor | High | Low to Medium | Low | Better | 0 mismatches and 3284984 boundary occurrences contribute to 330.63 MiB retained index memory. |

# 20. Recommended next step

## Decision answers

1. **Best overall:** Bi-Anchor. It was correct on all 23 queries, won all correct head-to-heads, and had a 229.182 ms median.
2. **Best for short queries:** No defensible full-corpus latency winner: length 1-5 raw candidate materialization was resource-guarded. Bi-Anchor delegates these queries to Naive, so both share the exhaustive path.
3. **Best for medium queries:** Bi-Anchor among correct implementations (456.244 ms median versus 42048.481 ms for Naive).
4. **Best for long queries:** Bi-Anchor (7.362 ms versus 62169.834 ms).
5. **Best for common substrings:** Bi-Anchor among correct implementations (167.658 ms); common anchors are nevertheless one of its expensive cases.
6. **Best for rare substrings:** Bi-Anchor (3.346 ms); rare seeds nearly eliminate verification work.
7. **Best for cross-word matching:** Bi-Anchor (2694.172 ms) and correct; Tree Hybrid does not support equivalent cross-word semantics.
8. **Least memory:** Naive, with 0.0011 MiB traced retained structure memory beyond the shared corpus.
9. **Cheapest offline build:** Naive at 0.043 ms; it effectively stores only the corpus reference.
10. **Best latency/memory tradeoff:** Bi-Anchor is the only practical correct indexed choice: 330.63 MiB for a 218.5x ratio of median latencies.
11. **Correctness failures:** Yes. Tree Hybrid mismatched 22/23 queries with 259869 false-negative candidates. Positional Q-Gram was not runnable.
12. **Hybrid runtime strategy:** Not yet beyond the existing Bi-Anchor-to-Naive short-query fallback. The other indexed implementations must first pass the raw-result correctness gate.

## Hybrid analysis

The existing Bi-Anchor short-query fallback already implements the only safe length-based routing supported by these correctness results. The Tree Hybrid and positional Q-Gram implementations cannot be routing targets until their raw-result contracts pass the Naive oracle.

## One next experiment

Prototype a benchmark-only packed representation for Bi-Anchor boundary occurrences (for example, packed integer arrays) and rerun the same correctness/memory/latency study. The real index stores 3,284,984 boundary occurrences and retains about 330.63 MiB; 76% more than the incorrect Tree Hybrid—so this is the clearest low-semantics-risk opportunity. Do not change production until all raw candidates remain identical to Naive.

## Limitations

- A full-corpus Naive pilot query did not finish within 120 seconds; the suggested 500-1000 queries and 10-30 repetitions were computationally impractical.
- Online results use 23 full-corpus queries and one timed repetition per query with no separate warm-up; percentile estimates are across query observations and are correspondingly coarse.
- Length 1-5 raw-result queries were resource-guarded to avoid explosive candidate materialization; short-query conclusions are based on code path and smaller scaling/profile observations, not full-corpus latency.
- CPU profiles use a stable 10% corpus prefix and are labeled as such.
- tracemalloc values estimate Python allocations made after corpus preparation; they are not exact recursive object sizes or process RSS.
