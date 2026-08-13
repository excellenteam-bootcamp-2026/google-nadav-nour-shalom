# Adaptive Multi-q Bi-Anchor: Short-Query Study

## Corpus

- source_archive: data\Archive3.zip
- prepared_sentences: 194392
- normalized_characters: 8158666
- source_files: 480
- latency_fraction: 0.1
- latency_sentences: 19440
- correctness_fraction: 0.02
- correctness_sentences: 3888
- expansion_guard: None

## Workload

- queries: 96
- per_length: 16
- lengths: [1, 2, 3, 4, 5, 6]
- tags: {'common_seed': 18, 'cross_word': 23, 'deletion': 10, 'exact': 60, 'insertion': 10, 'inside_word': 68, 'no_match': 5, 'rare_seed': 18, 'replacement': 11}

## Correctness gate

Oracle: Naive on 3888 sentences.

| Runtime | Queries | Matching | Mismatches | FN | FP |
| --- | --- | --- | --- | --- | --- |
| adaptive | 96 | 96 | 0 | 0 | 0 |
| q1 | 96 | 96 | 0 | 0 | 0 |
| q2 | 96 | 96 | 0 | 0 | 0 |
| q3 | 96 | 96 | 0 | 0 | 0 |

## Per-length results

| Length | Naive ms | q1 ms | q2 ms | q3 ms | Adaptive ms | Selected q | Speedup vs Naive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 5105.484 | N/A | N/A | N/A | N/A | fallback | n/a |
| 2 | 3162.616 | 2567.245 | N/A | N/A | 2521.319 | q1x16 | 1.3x |
| 3 | 3327.436 | 895.021 | N/A | N/A | 797.713 | q1x16 | 4.2x |
| 4 | 4864.435 | 897.427 | 105.095 | N/A | 144.533 | q2x16 | 33.7x |
| 5 | 9098.084 | 1946.205 | 172.791 | N/A | 192.257 | q2x16 | 47.3x |
| 6 | 6817.552 | 1428.664 | 201.476 | 94.047 | 85.475 | q2x1, q3x15 | 79.8x |

## Internal work

| Length | Runtime | Median occurrences | Median contexts | Median verifier calls | Fallback rate |
| --- | --- | --- | --- | --- | --- |
| 2 | q1 | 79510 | 595654 | 595654 | 0.00 |
| 2 | adaptive | 79510 | 595654 | 595654 | 0.00 |
| 3 | q1 | 29466 | 235910 | 235910 | 0.00 |
| 3 | adaptive | 29466 | 235910 | 235910 | 0.00 |
| 4 | q1 | 30339 | 199139 | 199139 | 0.00 |
| 4 | q2 | 3014 | 24720 | 24720 | 0.00 |
| 4 | adaptive | 3014 | 24720 | 24720 | 0.00 |
| 5 | q1 | 27286 | 191860 | 191860 | 0.00 |
| 5 | q2 | 3006 | 24384 | 24384 | 0.00 |
| 5 | adaptive | 3006 | 24384 | 24384 | 0.00 |
| 6 | q1 | 24550 | 188012 | 188012 | 0.00 |
| 6 | q2 | 3493 | 22046 | 22046 | 0.00 |
| 6 | q3 | 1504 | 11528 | 11528 | 0.00 |
| 6 | adaptive | 1504 | 11528 | 11528 | 0.00 |

## Index configurations

| Configuration | Build ms | Retained MiB | Peak MiB | Intra-word keys | Intra-word refs | Boundary keys | Boundary occ |
| --- | --- | --- | --- | --- | --- | --- | --- |
