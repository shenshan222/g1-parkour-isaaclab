# Humanoid Parkour Locomotion for Unitree G1 in Isaac Lab

> Submission-ready draft synchronized with `latex/main.tex`. The LaTeX version is the primary formatted report because the course template is located in `latex/`.

## Abstract

Robust humanoid locomotion over structured obstacles remains difficult because a policy must simultaneously track commands, maintain balance, and handle terrain discontinuities such as stairs, boxes, slopes, and gaps. This project builds a custom parkour-oriented locomotion task for the Unitree G1 robot in Isaac Lab. Starting from the official manager-based G1 rough locomotion task, I implement three increasing parkour terrain tiers, train PPO policies with RSL-RL, and evaluate them with survival, traversal-progress, and geometry-aware obstacle-crossing metrics. The results show a clear terrain difficulty gradient: easy parkour is stable, medium parkour is the first tier that transfers strongly to hard terrain, and hard parkour is the strongest source policy, reaching at least 95.31% timeout rate across rough/easy/medium/hard evaluation environments and 100.00% hard gap/stairs obstacle pass rate under the fixed-row stress protocol. A reward-shaping MDP ablation further shows that adding world-frame progress and foothold-safety terms to rough-terrain training improves hard-terrain timeout rate from 29.69% to 70.31% without any parkour terrain exposure. On hard terrain, the foothold-safety term mainly improves tracking precision and medium-gap crossing at the cost of lower forward speed. An additional ExtremeRandom out-of-distribution stress test confirms the same safety-vs-speed pattern.

## 1. Introduction

Humanoid parkour locomotion requires more than stable flat-ground walking. A useful policy must move over uneven terrain, climb or descend structured height changes, cross gaps, and avoid falls while still obeying a locomotion command. The goal of this project is to build a reproducible parkour-oriented locomotion environment for the Unitree G1 robot in Isaac Lab.

The repository is a compact Isaac Lab task package rather than a fork of Isaac Lab. It stores task registration code, terrain configurations, reward extensions, scripts, result summaries, figures, and this report. Isaac Lab itself remains an external dependency. Large artifacts such as checkpoints, TensorBoard event files, and raw rollout videos are kept outside Git under a separate run-storage root.

Main contributions:

- Three custom parkour terrain tiers for Unitree G1.
- PPO training and play scripts for easy, medium, and hard parkour tasks.
- A unified evaluation pipeline with timeout, traversal-progress, and obstacle-crossing metrics.
- A terrain difficulty ablation across flat, rough, easy, medium, and hard settings.
- A reward-shaping MDP ablation using world-frame progress and foothold-safety rewards.
- An additional ExtremeRandom OOD stress evaluation for hard and hard-MDP policies.

## 2. Method

All custom environments inherit from Isaac Lab's manager-based G1 rough velocity-tracking configuration. This preserves the official G1 robot model, action space, proprioceptive observations, height scan, terrain curriculum machinery, and base-contact failure termination. The policy outputs joint-position targets, and PPO is implemented through RSL-RL.

The parkour task replaces the official rough terrain generator with three custom presets:

| Tier | Terrain design |
|------|----------------|
| Easy | Conservative stairs, box grids, slopes, and rough terrain; no gaps |
| Medium | Higher obstacles and the first gap terrain setting |
| Hard | Taller obstacles, wider gaps, narrower platforms, and stronger terrain variation |

All parkour tiers add a world-frame forward progress reward:

```text
r_progress = clip(0.5 * v_x_world, 0, 0.75)
```

The MDP ablation further adds a foothold-safety cost using ankle contact forces and body-state signals. It penalizes foot sliding while in contact, support points that drop far below the base, and large height mismatch between simultaneously contacting feet.

## 3. Experimental Setup

Completed training runs:

| Experiment | Task family | Iterations |
|------------|-------------|-----------:|
| Flat baseline | Official flat G1 | 1500 |
| Rough baseline | Official rough G1 | 3000 |
| Parkour easy | Custom easy parkour | 3000 |
| Parkour medium | Custom medium parkour | 3000 |
| Parkour hard | Custom hard parkour | 3000 |
| Rough MDP | Rough terrain with MDP rewards | 3000 |
| Hard MDP | Hard parkour with MDP rewards | 3000 |

Evaluation uses three metric families:

- `timeout`: episode reaches timeout without base-contact failure.
- `progress`: no failure and maximum forward distance at least 4 m.
- `obstacle`: no failure and base crosses the generated gap/stairs geometry boundary.

## 4. Results

### 4.1 Reference baselines

| Metric | Flat | Rough |
|------|------:|------:|
| Mean reward | 28.77 | 24.01 |
| Mean episode length | 1000.0 | 984.5 |
| Timeout rate | 99.56% | 94.62% |
| Base-contact failure | 0.44% | 5.41% |
| XY tracking error | 0.2087 m/s | 0.3407 m/s |

The flat baseline verifies the pipeline. The rough baseline is harder but remains stable, confirming that the official rough task is a suitable parent for parkour.

### 4.2 Parkour training

| Metric | Easy | Medium | Hard |
|--------|-----:|-------:|-----:|
| Mean reward | 30.70 | 20.98 | 11.34 |
| Mean episode length | 983.2 | 988.1 | 941.7 |
| Timeout rate | 96.00% | 93.25% | 89.08% |
| Fall rate | 4.00% | 6.75% | 10.92% |
| XY tracking error | 0.3050 | 0.3590 | 0.4407 |
| Yaw tracking error | 0.6067 | 0.8445 | 1.0088 |

The same 3000-iteration budget produces a clear difficulty gradient. Easy remains stable, medium introduces moderate degradation, and hard has the lowest reward, highest fall rate, and largest tracking error.

### 4.3 Cross-terrain generalization

| Source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| Rough | 95.31% | 98.44% | 68.75% | 29.69% |
| Easy | 90.62% | 100.00% | 50.00% | 0.00% |
| Medium | 98.44% | 98.44% | 95.31% | 87.50% |
| Hard | 100.00% | 100.00% | 96.88% | 95.31% |

Rough locomotion and easy parkour do not transfer well to hard parkour. Medium is the first completed tier that transfers strongly to hard, while hard is the strongest source checkpoint.

### 4.4 Obstacle crossing

| Source | Eval hard obstacle pass | Eval hard gap pass | Eval hard stairs pass | Fall before obstacle |
|--------|------------------------:|-------------------:|----------------------:|---------------------:|
| Rough | 25.00% | 7.89% | 90.00% | 64.58% |
| Easy | 0.00% | 0.00% | 0.00% | 89.66% |
| Medium | 65.79% | 33.33% | 95.00% | 31.58% |
| Hard | 100.00% | 100.00% | 100.00% | 0.00% |

Medium-to-hard looks strong under timeout, but hard-gap crossing remains difficult. The hard checkpoint explicitly crosses all supported hard gap and stairs boundaries under the official stress protocol.

## 5. MDP Ablation

| Source | Eval rough | Eval easy | Eval medium | Eval hard |
|---|---:|---:|---:|---:|
| Rough | 95.31% | 98.44% | 68.75% | 29.69% |
| Rough MDP | 100.00% | 100.00% | 76.56% | 70.31% |
| Hard | 100.00% | 100.00% | 96.88% | 95.31% |
| Hard MDP | 100.00% | 100.00% | 96.88% | 92.19% |

The largest effect is from Rough Baseline to Rough MDP. Hard-terrain timeout increases from 29.69% to 70.31%, a gain of 40.62 percentage points, even though the policy has no parkour terrain exposure during training. This indicates that progress and foothold-safety shaping can extract transferable obstacle-competence skills from the official rough terrain distribution.

For Hard Baseline to Hard MDP, timeout rates are already near ceiling, so the main difference appears in secondary metrics. Hard MDP improves velocity tracking precision by approximately 0.41-0.72 m/s across evaluation environments and improves medium obstacle crossing from 87.50% to 100.00%. However, it also reduces mean forward distance by roughly 8-10 m under stress, indicating a safety-vs-speed tradeoff.

## 6. ExtremeRandom OOD Stress

The evaluation-only `Isaac-Velocity-Parkour-G1-ExtremeRandom-Play-v0` environment is used as an additional out-of-distribution stress test. Under this harder random terrain distribution, Hard MDP improves timeout and traversal-progress success from 90.62% to 95.31%, reduces fall rate from 9.38% to 4.69%, and lowers velocity tracking error from 13.2177 to 10.9671. Obstacle pass rises from 21.43% to 51.22%, and fall-before-obstacle decreases from 57.14% to 31.71%.

## 7. Discussion

The results establish a progression from flat locomotion to rough locomotion and then to structured parkour. Easy parkour is stable but narrow: it performs well on its own terrain but fails to transfer to hard. Medium parkour is the minimum completed terrain tier with strong hard-terrain survival transfer, but obstacle crossing reveals that medium still lacks reliable hard-gap competence. Hard parkour is the strongest source policy and fully solves the supported hard gap and stairs boundaries under stress.

The MDP ablation shows that reward design is not only a fine-tuning detail. Rough MDP substantially improves hard-terrain transfer without parkour terrain exposure, suggesting that the inherited velocity-tracking reward alone underuses available terrain information. On hard terrain, the additional foothold-safety cost makes the policy more conservative. This reduces average forward distance but improves tracking precision and out-of-distribution obstacle crossing.

The main limitation is metric semantics. Timeout measures survival, traversal progress checks forward movement, and obstacle crossing checks base-level boundary completion. These are sufficient for the current terrain generator, but they do not directly measure foot-contact quality, exact foothold placement, or mesh-level contact safety.

## 8. Conclusion

This project implements a complete custom parkour locomotion pipeline for Unitree G1 in Isaac Lab. It defines three increasing terrain tiers, trains PPO policies for each tier, evaluates cross-terrain generalization with three metric families, and studies reward-shaping effects through MDP ablations.

Main findings:

- Terrain difficulty increases clearly from easy to medium to hard in reward, fall rate, and tracking error.
- Medium is the first tier with strong survival transfer to hard terrain, but hard-gap crossing remains limited.
- Hard training gives the best overall source checkpoint, reaching at least 95.31% timeout rate across evaluation environments and 100.00% hard gap/stairs obstacle pass under stress.
- MDP reward shaping improves rough-to-hard timeout from 29.69% to 70.31% without parkour terrain exposure.
- Hard MDP improves precision and ExtremeRandom obstacle crossing while adopting a more conservative forward-speed profile.

Together, these results support the feasibility of using Isaac Lab's G1 rough locomotion stack as a base for structured humanoid parkour and provide a reproducible foundation for further navigation-style or foothold-aware extensions.
