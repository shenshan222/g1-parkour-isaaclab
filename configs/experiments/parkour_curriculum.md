# Parkour terrain experiment

## Task IDs

- Train: `Isaac-Velocity-Parkour-G1-{Easy,Medium,Hard}-v0`
- Play: `Isaac-Velocity-Parkour-G1-{Easy,Medium,Hard}-Play-v0`

## Terrain tiers

| Tier | Config symbol | Description |
|------|---------------|-------------|
| Easy | `PARKOUR_EASY_TERRAINS_CFG` | Stairs, random boxes, rough terrain, slopes; no gap terrain |
| Medium | `PARKOUR_MEDIUM_TERRAINS_CFG` | Adds gaps and increases obstacle height |
| Hard | `PARKOUR_HARD_TERRAINS_CFG` | Wider gaps, higher obstacles, narrower platforms |

## Training runs

| Tier | Run ID | Iterations | Final checkpoint |
|------|--------|------------|------------------|
| Easy | `2026-05-26_15-58-21` | 3000 | `model_2999.pt` |
| Medium | `2026-05-26_17-39-43` | 3000 | `model_2999.pt` |
| Hard | `2026-05-27_09-47-16` | 4499 | `model_4498.pt` |

Run artifacts are stored under `$HUMANOID_PARKOUR_RUNS_ROOT/parkour_{easy,medium,hard}/logs/rsl_rl/g1_parkour_{easy,medium,hard}/`.

## Evaluation

```bash
NUM_EPISODES=64 NUM_ENVS=32 bash scripts/eval_parkour.sh all
```

Current rollout success rates:

| Tier | Success rate | Fall rate |
|------|--------------|-----------|
| Easy | 100.00% | 0.00% |
| Medium | 95.31% | 4.69% |
| Hard | 92.19% | 7.81% |

Detailed metrics are in `results/metrics/parkour_eval.csv`.
