# Evaluation

## Play / record video

Use the play wrapper for quick visualization, or pass an explicit checkpoint for a specific case.

```bash
bash scripts/play_parkour.sh easy -- --video --video_length=800 --headless
CHECKPOINT_HARD=/path/to/model_2999.pt bash scripts/play_parkour.sh hard -- --video --video_length=800 --headless
```

Selected submission videos are stored in `report/assets/` and are force-added to Git despite the general `*.mp4` ignore rule. Raw run videos remain under `$HUMANOID_PARKOUR_RUNS_ROOT` and should stay out of Git.

## Fixed-checkpoint rollout metrics

```bash
NUM_EPISODES=64 NUM_ENVS=32 bash scripts/eval_parkour.sh all
```

Output: `results/metrics/parkour_eval.csv`.

The evaluator loads fixed checkpoints, runs policy inference in the play environments, and defines success as timeout without `base_contact` termination. It reports success rate, fall rate, timeout rate, episode length, direct velocity-tracking error, and terrain-level pass rates.

## Report figures

Learning-curve figures used by the report are stored in `results/figures/`. Compact CSV summaries are stored in `results/metrics/`; raw TensorBoard event files remain outside Git.
