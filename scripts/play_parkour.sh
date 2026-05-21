#!/usr/bin/env bash
# Play / record parkour policy. Set CHECKPOINT to a model_*.pt path.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=_env.sh
source "${SCRIPT_DIR}/_env.sh"
activate_conda
ensure_package_installed

TASK="Isaac-Velocity-Parkour-G1-Play-v0"
LOG_DIR="${HUMANOID_PARKOUR_RUNS_ROOT}/parkour"
CHECKPOINT="${CHECKPOINT:-${LOG_DIR}/model_3000.pt}"

python "${ISAACLAB_PLAY}" \
  --task="${TASK}" \
  --checkpoint="${CHECKPOINT}" \
  --num_envs=16

echo "Used checkpoint: ${CHECKPOINT}"
