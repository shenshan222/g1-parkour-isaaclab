# 项目工作日志

本文档按时间顺序记录项目推进过程、关键发现、修改原因和后续计划。它不是正式报告正文，而是用于组内汇报、实验复盘和后续交接。

## 2026-05-19：确定项目方向与课程路径

- 创建仓库并加入课程项目说明。
- 明确采用课程路径 B：Velocity-Tracking + Parkour Terrain Curriculum。
- 初始目标设定为：基于 Isaac Lab 的 G1 locomotion 任务，复现 flat / rough baseline，再扩展自定义 parkour 地形任务。
- 当时的判断是：先不要从 motion prior 或复杂 imitation 入手，而是优先完成完整的训练、评估、调参、报告闭环。

## 2026-05-21：搭建仓库结构与 baseline 工作流

- 建立外部 Isaac Lab 项目结构：
  - `humanoid_parkour/` 作为可安装 Python 包；
  - `scripts/` 放训练、play、评估 wrapper；
  - `configs/` 放实验设计记录；
  - `results/` 放可提交的小型结果文件；
  - `report/` 放课程报告和素材。
- 增加 flat / rough baseline 训练脚本。
- 修正训练脚本的日志路径处理：Isaac Lab 没有 `--log_root`，所以脚本通过 `cd` 到 run directory，让日志和 checkpoint 写到大盘路径。
- 完成 flat baseline：
  - run id：`2026-05-21_20-36-57`
  - checkpoint：`model_1499.pt`
  - mean reward：`28.77`
  - fall rate：`0.44%`
  - 结论：训练 pipeline 正常，flat locomotion 稳定。
- 完成 rough baseline：
  - run id：`2026-05-21_21-31-41`
  - checkpoint：`model_2999.pt`
  - mean reward：`24.01`
  - fall rate：`5.41%`
  - final curriculum terrain level scalar：`5.7961`
  - 发现：rough 比 flat 明显更难，reward 下降、fall rate 和 tracking error 上升。
- 初步结论：rough baseline 更适合作为 parkour 任务的父配置，因为它已有 terrain curriculum 和 height scanner。

## 2026-05-22：把 baseline 写入报告

- 将 flat / rough baseline 的训练结果、曲线和定量对比写入报告。
- 把 flat 作为 pipeline sanity check，把 rough 作为后续 parkour 的主要 parent configuration。
- 当时报告仍以“baseline 已完成，parkour 任务待实现”为主线。

## 2026-05-25：实现 Parkour Easy 任务雏形

- 新增 G1 parkour easy 相关环境配置。
- 设计第一版 easy parkour terrain，重点包含较保守的台阶、随机 boxes、rough terrain 和 slope。
- 任务仍继承 `G1RoughEnvCfg`，没有重写 reward / observation / termination。
- 设计思路：先验证“替换 terrain generator 后能否继续训练出稳定 policy”。

## 2026-05-26：扩展 Medium / Hard 地形与任务注册

- 增加 parkour medium 和 hard 两档 terrain preset。
- Medium 增加 gap terrain，并提高台阶、boxes、roughness、slope 参数范围。
- Hard 进一步扩大 gap、提高障碍、缩小平台宽度，作为压力测试。
- 形成三个独立任务：
  - `Isaac-Velocity-Parkour-G1-Easy-v0`
  - `Isaac-Velocity-Parkour-G1-Medium-v0`
  - `Isaac-Velocity-Parkour-G1-Hard-v0`
- 每个任务都有对应 `-Play-v0`。
- 重要澄清：当前不是 easy -> medium -> hard 的跨任务 curriculum，而是每个 tier 内部继承 rough 的 terrain-level curriculum。

## 2026-05-26：修正 terrain 与脚本问题

- 多次调整 `parkour_terrain_cfg.py`、训练脚本和报告表述。
- 主要目标是让 easy / medium / hard 的难度递增更清楚：
  - easy：无 gap，障碍较保守；
  - medium：加入 gap 和更高障碍；
  - hard：gap 更宽、平台更窄、障碍更强。
- 发现 hard 地形如果过强，会让 inherited rough MDP 的学习压力明显增大。
- 保留 `mdp_overrides.py` 作为未来工作文件，暂不接入训练。

## 2026-05-26：实现固定 checkpoint evaluation 结构

- 增加 `scripts/eval_parkour.py` 和 `scripts/eval_parkour.sh`。
- evaluation 逻辑：
  - 加载固定 checkpoint；
  - 在对应 `*-Play-v0` 环境中 rollout；
  - 收集固定数量 episode；
  - 统计 success rate、fall rate、timeout rate、episode length、velocity tracking error。
- 成功定义采用：
  - timeout 且没有 base contact；
  - 即 `timeout_without_base_contact`。
- 发现这个 success 只是 locomotion-survival success，不是逐障碍语义通过率。

## 2026-05-26 至 2026-05-27：完成三档 Parkour 训练

- Easy：
  - run id：`2026-05-26_15-58-21`
  - iterations：`3000`
  - checkpoint：`model_2999.pt`
  - mean reward：`30.7019`
  - fall rate：`4.00%`
  - 结论：easy 可稳定训练，甚至 mean reward 高于 rough baseline。
- Medium：
  - run id：`2026-05-26_17-39-43`
  - iterations：`3000`
  - checkpoint：`model_2999.pt`
  - mean reward：`20.9778`
  - fall rate：`6.75%`
  - 结论：加入 gap 后难度明显上升，但整体仍稳定。
- Hard：
  - initial run：`2026-05-26_20-22-02`
  - initial checkpoint：`model_2999.pt`
  - resume run：`2026-05-27_09-47-16`
  - final checkpoint：`model_4498.pt`
  - mean reward：`14.4443`
  - fall rate：`7.27%`
  - 发现：hard 初始训练在 2500-3000 iteration 附近出现 plateau；续训开始时 reward 有明显 drop，之后恢复并小幅提升。
- 解释调整：hard 的问题不只是训练时间不足，更可能说明 inherited rough velocity-tracking MDP 对最难 parkour terrain 不够充分。

## 2026-05-28：整理 Parkour 结果、视频和报告

- 添加 parkour training summary：
  - `results/metrics/parkour_training_summary.csv`
- 添加 fixed-checkpoint rollout evaluation：
  - `results/metrics/parkour_eval.csv`
- 使用命令：
  - `NUM_EPISODES=64 NUM_ENVS=32 bash scripts/eval_parkour.sh all`
- evaluation 结果：
  - Easy success：`100.00%`
  - Medium success：`95.31%`
  - Hard success：`92.19%`
- 添加 rollout 视频素材：
  - flat play；
  - rough play；
  - parkour easy；
  - parkour medium；
  - parkour hard 3000；
  - parkour hard 4500。
- 报告更新为“初版可提交”状态，包含 baseline、terrain design、三档训练结果、rollout evaluation 和视频说明。

## 2026-05-28：清理仓库结构与保留未来工作

- 清理项目结构和提交内容。
- 明确保留两个未来工作文件：
  - `configs/ablations/reward_ablation.md`
  - `humanoid_parkour/tasks/g1_parkour/mdp_overrides.py`
- 理由：
  - reward / observation / termination ablation 尚未正式运行；
  - 进阶一的 foothold safety、forward progress、obstacle-passing metrics 仍计划后续实现。
- 同时清理 `.gitignore`，保留与 Python、Isaac Lab、RSL-RL 训练产物相关的规则。

## 2026-05-28：补充 README 双语入口

- 将默认 `README.md` 改为英文。
- 新增 `README.zh.md` 作为中文入口。
- 后来确认不需要给 `docs/` 全部维护双语版本，因为维护成本较高，且课程仓库以英文默认文档更简洁。

## 2026-05-28：重新解释 Hard 训练曲线

- 发现 `parkour_mean_reward.png` 中 hard 曲线只显示 3000 到 4500 附近。
- 原因：hard 最终结果来自 resume run，图中 hard 曲线主要是续训段。
- 修正报告解释：
  - hard initial run 在 2500-3000 iteration 附近进入 plateau；
  - resume 段开始有 reward drop；
  - 后续只恢复并中等幅度提升。
- 由此强化结论：hard 是当前 inherited rough MDP 的主要压力边界。

## 2026-05-28：讨论消融实验方向

- 最初考虑做进阶一 MDP ablation：
  - forward progress；
  - foothold safety；
  - obstacle-passing metrics。
- 后来调整优先级：
  - 先做不重写 MDP 的 formal ablation；
  - 再做进阶一 MDP 改造。
- 原因：
  - 直接重写 MDP 风险较高；
  - reward scale 和训练稳定性不确定；
  - 当前更需要先形成一版有 formal ablation 的可提交版本。

## 2026-05-28：确定 Cross-Terrain Evaluation 作为下一步主消融

- 讨论后决定做 rough / easy / medium / hard 的 4x4 cross-evaluation。
- 核心问题从“每个环境能否训练出 policy”升级为：
  - 同一个 policy 是否能泛化到其他 terrain distribution？
  - rough checkpoint 是否能 zero-shot transfer 到 parkour？
  - hard checkpoint 是否能向下泛化到 easy / medium？
- 计划中的 evaluation matrix：
  - rows：rough、easy、medium、hard checkpoint；
  - columns：rough、easy、medium、hard eval environment。
- 初始计划使用：
  - `NUM_EPISODES=64`
  - `NUM_ENVS=32`
- 后续进一步讨论后，认为最终 cross-eval 应使用更稳定的 evaluation terrain grid：
  - 原 Play 配置是 5x5 random terrain grid；
  - 5x5 适合 play 和 smoke test，但正式 4x4 表格随机性偏强；
  - 建议正式 cross-eval 使用 10x10、fixed seed、curriculum disabled。

## 2026-05-30：完成 Cross-Terrain Evaluation

- 根据 `Cross_evaluation.md` 完成 4x4 cross-terrain evaluation 工具链。
- 已实现内容：
  - 扩展 `scripts/eval_parkour.py`，加入 `checkpoint_source`、`eval_env`、terrain grid override、terrain sampling 和 seed 等 CSV 元数据；
  - 新增 `scripts/eval_cross_terrain.sh`，统一运行 rough / easy / medium / hard checkpoint 到 rough / easy / medium / hard eval env 的 4x4 矩阵；
  - 新增 `scripts/summarize_cross_terrain_eval.py`，从 CSV 生成 4x4 Markdown 表格。
- 正式 evaluation 设置：
  - `NUM_EPISODES=64`；
  - `NUM_ENVS=32`；
  - `SEED=42`；
  - eval terrain grid：`10x10`；
  - terrain sampling：`random_uniform_difficulty`；
  - curriculum disabled。
- 输出文件：
  - `results/metrics/cross_terrain_eval.csv`；
  - `results/tables/cross_terrain_success_rate.md`；
  - `results/tables/cross_terrain_fall_rate.md`；
  - `results/tables/cross_terrain_tracking_error.md`。
- Success rate 结果：

| Checkpoint source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| rough | 95.31% | 98.44% | 68.75% | 29.69% |
| easy | 90.62% | 100.00% | 50.00% | 0.00% |
| medium | 98.44% | 98.44% | 95.31% | 87.50% |
| hard | 100.00% | 100.00% | 95.31% | 93.75% |

- 主要观察：
  - rough policy 能较好迁移到 easy，但迁移到 hard 明显失败，rough-to-hard success 只有 `29.69%`；
  - easy policy 在 hard eval 上完全失败，说明 easy training 没有学到足够强的 obstacle robustness；
  - medium policy 对 hard 有较强迁移，medium-to-hard success 为 `87.50%`；
  - hard policy 在 rough/easy/medium/hard 上都保持高 success，说明 hard training 学到的策略有较强向下泛化能力。
- 解释注意：
  - 该实验仍使用 `timeout_without_base_contact` 作为 success 定义；
  - cross-eval 衡量的是 survival-style generalization，不是逐障碍语义通过率；
  - 10x10 random grid 是平均泛化测试，不是固定最高难度压力测试。

## 2026-05-30：规划 Fixed-Row Stress Evaluation

- 在 cross-eval 结果符合预期后，决定增加一组压力测试作为补充。
- 目标仍是 4x4 cross evaluation，但不再随机采样 difficulty，而是固定 terrain row。
- 第一版计划：
  - 默认固定 `terrain_fixed_row=9`，即每个 terrain preset 内最高 difficulty index；
  - 不固定 terrain column，让并行 env 继续覆盖不同 terrain type；
  - 输出独立文件 `results/metrics/cross_terrain_stress_eval.csv`，避免覆盖 random cross-eval 主结果。
- 设计定位：
  - random 10x10 cross-eval 用于平均泛化能力分析；
  - fixed-row stress eval 用于边界条件和高难 terrain robustness 分析；
  - stress eval 不替代当前主结果，而是作为后续报告中的补充实验。
- 重要解释：easy / medium / hard 的 row 9 只表示各自 preset 内最高 difficulty index，不代表三者具有相同绝对物理难度。

## 当前关键理解

- 训练时：
  - easy / medium / hard 都开启 terrain curriculum；
  - terrain row 表示该 tier 内部的 difficulty level；
  - curriculum 根据机器人走的距离决定升降级。
- Evaluation 时：
  - 使用 `*-Play-v0`；
  - 关闭 curriculum；
  - 当前 play 配置默认生成 5x5 random terrain grid；
  - 评估是在对应 task 的地形参数范围中随机采样，而不是按 curriculum row 逐级测试。
- `curriculum_terrain_levels` 含义：
  - 是训练中所有并行 env 当前 terrain level 的平均值；
  - 不是所有环境的绝对难度分数；
  - easy / medium / hard 的 level 不能直接跨 tier 比较。

## 当前局限

- 现有 `parkour_eval.csv` 是 diagonal self-evaluation：
  - easy checkpoint eval easy；
  - medium checkpoint eval medium；
  - hard checkpoint eval hard。
- 它不能回答 cross-terrain generalization。
- success 定义仍是 timeout without base contact，不能说明是否语义上通过了某个 gap / stairs / platform。
- 目前还没有 generalist policy，也还没有多专家蒸馏。
- MDP 仍继承 rough locomotion，没有正式加入 parkour-specific reward。

## 下一步计划

1. 实现 fixed-row stress evaluation：
   - 扩展 `scripts/eval_parkour.py`，支持固定 terrain row / optional fixed column；
   - 新增 `scripts/eval_cross_terrain_stress.sh`；
   - 默认使用 `terrain_fixed_row=9`、`NUM_EPISODES=64`、`NUM_ENVS=32`、`SEED=42`；
   - 输出 `results/metrics/cross_terrain_stress_eval.csv` 和对应 4x4 Markdown 表格。
2. 报告中更新 cross-eval 解释：
   - diagonal 表示 specialist self-performance；
   - off-diagonal 表示泛化能力；
   - rough row 表示 rough-to-parkour zero-shot transfer；
   - hard row 表示 hard-to-easier transfer；
   - random cross-eval 是主泛化结果，fixed-row stress eval 是补充压力测试。
3. 后续再考虑：
   - generalist mixed-terrain policy；
   - 利用 rough/easy/medium/hard specialists 做 multi-teacher distillation；
   - 重写 MDP，加入 forward progress、foothold safety 和 obstacle-passing metrics。

## 2026-05-30：切换正式 Hard 结果口径到 3000 轮

- 为保证 easy / medium / hard 的训练预算公平，决定正式结果统一使用 3000 iteration checkpoint。
- hard 正式 checkpoint 改为 initial run：`2026-05-26_20-22-02/model_2999.pt`。
- hard 4500 / resume 训练保留为真实探索流程记录，但不再作为正式对比和报告结论的数据来源。
- 已补跑 hard3000 diagonal self-eval，并用 hard3000 替换正式 cross eval 与 fixed-row stress eval 中的 hard 行。

