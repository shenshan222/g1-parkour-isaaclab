#!/usr/bin/env bash
# Shared environment for all Humanoid Parkour scripts.
# Source from other scripts: source "$(dirname "$0")/_env.sh"

set -euo pipefail

: "${ISAACLAB_ROOT:=/root/autodl-tmp/isaac_workspace/IsaacLab}"
: "${HUMANOID_PARKOUR_ROOT:=$(cd "$(dirname "$0")/.." && pwd)}"
: "${HUMANOID_PARKOUR_RUNS_ROOT:=/root/autodl-tmp/humanoid_parkour_runs}"
# Prefix env (common on AutoDL); override with a conda *name* if you registered one.
: "${CONDA_ENV:=$(dirname "${ISAACLAB_ROOT}")/env_isaaclab}"

export ISAACLAB_ROOT HUMANOID_PARKOUR_ROOT HUMANOID_PARKOUR_RUNS_ROOT
export OMNI_KIT_ALLOW_ROOT=1
# Vulkan ICD — adjust for your GPU driver layout
if [[ -z "${VK_ICD_FILENAMES:-}" ]]; then
  if [[ -f /usr/share/vulkan/icd.d/nvidia_icd.json ]]; then
    export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/nvidia_icd.json
  fi
fi

ISAACLAB_TRAIN="${ISAACLAB_ROOT}/scripts/reinforcement_learning/rsl_rl/train.py"
ISAACLAB_PLAY="${ISAACLAB_ROOT}/scripts/reinforcement_learning/rsl_rl/play.py"

activate_conda() {
  # Already in the target env (path-based installs show up as CONDA_PREFIX, not a name).
  if [[ -n "${CONDA_PREFIX:-}" && "${CONDA_PREFIX}" == "${CONDA_ENV}" ]]; then
    return 0
  fi
  # shellcheck disable=SC1091
  if command -v conda &>/dev/null; then
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate "${CONDA_ENV}"
  fi
}

ensure_package_installed() {
  pip install -e "${HUMANOID_PARKOUR_ROOT}" -q
}
