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
NUM_EPISODES=64 NUM_ENVS=32 bash scripts/eval_timeout_parkour.sh all
```

Output: `results/metrics/parkour_timeout_eval.csv`.

The evaluator loads fixed checkpoints, runs policy inference in the corresponding play environments, and defines success as timeout without `base_contact` termination. It reports timeout rate, fall rate, episode length, and direct velocity-tracking error.

## Random 4x4 cross-terrain evaluation

```bash
NUM_EPISODES=64 NUM_ENVS=32 SEED=42 bash scripts/eval_cross_terrain.sh --metric timeout all
python scripts/summarize_timeout_cross_terrain_eval.py \
  --input_csv results/metrics/timeout_cross_terrain_eval.csv \
  --output_dir results/tables \
  --output_prefix timeout_cross_terrain
```

Output files:

- `results/metrics/timeout_cross_terrain_eval.csv`
- `results/tables/timeout_cross_terrain_summary.md`

This evaluation runs rough/easy/medium/hard checkpoints against rough/easy/medium/hard play environments. It uses a 10x10 terrain grid, fixed seed, disabled curriculum, and random terrain type/difficulty sampling within each eval task.

## Fixed-row 4x4 stress evaluation

```bash
NUM_EPISODES=64 NUM_ENVS=32 SEED=42 bash scripts/eval_cross_terrain_stress.sh --metric timeout all
python scripts/summarize_timeout_cross_terrain_eval.py \
  --input_csv results/metrics/timeout_cross_terrain_stress_eval.csv \
  --output_dir results/tables \
  --output_prefix timeout_cross_terrain_stress
```

Output files:

- `results/metrics/timeout_cross_terrain_stress_eval.csv`
- `results/tables/timeout_cross_terrain_stress_summary.md`

The default stress setting fixes `terrain_fixed_row=9` and leaves terrain columns unfixed, so the rollout covers all terrain types at the highest difficulty index within each preset. Row 9 is relative to each preset and should not be interpreted as the same absolute physical difficulty across rough/easy/medium/hard.


## Semantic obstacle traversal evaluation

Semantic obstacle evaluation uses the same unified cross/stress scripts as timeout evaluation, with `--metric semantic`. It does not keep a separate diagonal result table.

Random 4x4 semantic cross-terrain evaluation uses `eval_cross_terrain.sh --metric semantic` and runs rough/easy/medium/hard checkpoints against rough/easy/medium/hard play environments.

```bash
NUM_EPISODES=64 NUM_ENVS=32 SEED=42 bash scripts/eval_cross_terrain.sh --metric semantic all
python scripts/summarize_semantic_obstacle_eval.py \
  --input_csv results/metrics/semantic_obstacle_cross_terrain_eval.csv \
  --output_dir results/tables \
  --output_prefix semantic_obstacle_cross_terrain
```

Fixed-row semantic stress evaluation uses `eval_cross_terrain_stress.sh --metric semantic`. The default stress setting fixes `STRESS_ROW=9` and leaves terrain columns unfixed.

```bash
NUM_EPISODES=64 NUM_ENVS=32 SEED=42 bash scripts/eval_cross_terrain_stress.sh --metric semantic all
python scripts/summarize_semantic_obstacle_eval.py \
  --input_csv results/metrics/semantic_obstacle_cross_terrain_stress_eval.csv \
  --output_dir results/tables \
  --output_prefix semantic_obstacle_cross_terrain_stress
```

Output files:

- `results/metrics/semantic_obstacle_cross_terrain_eval.csv`
- `results/metrics/semantic_obstacle_cross_terrain_stress_eval.csv`
- `results/tables/semantic_obstacle_cross_terrain_summary.md`
- `results/tables/semantic_obstacle_cross_terrain_stress_summary.md`

Semantic pass is defined as no fall and `max_forward_distance_m >= 4.0`. Strong pass is defined as no fall and `max_forward_distance_m >= 6.0`. These metrics estimate obstacle traversal progress and complement timeout-based survival metrics; they should not replace the existing timeout tables.

## Result interpretation

The current timeout definition is `timeout_without_base_contact`. It measures locomotion survival over the sampled terrain distribution, not semantic obstacle-by-obstacle completion.

Random cross-terrain evaluation measures average generalization across terrain samples. Fixed-row stress evaluation measures high-row robustness inside each terrain preset.

## Report figures

Learning-curve figures used by the report are stored in `results/figures/`. Compact CSV summaries are stored in `results/metrics/`; raw TensorBoard event files remain outside Git.
