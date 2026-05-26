# Humanoid Parkour — Final Report

## 1. Introduction

This project aims to build a parkour-oriented locomotion environment for the Unitree G1 robot in Isaac Lab. The target setting is not generic flat-ground walking, but robust velocity-tracking locomotion over structured obstacles such as stairs, platforms, gaps, and mixed uneven terrain. The final objective is a reproducible training and evaluation pipeline that supports custom parkour terrain design, parkour-specific curriculum learning, quantitative evaluation, and qualitative rollout analysis.

The underlying task family is manager-based locomotion with velocity tracking. The policy observes proprioceptive state and terrain-related signals, and learns to follow commanded base velocity while maintaining balance and avoiding failure termination. Within this overall project, flat and rough official G1 tasks are used as reference baselines: they validate the training pipeline, provide quantitative comparison points, and motivate why the parkour task should inherit from the rough locomotion configuration rather than from the flat configuration.

This report is therefore organized as a final-form project report. The parkour-related sections are kept in their intended final positions, and any parts that depend on future custom-task training are explicitly marked as placeholders.

## 2. Method

### 2.1 Framework

- Simulator and task framework: Isaac Sim + Isaac Lab
- RL algorithm: PPO through RSL-RL
- Robot platform: Unitree G1
- Repository role: this repository stores task extensions, scripts, experiment records, figures, and report assets, while Isaac Lab remains an external dependency

### 2.2 Common locomotion formulation

All environments considered in this project belong to the same locomotion and velocity-tracking family.

- The policy observes base linear and angular velocity, gravity projection, joint states, previous actions, and task commands.
- The action space is joint position control for the whole robot.
- The command generator samples target base velocity.
- The reward combines command tracking quality, smoothness, posture regularization, and failure penalties.

This shared structure is important because it makes the baselines and the future parkour task directly comparable.

### 2.3 Parkour task design (placeholder)

The central design goal of the project is a custom parkour locomotion task for G1.

Planned task components:

- **Task IDs**: `Isaac-Velocity-Parkour-G1-{Easy,Medium,Hard}-v0` (train), `...-Play-v0` (play)
- **Base parent configuration**: inherit from `G1RoughEnvCfg`
- **Terrain design**: replace the default rough terrain generator with parkour-specific terrain presets
- **Difficulty structure**: easy / medium / hard parkour levels
- **Training strategy**: curriculum over terrain difficulty
- **Evaluation outputs**: success rate, fall rate, tracking quality, and rollout videos

Planned terrain elements:

- stairs
- short platforms
- mild height changes
- controlled gaps
- mixed obstacle sequences

Planned implementation files:

- `humanoid_parkour/tasks/g1_parkour/parkour_env_cfg.py` (train + play classes per tier)
- `humanoid_parkour/terrains/parkour_terrain_cfg.py`
- `humanoid_parkour/tasks/g1_parkour/mdp_overrides.py`
- `humanoid_parkour/tasks/g1_parkour/agents/rsl_rl_ppo_cfg.py`

Status: **placeholder; the parkour environment is the main project target, but its custom implementation and training results are not yet finalized.**

### 2.4 Reference baseline setup

To support the parkour task, two official Isaac Lab G1 baselines were trained first.

#### Flat reference baseline

- Task ID: `Isaac-Velocity-Flat-G1-v0`
- PPO policy MLP: `[256, 128, 128]`
- `num_envs = 4096`
- `num_steps_per_env = 24`
- `max_iterations = 1500`
- `episode_length_s = 20.0`

#### Rough reference baseline

- Task ID: `Isaac-Velocity-Rough-G1-v0`
- PPO policy MLP: `[512, 256, 128]`
- `num_envs = 4096`
- `num_steps_per_env = 24`
- `max_iterations = 3000`
- `episode_length_s = 20.0`
- Terrain generator: `ROUGH_TERRAINS_CFG`
- Additional sensing: `height_scanner` attached to `torso_link`
- Curriculum: `terrain_levels_vel`

These baselines are not the final contribution of the project. Their role is to validate the training pipeline and to provide a principled starting point for the parkour environment.

### 2.5 Experimental protocol

All completed runs were executed on the AutoDL Linux GPU environment with:

- GPU: NVIDIA GeForce RTX 3090
- Conda environment: `/root/autodl-tmp/isaac_workspace/env_isaaclab`
- Isaac Lab root: `/root/autodl-tmp/isaac_workspace/IsaacLab`
- Run storage root: `/root/autodl-tmp/humanoid_parkour_runs`

Training artifacts such as checkpoints, TensorBoard event files, and raw logs were kept on the data disk and were not committed to Git. Only compact summaries, figures, and report assets were kept in the repository.

## 3. Reference Baselines

### 3.1 Flat baseline

The flat baseline converged quickly and served as the first full pipeline validation.

- Run ID: `2026-05-21_20-36-57`
- Final checkpoint: `model_1499.pt`
- Wall time: about 40 minutes
- Final mean reward: `28.77`
- Final mean episode length: `1000.0`
- Timeout termination: `99.56%`
- Base-contact termination: `0.44%`
- Velocity tracking error in XY: `0.2087 m/s`
- Velocity tracking error in yaw: `0.4566 rad/s`

Interpretation:

- The policy learned a stable locomotion behavior on flat terrain.
- Almost all episodes ended by timeout rather than failure.
- The learning curves show rapid improvement after the early unstable exploration stage and then a clear plateau.

Relevant figures:

- `results/figures/flat_mean_reward.png`
- `results/figures/flat_episode_length.png`

### 3.2 Rough baseline

The rough baseline was intentionally harder and provides the more relevant parent configuration for the future parkour task.

- Run ID: `2026-05-21_21-31-41`
- Final checkpoint: `model_2999.pt`
- Wall time: about 101 minutes
- Final mean reward: `24.01`
- Final mean episode length: `984.5`
- Timeout termination: `94.62%`
- Base-contact termination: `5.41%`
- Velocity tracking error in XY: `0.3407 m/s`
- Velocity tracking error in yaw: `0.7501 rad/s`

Interpretation:

- The policy still converged, but the learned behavior is less stable than on flat terrain.
- Rough terrain introduces more falls, lower return, and worse tracking quality.
- Even so, the robot remains functional on most episodes, with the majority still ending by timeout.

Relevant figures:

- `results/figures/rough_mean_reward.png`
- `results/figures/rough_episode_length.png`

### 3.3 Baseline comparison

The comparison confirms that rough terrain is a meaningful difficulty increase rather than a broken setup.

| Metric | Flat | Rough |
|------|------|------|
| Max iterations | 1500 | 3000 |
| Mean reward | 28.77 | 24.01 |
| Mean episode length | 1000.0 | 984.5 |
| Failure rate (`base_contact`) | 0.44% | 5.41% |
| Timeout rate | 99.56% | 94.62% |
| XY velocity tracking reward | 0.9425 | 0.8441 |
| XY velocity tracking error | 0.2087 m/s | 0.3407 m/s |

The rough task is therefore the appropriate starting point for parkour. It preserves the same locomotion objective while adding uneven terrain, terrain sensing, and curriculum-based difficulty progression.

## 4. Experiments

### 4.1 Completed experiments

The completed experiments in the current project stage are:

- flat reference baseline training
- rough reference baseline training
- qualitative play-video generation for both reference baselines

### 4.2 Parkour training plan (placeholder)

The main project experiments will target the custom parkour environment.

Planned training stages:

1. **Parkour-easy**: conservative obstacle configuration for the first successful run
2. **Parkour curriculum**: easy / medium / hard terrain levels
3. **Parkour play**: qualitative rollout recording on trained checkpoints
4. **Parkour evaluation**: metrics export to CSV for final comparison

Status: **placeholder**

### 4.3 Ablation plan (placeholder)

Two ablation groups are planned:

1. **Terrain ablation**
   - easy-only vs. multi-level curriculum
   - reduced obstacle difficulty vs. full parkour terrain

2. **Reward / observation ablation**
   - with vs. without selected parkour-specific reward terms
   - with vs. without terrain-sensitive observation adjustments

Status: **placeholder**

## 5. Results

### 5.1 Quantitative summaries

The completed quantitative summaries currently available are stored in:

- `results/metrics/flat_baseline.csv`
- `results/metrics/rough_baseline.csv`

Parkour and ablation result tables remain placeholders:

- `results/metrics/parkour_eval.csv` — placeholder
- `results/tables/ablation_summary.md` — placeholder

### 5.2 Learning curves

Completed learning curves:

- Flat: `results/figures/flat_mean_reward.png`, `results/figures/flat_episode_length.png`
- Rough: `results/figures/rough_mean_reward.png`, `results/figures/rough_episode_length.png`

Planned parkour figures:

- Parkour reward curve — placeholder
- Parkour episode length curve — placeholder
- Success-rate-by-level figure — placeholder

### 5.3 Videos

The currently available videos are reference-baseline videos stored under `report/assets/`.

| Clip | File | Description |
|------|------|-------------|
| Flat baseline play | `report/assets/flat_play.mp4` | Stable velocity tracking on flat terrain with minimal falls |
| Rough baseline play | `report/assets/rough_play.mp4` | Locomotion on procedural rough terrain with visibly higher difficulty |
| Parkour play | `report/assets/parkour_play.mp4` | Placeholder |

These videos currently document the reference baselines. The final version of the project is expected to add parkour-specific rollout videos after the custom environment is trained.

## 6. Discussion

The current results establish a clear and internally consistent progression from flat to rough locomotion. Flat terrain serves as a relatively easy control setting in which the policy quickly converges to near-maximal episode length and very low failure rate. Rough terrain introduces a measurable degradation in reward, tracking quality, and stability, but the training still converges and remains usable as a locomotion prior.

This is important because the core project objective is a parkour task rather than a generic locomotion benchmark. A custom parkour environment should not be built on the flat baseline, since flat locomotion lacks terrain sensing and terrain curriculum. The rough baseline already contains the ingredients most relevant for parkour: uneven terrain, height scanning, and learning under terrain-dependent difficulty.

The main limitation of the current report is that the parkour-specific implementation is still incomplete. The report is therefore final in structure but partial in content: the parkour design has a dedicated place in the narrative, while its quantitative results, qualitative rollout evidence, and ablation findings remain placeholders.

## 7. Conclusion

This project is centered on building a custom parkour locomotion environment for the Unitree G1 robot in Isaac Lab.

- The completed flat baseline verified that the training, logging, checkpointing, and visualization workflow are correct.
- The completed rough baseline confirmed that the same pipeline remains effective under more difficult terrain, while also revealing the expected degradation in stability and tracking quality.
- Together, these baselines provide the technical foundation and comparison reference for the intended parkour task.

The next milestone is to implement a minimal trainable parkour-easy environment, train it successfully, and then extend it into a full parkour curriculum with parkour-specific evaluation metrics, videos, and ablation studies.
