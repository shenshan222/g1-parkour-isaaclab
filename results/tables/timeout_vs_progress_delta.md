# Timeout vs traversal progress delta

Delta is computed as `timeout_rate - progress_pass_rate`. Positive values mean the policy survived to timeout but did not always satisfy the 4 m forward-progress threshold. All values use the official 4×4 cross/stress result CSVs (6 checkpoint sources after MDP merge).

## Random cross-terrain delta

| Checkpoint source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| rough | 0.00% | 0.00% | 0.00% | 0.00% |
| easy | 1.56% | 0.00% | 0.00% | 0.00% |
| medium | 0.00% | 0.00% | 0.00% | 0.00% |
| hard | 0.00% | 0.00% | 0.00% | 0.00% |
| rough_mdp | 0.00% | 0.00% | 0.00% | 0.00% |
| hard_mdp | 0.00% | 0.00% | 0.00% | 0.00% |

## Fixed-row stress delta

| Checkpoint source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| rough | 0.00% | 0.00% | 0.00% | 0.00% |
| easy | 1.56% | 0.00% | 0.00% | 0.00% |
| medium | 0.00% | 0.00% | 0.00% | 0.00% |
| hard | 0.00% | 0.00% | 0.00% | 0.00% |
| rough_mdp | 0.00% | 0.00% | 0.00% | 0.00% |
| hard_mdp | 0.00% | 0.00% | 0.00% | 0.00% |

## Interpretation

The maximum observed delta is 1.56 percentage points. It appears only for easy-to-rough in both random and stress evaluation — exactly one episode out of 64 survived but did not reach the 4 m forward mark. Across all other 47 source/eval/metric combinations the delta is zero.

This means traversal progress adds a useful sanity check but only limited new information over timeout for the current result set. The current policies either fall early or survive while moving far enough forward; there are very few episodes that survive but fail the 4 m progress threshold. The MDP policies are no exception to this pattern.
