#!/usr/bin/env bash
# Shared environment for all Humanoid Parkour scripts.
# Source from other scripts: source "$(dirname "$0")/_env.sh"

set -euo pipefail

SCRIPT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

: "${ISAACLAB_ROOT:=/root/autodl-tmp/isaac_workspace/IsaacLab}"
: "${HUMANOID_PARKOUR_ROOT:=${SCRIPT_ROOT}}"
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

python_bin() {
  if [[ -n "${CONDA_PREFIX:-}" && -x "${CONDA_PREFIX}/bin/python" ]]; then
    echo "${CONDA_PREFIX}/bin/python"
  elif [[ -x "${CONDA_ENV}/bin/python" ]]; then
    echo "${CONDA_ENV}/bin/python"
  else
    command -v python
  fi
}

ensure_package_installed() {
  "$(python_bin)" -m pip install -e "${HUMANOID_PARKOUR_ROOT}" -q
}

run_isaaclab_entrypoint() {
  local entry_script="$1"
  shift
  "$(python_bin)" - "${entry_script}" "$@" <<'PY'
import runpy
import sys
from pathlib import Path

entry_script = sys.argv[1]
entry_args = sys.argv[2:]
sys.argv = [entry_script, *entry_args]
sys.path.insert(0, str(Path(entry_script).resolve().parent))

# Register Gym tasks before Isaac Lab resolves task id (import tasks only, not top-level humanoid_parkour).
import humanoid_parkour.tasks.g1_parkour  # noqa: F401

runpy.run_path(entry_script, run_name="__main__")
PY
}
