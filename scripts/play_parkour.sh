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
# Default: latest run under logs/rsl_rl (override with CHECKPOINT=.../model_*.pt)
CHECKPOINT="${CHECKPOINT:-}"

PLAY_ARGS=(--task="${TASK}" --num_envs=16)
if [[ -n "${CHECKPOINT}" ]]; then
  PLAY_ARGS+=(--checkpoint="${CHECKPOINT}")
fi

python "${ISAACLAB_PLAY}" "${PLAY_ARGS[@]}"

echo "Used checkpoint: ${CHECKPOINT}"
