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


## Traversal Progress Evaluation

Traversal progress evaluation uses the same unified cross/stress scripts as timeout evaluation, with `--metric progress`. It does not keep a separate diagonal result table.

Random 4x4 traversal progress cross-terrain evaluation uses `eval_cross_terrain.sh --metric progress` and runs rough/easy/medium/hard checkpoints against rough/easy/medium/hard play environments.

```bash
NUM_EPISODES=64 NUM_ENVS=32 SEED=42 bash scripts/eval_cross_terrain.sh --metric progress all
python scripts/summarize_traversal_progress_eval.py \
  --input_csv results/metrics/traversal_progress_cross_terrain_eval.csv \
  --output_dir results/tables \
  --output_prefix traversal_progress_cross_terrain
```

Fixed-row traversal progress stress evaluation uses `eval_cross_terrain_stress.sh --metric progress`. The default stress setting fixes `STRESS_ROW=9` and leaves terrain columns unfixed.

```bash
NUM_EPISODES=64 NUM_ENVS=32 SEED=42 bash scripts/eval_cross_terrain_stress.sh --metric progress all
python scripts/summarize_traversal_progress_eval.py \
  --input_csv results/metrics/traversal_progress_cross_terrain_stress_eval.csv \
  --output_dir results/tables \
  --output_prefix traversal_progress_cross_terrain_stress
```

Output files:

- `results/metrics/traversal_progress_cross_terrain_eval.csv`
- `results/metrics/traversal_progress_cross_terrain_stress_eval.csv`
- `results/tables/traversal_progress_cross_terrain_summary.md`
- `results/tables/traversal_progress_cross_terrain_stress_summary.md`

Progress pass is defined as no fall and `max_forward_distance_m >= 4.0`. Strong progress pass is defined as no fall and `max_forward_distance_m >= 6.0`. These metrics estimate obstacle traversal progress and complement timeout-based survival metrics; they should not replace the existing timeout tables.

## Obstacle Crossing Evaluation

Obstacle crossing evaluation uses the unified cross/stress scripts with `--metric obstacle`. This metric reports base-level geometry-boundary crossing success for gap and stairs terrain. It does not use the traversal-progress threshold as the official obstacle success definition.

Random 4x4 obstacle crossing evaluation is supported, but the recommended official protocol is fixed-row stress evaluation because obstacle terrain columns are deterministic and easier to interpret.

```bash
NUM_EPISODES=64 NUM_ENVS=32 SEED=42 bash scripts/eval_cross_terrain_stress.sh --metric obstacle all
python scripts/summarize_obstacle_crossing_eval.py   --input_csv results/metrics/obstacle_crossing_cross_terrain_stress_eval.csv   --output_dir results/tables   --output_prefix obstacle_crossing_cross_terrain_stress
```

Expected output files after running the official stress command:

- `results/metrics/obstacle_crossing_cross_terrain_stress_eval.csv`
- `results/tables/obstacle_crossing_cross_terrain_stress_summary.md`

Obstacle pass is defined as no `base_contact` failure and successful base-level crossing of a supported obstacle boundary. For gap terrain, the boundary is the far side of the gap plus a small margin. For stairs terrain, the boundary is the forward outer stair-field boundary. Unsupported terrain groups such as boxes, rough, and slope are recorded in coverage metadata but are not included in `obstacle_pass_rate`.

The generated obstacle CSV contains `obstacle_pass_rate`, `gap_pass_rate`, `stairs_pass_rate`, `fall_before_obstacle_rate`, `boundary_coverage`, and `mean_boundary_x_m`.

## Analysis tables

Result-analysis tables used by the report are stored in:

- `results/tables/generalization_analysis.md`
- `results/tables/timeout_vs_progress_delta.md`
- `results/tables/ablation_summary.md`

`generalization_analysis.md` combines timeout and traversal-progress random/stress matrices into report-oriented observations. `timeout_vs_progress_delta.md` reports `timeout_rate - progress_pass_rate`; the current maximum delta is 1.56 percentage points, so traversal progress should be interpreted as a forward-distance sanity check rather than an explicit obstacle-boundary pass metric.

## Result interpretation

The current timeout definition is `timeout_without_base_contact`. It measures locomotion survival over the sampled terrain distribution, not terrain-aware obstacle-by-obstacle completion.

Traversal progress measures forward-distance success without separating obstacle types. Obstacle crossing measures base-level geometry-boundary success for gap/stairs terrain. It still does not verify foot-contact-level obstacle completion.

Random cross-terrain evaluation measures average generalization across terrain samples. Fixed-row stress evaluation measures high-row robustness inside each terrain preset.

## Report figures

Learning-curve figures used by the report are stored in `results/figures/`. Compact CSV summaries are stored in `results/metrics/`; raw TensorBoard event files remain outside Git.
