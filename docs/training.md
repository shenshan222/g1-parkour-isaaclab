# Training

## Baselines (official Isaac Lab tasks)

```bash
bash scripts/train_flat_baseline.sh
bash scripts/train_rough_baseline.sh
```

Logs go to `$HUMANOID_PARKOUR_RUNS_ROOT/flat_baseline/logs/rsl_rl/` and `$HUMANOID_PARKOUR_RUNS_ROOT/rough_baseline/logs/rsl_rl/`. Isaac Lab has no `--log_root`; scripts `cd` into the run folder so checkpoints stay on the data disk.

Official baseline checkpoints:

| Run | Iterations | Checkpoint |
|-----|-----------:|------------|
| Flat baseline | 1500 | `model_1499.pt` |
| Rough baseline | 3000 | `model_2999.pt` |

## Parkour tasks

1. Implement or inspect `parkour_env_cfg.py` and `parkour_terrain_cfg.py`. All parkour tiers inherit `G1RoughEnvCfg` and replace the terrain generator.
2. Train:

```bash
bash scripts/train_parkour.sh          # all tiers (easy -> medium -> hard)
bash scripts/train_parkour.sh easy     # single tier
bash scripts/train_parkour.sh medium hard
```

3. Play:

```bash
bash scripts/play_parkour.sh
bash scripts/play_parkour.sh easy
```

4. Monitor:

```bash
bash scripts/launch_tensorboard.sh
# LOGDIR defaults to HUMANOID_PARKOUR_RUNS_ROOT
```

Official parkour comparison checkpoints:

| Tier | Run ID | Iterations | Checkpoint |
|------|--------|-----------:|------------|
| Easy | `2026-05-26_15-58-21` | 3000 | `model_2999.pt` |
| Medium | `2026-05-26_17-39-43` | 3000 | `model_2999.pt` |
| Hard | `2026-05-26_20-22-02` | 3000 | `model_2999.pt` |

The hard tier is intentionally compared at the same 3000-iteration budget as easy and medium. Compact training summaries are stored in `results/metrics/parkour_training_summary.csv`.

## Experiment log

Record each run in `configs/experiments/*.md` with task ID, command, hyperparameters, checkpoint path, metric trends, and interpretation. Keep raw checkpoints, TensorBoard events, and full logs outside Git.
