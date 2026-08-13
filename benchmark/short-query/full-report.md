# Adaptive Multi-q Bi-Anchor: Short-Query Study

## Corpus

- source_archive: data\Archive3.zip
- prepared_sentences: 194392
- normalized_characters: 8158666
- source_files: 480
- latency_fraction: 1.0
- latency_sentences: 194392
- correctness_fraction: 0.02
- correctness_sentences: 3888
- expansion_guard: 500000

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
| 1 | 34164.788 | N/A | N/A | N/A | N/A | fallback | n/a |
| 2 | 35946.484 | 2476.192 | N/A | N/A | 2428.180 | q1x16 | 14.8x |
| 3 | 44464.890 | 6646.651 | N/A | N/A | 6097.220 | q1x16 | 7.3x |
| 4 | 58367.750 | 6555.249 | 1221.715 | N/A | 1437.723 | q2x16 | 40.6x |
| 5 | 42236.445 | 11052.225 | 1655.369 | N/A | 2029.040 | q2x16 | 20.8x |
| 6 | 46895.123 | 5936.461 | 950.599 | 585.420 | 443.028 | q2x1, q3x15 | 105.9x |

## Internal work

| Length | Runtime | Median occurrences | Median contexts | Median verifier calls | Fallback rate |
| --- | --- | --- | --- | --- | --- |
| 2 | q1 | 77761 | 666621 | 666621 | 0.00 |
| 2 | adaptive | 77761 | 666621 | 666621 | 0.00 |
| 3 | q1 | 173349 | 1413847 | 1413847 | 0.00 |
| 3 | adaptive | 173349 | 1413847 | 1413847 | 0.00 |
| 4 | q1 | 173349 | 1393344 | 1393344 | 0.00 |
| 4 | q2 | 31398 | 257314 | 257314 | 0.00 |
| 4 | adaptive | 31398 | 257314 | 257314 | 0.00 |
| 5 | q1 | 173349 | 1362566 | 1362566 | 0.00 |
| 5 | q2 | 31398 | 254100 | 254100 | 0.00 |
| 5 | adaptive | 31398 | 254100 | 254100 | 0.00 |
| 6 | q1 | 162055 | 1227143 | 1227143 | 0.00 |
| 6 | q2 | 31888 | 221058 | 221058 | 0.00 |
| 6 | q3 | 14930 | 110170 | 110170 | 0.00 |
| 6 | adaptive | 14930 | 110170 | 110170 | 0.00 |

## Index configurations

| Configuration | Build ms | Retained MiB | Peak MiB | Intra-word keys | Intra-word refs | Boundary keys | Boundary occ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| q={3} | 22499 | 331.6 | 365.7 | 16060 | 640187 | 3416 | 3284984 |
| q={2,3} | 42627 | 501.0 | 535.2 | 17457 | 1343766 | 3563 | 5511986 |
| q={1,2,3} | 48332 | 615.1 | 649.2 | 17566 | 2110802 | 3564 | 6625487 |
