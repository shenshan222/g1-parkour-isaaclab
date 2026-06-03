# Cross-terrain generalization analysis

This table-level analysis combines timeout, traversal-progress, and obstacle-crossing cross/stress results. All entries use 64 episodes, 32 parallel environments, seed 42, 10×10 evaluation terrain grids, curriculum disabled, and the official 3000-iteration checkpoints for rough/easy/medium/hard/rough_mdp/hard_mdp.

## Random cross-terrain timeout

| Checkpoint source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| rough | 95.31% | 98.44% | 68.75% | 29.69% |
| easy | 90.62% | 100.00% | 50.00% | 0.00% |
| medium | 98.44% | 98.44% | 95.31% | 87.50% |
| hard | 100.00% | 100.00% | 96.88% | 95.31% |
| rough_mdp | 100.00% | 100.00% | 76.56% | 70.31% |
| hard_mdp | 100.00% | 100.00% | 96.88% | 92.19% |

Key observations:

- Rough and easy checkpoints transfer poorly to hard terrain: rough-to-hard reaches only 29.69%, and easy-to-hard is 0.00%.
- Medium is the first parkour tier that transfers strongly to hard, reaching 87.50% on hard evaluation.
- Hard is the strongest source policy among the baseline four: it reaches at least 95.31% timeout rate on all four evaluation environments.
- Rough MDP reaches 70.31% on hard despite never training on parkour terrain — it sits between rough baseline (29.69%) and medium baseline (87.50%).
- Hard MDP matches hard baseline on rough/easy/medium but drops 3.12pp on hard-to-hard (92.19% vs 95.31%). Both are near ceiling.

## Fixed-row stress timeout

| Checkpoint source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| rough | 98.44% | 78.12% | 56.25% | 31.25% |
| easy | 95.31% | 98.44% | 64.06% | 0.00% |
| medium | 95.31% | 100.00% | 100.00% | 92.19% |
| hard | 100.00% | 100.00% | 96.88% | 95.31% |
| rough_mdp | 98.44% | 100.00% | 92.19% | 70.31% |
| hard_mdp | 100.00% | 100.00% | 98.44% | 96.88% |

Key observations:

- The stress setting preserves the main ordering from random cross evaluation: rough/easy are weak on hard, while medium/hard remain strong.
- Easy-to-hard remains 0.00%, confirming that easy terrain without gap exposure is not sufficient for hard obstacle robustness.
- Hard remains robust under fixed high-row evaluation, with 95.31% hard-to-hard timeout rate.
- Rough MDP shows the largest stress-mode gains over its baseline: rough_mdp-to-medium reaches 92.19% vs rough-to-medium 56.25% (+35.94pp), and rough_mdp-to-easy reaches 100.00% vs rough-to-easy 78.12% (+21.88pp).
- Hard MDP improves on hard baseline in stress: hard_mdp-to-medium 98.44% (+1.56pp), hard_mdp-to-hard 96.88% (+1.57pp).

## Random cross-terrain traversal progress

| Checkpoint source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| rough | 95.31% | 98.44% | 68.75% | 29.69% |
| easy | 89.06% | 100.00% | 50.00% | 0.00% |
| medium | 98.44% | 98.44% | 95.31% | 87.50% |
| hard | 100.00% | 100.00% | 96.88% | 95.31% |
| rough_mdp | 100.00% | 100.00% | 76.56% | 70.31% |
| hard_mdp | 100.00% | 100.00% | 96.88% | 92.19% |

Key observations:

- Traversal progress almost exactly matches timeout in the random setting.
- The only nonzero timeout-progress difference among the 24 source/eval pairs is easy-to-rough, where timeout is 1.56 percentage points higher than progress pass.
- MDP rows show zero delta between timeout and progress — every episode that survives also clears the 4 m forward-distance threshold.
- This confirms that most successful timeout episodes also satisfy the 4 m forward-distance threshold across all 6 checkpoint sources.

## Fixed-row stress traversal progress

| Checkpoint source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| rough | 98.44% | 78.12% | 56.25% | 31.25% |
| easy | 93.75% | 98.44% | 64.06% | 0.00% |
| medium | 95.31% | 100.00% | 100.00% | 92.19% |
| hard | 100.00% | 100.00% | 96.88% | 95.31% |
| rough_mdp | 98.44% | 100.00% | 92.19% | 70.31% |
| hard_mdp | 100.00% | 100.00% | 98.44% | 96.88% |

Key observations:

- Stress progress again mirrors stress timeout. The only nonzero delta is easy-to-rough (−1.56pp, from 95.31% timeout to 93.75% progress).
- The progress metric supports the same generalization conclusion as timeout: medium is the minimum tier that adapts well to hard, while hard is the best generalist source among current specialists.
- Rough MDP stress progress on medium (92.19%) and hard (70.31%) substantially exceeds rough baseline (56.25% and 31.25%).
- Traversal progress should be reported as a forward-distance proxy, not as explicit terrain-aware obstacle-boundary passing.

## Fixed-row stress obstacle crossing

Obstacle crossing is evaluated only on supported gap/stairs terrain groups. Unsupported terrain groups such as boxes, rough, and slope are recorded in coverage metadata but excluded from `obstacle_pass_rate`.

| Checkpoint source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| rough | 88.46% | 88.46% | 16.39% | 25.00% |
| easy | 92.31% | 96.15% | 0.00% | 0.00% |
| medium | 100.00% | 100.00% | 96.88% | 65.79% |
| hard | 100.00% | 100.00% | 87.50% | 100.00% |
| rough_mdp | 100.00% | 100.00% | 77.78% | 41.03% |
| hard_mdp | 100.00% | 100.00% | 100.00% | 100.00% |

Gap pass rate:

| Checkpoint source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| rough | N/A | N/A | 0.00% | 7.89% |
| easy | N/A | N/A | 0.00% | 0.00% |
| medium | N/A | N/A | 91.67% | 33.33% |
| hard | N/A | N/A | 66.67% | 100.00% |
| rough_mdp | N/A | N/A | 50.00% | 21.43% |
| hard_mdp | N/A | N/A | 100.00% | 100.00% |

Stairs pass rate:

| Checkpoint source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| rough | 88.46% | 88.46% | 100.00% | 90.00% |
| easy | 92.31% | 96.15% | N/A | 0.00% |
| medium | 100.00% | 100.00% | 100.00% | 95.00% |
| hard | 100.00% | 100.00% | 100.00% | 100.00% |
| rough_mdp | 100.00% | 100.00% | 100.00% | 90.91% |
| hard_mdp | 100.00% | 100.00% | 100.00% | 100.00% |

Fall before obstacle rate:

| Checkpoint source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| rough | 0.00% | 0.00% | 70.49% | 64.58% |
| easy | 0.00% | 0.00% | 95.16% | 89.66% |
| medium | 0.00% | 0.00% | 3.12% | 31.58% |
| hard | 0.00% | 0.00% | 9.38% | 0.00% |
| rough_mdp | 0.00% | 0.00% | 19.44% | 51.28% |
| hard_mdp | 0.00% | 0.00% | 0.00% | 0.00% |

Key observations:

- Hard-to-hard reaches 100.00% obstacle, gap, and stairs pass rates, so the hard checkpoint solves the supported hard gap/stairs boundaries in the official stress protocol.
- Hard MDP also reaches 100.00% obstacle, gap, and stairs pass rates on all eval envs with obstacle coverage. It additionally achieves 100.00% on medium gaps (vs hard baseline 66.67%) and has 0.00% fall-before-obstacle rate everywhere.
- Medium-to-hard reaches 65.79% obstacle pass. Its stairs pass remains high at 95.00%, but hard gap pass falls to 33.33%, identifying hard gap crossing as the main terrain-specific gap between medium and hard policies.
- Easy-to-hard remains 0.00% in both obstacle and gap pass, which is consistent with easy training having no gap terrain.
- Rough MDP shows meaningful obstacle competence gains over rough baseline: rough_mdp-to-medium obstacle pass 77.78% vs rough-to-medium 16.39% (+61.39pp), driven by gap pass improving from 0.00% to 50.00%. Rough MDP fall-before-obstacle on medium drops from 70.49% to 19.44%, indicating that the MDP rewards help the robot reach obstacles rather than falling before them.
- Rough MDP-to-hard obstacle pass (41.03%) sits between rough baseline (25.00%) and medium baseline (65.79%), consistent with the timeout/progress pattern.

## Summary conclusion

The terrain difficulty ablation has clear reporting value. Easy training is stable but does not cover hard obstacles. Medium training, which introduces gaps and stronger terrain, substantially improves survival and forward-progress transfer, but the obstacle crossing metric shows that medium still struggles on hard gaps. Hard training is the strongest source policy across random timeout, fixed-row stress, and supported obstacle crossing, making the hard checkpoint the best current starting point for future mixed-terrain or generalist training.

The MDP ablation demonstrates that lightweight reward shaping (`parkour_progress` + `foothold_safety`) produces large, consistent gains on the weaker rough baseline: hard-terrain timeout improves from 29.69% to 70.31%, gap pass on medium goes from 0.00% to 50.00%, and forward distance on hard stress more than doubles. On the already-strong hard baseline, gains are more subtle — velocity tracking error drops by up to 48% and medium obstacle crossing reaches 100%, but forward distance decreases, reflecting a safety-vs-speed tradeoff from `foothold_safety`. The rough_mdp policy approaches medium baseline competence without any parkour terrain exposure, confirming that the reward terms extract transferable locomotion skills.

Timeout and traversal-progress results are nearly identical across all 24 source/eval pairs (max delta 1.56pp), so the explicit obstacle crossing metric is the more informative result for gap/stairs completion claims.
