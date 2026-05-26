#!/usr/bin/env bash
# Train G1 parkour velocity task (RSL-RL, headless).
#
# Usage:
#   bash scripts/train_parkour.sh [all|easy|medium|hard ...]
#
# Examples:
#   bash scripts/train_parkour.sh          # same as "all"
#   bash scripts/train_parkour.sh all
#   bash scripts/train_parkour.sh easy
#   bash scripts/train_parkour.sh easy hard
#
# Extra args are forwarded to Isaac Lab train.py (e.g. --max_iterations=1000).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=_env.sh
source "${SCRIPT_DIR}/_env.sh"

usage() {
  cat <<'EOF'
Usage: bash scripts/train_parkour.sh [LEVEL ...] [-- extra train.py args]

  LEVEL: all | easy | medium | hard  (default: all)

Examples:
  bash scripts/train_parkour.sh
  bash scripts/train_parkour.sh all
  bash scripts/train_parkour.sh medium
  bash scripts/train_parkour.sh easy hard -- --max_iterations=2000
EOF
}

# Split script args from args after "--" for train.py
SCRIPT_ARGS=()
TRAIN_EXTRA=()
while [[ $# -gt 0 ]]; do
  if [[ "$1" == "--" ]]; then
    shift
    TRAIN_EXTRA=("$@")
    break
  fi
  SCRIPT_ARGS+=("$1")
  shift
done

resolve_levels() {
  local -n _out=$1
  _out=()
  if [[ ${#SCRIPT_ARGS[@]} -eq 0 ]]; then
    _out=(easy medium hard)
    return 0
  fi
  for arg in "${SCRIPT_ARGS[@]}"; do
    case "${arg}" in
      all)
        _out=(easy medium hard)
        return 0
        ;;
      easy | medium | hard)
        _out+=("${arg}")
        ;;
      -h | --help)
        usage
        exit 0
        ;;
      *)
        echo "ERROR: unknown level '${arg}'" >&2
        usage >&2
        exit 1
        ;;
    esac
  done
}

train_one_level() {
  local level="$1"
  local task log_dir experiment_name

  case "${level}" in
    easy)
      task="Isaac-Velocity-Parkour-G1-Easy-v0"
      experiment_name="g1_parkour_easy"
      ;;
    medium)
      task="Isaac-Velocity-Parkour-G1-Medium-v0"
      experiment_name="g1_parkour_medium"
      ;;
    hard)
      task="Isaac-Velocity-Parkour-G1-Hard-v0"
      experiment_name="g1_parkour_hard"
      ;;
    *)
      echo "ERROR: internal unknown level '${level}'" >&2
      exit 1
      ;;
  esac

  log_dir="${HUMANOID_PARKOUR_RUNS_ROOT}/parkour_${level}"
  mkdir -p "${log_dir}"
  cd "${log_dir}"

  run_isaaclab_entrypoint "${ISAACLAB_TRAIN}" --task="${task}" --headless "${TRAIN_EXTRA[@]}"
  echo "Logs under: ${log_dir}/logs/rsl_rl/${experiment_name}/"
}

LEVELS=()
resolve_levels LEVELS

activate_conda
ensure_package_installed

for level in "${LEVELS[@]}"; do
  echo ""
  echo "============================================================"
  echo "  Parkour TRAIN — ${level}"
  echo "============================================================"
  train_one_level "${level}"
done

echo ""
echo "Parkour training finished: ${LEVELS[*]}"
