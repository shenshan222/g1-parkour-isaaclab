#!/usr/bin/env bash
# Run evaluation rollouts and write CSV under results/metrics/.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=_env.sh
source "${SCRIPT_DIR}/_env.sh"
activate_conda
ensure_package_installed

TASK="Isaac-Velocity-Parkour-G1-Play-v0"
CHECKPOINT="${CHECKPOINT:-${HUMANOID_PARKOUR_RUNS_ROOT}/parkour/model_3000.pt}"
OUT_CSV="${HUMANOID_PARKOUR_ROOT}/results/metrics/parkour_eval.csv"
NUM_EPISODES="${NUM_EPISODES:-100}"

# TODO: add a small Python entry (e.g. scripts/eval_parkour.py) that calls
# humanoid_parkour.evaluation and exports OUT_CSV after play rollouts.
echo "Eval stub: task=${TASK} checkpoint=${CHECKPOINT}"
echo "Target CSV: ${OUT_CSV} (${NUM_EPISODES} episodes)"
echo "Implement eval driver and re-run this script on the training server."
