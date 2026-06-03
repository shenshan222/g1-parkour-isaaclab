#!/usr/bin/env bash
# Train MDP ablation policies for G1 humanoid parkour (RSL-RL, headless).
#
# Usage:
#   bash scripts/train_mdp_ablation.sh [all|rough|hard ...] [-- extra train.py args]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=_env.sh
source "${SCRIPT_DIR}/_env.sh"

usage() {
  cat <<'EOF'
Usage: bash scripts/train_mdp_ablation.sh [LEVEL ...] [-- extra train.py args]

  LEVEL: all | rough | hard  (default: all)

Examples:
  bash scripts/train_mdp_ablation.sh
  bash scripts/train_mdp_ablation.sh all
  bash scripts/train_mdp_ablation.sh rough
  bash scripts/train_mdp_ablation.sh hard -- --max_iterations=3000
  bash scripts/train_mdp_ablation.sh rough -- --max_iterations=1
EOF
}

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
    _out=(rough hard)
    return 0
  fi
  for arg in "${SCRIPT_ARGS[@]}"; do
    case "${arg}" in
      all)
        _out=(rough hard)
        return 0
        ;;
      rough | hard)
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
    rough)
      task="Isaac-Velocity-Rough-G1-MDP-v0"
      experiment_name="g1_rough_mdp"
      log_dir="${HUMANOID_PARKOUR_RUNS_ROOT}/rough_mdp"
      ;;
    hard)
      task="Isaac-Velocity-Parkour-G1-Hard-MDP-v0"
      experiment_name="g1_parkour_hard_mdp"
      log_dir="${HUMANOID_PARKOUR_RUNS_ROOT}/parkour_hard_mdp"
      ;;
    *)
      echo "ERROR: internal unknown level '${level}'" >&2
      exit 1
      ;;
  esac

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
  echo "  MDP Ablation TRAIN - ${level}"
  echo "============================================================"
  train_one_level "${level}"
done

echo ""
echo "MDP ablation training finished: ${LEVELS[*]}"
