# Humanoid Parkour (Isaac Lab)

课程路径 B：在 Isaac Lab 中为 **Unitree G1** 定义 parkour 地形与 velocity-tracking 任务，使用 RSL-RL PPO 完成训练、评估与报告闭环。

Isaac Lab 保持为**外部依赖**；本仓库只包含自定义任务包、脚本与交付物。

## 环境要求

- NVIDIA Isaac Sim（与课程/实验室提供的版本一致）
- [Isaac Lab](https://github.com/isaac-sim/IsaacLab)（安装在独立目录，勿复制进本仓库）
- Python ≥ 3.10，Conda 环境（示例名：`env_isaaclab`）

## 安装

```bash
# 在已激活的 Isaac Lab conda 环境中
pip install -e /path/to/g1-parkour-isaaclab
```

安装后 Gym 任务 ID 可通过 `humanoid_parkour.tasks` 注册逻辑加载（见 `humanoid_parkour/tasks/g1_parkour/__init__.py`）。

## 常用命令

设置环境变量（按你的机器修改路径）：

```bash
export ISAACLAB_ROOT=/path/to/IsaacLab
export HUMANOID_PARKOUR_ROOT=/path/to/g1-parkour-isaaclab
```

| 用途 | 脚本 |
|------|------|
| Flat baseline 训练 | `bash scripts/train_flat_baseline.sh` |
| Rough baseline 训练 | `bash scripts/train_rough_baseline.sh` |
| Parkour 训练 | `bash scripts/train_parkour.sh` |
| Play / 录视频 | `bash scripts/play_parkour.sh` |
| 评估指标 | `bash scripts/eval_parkour.sh` |
| TensorBoard | `bash scripts/launch_tensorboard.sh` |

训练日志与 checkpoint 默认写到大盘路径（见 `humanoid_parkour/utils/paths.py`），**不**提交进 Git。

## 任务 ID

| 档位 | 训练 | Play |
|------|------|------|
| Easy | `Isaac-Velocity-Parkour-G1-Easy-v0` | `Isaac-Velocity-Parkour-G1-Easy-Play-v0` |
| Medium | `Isaac-Velocity-Parkour-G1-Medium-v0` | `Isaac-Velocity-Parkour-G1-Medium-Play-v0` |
| Hard | `Isaac-Velocity-Parkour-G1-Hard-v0` | `Isaac-Velocity-Parkour-G1-Hard-Play-v0` |

脚本：`bash scripts/train_parkour.sh [all\|easy\|medium\|hard]`，`bash scripts/play_parkour.sh` 同上。

## 仓库结构

```
g1-parkour-isaaclab/
├── humanoid_parkour/     # 可安装 Python 包（任务、地形、评估）
├── scripts/              # 训练 / play / eval 流程脚本
├── configs/              # 实验与消融设计说明（Markdown）
├── results/              # 可提交的 CSV / 图表 / 表格
├── report/               # 课程报告与视频素材
└── docs/                 # 安装、训练、评估文档
```

详细说明见 [docs/repo_structure.md](docs/repo_structure.md)。

## 课程目标

见 [humanoid_parkour_course_project.md](humanoid_parkour_course_project.md)。

## 许可证

本仓库自有代码采用 [BSD 3-Clause License](LICENSE)，与源码文件头部的 `SPDX-License-Identifier: BSD-3-Clause` 一致。

**外部依赖**：[Isaac Lab](https://github.com/isaac-sim/IsaacLab) / Isaac Sim 等由各自许可证约束；在本仓库中引用或继承其配置时，请遵守上游许可条款。若将版权持有人改为你本人或小组，请同步更新 `LICENSE` 首行与相关 `.py` 文件头。
