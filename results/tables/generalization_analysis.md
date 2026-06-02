# Cross-terrain generalization analysis

This table-level analysis combines timeout and traversal-progress cross/stress results. All entries use 64 episodes, 32 parallel environments, seed 42, 10x10 evaluation terrain grids, curriculum disabled, and the official 3000-iteration checkpoints for rough/easy/medium/hard.

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

## Summary conclusion

The terrain difficulty ablation has clear reporting value. Easy training is stable but does not cover hard obstacles. Medium training, which introduces gaps and stronger terrain, substantially improves hard transfer. Hard training is the strongest source policy across random and fixed-row stress evaluation, making the hard checkpoint the best current starting point for future mixed-terrain or generalist training. Timeout and traversal-progress results are nearly identical, so current failures are dominated by base-contact falls rather than by long-lived but non-progressing behavior.
