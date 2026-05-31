# Evaluation

## Play / record video

Use the play wrapper for quick visualization, or pass an explicit checkpoint for a specific case.

```bash
bash scripts/play_parkour.sh easy -- --video --video_length=800 --headless
CHECKPOINT_HARD=/path/to/model_2999.pt bash scripts/play_parkour.sh hard -- --video --video_length=800 --headless
```

Selected submission videos are stored in `report/assets/` and are force-added to Git despite the general `*.mp4` ignore rule. Raw run videos remain under `$HUMANOID_PARKOUR_RUNS_ROOT` and should stay out of Git.

## Diagonal fixed-checkpoint rollout metrics

```bash
NUM_EPISODES=64 NUM_ENVS=32 bash scripts/eval_parkour.sh all
```

Output: `results/metrics/parkour_eval.csv`.

The evaluator loads fixed checkpoints, runs policy inference in the corresponding play environments, and defines success as timeout without `base_contact` termination. It reports success rate, fall rate, timeout rate, episode length, direct velocity-tracking error, and terrain-level pass rates.

## Random 4x4 cross-terrain evaluation

```bash
NUM_EPISODES=64 NUM_ENVS=32 SEED=42 bash scripts/eval_cross_terrain.sh all
python scripts/summarize_cross_terrain_eval.py \
  --input_csv results/metrics/cross_terrain_eval.csv \
  --output_dir results/tables \
  --output_prefix cross_terrain
```

Output files:

- `results/metrics/cross_terrain_eval.csv`
- `results/tables/cross_terrain_success_rate.md`
- `results/tables/cross_terrain_fall_rate.md`
- `results/tables/cross_terrain_tracking_error.md`

This evaluation runs rough/easy/medium/hard checkpoints against rough/easy/medium/hard play environments. It uses a 10x10 terrain grid, fixed seed, disabled curriculum, and random terrain type/difficulty sampling within each eval task.

## Fixed-row 4x4 stress evaluation

```bash
NUM_EPISODES=64 NUM_ENVS=32 SEED=42 bash scripts/eval_cross_terrain_stress.sh all
python scripts/summarize_cross_terrain_eval.py \
  --input_csv results/metrics/cross_terrain_stress_eval.csv \
  --output_dir results/tables \
  --output_prefix cross_terrain_stress
```

Output files:

- `results/metrics/cross_terrain_stress_eval.csv`
- `results/tables/cross_terrain_stress_success_rate.md`
- `results/tables/cross_terrain_stress_fall_rate.md`
- `results/tables/cross_terrain_stress_tracking_error.md`

The default stress setting fixes `terrain_fixed_row=9` and leaves terrain columns unfixed, so the rollout covers all terrain types at the highest difficulty index within each preset. Row 9 is relative to each preset and should not be interpreted as the same absolute physical difficulty across rough/easy/medium/hard.

## Result interpretation

The current success definition is `timeout_without_base_contact`. It measures locomotion survival over the sampled terrain distribution, not semantic obstacle-by-obstacle completion.

Random cross-terrain evaluation measures average generalization across terrain samples. Fixed-row stress evaluation measures high-row robustness inside each terrain preset.

## Report figures

Learning-curve figures used by the report are stored in `results/figures/`. Compact CSV summaries are stored in `results/metrics/`; raw TensorBoard event files remain outside Git.
