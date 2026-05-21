# Flat baseline experiment

## Task

- Gym ID: `Isaac-Velocity-Flat-G1-v0` (official Isaac Lab)
- Robot: Unitree G1, flat terrain, velocity command tracking
- Purpose: verify training pipeline; lower-bound baseline before rough / parkour

## Command

```bash
cd ~/g1-parkour-isaaclab
bash scripts/train_flat_baseline.sh
```

Environment (this run):

- `ISAACLAB_ROOT=/root/autodl-tmp/isaac_workspace/IsaacLab`
- `HUMANOID_PARKOUR_RUNS_ROOT=/root/autodl-tmp/humanoid_parkour_runs`
- Conda env: `/root/autodl-tmp/isaac_workspace/env_isaaclab` (path-based)

## Hyperparameters


| Field             | Value                                                  |
| ----------------- | ------------------------------------------------------ |
| algorithm         | PPO (`OnPolicyRunner`, Isaac Lab `G1FlatPPORunnerCfg`) |
| num_envs          | 4096                                                   |
| num_steps_per_env | 24                                                     |
| max_iterations    | 1500                                                   |
| save_interval     | 50                                                     |
| seed              | 42                                                     |
| learning_rate     | 0.001 (adaptive schedule)                              |
| episode_length_s  | 20.0                                                   |
| experiment_name   | `g1_flat`                                              |
| policy MLP        | [256, 128, 128] (actor & critic)                       |
| headless          | yes                                                    |
| wall_time         | ~40 min (RTX 3090, AutoDL)                             |


## Run identity


| Field              | Value                                                                                          |
| ------------------ | ---------------------------------------------------------------------------------------------- |
| run_id             | `2026-05-21_20-36-57`                                                                          |
| date               | 2026-05-21                                                                                     |
| log_root           | `$HUMANOID_PARKOUR_RUNS_ROOT/flat_baseline`                                                    |
| log_dir (absolute) | `/root/autodl-tmp/humanoid_parkour_runs/flat_baseline/logs/rsl_rl/g1_flat/2026-05-21_20-36-57` |
| tensorboard        | `tensorboard --logdir=/root/autodl-tmp/humanoid_parkour_runs/flat_baseline`                    |


Artifacts are on the data disk only (not committed to Git).

## Results (iteration 1499)


| Metric                            | Value                      |
| --------------------------------- | -------------------------- |
| mean_reward                       | 28.77                      |
| mean_episode_length               | 1000.0 (max steps reached) |
| Episode_Termination/time_out      | 99.56%                     |
| Episode_Termination/base_contact  | 0.44%                      |
| track_lin_vel_xy_exp              | 0.9425                     |
| track_ang_vel_z_exp               | 0.7790                     |
| error_vel_xy                      | 0.2087 m/s                 |
| error_vel_yaw                     | 0.4566 rad/s               |
| termination_penalty (reward term) | 0.0                        |
| value_loss                        | 0.0014                     |


Summary CSV row: `results/metrics/flat_baseline.csv`

## Figures

| File | Metric |
|------|--------|
| `results/figures/flat_mean_reward.png` | `Train/mean_reward` |
| `results/figures/flat_episode_length.png` | `Train/mean_episode_length` |


## Checkpoint


| Field           | Value                                                                                                        |
| --------------- | ------------------------------------------------------------------------------------------------------------ |
| final           | `model_1499.pt`                                                                                              |
| path (absolute) | `/root/autodl-tmp/humanoid_parkour_runs/flat_baseline/logs/rsl_rl/g1_flat/2026-05-21_20-36-57/model_1499.pt` |


## Observations

### Reward curve

- iter 0: mean_reward ≈ -0.60; episode length ≈ 13 (policy still exploring).
- iter 100: brief dip (mean_reward ≈ -6.5, high fall rate) — normal early-training instability.
- iter 500+: reward rises and plateaus around **28–29**; last 100 iters std ≈ 0.17 → **converged**.

### Behavior

- ~99.5% episodes end by **timeout**, not fall → stable upright locomotion on flat ground.
- Velocity-tracking reward terms dominate the final return (`track_lin_vel_xy_exp` ≈ 0.94).
- Training completed **1500/1500** iterations with no early stop; pipeline (Isaac Sim + Isaac Lab + scripts) is healthy.
