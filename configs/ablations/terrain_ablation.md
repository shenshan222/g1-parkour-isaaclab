# Terrain difficulty comparison

This is the completed ablation-style comparison used in the report. It varies terrain complexity while keeping the task family, robot, and PPO setup fixed.

| Setting | Terrain source | Role |
|---------|----------------|------|
| Flat baseline | Official Isaac Lab G1 flat task | Easy reference |
| Rough baseline | Official Isaac Lab G1 rough task | Parent configuration and rough-terrain reference |
| Parkour easy | `PARKOUR_EASY_TERRAINS_CFG` | Structured terrain without gaps |
| Parkour medium | `PARKOUR_MEDIUM_TERRAINS_CFG` | Adds gaps and larger obstacles |
| Parkour hard | `PARKOUR_HARD_TERRAINS_CFG` | Widest gaps, higher obstacles, narrower platforms |

Primary outputs:

- Training summaries: `results/metrics/flat_baseline.csv`, `results/metrics/rough_baseline.csv`, `results/metrics/parkour_training_summary.csv`
- Rollout evaluation: `results/metrics/parkour_timeout_eval.csv`
- Cross/stress timeout metrics: `results/metrics/timeout_cross_terrain_eval.csv`, `results/metrics/timeout_cross_terrain_stress_eval.csv`
- Cross/stress traversal-progress metrics: `results/metrics/traversal_progress_cross_terrain_eval.csv`, `results/metrics/traversal_progress_cross_terrain_stress_eval.csv`
- Report tables: `results/tables/ablation_summary.md`, `results/tables/generalization_analysis.md`, `results/tables/timeout_vs_progress_delta.md`

The comparison table also reports final curriculum terrain level where applicable; flat terrain has no terrain curriculum.

## Current conclusion

The ablation supports three reportable findings:

- Easy terrain is stable but narrow: it reaches 100.00% diagonal timeout, but easy-to-hard is 0.00% in both random and fixed-row stress evaluation.
- Medium is the minimum completed parkour tier with strong hard transfer: medium-to-hard reaches 87.50% random timeout and 92.19% stress timeout.
- Hard is the best current source checkpoint for generalization: it reaches at least 95.31% timeout and progress pass across rough/easy/medium/hard evaluation.

Traversal progress is kept as a forward-distance proxy. Because timeout-progress deltas are at most 1.56 percentage points in the current result set, it should not be framed as a terrain-aware obstacle-boundary metric.
