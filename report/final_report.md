# Humanoid Parkour — Final Report

## Document map

| Section | Content | Status |
|---------|---------|--------|
| §1 Introduction | Project goal and report scope | Complete |
| §2 Method | Framework, formulation, protocol, baseline setup | Complete |
| §3 Task and environment design | Parkour task and terrain implementation | Complete |
| §4 Reference baselines | Flat and rough quantitative results | Complete |
| §5 Parkour experiments | Training results, difficulty comparison, remaining evaluation gaps | Mostly complete; rollout eval/media pending |
| §6 Discussion and conclusion | Interpretation and next steps | Updated with parkour training results |

---

## 1. Introduction

This project aims to build a parkour-oriented locomotion environment for the Unitree G1 robot in Isaac Lab. The target setting is not generic flat-ground walking, but robust velocity-tracking locomotion over structured obstacles such as stairs, platforms, gaps, and mixed uneven terrain. The final objective is a reproducible training and evaluation pipeline that supports custom parkour terrain design, parkour-specific curriculum learning, quantitative evaluation, and qualitative rollout analysis.

The underlying task family is manager-based locomotion with velocity tracking. The policy observes proprioceptive state and terrain-related signals, and learns to follow commanded base velocity while maintaining balance and avoiding failure termination. Within this overall project, flat and rough official G1 tasks are used as reference baselines: they validate the training pipeline, provide quantitative comparison points, and motivate why the parkour task should inherit from the rough locomotion configuration rather than from the flat configuration.

This report is organized as a final-form project report. The parkour environment has now been implemented and trained across three difficulty tiers. The remaining gaps are fixed-checkpoint rollout evaluation, parkour video capture, and formal reward/observation ablations.

---

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

### 2.3 Experimental protocol

All completed runs were executed on the AutoDL Linux GPU environment with:

- GPU: NVIDIA GeForce RTX 3090
- Conda environment: `/root/autodl-tmp/isaac_workspace/env_isaaclab`
- Isaac Lab root: `/root/autodl-tmp/isaac_workspace/IsaacLab`
- Run storage root: `/root/autodl-tmp/humanoid_parkour_runs`

Training artifacts such as checkpoints, TensorBoard event files, and raw logs were kept on the data disk and were not committed to Git. Only compact summaries, figures, and report assets were kept in the repository.

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

---

## 3. Task and environment design

### 3.1 Parkour task design

The custom parkour task is implemented as a direct extension of Isaac Lab's G1 rough velocity-tracking environment. This choice keeps the same locomotion objective and PPO setup as the rough baseline while replacing the default rough terrain generator with structured obstacle terrains.

Implemented task components:

- **Task IDs**: `Isaac-Velocity-Parkour-G1-{Easy,Medium,Hard}-v0` for training and `...-Play-v0` for visualization.
- **Base parent configuration**: all tiers inherit from `G1RoughEnvCfg`, preserving the rough-terrain observation structure and height scanner.
- **Terrain design**: `PARKOUR_EASY_TERRAINS_CFG`, `PARKOUR_MEDIUM_TERRAINS_CFG`, and `PARKOUR_HARD_TERRAINS_CFG` replace the default rough terrain generator.
- **Training strategy**: each tier enables terrain curriculum through the inherited rough locomotion curriculum mechanism.
- **Play settings**: play environments reduce parallel environment count, disable observation corruption and push events, and use fixed forward velocity commands for clearer rollout inspection.

Implementation files:

- `humanoid_parkour/tasks/g1_parkour/parkour_env_cfg.py`
- `humanoid_parkour/terrains/parkour_terrain_cfg.py`
- `humanoid_parkour/tasks/g1_parkour/__init__.py`
- `humanoid_parkour/tasks/g1_parkour/agents/rsl_rl_ppo_cfg.py`

### 3.2 Terrain difficulty tiers

The three parkour tiers are independent terrain-generator presets rather than a single terrain with one scalar knob. This makes each tier interpretable and supports direct difficulty comparison.

| Tier | Main terrain elements | Difficulty design |
|------|-----------------------|-------------------|
| Easy | Pyramid stairs, inverted stairs, random box grid, random rough terrain, slopes | Conservative obstacle heights; no gap terrain |
| Medium | Easy elements plus gap terrain | Higher stairs/boxes/roughness and controlled gaps |
| Hard | Stairs, boxes, rough terrain, gaps, slopes | Taller obstacles, wider gaps, narrower platforms, stronger terrain stress |

This design satisfies the path-B requirement of defining at least three increasing parkour terrain difficulty levels. It also gives a usable terrain-ablation axis: flat, rough, parkour easy, parkour medium, and parkour hard.

### 3.3 Scope of custom MDP terms

The current trained parkour policies use the inherited G1 rough locomotion reward, observation, termination, and curriculum terms. Placeholder hooks for future parkour-specific rewards and termination checks exist in `humanoid_parkour/tasks/g1_parkour/mdp_overrides.py`, but they are not used in the completed training runs.

This means the current contribution is primarily terrain and task-configuration design. Reward/observation ablations remain future work and should not be interpreted as completed experiments in this report.

---

## 4. Reference baselines

### 4.1 Flat baseline

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

### 4.2 Rough baseline

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

### 4.3 Baseline comparison

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

---

## 5. Parkour experiments and results

### 5.1 Completed experiments

The completed experiments now include the two reference baselines and three custom parkour training runs. The parkour runs use the custom easy, medium, and hard terrain generators described in Section 3.

| Experiment | Task | Iterations | Final checkpoint |
|------------|------|------------|------------------|
| Parkour easy | `Isaac-Velocity-Parkour-G1-Easy-v0` | 3000 | `model_2999.pt` |
| Parkour medium | `Isaac-Velocity-Parkour-G1-Medium-v0` | 3000 | `model_2999.pt` |
| Parkour hard | `Isaac-Velocity-Parkour-G1-Hard-v0` | 4499 | `model_4498.pt` |

Hard was first trained to iteration 2999 and then resumed to iteration 4498 because the initial hard run had the lowest reward and highest instability among the three tiers.

### 5.2 Parkour quantitative summary

The following numbers are final TensorBoard training scalars, not fixed-seed rollout evaluation results. They are still useful for comparing convergence and relative terrain difficulty because they use the same task family and logging definitions as the flat and rough baselines.

| Metric | Easy | Medium | Hard |
|--------|------|--------|------|
| Mean reward | 30.70 | 20.98 | 14.44 |
| Mean episode length | 983.2 | 988.1 | 977.2 |
| Timeout rate | 96.00% | 93.25% | 92.73% |
| Base-contact/fall rate | 4.00% | 6.75% | 7.27% |
| XY velocity tracking reward | 0.8741 | 0.8539 | 0.7836 |
| XY velocity tracking error | 0.3050 m/s | 0.3590 m/s | 0.4689 m/s |
| Yaw tracking error | 0.6067 rad/s | 0.8445 rad/s | 0.9720 rad/s |
| Curriculum terrain level scalar | 5.7907 | 5.8001 | 5.6135 |

The results show a clear difficulty gradient. Easy parkour is trainable and even achieves a higher final mean reward than the rough baseline, while maintaining a lower fall rate than rough. Medium introduces gaps and higher obstacles; reward drops and tracking error increases. Hard is the strongest stress test: after resumed training it keeps most episodes alive until timeout, but its reward and velocity-tracking quality remain substantially worse than easy and medium.

### 5.3 Baseline-to-parkour comparison

| Metric | Flat | Rough | Parkour easy | Parkour medium | Parkour hard |
|--------|------|-------|--------------|----------------|--------------|
| Mean reward | 28.77 | 24.01 | 30.70 | 20.98 | 14.44 |
| Mean episode length | 1000.0 | 984.5 | 983.2 | 988.1 | 977.2 |
| Fall rate | 0.44% | 5.41% | 4.00% | 6.75% | 7.27% |
| XY tracking error | 0.2087 m/s | 0.3407 m/s | 0.3050 m/s | 0.3590 m/s | 0.4689 m/s |

This comparison supports two observations. First, rough terrain is a useful parent configuration: parkour easy starts from the same rough-terrain sensing and curriculum structure and remains stable. Second, the custom hard terrain is meaningfully harder than the official rough baseline, especially in tracking error and reward.

### 5.4 Difficulty ablation

The current completed ablation is a terrain-difficulty ablation over the environment generator. The independent variables are obstacle type and terrain severity: easy removes gaps, medium adds gaps and increases obstacle height, and hard further widens gaps, increases obstacle height, and narrows safe platforms.

| Ablation axis | Evidence | Result |
|---------------|----------|--------|
| Flat vs. rough terrain | Official Isaac Lab baselines | Fall rate increases from 0.44% to 5.41%; XY tracking error increases from 0.2087 to 0.3407 m/s |
| Easy vs. medium vs. hard parkour terrain | Custom parkour runs | Fall rate increases from 4.00% to 6.75% to 7.27%; XY tracking error increases from 0.3050 to 0.3590 to 0.4689 m/s |

Reward/observation ablations have not been run yet. The placeholder `mdp_overrides.py` file should be treated as planned extension work rather than a completed ablation.

### 5.5 Result files and figures

Quantitative result files:

- `results/metrics/flat_baseline.csv`
- `results/metrics/rough_baseline.csv`
- `results/metrics/parkour_training_summary.csv`
- `results/tables/ablation_summary.md`

`results/metrics/parkour_eval.csv` is reserved for future fixed-checkpoint rollout evaluation and currently should not be used as the source of success-rate claims.

Learning-curve figures:

- Flat: `results/figures/flat_mean_reward.png`, `results/figures/flat_episode_length.png`
- Rough: `results/figures/rough_mean_reward.png`, `results/figures/rough_episode_length.png`
- Parkour: `results/figures/parkour_mean_reward.png`
- Parkour episode length by tier: `results/figures/parkour_easy_episode_length.png`, `results/figures/parkour_medium_episode_length.png`, `results/figures/parkour_hard_episode_length.png`

### 5.6 Videos

The currently available videos are reference-baseline videos stored under `report/assets/`.

| Clip | File | Description |
|------|------|-------------|
| Flat baseline play | `report/assets/flat_play.mp4` | Stable velocity tracking on flat terrain with minimal falls |
| Rough baseline play | `report/assets/rough_play.mp4` | Locomotion on procedural rough terrain with visibly higher difficulty |

Parkour-specific rollout videos have not yet been captured into `report/assets/`. The highest-priority missing media are one successful easy or medium parkour rollout and one hard-tier failure or near-failure case for qualitative analysis.

---

## 6. Discussion

The results establish a progression from flat locomotion to rough locomotion and then to structured parkour terrain. Flat terrain remains the easiest setting, with near-perfect timeout rate and the lowest tracking error. Rough terrain increases failure rate and tracking error, which confirms that terrain complexity is visible in the training metrics.

The custom parkour results show that the inherited rough G1 configuration is a viable base for path-B parkour. Easy parkour converges reliably and keeps the fall rate below the rough baseline, despite using structured obstacles instead of generic rough terrain. Medium and hard then expose the expected degradation as gaps, obstacle heights, and platform constraints increase.

The hard result is the most informative failure boundary. Resuming hard training from 3000 to 4498 iterations improves stability relative to the initial hard checkpoint, but the final policy still has the worst reward and tracking error. This suggests that the terrain generator is difficult enough to stress the inherited rough reward. Further improvement likely requires either longer training, tuned command ranges, or parkour-specific reward/termination terms such as forward progress, foothold safety, or obstacle-passing success.

The main limitation is evaluation. The current tables use training scalars, not a separate fixed-seed rollout evaluator. Therefore, this report can defensibly claim that the three parkour tiers were implemented and trained, and that their training metrics show increasing difficulty. It should not yet claim formal task success rate or obstacle pass rate until `scripts/eval_parkour.sh` is replaced with a real rollout evaluation driver.

---

## 7. Conclusion

This project built and trained a custom parkour locomotion setup for the Unitree G1 robot in Isaac Lab under path B.

- The flat baseline verified the training, logging, checkpointing, and visualization workflow.
- The rough baseline confirmed that the pipeline remains effective with terrain sensing and curriculum.
- The custom parkour environment adds three terrain difficulty tiers and trains policies for easy, medium, and hard obstacle settings.
- The parkour metrics show a clear difficulty gradient: fall rate and tracking error increase from easy to medium to hard, while reward decreases.

The remaining work is to run fixed-checkpoint parkour rollout evaluation, capture parkour success and failure videos, and complete formal reward/observation ablations.
