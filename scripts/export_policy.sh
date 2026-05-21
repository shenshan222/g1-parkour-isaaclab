#!/usr/bin/env bash
# Export trained policy for deployment or sim-to-sim (placeholder).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=_env.sh
source "${SCRIPT_DIR}/_env.sh"
activate_conda

CHECKPOINT="${CHECKPOINT:-${HUMANOID_PARKOUR_RUNS_ROOT}/parkour/model_3000.pt}"
EXPORT_DIR="${EXPORT_DIR:-${HUMANOID_PARKOUR_RUNS_ROOT}/exports/parkour}"

mkdir -p "${EXPORT_DIR}"
echo "Export stub: copy or torch.jit export from ${CHECKPOINT} -> ${EXPORT_DIR}"
echo "Add export script when policy format is finalized."
