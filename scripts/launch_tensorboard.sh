#!/usr/bin/env bash
# Launch TensorBoard on training logs (gitignored under RUNS_ROOT).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=_env.sh
source "${SCRIPT_DIR}/_env.sh"

PORT="${PORT:-6006}"
LOGDIR="${LOGDIR:-${HUMANOID_PARKOUR_RUNS_ROOT}}"

tensorboard --logdir="${LOGDIR}" --port="${PORT}" --bind_all
echo "TensorBoard: http://localhost:${PORT}  logdir=${LOGDIR}"
