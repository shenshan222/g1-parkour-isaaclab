# Ablation summary

Current table combines training-summary metrics with fixed-checkpoint rollout timeout metrics from `results/metrics/parkour_timeout_eval.csv`.

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
- The hard tier is the clearest stress test under a fair 3000-iteration budget: it has the lowest reward, highest fall rate, and weakest rollout timeout among the parkour tiers.

## Pending formal ablations

- Reward/observation ablations have not been run yet.
- Fixed-checkpoint rollout evaluation has been run for easy/medium/hard with 64 episodes each.
- `results/metrics/parkour_timeout_eval.csv` contains the current formal timeout evaluation table.
