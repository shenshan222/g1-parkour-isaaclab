# Cross-terrain generalization analysis

This table-level analysis combines timeout, traversal-progress, and obstacle-crossing cross/stress results. All entries use 64 episodes, 32 parallel environments, seed 42, 10x10 evaluation terrain grids, curriculum disabled, and the official 3000-iteration checkpoints for rough/easy/medium/hard.

## Random cross-terrain timeout

| Checkpoint source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| rough | 95.31% | 98.44% | 68.75% | 29.69% |
| easy | 90.62% | 100.00% | 50.00% | 0.00% |
| medium | 98.44% | 98.44% | 95.31% | 87.50% |
| hard | 100.00% | 100.00% | 96.88% | 95.31% |

Key observations:

- Rough and easy checkpoints transfer poorly to hard terrain: rough-to-hard reaches only 29.69%, and easy-to-hard is 0.00%.
- Medium is the first parkour tier that transfers strongly to hard, reaching 87.50% on hard evaluation.
- Hard is the strongest source policy: it reaches at least 95.31% timeout rate on all four evaluation environments.

## Fixed-row stress timeout

| Checkpoint source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| rough | 98.44% | 78.12% | 56.25% | 31.25% |
| easy | 95.31% | 98.44% | 64.06% | 0.00% |
| medium | 95.31% | 100.00% | 100.00% | 92.19% |
| hard | 100.00% | 100.00% | 96.88% | 95.31% |

Key observations:

- The stress setting preserves the main ordering from random cross evaluation: rough/easy are weak on hard, while medium/hard remain strong.
- Easy-to-hard remains 0.00%, confirming that easy terrain without gap exposure is not sufficient for hard obstacle robustness.
- Hard remains robust under fixed high-row evaluation, with 95.31% hard-to-hard timeout rate.

## Random cross-terrain traversal progress

| Checkpoint source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| rough | 95.31% | 98.44% | 68.75% | 29.69% |
| easy | 89.06% | 100.00% | 50.00% | 0.00% |
| medium | 98.44% | 98.44% | 95.31% | 87.50% |
| hard | 100.00% | 100.00% | 96.88% | 95.31% |

Key observations:

- Traversal progress almost exactly matches timeout in the random setting.
- The only nonzero timeout-progress difference is easy-to-rough, where timeout is 1.56 percentage points higher than progress pass.
- This confirms that most successful timeout episodes also satisfy the 4 m forward-distance threshold.

## Fixed-row stress traversal progress

| Checkpoint source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| rough | 98.44% | 78.12% | 56.25% | 31.25% |
| easy | 93.75% | 98.44% | 64.06% | 0.00% |
| medium | 95.31% | 100.00% | 100.00% | 92.19% |
| hard | 100.00% | 100.00% | 96.88% | 95.31% |

Key observations:

- Stress progress again mirrors stress timeout, with only easy-to-rough lower by 1.56 percentage points.
- The progress metric therefore supports the same generalization conclusion as timeout: medium is the minimum tier that adapts well to hard, while hard is the best generalist source among current specialists.
- Traversal progress should be reported as a forward-distance proxy, not as explicit terrain-aware obstacle-boundary passing.

## Fixed-row stress obstacle crossing

Obstacle crossing is evaluated only on supported gap/stairs terrain groups. Unsupported terrain groups such as boxes, rough, and slope are recorded in coverage metadata but excluded from `obstacle_pass_rate`.

| Checkpoint source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| rough | 88.46% | 88.46% | 16.39% | 25.00% |
| easy | 92.31% | 96.15% | 0.00% | 0.00% |
| medium | 100.00% | 100.00% | 96.88% | 65.79% |
| hard | 100.00% | 100.00% | 87.50% | 100.00% |

Gap pass rate:

| Checkpoint source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| rough | N/A | N/A | 0.00% | 7.89% |
| easy | N/A | N/A | 0.00% | 0.00% |
| medium | N/A | N/A | 91.67% | 33.33% |
| hard | N/A | N/A | 66.67% | 100.00% |

Key observations:

- Hard-to-hard reaches 100.00% obstacle, gap, and stairs pass rates, so the hard checkpoint solves the supported hard gap/stairs boundaries in the official stress protocol.
- Medium-to-hard reaches 65.79% obstacle pass. Its stairs pass remains high at 95.00%, but hard gap pass falls to 33.33%, identifying hard gap crossing as the main terrain-specific gap between medium and hard policies.
- Easy-to-hard remains 0.00% in both obstacle and gap pass, which is consistent with easy training having no gap terrain.
- Rough-to-medium and rough-to-hard should be interpreted through the gap/stairs split: rough is poor on gaps in both cases, while the aggregate differs because each source/eval pair covers a different supported-obstacle denominator.

## Summary conclusion

The terrain difficulty ablation has clear reporting value. Easy training is stable but does not cover hard obstacles. Medium training, which introduces gaps and stronger terrain, substantially improves survival and forward-progress transfer, but the obstacle crossing metric shows that medium still struggles on hard gaps. Hard training is the strongest source policy across random timeout, fixed-row stress, and supported obstacle crossing, making the hard checkpoint the best current starting point for future mixed-terrain or generalist training. Timeout and traversal-progress results are nearly identical, so the explicit obstacle crossing metric is the more informative result for gap/stairs completion claims.
