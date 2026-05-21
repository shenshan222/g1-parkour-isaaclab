#!/usr/bin/env bash
# Train official Isaac Lab flat G1 baseline for comparison.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=_env.sh
source "${SCRIPT_DIR}/_env.sh"
activate_conda
ensure_package_installed

TASK="Isaac-Velocity-Flat-G1-v0"
LOG_DIR="${HUMANOID_PARKOUR_RUNS_ROOT}/flat_baseline"
mkdir -p "${LOG_DIR}"
# Isaac Lab writes to {cwd}/logs/rsl_rl/<experiment_name>/ (no --log_root flag).
cd "${LOG_DIR}"

python "${ISAACLAB_TRAIN}" \
  --task="${TASK}" \
  --headless

echo "Logs under: ${LOG_DIR}/logs/rsl_rl/"
