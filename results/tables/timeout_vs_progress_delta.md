# Timeout vs traversal progress delta

Delta is computed as `timeout_rate - progress_pass_rate`. Positive values mean the policy survived to timeout but did not always satisfy the 4 m forward-progress threshold. All values use the official 4x4 cross/stress result CSVs.

## Random cross-terrain delta

| Checkpoint source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| rough | 0.00% | 0.00% | 0.00% | 0.00% |
| easy | 1.56% | 0.00% | 0.00% | 0.00% |
| medium | 0.00% | 0.00% | 0.00% | 0.00% |
| hard | 0.00% | 0.00% | 0.00% | 0.00% |

## Fixed-row stress delta

| Checkpoint source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| rough | 0.00% | 0.00% | 0.00% | 0.00% |
| easy | 1.56% | 0.00% | 0.00% | 0.00% |
| medium | 0.00% | 0.00% | 0.00% | 0.00% |
| hard | 0.00% | 0.00% | 0.00% | 0.00% |

## Interpretation

The maximum observed delta is 1.56 percentage points, and it appears only for easy-to-rough in both random and stress evaluation. This means traversal progress adds a useful sanity check but only limited new information over timeout for the current result set. The current policies either fall early or survive while moving far enough forward; there are very few episodes that survive but fail the 4 m progress threshold.
