# Humanoid Parkour 课程项目（4 周）

## 要做什么

在仿真中让 humanoid（最好 **G1**；也可使用 **SMPL-X**）在含障碍 / 不平整地面的场景里完成一段简单的 parkour 行为，例如：上下台阶、跨小沟、绕障、踏上低台、连续跳跃等。要求完成一个完整的 **训练 — 评估 — 调参 — 报告** 闭环。

## 怎么做

下面的路径以从易到难给出：

### 路径 A：纯 Replay 改写 BeyondMimic

- 基于 [BeyondMimic / whole_body_tracking](https://github.com/HybridRobotics/whole_body_tracking)，在 [MimicKit](https://github.com/xbpeng/MimicKit)、[Project Instinct](https://project-instinct.github.io/) 等地方找 parkour 相关的 reference motions。
- 用 Isaac Lab 的 `RigidObjectCfg`、`TerrainImporter` 等 APIs 在场景里摆障碍物 / 台阶 / 盒子。
- 修改 reward / obs 等 MDP terms，让 motion 在含物体的场景下被稳定 track。
- 缺点：本质 replay，不是真正的交互式 parkour。

### 路径 B：Velocity-Tracking + Parkour Terrain Curriculum

把 parkour 简化为“在带障碍 / 起伏地形上跟踪给定速度指令”。

- 直接复用 Isaac Lab 的 G1 locomotion 配置 [`flat_env_cfg.py`](https://github.com/isaac-sim/IsaacLab/blob/main/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/g1/flat_env_cfg.py)（含 velocity command、reward、push 扰动、PLAY 调试）和对应的 `rough_env_cfg.py`（自带 terrain curriculum + height scanner）。
- 在 `TerrainGeneratorCfg` 里组合 Isaac Lab 自带的子地形 APIs，定义难度递增的 parkour terrain。
- 训练算法直接用 RSL-RL 的 PPO（Isaac Lab 有现成 entrypoint）。
- 进阶一：[Hiking in the Wild](https://project-instinct.github.io/hiking-in-the-wild/)（同样基于 Isaac Lab + G1 + 单阶段 RL，含台阶 / 缝隙 / 平台，含 foothold safety 等机制）。
- 进阶二：加入 AMP/SMP 等 motion prior 以获得更好的姿态、更高的 task 成功率。[MimicKit](https://github.com/xbpeng/MimicKit) 中有相关实现。

### 路径 C：利用 MaskedMimic sparse keypoints

- 用 [ProtoMotions](https://github.com/NVlabs/ProtoMotions)（自带 MaskedMimic、AMP 等实现）。
- 用 MaskedMimic，把 keypoint target 设到多帧之后并更 sparse、远一些，从而达到 parkour 到某一地点的目的。
- 进阶一：Pretrained MaskedMimic checkpoint 可能没有足够强的地形/物体交互能力，可能需要在它的基础上在复杂地形或物体交互上 RL fine-tune。
- 进阶二：把 SMPL-X 换成 G1。ProtoMotions 好像有 G1 checkpoint 了，但是效果大概没有 SMPL-X 好，可以分析原因并重新进行 reward shaping 和 training。
- 进阶三：也可考虑用 [BFM-Zero](https://github.com/LeCAR-Lab/BFM-Zero) 的 goal reaching / reward-optimized inference。同样可能需要 RL fine-tune。

### 路径 D：利用 motion generator（PARC）

- [PARC](https://github.com/mshoe/PARC)：motion-generator + tracker 迭代式扩数据，问题是训练时间可能比较久，工程量较大。
- 进阶：使用 G1 而不是 SMPL-X。

### 路径 E：复现 PHP

- 在 Isaac Lab 中复现 [Perceptive Humanoid Parkour](https://php-parkour.github.io/)
- 难点：未开源，虽然可以基于 BeyondMimic codebase、可以用 RSL-RL distillation runner，但是需要 from scratch 实现 motion matching 等模块。

## 哪些是基础的

1. **跑通 baseline**：能成功训练 / inference，看到训练曲线上升，能 play 出 rollout 视频。
2. **改造场景**：让角色真正在含障碍 / 不平整地面的场景里行动——路径 A 至少摆 ≥2 类 RigidObject；路径 B 至少定义 3 档难度递增的 parkour terrain；路径 C 至少在 1 个含障碍 / 起伏地面的 scene 下完成 inference；路径 D 至少跑通一轮完整的 motion 生成 + 物理 tracking 流程；路径 E 至少能复现一种 motion pattern 的交互式部署（仿真中）。
3. **量化评估**：评估多个指标，例如成功率（到达目标 / 通过指定障碍 / 不跌倒）、（reference motion / velocity）tracking error 等。
4. **对照实验**：至少 2 组 ablation，给出曲线或表格形式的对比。
5. **可视化与归因**：录制 ≥3 段 rollout 视频，其中至少 1 段是失败案例，并在报告里做归因分析。

## 哪些是需要探索的

注：各路径自身已经写出的“进阶”条目也算在内。

- **Reward / termination / obs ablation**：不同的 MDP terms、权重等。
- 不同的 perception，如 height scan vs depth image vs point cloud（lidar）。
- **Task formulation 切换**：路径 B 中把 velocity command 改成 goal-position（navigation 风格），自己设计 reward。
- **Sim-to-sim**：把同一份 policy 在 Isaac Lab 与 MuJoCo / [mjlab](https://github.com/mujocolab/mjlab) 中各跑一次，比较成功率差距。
