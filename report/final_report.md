# Humanoid Parkour — Final Report

## Document map

| Section | Content | Status |
|---------|---------|--------|
| §1 Introduction | Project goal and report scope | Complete |
| §2 Method | Framework, formulation, protocol, baseline setup | Complete |
| §3 Task and environment design | Parkour task and terrain implementation | Complete |
| §4 Reference baselines | Flat and rough quantitative results | Complete |
| §5 Parkour experiments | Training results, rollout evaluation, difficulty comparison, media | Complete for initial submission |
| §6 Discussion and conclusion | Interpretation and next steps | Updated with parkour training results |

---

## 1. Introduction

This project aims to build a parkour-oriented locomotion environment for the Unitree G1 robot in Isaac Lab. The target setting is not generic flat-ground walking, but robust velocity-tracking locomotion over structured obstacles such as stairs, platforms, gaps, and mixed uneven terrain. The final objective is a reproducible training and evaluation pipeline that supports custom parkour terrain design, parkour-specific curriculum learning, quantitative evaluation, and qualitative rollout analysis.

The underlying task family is manager-based locomotion with velocity tracking. The policy observes proprioceptive state and terrain-related signals, and learns to follow commanded base velocity while maintaining balance and avoiding failure termination. Within this overall project, flat and rough official G1 tasks are used as reference baselines: they validate the training pipeline, provide quantitative comparison points, and motivate why the parkour task should inherit from the rough locomotion configuration rather than from the flat configuration.

This report is organized as a final-form project report. The parkour environment has now been implemented and trained across three difficulty tiers. Fixed-checkpoint rollout evaluation and parkour video capture have been added for the initial submission. Formal reward/observation ablations remain future work, while the completed terrain-difficulty ablation is analyzed through training metrics, diagonal rollout evaluation, cross-terrain evaluation, fixed-row stress evaluation, traversal-progress sanity checks, and terrain-aware obstacle crossing stress evaluation.

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

### 3.3 Scope of reward and termination terms

The current trained parkour policies use the inherited G1 rough locomotion reward, observation, termination, and curriculum terms. The project contribution is therefore focused on terrain design, task registration, training, rollout evaluation, and reportable artifacts rather than on a new reward formulation. Reward/observation ablations remain future work and are not claimed as completed experiments in this report.

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
- Final curriculum terrain level scalar: `5.7961`

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
| Curriculum terrain level scalar | N/A | 5.7961 |

The rough task is therefore the appropriate starting point for parkour. It preserves the same locomotion objective while adding uneven terrain, terrain sensing, and curriculum-based difficulty progression.

---

## 5. Parkour experiments and results

### 5.1 Completed experiments

The completed experiments now include the two reference baselines and three custom parkour training runs. The parkour runs use the custom easy, medium, and hard terrain generators described in Section 3.

| Experiment | Task | Iterations | Final checkpoint |
|------------|------|------------|------------------|
| Parkour easy | `Isaac-Velocity-Parkour-G1-Easy-v0` | 3000 | `model_2999.pt` |
| Parkour medium | `Isaac-Velocity-Parkour-G1-Medium-v0` | 3000 | `model_2999.pt` |
| Parkour hard | `Isaac-Velocity-Parkour-G1-Hard-v0` | 3000 | `model_2999.pt` |

All three parkour tiers are compared at the 3000-iteration checkpoint. The hard tier uses the initial hard run checkpoint so that the training budget is consistent with easy and medium.

### 5.2 Parkour quantitative summary

The following numbers are final TensorBoard training scalars, not fixed-seed rollout evaluation results. They are still useful for comparing convergence and relative terrain difficulty because they use the same task family and logging definitions as the flat and rough baselines.

| Metric | Easy | Medium | Hard |
|--------|------|--------|------|
| Mean reward | 30.70 | 20.98 | 11.34 |
| Mean episode length | 983.2 | 988.1 | 941.7 |
| Timeout rate | 96.00% | 93.25% | 89.08% |
| Base-contact/fall rate | 4.00% | 6.75% | 10.92% |
| XY velocity tracking reward | 0.8741 | 0.8539 | 0.7101 |
| XY velocity tracking error | 0.3050 m/s | 0.3590 m/s | 0.4407 m/s |
| Yaw tracking error | 0.6067 rad/s | 0.8445 rad/s | 1.0088 rad/s |
| Curriculum terrain level scalar | 5.7907 | 5.8001 | 5.6389 |

The results show a clear difficulty gradient under the same 3000-iteration training budget. Easy parkour is trainable and even achieves a higher final mean reward than the rough baseline, while maintaining a lower fall rate than rough. Medium introduces gaps and higher obstacles; reward drops and tracking error increases. Hard is the strongest stress test: it has the lowest reward, the highest fall rate, and the weakest velocity-tracking quality among the three parkour tiers.

### 5.3 Baseline-to-parkour comparison

| Metric | Flat | Rough | Parkour easy | Parkour medium | Parkour hard |
|--------|------|-------|--------------|----------------|--------------|
| Mean reward | 28.77 | 24.01 | 30.70 | 20.98 | 11.34 |
| Mean episode length | 1000.0 | 984.5 | 983.2 | 988.1 | 941.7 |
| Fall rate | 0.44% | 5.41% | 4.00% | 6.75% | 10.92% |
| XY tracking error | 0.2087 m/s | 0.3407 m/s | 0.3050 m/s | 0.3590 m/s | 0.4407 m/s |
| Curriculum terrain level scalar | N/A | 5.7961 | 5.7907 | 5.8001 | 5.6389 |

This comparison supports two observations. First, rough terrain is a useful parent configuration: parkour easy starts from the same rough-terrain sensing and curriculum structure and remains stable. Rough, easy, and medium all finish close to curriculum level 5.8, while hard reaches 5.6389 under the same 3000-iteration budget. These curriculum scalars are useful within each terrain preset but should not be interpreted as identical absolute physical difficulty across presets. Second, the custom hard terrain is meaningfully harder than the official rough baseline, especially in tracking error and reward.

### 5.4 Terrain difficulty ablation

The completed formal ablation is a terrain-difficulty ablation over the environment generator. The independent variables are obstacle type and terrain severity: easy removes gaps, medium adds gaps and increases obstacle height, and hard further widens gaps, increases obstacle height, and narrows safe platforms. Robot, base task family, PPO setup, and 3000-iteration checkpoint budget are kept fixed across the three parkour tiers.

| Ablation axis | Evidence | Result |
|---------------|----------|--------|
| Flat vs. rough terrain | Official Isaac Lab baselines | Fall rate increases from 0.44% to 5.41%; XY tracking error increases from 0.2087 to 0.3407 m/s |
| Easy vs. medium vs. hard parkour terrain | Custom parkour runs | Fall rate increases from 4.00% to 6.75% to 10.92%; XY tracking error increases from 0.3050 to 0.3590 to 0.4407 m/s |
| Easy/medium/hard cross-terrain transfer | 4x4 random and fixed-row stress evaluation | Easy-to-hard remains 0.00%; medium-to-hard reaches 87.50% random timeout and 92.19% stress timeout; hard reaches at least 95.31% across all eval tiers |
| Gap/stairs obstacle completion | Fixed-row obstacle crossing stress evaluation | Easy-to-hard obstacle pass is 0.00%; medium-to-hard reaches 65.79% obstacle pass but only 33.33% gap pass; hard-to-hard reaches 100.00% obstacle, gap, and stairs pass |

This makes the ablation stronger than a training-curve comparison alone. Easy is stable but narrow, medium is the first completed tier that transfers well to hard, and hard is the best current source checkpoint for a future generalist policy. Reward/observation ablations have not been run yet, so no reward-term or observation-term causal claim is made.

### 5.5 Fixed-checkpoint rollout evaluation

A separate rollout evaluator was implemented in `scripts/eval_timeout_parkour.py` and launched through `scripts/eval_timeout_parkour.sh`. Unlike the training-summary table, this evaluation loads fixed checkpoints and runs policy inference in the play environments. The timeout definition is conservative and directly tied to Isaac Lab termination signals: an episode is successful if it reaches timeout without `base_contact` termination.

Evaluation command:

```bash
NUM_EPISODES=64 NUM_ENVS=32 bash scripts/eval_timeout_parkour.sh all
```

| Metric | Easy | Medium | Hard |
|--------|------|--------|------|
| Episodes | 64 | 64 | 64 |
| Timeout rate | 100.00% | 95.31% | 87.50% |
| Fall rate | 0.00% | 4.69% | 12.50% |
| Mean episode length | 2000.00 | 1945.97 | 1809.97 |
| Mean XY tracking error | 3.2648 | 3.4487 | 3.5624 |
| Mean yaw tracking error | 0.3719 | 0.3106 | 0.4984 |

The rollout evaluation confirms the same difficulty ordering as the training logs. Easy completes all sampled episodes. Medium introduces some base-contact failures, and hard has the highest failure rate. The tracking-error numbers are computed as direct pre-step velocity-command error during rollout, so their absolute scale should be interpreted as an evaluation statistic rather than as the same normalized TensorBoard command metric used during training.

### 5.6 Cross-terrain generalization

The 4x4 cross-terrain evaluation runs rough/easy/medium/hard checkpoints against rough/easy/medium/hard play environments. Random cross-terrain evaluation samples terrain type and difficulty inside a 10x10 grid. Fixed-row stress evaluation fixes row 9 inside each preset and leaves columns unfixed, so it tests the highest difficulty index while still covering terrain types. Row 9 is preset-relative and should not be treated as the same absolute physical difficulty across rough/easy/medium/hard.

| Checkpoint source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| rough | 95.31% | 98.44% | 68.75% | 29.69% |
| easy | 90.62% | 100.00% | 50.00% | 0.00% |
| medium | 98.44% | 98.44% | 95.31% | 87.50% |
| hard | 100.00% | 100.00% | 96.88% | 95.31% |

The random timeout matrix shows the main generalization pattern. Rough-to-hard is only 29.69%, and easy-to-hard is 0.00%, so rough locomotion and easy parkour do not cover the hard obstacle distribution. Medium-to-hard reaches 87.50%, indicating that adding gaps and stronger obstacles is the minimum completed terrain tier that transfers well to hard. Hard is the strongest source policy, with at least 95.31% timeout rate across all four evaluation environments.

The fixed-row stress matrix preserves this conclusion: easy-to-hard remains 0.00%, medium-to-hard improves to 92.19%, and hard-to-hard remains 95.31%. Thus the cross/stress results support a clear terrain-difficulty ablation: obstacle exposure matters, and hard training is currently the best starting point for a generalist policy.

Traversal-progress evaluation uses the same cross/stress structure and defines progress pass as no fall plus `max_forward_distance_m >= 4.0`. It almost exactly matches timeout: the largest timeout-progress delta is 1.56 percentage points, appearing only for easy-to-rough. This means traversal progress is useful as a forward-distance sanity check, but the current result set is still dominated by base-contact failures rather than by long-lived non-progressing episodes.

### 5.7 Obstacle crossing stress evaluation

The obstacle crossing evaluation uses the unified rollout evaluator with `--metric obstacle`. Unlike traversal progress, it does not use a fixed forward-distance threshold. Instead, it checks whether the robot avoids `base_contact` failure and whether the base crosses the geometry boundary of supported obstacle types. Gap success requires crossing the far side of the gap plus a margin; stairs success requires reaching the forward outer stair-field boundary. Boxes, rough terrain, and slopes are recorded in coverage metadata but are not included in the official `obstacle_pass_rate`.

Official command:

```bash
NUM_EPISODES=64 NUM_ENVS=32 SEED=42 bash scripts/eval_cross_terrain_stress.sh --metric obstacle all
```

Key hard-evaluation results:

| Checkpoint source | Eval hard obstacle pass | Eval hard gap pass | Eval hard stairs pass | Fall before obstacle |
|-------------------|------------------------:|-------------------:|----------------------:|---------------------:|
| rough | 25.00% | 7.89% | 90.00% | 64.58% |
| easy | 0.00% | 0.00% | 0.00% | 89.66% |
| medium | 65.79% | 33.33% | 95.00% | 31.58% |
| hard | 100.00% | 100.00% | 100.00% | 0.00% |

This result refines the timeout/progress conclusion. Medium-to-hard looks strong under survival-style metrics, but obstacle crossing reveals that medium still fails many hard-gap episodes. Its hard stairs pass rate is 95.00%, while its hard gap pass rate is only 33.33%. The hard checkpoint is therefore not merely surviving longer; under the official stress protocol it explicitly crosses the supported hard gap and stairs boundaries at 100.00%.

### 5.8 Result files and figures

Quantitative result files:

- `results/metrics/flat_baseline.csv`
- `results/metrics/rough_baseline.csv`
- `results/metrics/parkour_training_summary.csv`
- `results/metrics/parkour_timeout_eval.csv`
- `results/metrics/obstacle_crossing_cross_terrain_stress_eval.csv`
- `results/tables/ablation_summary.md`
- `results/tables/generalization_analysis.md`
- `results/tables/timeout_vs_progress_delta.md`
- `results/tables/timeout_cross_terrain_summary.md`
- `results/tables/timeout_cross_terrain_stress_summary.md`
- `results/tables/traversal_progress_cross_terrain_summary.md`
- `results/tables/traversal_progress_cross_terrain_stress_summary.md`
- `results/tables/obstacle_crossing_cross_terrain_stress_summary.md`

Learning-curve figures:

- Flat: `results/figures/flat_mean_reward.png`, `results/figures/flat_episode_length.png`
- Rough: `results/figures/rough_mean_reward.png`, `results/figures/rough_episode_length.png`
- Parkour: `results/figures/parkour_mean_reward.png`
- Parkour episode length by tier: `results/figures/parkour_easy_episode_length.png`, `results/figures/parkour_medium_episode_length.png`, `results/figures/parkour_hard_episode_length.png`

### 5.9 Videos

The rollout videos are stored under `report/assets/`.

| Clip | File | Description |
|------|------|-------------|
| Flat baseline play | `report/assets/flat_play.mp4` | Stable velocity tracking on flat terrain with minimal falls |
| Rough baseline play | `report/assets/rough_play.mp4` | Locomotion on procedural rough terrain with visibly higher difficulty |
| Parkour easy play | `report/assets/parkour_easy_play.mp4` | Successful custom parkour rollout on the easiest terrain tier |
| Parkour medium play | `report/assets/parkour_medium_play.mp4` | Custom parkour rollout with gap terrain and higher obstacles |
| Parkour hard | `report/assets/parkour_hard_play.mp4` | Official 3000-iteration hard-tier rollout |

The hard checkpoint is kept at 3000 iterations so the qualitative video uses the same training budget as easy and medium. This supports the interpretation that the hard terrain is a real stress test under a fair comparison protocol rather than only a longer-training comparison.

---

## 6. Discussion

The results establish a progression from flat locomotion to rough locomotion and then to structured parkour terrain. Flat terrain remains the easiest setting, with near-perfect timeout rate and the lowest tracking error. Rough terrain increases failure rate and tracking error, which confirms that terrain complexity is visible in the training metrics.

The custom parkour results show that the inherited rough G1 configuration is a viable base for path-B parkour. Easy parkour converges reliably and keeps the fall rate below the rough baseline, despite using structured obstacles instead of generic rough terrain. Medium and hard then expose the expected degradation as gaps, obstacle heights, and platform constraints increase.

The hard result has two sides. Training metrics still show that hard is the most difficult tier under the same 3000-iteration budget: it has the lowest reward, highest fall rate, and weakest tracking quality among the parkour tiers. However, the formal obstacle crossing stress evaluation shows that the hard checkpoint has learned the supported hard gap/stairs geometry well: hard-to-hard reaches 100.00% obstacle, gap, and stairs pass rates. The remaining weakness is therefore not that the current hard policy cannot solve the official hard obstacles, but that lower-difficulty policies, especially medium, do not fully transfer to hard gaps.

The main evaluation limitation is now the level of semantic precision. Timeout measures survival without base-contact failure. Traversal progress adds a forward-distance sanity check. Obstacle crossing adds base-level gap/stairs boundary success, which is enough to support obstacle-completion claims for the current terrain generator. It still does not verify foot-contact-level safety, precise foothold placement, or mesh-contact semantics. Further improvement should therefore focus on foothold safety, stricter contact-aware obstacle metrics, out-of-distribution obstacle layouts, and optional AMP/SMP-style motion priors rather than on another survival-only metric.

---

## 7. Conclusion

This project built and trained a custom parkour locomotion setup for the Unitree G1 robot in Isaac Lab under path B.

- The flat baseline verified the training, logging, checkpointing, and visualization workflow.
- The rough baseline confirmed that the pipeline remains effective with terrain sensing and curriculum.
- The custom parkour environment adds three terrain difficulty tiers and trains policies for easy, medium, and hard obstacle settings.
- The parkour metrics show a clear difficulty gradient: fall rate and tracking error increase from easy to medium to hard, while reward decreases.
- Cross-terrain timeout/progress evaluation shows that easy is stable but narrow, medium is the first tier with strong survival transfer to hard, and hard is the strongest generalist source policy.
- Terrain-aware obstacle crossing stress evaluation shows that hard-to-hard reaches 100.00% obstacle, gap, and stairs pass rates, while medium-to-hard remains limited by hard gaps at 33.33%.

The remaining work beyond this submission is to complete formal reward/observation ablations, add stricter foot-contact or foothold-safety metrics, test more out-of-distribution obstacle layouts, and optionally explore AMP/SMP motion-prior extensions.
