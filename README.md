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

Official run-level metrics are stored in:

- `results/metrics/parkour_training_summary.csv`
- `results/metrics/parkour_timeout_eval.csv`
- `results/metrics/timeout_cross_terrain_eval.csv`
- `results/metrics/timeout_cross_terrain_stress_eval.csv`
- `results/metrics/traversal_progress_cross_terrain_eval.csv`
- `results/metrics/traversal_progress_cross_terrain_stress_eval.csv`

Report-oriented analysis tables are stored in:

- `results/tables/ablation_summary.md`
- `results/tables/generalization_analysis.md`
- `results/tables/timeout_vs_progress_delta.md`

The current evaluation chain is: diagonal fixed-checkpoint timeout rollout evaluation, timeout 4x4 random cross-terrain evaluation, timeout 4x4 fixed-row stress evaluation, traversal progress 4x4 random cross-terrain evaluation, and traversal progress 4x4 fixed-row stress evaluation.

Cross/stress rollouts share the unified evaluator `scripts/eval_parkour_rollout.py`; select timeout or traversal progress metrics through `--metric timeout|progress` in `eval_cross_terrain.sh` and `eval_cross_terrain_stress.sh`.

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
| Play / record videos | `bash scripts/play_parkour.sh [all|easy|medium|hard]` |
| Diagonal rollout evaluation | `NUM_EPISODES=64 NUM_ENVS=32 bash scripts/eval_timeout_parkour.sh all` |
| Timeout random 4x4 cross-terrain evaluation | `NUM_EPISODES=64 NUM_ENVS=32 SEED=42 bash scripts/eval_cross_terrain.sh --metric timeout all` |
| Timeout fixed-row 4x4 stress evaluation | `NUM_EPISODES=64 NUM_ENVS=32 SEED=42 bash scripts/eval_cross_terrain_stress.sh --metric timeout all` |
| Progress random 4x4 cross-terrain evaluation | `NUM_EPISODES=64 NUM_ENVS=32 SEED=42 bash scripts/eval_cross_terrain.sh --metric progress all` |
| Progress fixed-row 4x4 stress evaluation | `NUM_EPISODES=64 NUM_ENVS=32 SEED=42 bash scripts/eval_cross_terrain_stress.sh --metric progress all` |
| Generate cross/stress tables | `python scripts/summarize_timeout_cross_terrain_eval.py --input_csv <csv> --output_dir results/tables` |
| Generate progress cross/stress tables | `python scripts/summarize_traversal_progress_eval.py --input_csv <csv> --output_dir results/tables --output_prefix <prefix>` |
| TensorBoard | `bash scripts/launch_tensorboard.sh` |

Training logs and checkpoints are written to the large-disk run root by default; see `humanoid_parkour/utils/paths.py`. They should **not** be committed to Git.

## Task IDs

| Tier | Train | Play |
|------|-------|------|
| Easy | `Isaac-Velocity-Parkour-G1-Easy-v0` | `Isaac-Velocity-Parkour-G1-Easy-Play-v0` |
| Medium | `Isaac-Velocity-Parkour-G1-Medium-v0` | `Isaac-Velocity-Parkour-G1-Medium-Play-v0` |
| Hard | `Isaac-Velocity-Parkour-G1-Hard-v0` | `Isaac-Velocity-Parkour-G1-Hard-Play-v0` |

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
