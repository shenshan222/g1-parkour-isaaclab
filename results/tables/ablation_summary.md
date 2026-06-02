# Ablation summary

Current table combines training-summary metrics with fixed-checkpoint rollout timeout metrics from `results/metrics/parkour_timeout_eval.csv`. Cross-terrain, fixed-row stress, traversal-progress, and obstacle-crossing evidence are summarized below to make the terrain-difficulty ablation reportable as both a training comparison and a generalization comparison.

| Comparison | Run | Mean reward | Fall rate | XY tracking error | Mean episode length | Curriculum level | Notes |
|------------|-----|-------------|-----------|-------------------|---------------------|------------------|-------|
| Baseline terrain | Flat baseline | 28.77 | 0.44% | 0.2087 m/s | 1000.0 | N/A | Official flat G1 velocity task; easiest reference setting |
| Baseline terrain | Rough baseline | 24.01 | 5.41% | 0.3407 m/s | 984.5 | 5.7961 | Official rough G1 velocity task; parent configuration for parkour |
| Parkour difficulty | Easy | 30.70 | 4.00% train / 0.00% eval | 0.3050 train | 983.2 train / 2000.0 eval | 5.7907 | 100.00% rollout timeout; no gap terrain |
| Parkour difficulty | Medium | 20.98 | 6.75% train / 4.69% eval | 0.3590 train | 988.1 train / 1946.0 eval | 5.8001 | 95.31% rollout timeout; adds gaps and higher obstacles |
| Parkour difficulty | Hard | 11.34 | 10.92% train / 12.50% eval | 0.4407 train | 941.7 train / 1810.0 eval | 5.6389 | 87.50% rollout timeout; widest gaps and hardest platforms |

## Interpretation

- Flat to rough validates the environment-complexity effect: rough terrain increases falls and velocity-tracking error.
- Easy to medium to hard acts as a terrain-difficulty ablation over the custom parkour generator.
- Rough, easy, and medium all finish near curriculum level 5.8; hard is lower at 5.6389 under the same 3000-iteration budget.
- The hard tier is the clearest training stress test under a fair 3000-iteration budget: it has the lowest reward, highest fall rate, and weakest rollout timeout among the parkour tiers.

## Cross/stress evidence

| Comparison | Random timeout | Stress timeout | Random progress | Stress progress | Interpretation |
|------------|---------------:|---------------:|----------------:|----------------:|----------------|
| rough -> hard | 29.69% | 31.25% | 29.69% | 31.25% | Rough locomotion does not transfer reliably to hard parkour obstacles |
| easy -> hard | 0.00% | 0.00% | 0.00% | 0.00% | Easy terrain without gaps is insufficient for hard obstacle robustness |
| medium -> hard | 87.50% | 92.19% | 87.50% | 92.19% | Medium is the minimum completed tier that transfers strongly by survival/progress metrics |
| hard -> hard | 95.31% | 95.31% | 95.31% | 95.31% | Hard remains robust under both average and high-row evaluation |
| hard -> rough/easy/medium | >= 96.88% | >= 96.88% | >= 96.88% | >= 96.88% | Hard training transfers downward to easier or parent terrains |

## Obstacle crossing stress evidence

| Comparison | Obstacle pass | Gap pass | Stairs pass | Fall before obstacle | Interpretation |
|------------|--------------:|---------:|------------:|---------------------:|----------------|
| rough -> hard | 25.00% | 7.89% | 90.00% | 64.58% | Rough can sometimes handle stairs but fails hard gaps early |
| easy -> hard | 0.00% | 0.00% | 0.00% | 89.66% | Easy has no usable hard obstacle transfer |
| medium -> hard | 65.79% | 33.33% | 95.00% | 31.58% | Medium transfers to hard stairs but not reliably to hard gaps |
| hard -> hard | 100.00% | 100.00% | 100.00% | 0.00% | Hard solves supported hard gap/stairs boundaries in the official stress protocol |
| hard -> medium | 87.50% | 66.67% | 100.00% | 9.38% | Hard transfers back to medium but remains less perfect on medium gaps than on hard gaps under sampled coverage |

## Reporting conclusion

The completed formal ablation is the terrain-difficulty ablation. It shows a monotonic increase in training difficulty from easy to medium to hard. Cross-terrain evaluation adds stronger evidence that obstacle exposure matters: easy is stable but narrow, medium is the first tier with strong survival/progress transfer to hard, and hard is the best current source checkpoint for a generalist policy.

Timeout and traversal-progress results are almost identical. The largest timeout-progress gap is 1.56 percentage points, so traversal progress should be reported as a forward-distance sanity check. The obstacle crossing stress metric adds the missing terrain-aware interpretation: medium-to-hard is mostly a hard-gap failure, while hard-to-hard reaches 100.00% on supported hard gap/stairs boundaries.

## Pending ablations

- Reward/observation ablations have not been run yet.
- Fixed-checkpoint rollout evaluation has been run for easy/medium/hard with 64 episodes each.
- `results/metrics/parkour_timeout_eval.csv` contains the current formal timeout evaluation table.
- `results/metrics/obstacle_crossing_cross_terrain_stress_eval.csv` contains the formal obstacle crossing stress table.
