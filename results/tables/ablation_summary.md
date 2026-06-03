# Ablation summary

Current table combines training-summary metrics with fixed-checkpoint rollout timeout metrics from `results/metrics/parkour_timeout_eval.csv`. Cross-terrain, fixed-row stress, traversal-progress, and obstacle-crossing evidence are summarized below to make the terrain-difficulty ablation reportable as both a training comparison and a generalization comparison.

| Comparison | Run | Mean reward | Fall rate | XY tracking error | Mean episode length | Curriculum level | Notes |
|------------|-----|-------------|-----------|-------------------|---------------------|------------------|-------|
| Baseline terrain | Flat baseline | 28.77 | 0.44% | 0.2087 m/s | 1000.0 | N/A | Official flat G1 velocity task; easiest reference setting |
| Baseline terrain | Rough baseline | 24.01 | 5.41% | 0.3407 m/s | 984.5 | 5.7961 | Official rough G1 velocity task; parent configuration for parkour |
| Parkour difficulty | Easy | 30.70 | 4.00% train / 0.00% eval | 0.3050 train | 983.2 train / 2000.0 eval | 5.7907 | 100.00% rollout timeout; no gap terrain |
| Parkour difficulty | Medium | 20.98 | 6.75% train / 4.69% eval | 0.3590 train | 988.1 train / 1946.0 eval | 5.8001 | 95.31% rollout timeout; adds gaps and higher obstacles |
| Parkour difficulty | Hard | 11.34 | 10.92% train / 12.50% eval | 0.4407 train | 941.7 train / 1810.0 eval | 5.6389 | 87.50% rollout timeout; widest gaps and hardest platforms |

## Interpretation

- Flat to rough validates the environment-complexity effect: rough terrain increases falls and velocity-tracking error.
- Easy to medium to hard acts as a terrain-difficulty ablation over the custom parkour generator.
- Rough, easy, and medium all finish near curriculum level 5.8; hard is lower at 5.6389 under the same 3000-iteration budget.
- The hard tier is the clearest training stress test under a fair 3000-iteration budget: it has the lowest reward, highest fall rate, and weakest rollout timeout among the parkour tiers.

## Cross/stress evidence

| Comparison | Random timeout | Stress timeout | Random progress | Stress progress | Interpretation |
|------------|---------------:|---------------:|----------------:|----------------:|----------------|
| rough -> hard | 29.69% | 31.25% | 29.69% | 31.25% | Rough locomotion does not transfer reliably to hard parkour obstacles |
| easy -> hard | 0.00% | 0.00% | 0.00% | 0.00% | Easy terrain without gaps is insufficient for hard obstacle robustness |
| medium -> hard | 87.50% | 92.19% | 87.50% | 92.19% | Medium is the minimum completed tier that transfers strongly by survival/progress metrics |
| hard -> hard | 95.31% | 95.31% | 95.31% | 95.31% | Hard remains robust under both average and high-row evaluation |
| hard -> rough/easy/medium | >= 96.88% | >= 96.88% | >= 96.88% | >= 96.88% | Hard training transfers downward to easier or parent terrains |

## Obstacle crossing stress evidence

| Comparison | Obstacle pass | Gap pass | Stairs pass | Fall before obstacle | Interpretation |
|------------|--------------:|---------:|------------:|---------------------:|----------------|
| rough -> hard | 25.00% | 7.89% | 90.00% | 64.58% | Rough can sometimes handle stairs but fails hard gaps early |
| easy -> hard | 0.00% | 0.00% | 0.00% | 89.66% | Easy has no usable hard obstacle transfer |
| medium -> hard | 65.79% | 33.33% | 95.00% | 31.58% | Medium transfers to hard stairs but not reliably to hard gaps |
| hard -> hard | 100.00% | 100.00% | 100.00% | 0.00% | Hard solves supported hard gap/stairs boundaries in the official stress protocol |
| hard -> medium | 87.50% | 66.67% | 100.00% | 9.38% | Hard transfers back to medium but remains less perfect on medium gaps than on hard gaps under sampled coverage |

## Reporting conclusion

The completed formal ablation is the terrain-difficulty ablation. It shows a monotonic increase in training difficulty from easy to medium to hard. Cross-terrain evaluation adds stronger evidence that obstacle exposure matters: easy is stable but narrow, medium is the first tier with strong survival/progress transfer to hard, and hard is the best current source checkpoint for a generalist policy.

Timeout and traversal-progress results are almost identical. The largest timeout-progress gap is 1.56 percentage points, so traversal progress should be reported as a forward-distance sanity check. The obstacle crossing stress metric adds the missing terrain-aware interpretation: medium-to-hard is mostly a hard-gap failure, while hard-to-hard reaches 100.00% on supported hard gap/stairs boundaries.

## MDP ablation (reward shaping)

The MDP ablation tests two lightweight reward terms added on top of the upstream G1 velocity-tracking rewards:

| Term | Weight | What it does |
|------|--------|---------------|
| `parkour_progress` | +0.5 | Reward world-x forward velocity, clamped to [0, 0.75] |
| `foothold_safety` | −0.2 | Penalize foot sliding, support drop (proxy for edge/gap stepping), and bilateral contact height mismatch |

Two pairs are compared, each at 3000 iterations (`model_2999.pt`):

- **Rough Baseline** (official rough terrain, upstream rewards only) vs **Rough MDP** (same terrain + MDP rewards)
- **Hard Baseline** (hard parkour terrain, `G1ParkourRewards` = upstream + `parkour_progress`) vs **Hard MDP** (same terrain + `G1ParkourMDPRewards` = upstream + `parkour_progress` + `foothold_safety`)

Note: Hard Baseline already includes `parkour_progress` because all parkour tier configs use `G1ParkourRewards`. The Hard Baseline → Hard MDP comparison therefore isolates the effect of adding `foothold_safety`.

### Timeout comparison

**Random cross-terrain:**

| Source | → rough | → easy | → medium | → hard |
|---|---:|---:|---:|---:|
| rough | 95.31% | 98.44% | 68.75% | 29.69% |
| rough_mdp | 100.00% | 100.00% | 76.56% | 70.31% |
| Δ | +4.69 | +1.56 | +7.81 | **+40.62** |
| hard | 100.00% | 100.00% | 96.88% | 95.31% |
| hard_mdp | 100.00% | 100.00% | 96.88% | 92.19% |
| Δ | 0.00 | 0.00 | 0.00 | −3.12 |

**Fixed-row stress (row 9):**

| Source | → rough | → easy | → medium | → hard |
|---|---:|---:|---:|---:|
| rough | 98.44% | 78.12% | 56.25% | 31.25% |
| rough_mdp | 98.44% | 100.00% | 92.19% | 70.31% |
| Δ | 0.00 | **+21.88** | **+35.94** | **+39.06** |
| hard | 100.00% | 100.00% | 96.88% | 95.31% |
| hard_mdp | 100.00% | 100.00% | 98.44% | 96.88% |
| Δ | 0.00 | 0.00 | +1.56 | +1.57 |

### Obstacle crossing comparison (stress)

**Obstacle pass rate:**

| Source | → rough | → easy | → medium | → hard |
|---|---:|---:|---:|---:|
| rough | 88.46% | 88.46% | 16.39% | 25.00% |
| rough_mdp | 100.00% | 100.00% | 77.78% | 41.03% |
| Δ | +11.54 | +11.54 | **+61.39** | +16.03 |
| hard | 100.00% | 100.00% | 87.50% | 100.00% |
| hard_mdp | 100.00% | 100.00% | 100.00% | 100.00% |
| Δ | 0.00 | 0.00 | **+12.50** | 0.00 |

**Gap pass rate:**

| Source | → medium | → hard |
|---|---:|---:|
| rough | 0.00% | 7.89% |
| rough_mdp | 50.00% | 21.43% |
| Δ | **+50.00** | +13.54 |
| hard | 66.67% | 100.00% |
| hard_mdp | 100.00% | 100.00% |
| Δ | **+33.33** | 0.00 |

**Stairs pass rate:**

| Source | → rough | → easy | → medium | → hard |
|---|---:|---:|---:|---:|
| rough | 88.46% | 88.46% | 100.00% | 90.00% |
| rough_mdp | 100.00% | 100.00% | 100.00% | 90.91% |
| Δ | +11.54 | +11.54 | 0.00 | +0.91 |
| hard | 100.00% | 100.00% | 100.00% | 100.00% |
| hard_mdp | 100.00% | 100.00% | 100.00% | 100.00% |
| Δ | 0.00 | 0.00 | 0.00 | 0.00 |

**Fall before obstacle rate (lower is better):**

| Source | → medium | → hard |
|---|---:|---:|
| rough | 70.49% | 64.58% |
| rough_mdp | 19.44% | 51.28% |
| Δ | **−51.05** | −13.30 |
| hard | 9.38% | 0.00% |
| hard_mdp | 0.00% | 0.00% |
| Δ | −9.38 | 0.00 |

### Velocity tracking error comparison (random, lower is better)

| Source | → rough | → easy | → medium | → hard |
|---|---:|---:|---:|---:|
| rough | 1.5554 | 1.9577 | 1.4882 | 1.0139 |
| rough_mdp | 1.1698 | 1.5782 | 1.1140 | 1.1079 |
| Δ | −0.39 | −0.38 | −0.37 | +0.09 |
| hard | 1.5013 | 2.0220 | 1.2949 | 1.4965 |
| hard_mdp | 0.9978 | 1.6108 | 0.8473 | 0.7741 |
| Δ | **−0.50** | −0.41 | **−0.45** | **−0.72** |

### Mean forward distance comparison (stress, meters)

| Source | → rough | → easy | → medium | → hard |
|---|---:|---:|---:|---:|
| rough | 35.83 | 31.38 | 23.26 | 13.22 |
| rough_mdp | 35.81 | 46.37 | 43.52 | 32.75 |
| Δ | −0.02 | **+14.99** | **+20.26** | **+19.53** |
| hard | 36.68 | 44.14 | 43.18 | 41.24 |
| hard_mdp | 33.85 | 34.56 | 33.29 | 33.32 |
| Δ | −2.83 | −9.58 | −9.89 | −7.92 |

### MDP ablation conclusions

1. **Rough Baseline → Rough MDP is the largest effect.** On hard terrain, timeout rate increases from 29.69% to 70.31% (+40.62pp random) and from 31.25% to 70.31% (+39.06pp stress). Fall rate on hard drops from 70.31% to 29.69%. The MDP rewards teach basic obstacle competence even though rough_mdp was never exposed to parkour terrain during training — it only saw the official rough terrain generator. Medium stress timeout improves from 56.25% to 92.19% (+35.94pp), and obstacle pass rate on medium jumps from 16.39% to 77.78% (+61.39pp), driven primarily by gap pass rate going from 0.00% to 50.00%. Forward distance on hard stress more than doubles (13.22m → 32.75m, +148%).

2. **Hard Baseline → Hard MDP shows precision gains at a speed cost.** Timeout rates are near ceiling for both (≥92.19% across all eval envs), so the comparison is dominated by secondary metrics. Velocity tracking error drops consistently (−0.41 to −0.72 m/s across all eval envs), with the largest improvement on hard (−0.72, a 48% reduction). Medium obstacle pass rate reaches 100% (from 87.50%), driven by gap pass improvement from 66.67% to 100%. However, mean forward distance decreases by 7.92–9.89 m in stress mode, indicating that `foothold_safety` produces a more conservative gait — more precise foot placement at the cost of raw forward speed.

3. **`parkour_progress` alone is already strong.** Hard Baseline (which includes `parkour_progress` but not `foothold_safety`) reaches ≥95.31% timeout and 100% obstacle pass on hard. The additional gain from `foothold_safety` is concentrated in tracking precision and gap crossing on medium terrain.

4. **The Rough MDP policy approaches Medium Baseline competence without parkour terrain exposure.** Rough MDP → hard timeout (70.31% random, 70.31% stress) falls between rough baseline (29.69%) and medium baseline (87.50%) on hard. Its obstacle pass on hard (41.03%) also sits between rough (25.00%) and medium (65.79%). This confirms that reward shaping alone can extract transferable locomotion skills from non-parkour terrain.
