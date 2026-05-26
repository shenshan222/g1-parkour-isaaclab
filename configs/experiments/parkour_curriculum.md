# Parkour curriculum experiment

## Task

- Train: `Isaac-Velocity-Parkour-G1-{Easy,Medium,Hard}-v0`
- Play: `Isaac-Velocity-Parkour-G1-{Easy,Medium,Hard}-Play-v0`

## Terrain levels

| Level | Config symbol | Description |
|-------|---------------|-------------|
| 0 | `PARKOUR_EASY_TERRAINS_CFG` | Stairs, mild slopes |
| 1 | `PARKOUR_MEDIUM_TERRAINS_CFG` | Gaps, platforms |
| 2 | `PARKOUR_HARD_TERRAINS_CFG` | Narrow gaps, high steps |

## Command

```bash
bash scripts/train_parkour.sh
bash scripts/play_parkour.sh all   # or: easy | medium | hard
bash scripts/eval_parkour.sh
```

## Hyperparameters (fill after first run)

| Field | Value |
|-------|-------|
| num_envs | TBD |
| max_iterations | TBD |
| curriculum | terrain row 0 → 2 |
| log_dir | `$HUMANOID_PARKOUR_RUNS_ROOT/parkour` |

## Observations

- Success rate by terrain level: see `results/metrics/parkour_eval.csv`
- Notes: TBD
