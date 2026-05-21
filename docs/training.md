# Training

## Baselines (official Isaac Lab tasks)

```bash
bash scripts/train_flat_baseline.sh
bash scripts/train_rough_baseline.sh
```

Logs go to `$HUMANOID_PARKOUR_RUNS_ROOT/flat_baseline/logs/rsl_rl/` (and `.../rough_baseline/logs/rsl_rl/`). Isaac Lab has no `--log_root`; scripts `cd` into the run folder so checkpoints stay on the data disk.

## Parkour task

1. Implement `parkour_env_cfg.py` (inherit `G1RoughEnvCfg`) and `parkour_terrain_cfg.py`.
2. Train:

```bash
bash scripts/train_parkour.sh
```

3. Monitor:

```bash
bash scripts/launch_tensorboard.sh
# LOGDIR defaults to HUMANOID_PARKOUR_RUNS_ROOT
```

## Experiment log

Record each run in `configs/experiments/*.md` (task, command, hyperparameters, checkpoint path, trends).
