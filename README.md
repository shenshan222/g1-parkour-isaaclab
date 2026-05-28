# Humanoid Parkour (Isaac Lab)

[中文版](README.zh.md)

Course path B: define parkour terrains and velocity-tracking tasks for **Unitree G1** in Isaac Lab, then complete the training, evaluation, and reporting loop with RSL-RL PPO.

Isaac Lab remains an **external dependency**. This repository only contains the custom task package, workflow scripts, and deliverables.

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
| Train parkour tasks | `bash scripts/train_parkour.sh` |
| Play / record videos | `bash scripts/play_parkour.sh` |
| Evaluate metrics | `bash scripts/eval_parkour.sh` |
| TensorBoard | `bash scripts/launch_tensorboard.sh` |

Training logs and checkpoints are written to the large-disk run root by default; see `humanoid_parkour/utils/paths.py`. They should **not** be committed to Git.

## Task IDs

| Tier | Train | Play |
|------|-------|------|
| Easy | `Isaac-Velocity-Parkour-G1-Easy-v0` | `Isaac-Velocity-Parkour-G1-Easy-Play-v0` |
| Medium | `Isaac-Velocity-Parkour-G1-Medium-v0` | `Isaac-Velocity-Parkour-G1-Medium-Play-v0` |
| Hard | `Isaac-Velocity-Parkour-G1-Hard-v0` | `Isaac-Velocity-Parkour-G1-Hard-Play-v0` |

Use `bash scripts/train_parkour.sh [all|easy|medium|hard]`; `bash scripts/play_parkour.sh` accepts the same tier arguments.

## Repository Structure

```text
g1-parkour-isaaclab/
├── humanoid_parkour/     # Installable Python package: tasks, terrains, evaluation
├── scripts/              # Training / play / eval workflow scripts
├── configs/              # Experiment and ablation design notes in Markdown
├── results/              # Commit-ready CSV files, figures, and tables
├── report/               # Course report and media assets
└── docs/                 # Setup, training, and evaluation documentation
```

See [docs/repo_structure.md](docs/repo_structure.md) for details.

## Course Objective

See [humanoid_parkour_course_project.md](humanoid_parkour_course_project.md).

## License

Project-owned code is released under the [BSD 3-Clause License](LICENSE), consistent with the `SPDX-License-Identifier: BSD-3-Clause` headers in source files.

**External dependencies** such as [Isaac Lab](https://github.com/isaac-sim/IsaacLab) and Isaac Sim are governed by their own licenses. When referencing or inheriting upstream configurations in this repository, follow the corresponding upstream license terms. If you change the copyright holder to yourself or your project group, update the first line of `LICENSE` and the relevant `.py` file headers accordingly.
