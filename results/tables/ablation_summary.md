# Ablation summary

Current table combines training-summary metrics with fixed-checkpoint rollout success metrics from `results/metrics/parkour_eval.csv`.

| Comparison | Run | Mean reward | Fall rate | XY tracking error | Mean episode length | Notes |
|------------|-----|-------------|-----------|-------------------|---------------------|-------|
| Baseline terrain | Flat baseline | 28.77 | 0.44% | 0.2087 m/s | 1000.0 | Official flat G1 velocity task; easiest reference setting |
| Baseline terrain | Rough baseline | 24.01 | 5.41% | 0.3407 m/s | 984.5 | Official rough G1 velocity task; parent configuration for parkour |
| Parkour difficulty | Easy | 30.70 | 4.00% train / 0.00% eval | 0.3050 train | 983.2 train / 2000.0 eval | 100.00% rollout success; no gap terrain |
| Parkour difficulty | Medium | 20.98 | 6.75% train / 4.69% eval | 0.3590 train | 988.1 train / 1946.0 eval | 95.31% rollout success; adds gaps and higher obstacles |
| Parkour difficulty | Hard | 11.34 | 10.92% train / 12.50% eval | 0.4407 train | 941.7 train / 1810.0 eval | 87.50% rollout success; widest gaps and hardest platforms |

## Interpretation

- Flat to rough validates the environment-complexity effect: rough terrain increases falls and velocity-tracking error.
- Easy to medium to hard acts as a terrain-difficulty ablation over the custom parkour generator.
- The hard tier is the clearest stress test under a fair 3000-iteration budget: it has the lowest reward, highest fall rate, and weakest rollout success among the parkour tiers.

## Pending formal ablations

- Reward/observation ablations have not been run yet.
- Fixed-checkpoint rollout evaluation has been run for easy/medium/hard with 64 episodes each.
- `results/metrics/parkour_eval.csv` contains the current formal evaluation table.
