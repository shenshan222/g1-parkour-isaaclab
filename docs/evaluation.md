# Evaluation

## Play / record video

```bash
export CHECKPOINT=$HUMANOID_PARKOUR_RUNS_ROOT/parkour/model_3000.pt
bash scripts/play_parkour.sh
```

Save videos to `report/assets/` locally; large files stay out of Git (see `.gitignore`).

## Metrics CSV

```bash
bash scripts/eval_parkour.sh
```

Target output: `results/metrics/parkour_eval.csv`

Implementation uses:

- `humanoid_parkour.evaluation.success_criteria`
- `humanoid_parkour.evaluation.metrics`

## Report figures

Export plots (reward, episode length, success rate) to `results/figures/` for inclusion in `report/final_report.md`.
