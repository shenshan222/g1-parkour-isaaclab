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
- Report table: `results/tables/ablation_summary.md`
