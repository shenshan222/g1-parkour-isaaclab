#!/usr/bin/env bash
# Run evaluation rollouts and write CSV under results/metrics/.
#
# Usage:
#   bash scripts/eval_parkour.sh [easy|medium|hard]   (default: easy)
#
# Checkpoint: CHECKPOINT_<TIER> or latest under parkour_<tier>/logs/rsl_rl/g1_parkour_<tier>/
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=_env.sh
source "${SCRIPT_DIR}/_env.sh"
activate_conda
ensure_package_installed

LEVEL="${1:-easy}"
case "${LEVEL}" in
  easy)
    TASK="Isaac-Velocity-Parkour-G1-Easy-Play-v0"
  ;;
  medium)
    TASK="Isaac-Velocity-Parkour-G1-Medium-Play-v0"
  ;;
  hard)
    TASK="Isaac-Velocity-Parkour-G1-Hard-Play-v0"
  ;;
  *)
    echo "ERROR: unknown level '${LEVEL}' (use easy, medium, or hard)" >&2
    exit 1
    ;;
esac

LOG_DIR="${HUMANOID_PARKOUR_RUNS_ROOT}/parkour_${LEVEL}"
OUT_CSV="${HUMANOID_PARKOUR_ROOT}/results/metrics/parkour_eval_${LEVEL}.csv"
NUM_EPISODES="${NUM_EPISODES:-100}"

var_name="CHECKPOINT_$(echo "${LEVEL}" | tr '[:lower:]' '[:upper:]')"
CHECKPOINT="${!var_name:-${CHECKPOINT:-}}"

# TODO: add scripts/eval_parkour.py driver; reuse play_parkour.sh checkpoint discovery.
echo "Eval stub: level=${LEVEL} task=${TASK} checkpoint=${CHECKPOINT:-<auto TBD>}"
echo "Log dir: ${LOG_DIR}/logs/rsl_rl/g1_parkour_${LEVEL}/"
echo "Target CSV: ${OUT_CSV} (${NUM_EPISODES} episodes)"
echo "Implement eval driver and re-run this script on the training server."
