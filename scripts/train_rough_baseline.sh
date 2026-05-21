#!/usr/bin/env bash
# Train official Isaac Lab rough G1 baseline (terrain curriculum + height scan).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=_env.sh
source "${SCRIPT_DIR}/_env.sh"
activate_conda
ensure_package_installed

TASK="Isaac-Velocity-Rough-G1-v0"
LOG_DIR="${HUMANOID_PARKOUR_RUNS_ROOT}/rough_baseline"

python "${ISAACLAB_TRAIN}" \
  --task="${TASK}" \
  --headless \
  --log_root="${LOG_DIR}"

echo "Logs: ${LOG_DIR}"
