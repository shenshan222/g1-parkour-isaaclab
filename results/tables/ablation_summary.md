# Ablation summary

Current table uses training-summary metrics from TensorBoard logs, not a separate fixed-seed rollout evaluator. Formal success-rate evaluation is still pending because `scripts/eval_parkour.sh` is a stub.

| Comparison | Run | Mean reward | Fall rate | XY tracking error | Mean episode length | Notes |
|------------|-----|-------------|-----------|-------------------|---------------------|-------|
| Baseline terrain | Flat baseline | 28.77 | 0.44% | 0.2087 m/s | 1000.0 | Official flat G1 velocity task; easiest reference setting |
| Baseline terrain | Rough baseline | 24.01 | 5.41% | 0.3407 m/s | 984.5 | Official rough G1 velocity task; parent configuration for parkour |
| Parkour difficulty | Easy | 30.70 | 4.00% | 0.3050 m/s | 983.2 | Custom stairs/boxes/rough/slopes; no gap terrain |
| Parkour difficulty | Medium | 20.98 | 6.75% | 0.3590 m/s | 988.1 | Adds gaps and increases obstacle height |
| Parkour difficulty | Hard | 14.44 | 7.27% | 0.4689 m/s | 977.2 | Wider gaps, higher obstacles, narrower platforms; trained to 4498 |

## Interpretation

- Flat to rough validates the environment-complexity effect: rough terrain increases falls and velocity-tracking error.
- Easy to medium to hard acts as a terrain-difficulty ablation over the custom parkour generator.
- The hard tier is the clearest stress test: it maintains high timeout rate after resumed training, but reward and tracking quality remain substantially worse than easy/medium.

## Pending formal ablations

- Reward/observation ablations have not been run yet.
- Fixed-checkpoint rollout evaluation has not been run yet.
- `results/metrics/parkour_eval.csv` should remain the target output for formal success-rate evaluation.
