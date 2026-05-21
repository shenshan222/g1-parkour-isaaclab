#!/usr/bin/env bash
# Train custom G1 parkour task (requires pip install -e this repo).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=_env.sh
source "${SCRIPT_DIR}/_env.sh"
activate_conda
ensure_package_installed

TASK="Isaac-Velocity-Parkour-G1-v0"
LOG_DIR="${HUMANOID_PARKOUR_RUNS_ROOT}/parkour"
mkdir -p "${LOG_DIR}"
cd "${LOG_DIR}"

python "${ISAACLAB_TRAIN}" \
  --task="${TASK}" \
  --headless

echo "Logs under: ${LOG_DIR}/logs/rsl_rl/"
