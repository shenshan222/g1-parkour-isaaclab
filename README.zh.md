# Humanoid Parkour (Isaac Lab)

[English](README.md)

课程路径 B 项目：在 Isaac Lab 中为 **Unitree G1** 构建自定义 parkour 地形课程和速度跟踪任务，并完成可复现的 PPO 训练、评估与报告流程。

Isaac Lab 保持为**外部依赖**。本仓库只包含自定义任务包、工作流脚本、轻量结果文件和报告交付物。

## 当前结果

正式对比采用统一的 checkpoint 预算，三个 parkour 难度均使用 3000 iteration 结果。

| 运行 | Iterations | Checkpoint | 说明 |
|------|-----------:|------------|------|
| Flat baseline | 1500 | `model_1499.pt` | 官方 flat G1 参考 |
| Rough baseline | 3000 | `model_2999.pt` | 官方 rough G1 父任务 |
| Parkour easy | 3000 | `model_2999.pt` | 保守结构化障碍 |
| Parkour medium | 3000 | `model_2999.pt` | 加入 gap 和更强障碍 |
| Parkour hard | 3000 | `model_2999.pt` | 最大 gap 和最困难平台约束 |
| Rough-MDP ablation | 3000 | `model_2999.pt` | 新 MDP：progress + foothold safety，cross/stress 评估已完成 |
| Hard-MDP ablation | 3000 | `model_2999.pt` | 新 MDP 在 hard terrain 上的消融实验，cross/stress 评估已完成 |

### 当前 MDP 消融状态

新增 MDP 消融不注册额外的 Hiking 任务，而是复用两个独立任务：`rough_mdp` 和 `hard_mdp`。设计目标是吸收 Hiking in the Wild 中 foothold safety 的思想，同时保持本项目的 velocity-tracking parkour pipeline 简洁可控。

当前 MDP 相对原始 G1 rough locomotion 只修改 reward，不修改 observation、action 或 terrain：

- `parkour_progress`：奖励世界 x 方向前进，用于强化穿越障碍的 forward progress；
- `foothold_safety`：轻量落脚安全 cost，基于已有 ankle contact 和 body state，惩罚接触滑移、疑似踏空/边缘支撑，以及双脚接触高度差过大；
- `termination_fall`：早期实验中会过早截断探索，已从当前 MDP 中移除。

Rough-MDP 和 Hard-MDP 正式训练均已完成，checkpoint 为：

```text
# Rough-MDP
/root/autodl-tmp/humanoid_parkour_runs/rough_mdp/logs/rsl_rl/g1_rough_mdp/2026-06-03_11-40-18/model_2999.pt
# Hard-MDP
/root/autodl-tmp/humanoid_parkour_runs/parkour_hard_mdp/logs/rsl_rl/g1_parkour_hard_mdp/2026-06-03_14-56-13/model_2999.pt
```

MDP 的 timeout/progress/obstacle cross 与 stress 评估均已完成。Cross 和 stress 输出有意分离，避免重跑某个协议时覆盖另一个协议的结果。

正式指标文件：

- `results/metrics/parkour_training_summary.csv`
- `results/metrics/parkour_timeout_eval.csv`
- `results/metrics/timeout_cross_terrain_eval.csv`
- `results/metrics/timeout_cross_terrain_stress_eval.csv`
- `results/metrics/traversal_progress_cross_terrain_eval.csv`
- `results/metrics/traversal_progress_cross_terrain_stress_eval.csv`
- `results/metrics/obstacle_crossing_cross_terrain_stress_eval.csv`

MDP 消融数据（`rough_mdp` 和 `hard_mdp`）已通过 `scripts/merge_mdp_into_baseline.py` 直接合并到上述 baseline cross/stress CSV 中，不保留独立的 MDP-only 指标文件。

分析表格与图表：

- `results/tables/ablation_summary.md`：MDP 消融综合分析
- `results/tables/generalization_analysis.md`：timeout + progress 交叉泛化分析
- `results/tables/timeout_vs_progress_delta.md`：timeout 与 progress 差异分析
- `results/tables/obstacle_crossing_cross_terrain_stress_summary.md`：obstacle crossing 压力评估
- `results/figures/`：MDP 训练曲线与消融对比图，作为最终报告产物提交。原始 TensorBoard event 文件保存在 `$HUMANOID_PARKOUR_RUNS_ROOT`，不纳入 Git；图表生成辅助脚本已从本精简提交仓库中删除。

主评估链条包括：固定 checkpoint diagonal rollout、4x4 random cross-terrain evaluation、4x4 fixed-row stress evaluation、MDP 消融对比分析。

## 环境要求

- NVIDIA Isaac Sim（版本需与课程或实验环境一致）
- [Isaac Lab](https://github.com/isaac-sim/IsaacLab)，安装在独立目录，不复制进本仓库
- Python >= 3.10，Conda 环境（例如 `env_isaaclab`）

## 安装

```bash
# 在已激活的 Isaac Lab conda 环境中运行
pip install -e /path/to/g1-parkour-isaaclab
```

安装后，可通过 `humanoid_parkour.tasks` 的注册逻辑加载 Gym 任务 ID；参见 `humanoid_parkour/tasks/g1_parkour/__init__.py`。

## 常用命令

先按机器环境设置路径：

```bash
export ISAACLAB_ROOT=/path/to/IsaacLab
export HUMANOID_PARKOUR_ROOT=/path/to/g1-parkour-isaaclab
```

| 用途 | 脚本 |
|------|------|
| Flat baseline 训练 | `bash scripts/train_flat_baseline.sh` |
| Rough baseline 训练 | `bash scripts/train_rough_baseline.sh` |
| Parkour 训练 | `bash scripts/train_parkour.sh [all|easy|medium|hard]` |
| MDP 消融训练 | `bash scripts/train_mdp_ablation.sh [all|rough|hard] -- --max_iterations=3000` |
| Play / 录视频 | `bash scripts/play_parkour.sh [all|easy|medium|hard]` |
| Diagonal rollout 评估 | `NUM_EPISODES=64 NUM_ENVS=32 bash scripts/eval_timeout_parkour.sh all` |
| Timeout random 4x4 交叉评估 | `NUM_EPISODES=64 NUM_ENVS=32 SEED=42 bash scripts/eval_cross_terrain.sh --metric timeout all` |
| Timeout fixed-row 4x4 压力测试 | `NUM_EPISODES=64 NUM_ENVS=32 SEED=42 bash scripts/eval_cross_terrain_stress.sh --metric timeout all` |
| Progress random 4x4 交叉评估 | `NUM_EPISODES=64 NUM_ENVS=32 SEED=42 bash scripts/eval_cross_terrain.sh --metric progress all` |
| Progress fixed-row 4x4 压力测试 | `NUM_EPISODES=64 NUM_ENVS=32 SEED=42 bash scripts/eval_cross_terrain_stress.sh --metric progress all` |
| Obstacle random 4x4 交叉评估 | `NUM_EPISODES=64 NUM_ENVS=32 SEED=42 bash scripts/eval_cross_terrain.sh --metric obstacle all` |
| Obstacle fixed-row 4x4 压力测试（推荐） | `NUM_EPISODES=64 NUM_ENVS=32 SEED=42 bash scripts/eval_cross_terrain_stress.sh --metric obstacle all` |
| 生成 cross/stress 表格 | `python scripts/summarize_timeout_cross_terrain_eval.py --input_csv <csv> --output_dir results/tables` |
| TensorBoard | `bash scripts/launch_tensorboard.sh` |

训练日志与 checkpoint 默认写入大盘路径；参见 `humanoid_parkour/utils/paths.py`。这些文件**不应提交到 Git**。

## 任务 ID

| 档位 | 训练 | Play |
|------|------|------|
| Easy | `Isaac-Velocity-Parkour-G1-Easy-v0` | `Isaac-Velocity-Parkour-G1-Easy-Play-v0` |
| Medium | `Isaac-Velocity-Parkour-G1-Medium-v0` | `Isaac-Velocity-Parkour-G1-Medium-Play-v0` |
| Hard | `Isaac-Velocity-Parkour-G1-Hard-v0` | `Isaac-Velocity-Parkour-G1-Hard-Play-v0` |
| Rough-MDP | `Isaac-Velocity-Rough-G1-MDP-v0` | `Isaac-Velocity-Rough-G1-MDP-Play-v0` |
| Hard-MDP | `Isaac-Velocity-Parkour-G1-Hard-MDP-v0` | `Isaac-Velocity-Parkour-G1-Hard-MDP-Play-v0` |
| ExtremeRandom | - | `Isaac-Velocity-Parkour-G1-ExtremeRandom-Play-v0` |

官方 rough baseline 和 cross-eval source 任务使用 `Isaac-Velocity-Rough-G1-v0` / `Isaac-Velocity-Rough-G1-Play-v0`。

## 仓库结构

```text
g1-parkour-isaaclab/
|-- humanoid_parkour/     # 可安装 Python 包：任务、地形、评估
|-- scripts/              # 训练 / play / eval 工作流脚本
|-- results/              # 可提交的 CSV、图表、表格
|-- report/               # 课程报告与精选媒体素材
`-- docs/                 # 安装、训练、评估文档
```

详细说明见 [docs/repo_structure.md](docs/repo_structure.md)。

## 课程目标

见 [humanoid_parkour_course_project.md](humanoid_parkour_course_project.md)。

## 许可证

本仓库自有代码采用 [BSD 3-Clause License](LICENSE)，与源码文件头部的 `SPDX-License-Identifier: BSD-3-Clause` 一致。

**外部依赖**，例如 [Isaac Lab](https://github.com/isaac-sim/IsaacLab) 和 Isaac Sim，由各自许可证约束。在本仓库中引用或继承其配置时，请遵守上游许可证条款。如果将版权持有人改为你本人或项目组，请同步更新 `LICENSE` 首行与相关 `.py` 文件头。
