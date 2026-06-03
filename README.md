# Humanoid Parkour (Isaac Lab)

[中文版](README.zh.md)

Course path B project: build custom parkour terrain curricula and velocity-tracking tasks for **Unitree G1** in Isaac Lab, then complete a reproducible PPO training, evaluation, and reporting workflow.

Isaac Lab remains an **external dependency**. This repository contains only the custom task package, workflow scripts, compact result artifacts, and report deliverables.

## Current Results

The official comparison uses a consistent checkpoint budget for the three parkour tiers.

| Run | Iterations | Checkpoint | Summary |
|-----|-----------:|------------|---------|
| Flat baseline | 1500 | `model_1499.pt` | Official flat G1 reference |
| Rough baseline | 3000 | `model_2999.pt` | Official rough G1 parent task |
| Parkour easy | 3000 | `model_2999.pt` | Conservative structured obstacles |
| Parkour medium | 3000 | `model_2999.pt` | Adds gaps and stronger obstacles |
| Parkour hard | 3000 | `model_2999.pt` | Widest gaps and hardest platforms |
| Rough-MDP ablation | 3000 | `model_2999.pt` | New MDP: progress + foothold safety, cross/stress eval complete |
| Hard-MDP ablation | pending | - | Follow-up new-MDP experiment on hard terrain |

### Current MDP Ablation Status

The MDP ablation does not add a separate Hiking task. It reuses the two dedicated MDP tasks, `rough_mdp` and `hard_mdp`, and keeps the project aligned with the existing velocity-tracking parkour pipeline while borrowing the foothold-safety idea from Hiking in the Wild.

Relative to the inherited G1 rough locomotion MDP, the current ablation changes rewards only; observations, actions, and terrain generation are unchanged:

- `parkour_progress`: rewards world-x forward progress;
- `foothold_safety`: a lightweight contact/state-based cost for foot sliding, low support points that approximate stepping into gaps or edges, and large contacting-foot height mismatch;
- `termination_fall` was removed after an early run showed that it truncated exploration too aggressively.

The completed Rough-MDP checkpoint is:

```text
/root/autodl-tmp/humanoid_parkour_runs/rough_mdp/logs/rsl_rl/g1_rough_mdp/2026-06-03_11-40-18/model_2999.pt
```

Rough-MDP timeout/progress/stress evaluation is complete. Cross and stress outputs are intentionally separated so rerunning one protocol does not overwrite the other.

Official run-level metrics are stored in:

- `results/metrics/parkour_training_summary.csv`
- `results/metrics/parkour_timeout_eval.csv`
- `results/metrics/timeout_cross_terrain_eval.csv`
- `results/metrics/timeout_cross_terrain_stress_eval.csv`
- `results/metrics/traversal_progress_cross_terrain_eval.csv`
- `results/metrics/traversal_progress_cross_terrain_stress_eval.csv`
- `results/metrics/obstacle_crossing_cross_terrain_stress_eval.csv`
- `results/metrics/mdp_ablation_timeout_eval.csv`
- `results/metrics/mdp_ablation_progress_eval.csv`
- `results/metrics/mdp_ablation_timeout_stress_eval.csv`
- `results/metrics/mdp_ablation_progress_stress_eval.csv`
- `results/metrics/mdp_ablation_obstacle_stress_eval.csv`

Report-oriented analysis tables are stored in:

- `results/tables/ablation_summary.md`
- `results/tables/generalization_analysis.md`
- `results/tables/timeout_vs_progress_delta.md`
- `results/tables/obstacle_crossing_cross_terrain_stress_summary.md`

The current completed result chain is: diagonal fixed-checkpoint timeout rollout evaluation, timeout/progress 4x4 random and fixed-row stress evaluation, and terrain-aware obstacle crossing fixed-row stress evaluation.

Cross/stress rollouts share the unified evaluator `scripts/eval_parkour_rollout.py`; select timeout, traversal progress, or obstacle crossing metrics through `--metric timeout|progress|obstacle` in `eval_cross_terrain.sh` and `eval_cross_terrain_stress.sh`. Obstacle crossing measures base-level geometry-boundary success for gap/stairs terrain. The official stress result shows hard-to-hard obstacle, gap, and stairs pass rates of 100.00%; medium-to-hard remains strong on stairs at 95.00% but drops to 33.33% on hard gaps, making hard gap crossing the main remaining terrain-specific bottleneck.

## Requirements

- NVIDIA Isaac Sim, using the version required by the course or lab environment
- [Isaac Lab](https://github.com/isaac-sim/IsaacLab), installed in a separate directory and not copied into this repository
- Python >= 3.10 and a Conda environment, for example `env_isaaclab`

## Installation

```bash
# Run inside the activated Isaac Lab conda environment
pip install -e /path/to/g1-parkour-isaaclab
```

After installation, the Gym task IDs can be loaded through the registration logic in `humanoid_parkour.tasks`; see `humanoid_parkour/tasks/g1_parkour/__init__.py`.

## Common Commands

Set environment variables first, adjusting paths for your machine:

```bash
export ISAACLAB_ROOT=/path/to/IsaacLab
export HUMANOID_PARKOUR_ROOT=/path/to/g1-parkour-isaaclab
```

| Purpose | Script |
|---------|--------|
| Train flat baseline | `bash scripts/train_flat_baseline.sh` |
| Train rough baseline | `bash scripts/train_rough_baseline.sh` |
| Train parkour tasks | `bash scripts/train_parkour.sh [all|easy|medium|hard]` |
| Train MDP ablation tasks | `bash scripts/train_mdp_ablation.sh [all|rough|hard] -- --max_iterations=3000` |
| Play / record videos | `bash scripts/play_parkour.sh [all|easy|medium|hard]` |
| Diagonal rollout evaluation | `NUM_EPISODES=64 NUM_ENVS=32 bash scripts/eval_timeout_parkour.sh all` |
| Timeout random 4x4 cross-terrain evaluation | `NUM_EPISODES=64 NUM_ENVS=32 SEED=42 bash scripts/eval_cross_terrain.sh --metric timeout all` |
| Timeout fixed-row 4x4 stress evaluation | `NUM_EPISODES=64 NUM_ENVS=32 SEED=42 bash scripts/eval_cross_terrain_stress.sh --metric timeout all` |
| Progress random 4x4 cross-terrain evaluation | `NUM_EPISODES=64 NUM_ENVS=32 SEED=42 bash scripts/eval_cross_terrain.sh --metric progress all` |
| Progress fixed-row 4x4 stress evaluation | `NUM_EPISODES=64 NUM_ENVS=32 SEED=42 bash scripts/eval_cross_terrain_stress.sh --metric progress all` |
| Obstacle random 4x4 cross-terrain evaluation | `NUM_EPISODES=64 NUM_ENVS=32 SEED=42 bash scripts/eval_cross_terrain.sh --metric obstacle all` |
| Obstacle fixed-row 4x4 stress evaluation, recommended | `NUM_EPISODES=64 NUM_ENVS=32 SEED=42 bash scripts/eval_cross_terrain_stress.sh --metric obstacle all` |
| Generate cross/stress tables | `python scripts/summarize_timeout_cross_terrain_eval.py --input_csv <csv> --output_dir results/tables` |
| Generate progress cross/stress tables | `python scripts/summarize_traversal_progress_eval.py --input_csv <csv> --output_dir results/tables --output_prefix <prefix>` |
| Generate obstacle cross/stress tables | `python scripts/summarize_obstacle_crossing_eval.py --input_csv <csv> --output_dir results/tables --output_prefix <prefix>` |
| TensorBoard | `bash scripts/launch_tensorboard.sh` |

Training logs and checkpoints are written to the large-disk run root by default; see `humanoid_parkour/utils/paths.py`. They should **not** be committed to Git.

## Task IDs

| Tier | Train | Play |
|------|-------|------|
| Easy | `Isaac-Velocity-Parkour-G1-Easy-v0` | `Isaac-Velocity-Parkour-G1-Easy-Play-v0` |
| Medium | `Isaac-Velocity-Parkour-G1-Medium-v0` | `Isaac-Velocity-Parkour-G1-Medium-Play-v0` |
| Hard | `Isaac-Velocity-Parkour-G1-Hard-v0` | `Isaac-Velocity-Parkour-G1-Hard-Play-v0` |
| Rough-MDP | `Isaac-Velocity-Rough-G1-MDP-v0` | `Isaac-Velocity-Rough-G1-MDP-Play-v0` |
| Hard-MDP | `Isaac-Velocity-Parkour-G1-Hard-MDP-v0` | `Isaac-Velocity-Parkour-G1-Hard-MDP-Play-v0` |
| ExtremeRandom | - | `Isaac-Velocity-Parkour-G1-ExtremeRandom-Play-v0` |

The official rough baseline and cross-eval source task use `Isaac-Velocity-Rough-G1-v0` / `Isaac-Velocity-Rough-G1-Play-v0`.

## Repository Structure

```text
g1-parkour-isaaclab/
├── humanoid_parkour/     # Installable Python package: tasks, terrains, evaluation
├── scripts/              # Training / play / eval workflow scripts
├── configs/              # Experiment and ablation design notes in Markdown
├── results/              # Commit-ready CSV files, figures, and tables
├── report/               # Course report and selected media assets
└── docs/                 # Setup, training, and evaluation documentation
```

See [docs/repo_structure.md](docs/repo_structure.md) for details.

## Course Objective

See [humanoid_parkour_course_project.md](humanoid_parkour_course_project.md).

## License

Project-owned code is released under the [BSD 3-Clause License](LICENSE), consistent with the `SPDX-License-Identifier: BSD-3-Clause` headers in source files.

**External dependencies** such as [Isaac Lab](https://github.com/isaac-sim/IsaacLab) and Isaac Sim are governed by their own licenses. When referencing or inheriting upstream configurations in this repository, follow the corresponding upstream license terms. If you change the copyright holder to yourself or your project group, update the first line of `LICENSE` and the relevant `.py` file headers accordingly.
