# Rough baseline experiment

## Task

- Gym ID: `Isaac-Velocity-Rough-G1-v0` (official Isaac Lab)
- Robot: Unitree G1, procedural rough terrain + height scanner + terrain curriculum
- Purpose: harder locomotion baseline before parkour; inherits velocity tracking on uneven ground

## Command

```bash
cd ~/g1-parkour-isaaclab
bash scripts/train_rough_baseline.sh
```

Environment (this run):

- `ISAACLAB_ROOT=/root/autodl-tmp/isaac_workspace/IsaacLab`
- `HUMANOID_PARKOUR_RUNS_ROOT=/root/autodl-tmp/humanoid_parkour_runs`
- Conda env: `/root/autodl-tmp/isaac_workspace/env_isaaclab` (path-based)

## Hyperparameters


| Field             | Value                                                   |
| ----------------- | ------------------------------------------------------- |
| algorithm         | PPO (`OnPolicyRunner`, Isaac Lab `G1RoughPPORunnerCfg`) |
| num_envs          | 4096                                                    |
| num_steps_per_env | 24                                                      |
| max_iterations    | 3000                                                    |
| save_interval     | 50                                                      |
| seed              | 42                                                      |
| learning_rate     | 0.001 (adaptive schedule)                               |
| episode_length_s  | 20.0                                                    |
| experiment_name   | `g1_rough`                                              |
| policy MLP        | [512, 256, 128]                                         |
| headless          | yes                                                     |
| wall_time         | ~101 min (RTX 3090, AutoDL)                             |


Terrain / sensing (from cfg): `ROUGH_TERRAINS_CFG`, `height_scanner` on `torso_link`, `terrain_levels_vel` curriculum.

## Run identity


| Field              | Value                                                                                            |
| ------------------ | ------------------------------------------------------------------------------------------------ |
| run_id             | `2026-05-21_21-31-41`                                                                            |
| date               | 2026-05-21                                                                                       |
| log_root           | `$HUMANOID_PARKOUR_RUNS_ROOT/rough_baseline`                                                     |
| log_dir (absolute) | `/root/autodl-tmp/humanoid_parkour_runs/rough_baseline/logs/rsl_rl/g1_rough/2026-05-21_21-31-41` |
| tensorboard        | `tensorboard --logdir=/root/autodl-tmp/humanoid_parkour_runs/rough_baseline`                     |


Artifacts are on the data disk only (not committed to Git).

## Results (iteration 2999)


| Metric                           | Value            |
| -------------------------------- | ---------------- |
| mean_reward                      | 24.01            |
| mean_episode_length              | 984.5 (max 1000) |
| Episode_Termination/time_out     | 94.62%           |
| Episode_Termination/base_contact | 5.41%            |
| track_lin_vel_xy_exp             | 0.8441           |
| track_ang_vel_z_exp              | 1.1755           |
| error_vel_xy                     | 0.3407 m/s       |
| error_vel_yaw                    | 0.7501 rad/s     |
| value_loss                       | 0.0141           |


Summary CSV row: `results/metrics/rough_baseline.csv`

## Comparison vs flat baseline


| Metric                   | Flat (`2026-05-21_20-36-57`) | Rough (this run) |
| ------------------------ | ---------------------------- | ---------------- |
| max_iterations           | 1500                         | 3000             |
| mean_reward              | 28.77                        | 24.01            |
| mean_episode_length      | 1000.0                       | 984.5            |
| fall rate (base_contact) | 0.44%                        | 5.41%            |
| timeout rate             | 99.56%                       | 94.62%           |
| track_lin_vel_xy_exp     | 0.9425                       | 0.8441           |
| error_vel_xy             | 0.21 m/s                     | 0.34 m/s         |


Rough is harder as expected: lower return, more falls, slightly worse xy velocity tracking; episode length still near cap.

## Figures


| File                                       | Metric                      |
| ------------------------------------------ | --------------------------- |
| `results/figures/rough_mean_reward.png`    | `Train/mean_reward`         |
| `results/figures/rough_episode_length.png` | `Train/mean_episode_length` |


## Checkpoint


| Field           | Value                                                                                                          |
| --------------- | -------------------------------------------------------------------------------------------------------------- |
| final           | `model_2999.pt`                                                                                                |
| path (absolute) | `/root/autodl-tmp/humanoid_parkour_runs/rough_baseline/logs/rsl_rl/g1_rough/2026-05-21_21-31-41/model_2999.pt` |


## Observations

### Reward curve

- iter 0: mean_reward ≈ -0.47; episode length ≈ 12.
- iter 100: dip (mean_reward ≈ -5.6, fall rate ~100%) — early exploration on rough terrain.
- iter 500: mean_reward ≈ 7.7; episode length ≈ 910; still learning terrain.
- iter 1500+: gradual rise; last 100 iters mean_reward ≈ 23.6, std ≈ 0.42 → **converged but below flat plateau (~29)**.

### Behavior

- ~94.6% episodes end by **timeout**, ~5.4% by **torso contact** (vs flat ~0.4% falls).
- `track_lin_vel_xy_exp` ≈ 0.84 (< flat 0.94): rough ground hurts forward tracking.
- Training completed **3000/3000** iterations; suitable reference for parkour (inherit `G1RoughEnvCfg`, not flat).

