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

- 增加 `scripts/eval_timeout_parkour.py` 和 `scripts/eval_timeout_parkour.sh`。
- evaluation 逻辑：
  - 加载固定 checkpoint；
  - 在对应 `*-Play-v0` 环境中 rollout；
  - 收集固定数量 episode；
  - 统计 timeout rate、fall rate、episode length、velocity tracking error。
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
  - `results/metrics/parkour_timeout_eval.csv`
- 使用命令：
  - `NUM_EPISODES=64 NUM_ENVS=32 bash scripts/eval_timeout_parkour.sh all`
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
  - 扩展 `scripts/eval_timeout_parkour.py`，加入 `checkpoint_source`、`eval_env`、terrain grid override、terrain sampling 和 seed 等 CSV 元数据；
  - 新增 `scripts/eval_timeout_cross_terrain.sh`，统一运行 rough / easy / medium / hard checkpoint 到 rough / easy / medium / hard eval env 的 4x4 矩阵；
  - 新增 `scripts/summarize_timeout_cross_terrain_eval.py`，从 CSV 生成 4x4 Markdown 表格。
- 正式 evaluation 设置：
  - `NUM_EPISODES=64`；
  - `NUM_ENVS=32`；
  - `SEED=42`；
  - eval terrain grid：`10x10`；
  - terrain sampling：`random_uniform_difficulty`；
  - curriculum disabled。
- 输出文件：
  - `results/metrics/timeout_cross_terrain_eval.csv`；
  - `results/tables/timeout_cross_terrain_summary.md`；
- Timeout rate 结果：

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
  - 输出独立文件 `results/metrics/timeout_cross_terrain_stress_eval.csv`，避免覆盖 random cross-eval 主结果。
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

- 现有 `parkour_timeout_eval.csv` 是 diagonal self-evaluation：
  - easy checkpoint eval easy；
  - medium checkpoint eval medium；
  - hard checkpoint eval hard。
- 它不能回答 cross-terrain generalization。
- success 定义仍是 timeout without base contact，不能说明是否语义上通过了某个 gap / stairs / platform。
- 目前还没有 generalist policy，也还没有多专家蒸馏。
- MDP 仍继承 rough locomotion，没有正式加入 parkour-specific reward。

## 下一步计划

1. 实现 fixed-row stress evaluation：
   - 扩展 `scripts/eval_timeout_parkour.py`，支持固定 terrain row / optional fixed column；
   - 新增 `scripts/eval_timeout_cross_terrain_stress.sh`；
   - 默认使用 `terrain_fixed_row=9`、`NUM_EPISODES=64`、`NUM_ENVS=32`、`SEED=42`；
   - 输出 `results/metrics/timeout_cross_terrain_stress_eval.csv` 和对应 4x4 Markdown 表格。
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

## 2026-06-01：完成 Traversal Progress Evaluation 并统一评估入口

- 在 timeout cross/stress 结构基础上实现 traversal progress evaluation。
- Progress pass 定义为：未发生 base-contact fall，且 `max_forward_distance_m >= 4.0`。
- Strong progress pass 定义为：未发生 base-contact fall，且 `max_forward_distance_m >= 6.0`。
- 正式 progress evaluation 与 timeout 严格对齐，只保留 4x4 random cross-terrain 和 4x4 fixed-row stress 两类结果，不再保留 diagonal progress 表和 episode-level 明细表。
- 正式输出文件：
  - `results/metrics/traversal_progress_cross_terrain_eval.csv`
  - `results/metrics/traversal_progress_cross_terrain_stress_eval.csv`
  - `results/tables/traversal_progress_cross_terrain_summary.md`
  - `results/tables/traversal_progress_cross_terrain_stress_summary.md`
- Progress random cross-terrain 主要结果：

| Checkpoint source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| rough | 95.31% | 98.44% | 68.75% | 29.69% |
| easy | 89.06% | 100.00% | 50.00% | 0.00% |
| medium | 98.44% | 98.44% | 95.31% | 87.50% |
| hard | 100.00% | 100.00% | 96.88% | 95.31% |

- Progress fixed-row stress 主要结果：

| Checkpoint source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| rough | 98.44% | 78.12% | 56.25% | 31.25% |
| easy | 93.75% | 98.44% | 64.06% | 0.00% |
| medium | 95.31% | 100.00% | 100.00% | 92.19% |
| hard | 100.00% | 100.00% | 96.88% | 95.31% |

- 随后将 timeout 与 progress 的 cross/stress rollout 脚本合并：
  - 新增 `scripts/eval_parkour_rollout.py` 作为统一底层 evaluator；
  - 新增 `scripts/eval_cross_terrain.sh`，通过 `--metric timeout|progress` 控制输出 timeout 或 progress CSV；
  - 新增 `scripts/eval_cross_terrain_stress.sh`，通过 `--metric timeout|progress` 控制 stress evaluation；
  - 删除旧的 cross/stress 分离 wrapper：`eval_timeout_cross_terrain*.sh` 和 `eval_traversal_progress_cross_terrain*.sh`；
  - 保留 `eval_timeout_parkour.py` / `eval_timeout_parkour.sh`，因为 diagonal timeout self-evaluation 仍是正式链路的一部分。
- 当前解释：traversal progress metrics 与 timeout metrics 在 cross/stress 结构上完全对齐，但衡量对象不同。timeout 衡量 survival-style locomotion robustness；progress pass 进一步要求策略在未摔倒前达到最小前进距离阈值。

## 2026-06-02：完成结果分析与消融实验整理

- 基于现有正式结果完成报告型分析整理，不新增训练或 Isaac Sim evaluation。
- 新增 `results/tables/generalization_analysis.md`：统一解释 timeout random、timeout stress、traversal progress random、traversal progress stress 四组 4x4 结果。
- 新增 `results/tables/timeout_vs_progress_delta.md`：计算 `timeout_rate - progress_pass_rate`，确认当前最大差值只有 `1.56%`，且仅出现在 easy-to-rough。
- 扩展 `results/tables/ablation_summary.md` 和 `configs/ablations/terrain_ablation.md`：把 terrain difficulty ablation 从训练指标对比升级为训练指标、diagonal rollout、cross-terrain、stress、progress 共同支撑的结论。
- 更新 `report/final_report.md`：新增 cross-terrain generalization 分析，明确 easy 稳定但泛化窄、medium 是最小 strong hard-transfer tier、hard 是当前最强 generalist source。
- 更新 `docs/evaluation.md` 和 `README.md`：加入新增分析表入口。
- 重要解释：traversal progress 仍是 forward-distance proxy，不是 terrain-aware obstacle-boundary crossing；当时还缺少逐障碍通过率，后续已通过 obstacle crossing stress evaluation 补上 base-level gap/stairs boundary metric。

## 2026-06-02：实现 Obstacle Crossing Evaluation

- 新增正式 obstacle crossing evaluation，作为 timeout/progress 之后的第三类 cross/stress evaluation metric。
- `scripts/eval_parkour_rollout.py` 支持 `--metric obstacle`，并在 obstacle 模式下使用 deterministic terrain columns，以保证 terrain column 与 gap/stairs 类型映射可靠。
- `scripts/eval_cross_terrain.sh` 与 `scripts/eval_cross_terrain_stress.sh` 支持 `--metric timeout|progress|obstacle`。
- 新增 `humanoid_parkour/evaluation/obstacle_crossing.py` 和 `scripts/summarize_obstacle_crossing_eval.py`。
- 正式 success 定义：未发生 base-contact fall，且 base 跨过 gap 或 stairs 的几何边界。
- Gap boundary 使用中心平台远侧 gap 边界加 margin；stairs boundary 使用前向外侧 stair-field 边界。
- CSV 输出字段包括 `obstacle_pass_rate`、`gap_pass_rate`、`stairs_pass_rate`、`fall_before_obstacle_rate`、`boundary_coverage`。
- 解释边界：该指标是 base-level geometry-boundary obstacle crossing，不是 foot-contact-level verification；boxes/rough/slope 不纳入正式 obstacle pass aggregation。
- 已完成静态检查和最小 smoke 检查；正式 4x4 obstacle stress evaluation 已在下一条日志中完成。



## 2026-06-02：完成正式 Obstacle Crossing Stress Evaluation

- 先运行 hard-to-hard smoke：`NUM_EPISODES=4 NUM_ENVS=4 SEED=42 bash scripts/eval_cross_terrain_stress.sh --metric obstacle hard hard`，并显式指定 rough/easy/medium/hard checkpoint，确认 hard 使用的是 `2026-05-26_20-22-02/model_2999.pt`，没有误用 smoke training 产生的 `model_0.pt`。
- 随后运行正式 4x4 fixed-row stress obstacle evaluation：`NUM_EPISODES=64 NUM_ENVS=32 SEED=42 bash scripts/eval_cross_terrain_stress.sh --metric obstacle all`。
- 正式输出：
  - `results/metrics/obstacle_crossing_cross_terrain_stress_eval.csv`
  - `results/tables/obstacle_crossing_cross_terrain_stress_summary.md`
- 完整性检查：CSV 共 16 行，rough/easy/medium/hard 的 source-env pair 全部覆盖；checkpoint 字段未出现 `model_0.pt`。
- 关键结论：
  - hard -> hard: obstacle/gap/stairs pass 全部为 `100.00%`；
  - medium -> hard: obstacle pass `65.79%`，stairs pass `95.00%`，但 gap pass 只有 `33.33%`；
  - easy -> hard: obstacle/gap/stairs pass 均为 `0.00%`；
  - rough -> hard: aggregate obstacle pass `25.00%`，主要来自 stairs，gap pass 只有 `7.89%`。
- 解释：timeout/progress 证明 medium 已有较强 hard survival transfer，但 obstacle crossing 进一步说明 medium 的短板集中在 hard gap crossing；hard checkpoint 则已经在官方 hard gap/stairs stress protocol 下形成明确优势。
- 后续优先级调整：重写 MDP 的紧迫性下降；更有汇报价值的方向是 foothold safety、contact-aware crossing、OOD obstacle layouts，以及 AMP/SMP motion prior。

## 2026-06-03：实现并修正 MDP 消融任务

- 根据课程进阶一参考 Hiking in the Wild 的 foothold safety 思想，实现一版贴合本项目的轻量 MDP ablation。
- 设计约束：
  - 不新增独立 hiking task；
  - 不改 obstacle / terrain generator 主体；
  - 不引入 depth camera、foot volume points、AMP 或 motion reference；
  - 复用现有 `rough_mdp` 与 `hard_mdp` 两个任务承载 MDP 改动。
- 新增任务与评估入口：
  - `Isaac-Velocity-Rough-G1-MDP-v0` / `Isaac-Velocity-Rough-G1-MDP-Play-v0`；
  - `Isaac-Velocity-Parkour-G1-Hard-MDP-v0` / `Isaac-Velocity-Parkour-G1-Hard-MDP-Play-v0`；
  - `Isaac-Velocity-Parkour-G1-ExtremeRandom-Play-v0` 作为 evaluation-only OOD stress terrain。
- 新增 `scripts/train_mdp_ablation.sh`，支持 `rough`、`hard`、`all`，日志目录分别为：
  - `/root/autodl-tmp/humanoid_parkour_runs/rough_mdp/logs/rsl_rl/g1_rough_mdp/`；
  - `/root/autodl-tmp/humanoid_parkour_runs/parkour_hard_mdp/logs/rsl_rl/g1_parkour_hard_mdp/`。
- 扩展 `scripts/eval_cross_terrain.sh` 与 `scripts/eval_cross_terrain_stress.sh`：
  - `all` 默认仍只覆盖 rough/easy/medium/hard；
  - 显式支持 source `rough_mdp` / `hard_mdp`；
  - 显式支持 eval env `extreme`；
  - MDP 结果写入 `results/metrics/mdp_ablation_*`，ExtremeRandom 结果按 metric 写入 `extreme_random_*`，避免污染原 official CSV。
- 第一个 MDP 版本包含 `parkour_progress`、`foothold_safety` 和 `termination_fall`。
- 早期 rough_mdp 训练到约 396 iteration 时 `mean_episode_length` 仍约 `5.02`，判断 `termination_fall` 过早截断探索，停止该 run，不作为正式结果。
- 随后移除 `termination_fall`，保留 reward-only MDP：
  - `parkour_progress`：奖励世界 x 方向前进；
  - `foothold_safety`：基于已有 ankle contact 与 body state 的轻量落脚安全 cost，惩罚脚接触滑移、疑似踩空/边缘支撑、双脚接触高度差过大。
- 移除 `termination_fall` 后的 smoke test 通过：Termination Manager 只剩 `time_out` 与 `base_contact`，Reward Manager 包含 `parkour_progress` 与 `foothold_safety`。
- Rough-MDP 正式 3000 iteration 训练已完成：
  - checkpoint：`/root/autodl-tmp/humanoid_parkour_runs/rough_mdp/logs/rsl_rl/g1_rough_mdp/2026-06-03_11-40-18/model_2999.pt`。
- Rough-MDP 与 rough baseline 对齐的 timeout/progress/stress evaluation 正在运行。当前只应记录”评估进行中”，不要在评估 CSV 完成前写入最终结论。
- 注意：多个 smoke run 产生了 `model_0.pt`，正式评估必须使用 `model_2999.pt`；eval 脚本已优先选择 `model_2999.pt` 并跳过自动选择 `model_0.pt`。

## 2026-06-03：完成 Hard-MDP 训练

- Hard-MDP 正式 3000 iteration 训练已完成：
  - checkpoint：`/root/autodl-tmp/humanoid_parkour_runs/parkour_hard_mdp/logs/rsl_rl/g1_parkour_hard_mdp/2026-06-03_14-56-13/model_2999.pt`。
- Hard-MDP 继承 hard parkour terrain（`PARKOUR_HARD_TERRAINS_CFG`），使用 `G1ParkourMDPRewards`（upstream + `parkour_progress` + `foothold_safety`）。
- 与 hard baseline 的关键区别：hard baseline 已包含 `parkour_progress`（通过 `G1ParkourRewards`），Hard-MDP 在此基础上额外增加 `foothold_safety`（weight −0.2）。

## 2026-06-03：完成 MDP 消融正式评估

- 对 rough_mdp 和 hard_mdp 两个 checkpoint（均为 `model_2999.pt`）完成完整的 timeout/progress/obstacle cross 与 stress evaluation。
- 评估覆盖 4×4 矩阵（source × eval env），source 包括 rough_baseline、rough_mdp、hard_baseline、hard_mdp；eval env 包括 rough、easy、medium、hard。
- 正式输出文件：
  - `results/metrics/mdp_ablation_timeout_eval.csv`
  - `results/metrics/mdp_ablation_progress_eval.csv`
  - `results/metrics/mdp_ablation_timeout_stress_eval.csv`
  - `results/metrics/mdp_ablation_progress_stress_eval.csv`
  - `results/metrics/mdp_ablation_obstacle_stress_eval.csv`
- 新增 `scripts/merge_mdp_into_baseline.py`，将 MDP 消融 CSV 按 metric 与 mode 合并到对应的 baseline 4×4 CSV，使 baseline 表中包含 `rough_mdp` 和 `hard_mdp` 行。
- 更新 `results/tables/ablation_summary.md`：从训练指标对比升级为覆盖 timeout、progress、obstacle crossing、velocity tracking error、forward distance 的完整 MDP 消融分析。
- Rough Baseline → Rough MDP 是最大效应：hard terrain timeout 从 29.69% → 70.31%（+40.62pp random），hard stress 从 31.25% → 70.31%（+39.06pp），fall rate 减半，medium gap pass 从 0% → 50%。
- Hard Baseline → Hard MDP 展示精度-vs-速度权衡：timeout 已近天花板，主要收益在 velocity tracking error 降低（−0.4 到 −0.7 m/s）和 medium obstacle pass 达到 100%，但 forward distance 下降 8–10 m（`foothold_safety` 导致更保守的步态）。
- Rough-MDP 在无 parkour terrain 暴露的情况下，hard timeout 已接近 medium baseline 水平，说明 reward shaping 能从非 parkour 地形提取可迁移的 locomotion skills。

## 2026-06-03：生成 MDP 训练曲线与消融对比图

- 新增 `scripts/generate_figures.py`，从 TensorBoard event files 读取数据并生成 6 张图。
- 个体训练曲线（4 张）：
  - `results/figures/rough_mdp_episode_length.png` — rough_mdp 训练 episode length 曲线
  - `results/figures/rough_mdp_mean_reward.png` — rough_mdp 训练 mean reward 曲线
  - `results/figures/parkour_hard_mdp_episode_length.png` — hard_mdp 训练 episode length 曲线
  - `results/figures/parkour_hard_mdp_mean_reward.png` — hard_mdp 训练 mean reward 曲线
- 消融对比图（2 张），每张 2×2 布局（baseline vs MDP × mean_reward vs episode_length）：
  - `results/figures/mdp_ablation_rough_comparison.png` — Rough Baseline vs Rough MDP 并排对比
  - `results/figures/mdp_ablation_hard_comparison.png` — Hard Baseline（仅前 3000 步，不含 resume） vs Hard MDP 并排对比
- 数据来源：直接读取 `$HUMANOID_PARKOUR_RUNS_ROOT` 下的 TensorBoard event files，不依赖训练脚本或额外数据采集。

## 2026-06-03：同步 README 与工作日志

- 更新 README.md / README.zh.md：将 Hard-MDP 状态从 pending 更新为已完成，补充 checkpoint 路径、新增 metrics 文件、figures 目录和 `generate_figures.py` 脚本入口。
- 更新 WORK_LOG.md：补录 Hard-MDP 训练、MDP 评估完成、CSV 合并、ablation summary 升级、figure generation 等条目。
- 更新 CLAUDE.md：将 `check_obstacle_passed` 从 "planned for future work" 更新为 deprecated stub，说明 obstacle passing 已在评估端全覆盖、hard checkpoint 已达 100% obstacle pass，无需训练期 reward。

## 2026-06-03：仓库清理

- 删除 `outputs/`：106 个废弃 Hydra 配置日志目录（4.6 MB），均为训练启动时自动生成的配置快照，不含训练数据。
- 删除 `configs/` 整个目录：包含 4 个早期实验记录文件（`flat_baseline.md`、`rough_baseline.md`、`parkour_curriculum.md`、`terrain_ablation.md`），其内容已全部被 WORK_LOG、CLAUDE.md 和 results/tables 覆盖。
- 同步更新 README.md / README.zh.md 仓库结构图，移除 `configs/` 条目。

## 2026-06-03：清理过时计划

- 确认不再需要 multi-teacher distillation / generalist 策略：hard checkpoint 在所有 eval 环境（rough/easy/medium/hard）上 timeout ≥ 95.31%、obstacle pass ≥ 87.50%，已经是事实上的 generalist。蒸馏一个混合专家只会引入不必要的复杂度，且存在 capacity trade-off 导致性能下降的风险。
- 确认 `check_obstacle_passed` stub 无实现价值：obstacle crossing evaluation 已在评估端完整运行（geometry-boundary gap/stairs pass/fail），hard checkpoint 在 hard 地形上 obstacle/gap/stairs pass 全部 100%。训练期加入 obstacle-passed reward/termination 从经验看（参考 `termination_fall`）更可能破坏训练稳定性。
- 当前项目剩余可推进方向调整为：
  1. 报告撰写与最终定稿；
  2. ExtremeRandom OOD 压力测试（`Isaac-Velocity-Parkour-G1-ExtremeRandom-Play-v0` 已注册，可做系统性 4×4 evaluation）；
  3. 仓库清理（废弃 smoke run 的 `model_0.pt`、统一 figure 命名等）。


## 2026-06-04：完成 ExtremeRandom OOD 压力测试

- 根据 `/root/Eval.md` 的计划，完成 `hard` 与 `hard_mdp` 两个 checkpoint 在 `Isaac-Velocity-Parkour-G1-ExtremeRandom-Play-v0` 上的附加 OOD stress 对比。
- 评估不并入正式 4×4 矩阵，只写入独立 CSV：
  - `results/metrics/extreme_random_timeout_stress_eval.csv`
  - `results/metrics/extreme_random_progress_stress_eval.csv`
  - `results/metrics/extreme_random_obstacle_stress_eval.csv`
- 协议保持与 fixed-row stress 一致：`NUM_EPISODES=64`、`NUM_ENVS=32`、`SEED=42`、`STRESS_ROW=9`、`STRESS_MODE=max`。
- 主要结果：
  - timeout/progress：hard 为 `90.62%`，hard_mdp 为 `95.31%`；
  - obstacle pass：hard 为 `21.43%`，hard_mdp 为 `51.22%`；
  - fall-before-obstacle：hard 为 `57.14%`，hard_mdp 为 `31.71%`。
- 解释：Hard-MDP 在更极端的随机障碍分布下更稳，尤其 stairs crossing 明显提升；同时平均最大前进距离低于 hard，延续了 `foothold_safety` 带来的保守性与稳定性权衡。
- 同步更新 README.md、README.zh.md、report/final_report.md 和 CLAUDE.md。暂未新增独立汇总表，保留三个原始 CSV 作为结果入口。
