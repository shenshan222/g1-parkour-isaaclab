# Obstacle pass rate

| Checkpoint source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| rough | 88.46% | 88.46% | 16.39% | 25.00% |
| easy | 92.31% | 96.15% | 0.00% | 0.00% |
| medium | 100.00% | 100.00% | 96.88% | 65.79% |
| hard | 100.00% | 100.00% | 87.50% | 100.00% |
| rough_mdp | 100.00% | 100.00% | 77.78% | 41.03% |
| hard_mdp | 100.00% | 100.00% | 100.00% | 100.00% |

# Gap pass rate

| Checkpoint source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| rough | N/A | N/A | 0.00% | 7.89% |
| easy | N/A | N/A | 0.00% | 0.00% |
| medium | N/A | N/A | 91.67% | 33.33% |
| hard | N/A | N/A | 66.67% | 100.00% |
| rough_mdp | N/A | N/A | 50.00% | 21.43% |
| hard_mdp | N/A | N/A | 100.00% | 100.00% |

# Stairs pass rate

| Checkpoint source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| rough | 88.46% | 88.46% | 100.00% | 90.00% |
| easy | 92.31% | 96.15% | N/A | 0.00% |
| medium | 100.00% | 100.00% | 100.00% | 95.00% |
| hard | 100.00% | 100.00% | 100.00% | 100.00% |
| rough_mdp | 100.00% | 100.00% | 100.00% | 90.91% |
| hard_mdp | 100.00% | 100.00% | 100.00% | 100.00% |

# Fall before obstacle rate

| Checkpoint source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| rough | 0.00% | 0.00% | 70.49% | 64.58% |
| easy | 0.00% | 0.00% | 95.16% | 89.66% |
| medium | 0.00% | 0.00% | 3.12% | 31.58% |
| hard | 0.00% | 0.00% | 9.38% | 0.00% |
| rough_mdp | 0.00% | 0.00% | 19.44% | 51.28% |
| hard_mdp | 0.00% | 0.00% | 0.00% | 0.00% |

# Mean boundary x

| Checkpoint source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| rough | 2.80 | 2.80 | 1.70 | 1.69 |
| easy | 2.80 | 2.80 | 1.48 | 1.52 |
| medium | 2.80 | 2.80 | 2.31 | 2.14 |
| hard | 2.80 | 2.80 | 2.31 | 2.27 |
| rough_mdp | 2.80 | 2.80 | 2.21 | 1.79 |
| hard_mdp | 2.80 | 2.80 | 2.31 | 2.27 |

# Mean max local x

| Checkpoint source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| rough | 34.79 | 33.04 | 6.49 | 10.20 |
| easy | 33.22 | 34.15 | 0.74 | 0.71 |
| medium | 35.07 | 36.53 | 34.65 | 24.12 |
| hard | 36.70 | 44.76 | 39.34 | 44.33 |
| rough_mdp | 36.88 | 48.91 | 38.55 | 21.03 |
| hard_mdp | 34.59 | 34.69 | 34.91 | 35.05 |

Note: obstacle pass is computed for gap and stairs terrain groups using base-level geometry boundaries.
Gap pass requires crossing the far side of the gap plus a margin; stairs pass requires reaching the forward outer stair-field boundary.
N/A means no gap/stairs boundary episode was covered for that source/eval pair.
