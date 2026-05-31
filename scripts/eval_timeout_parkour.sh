#!/usr/bin/env bash
# Run fixed-checkpoint evaluation rollouts and write CSV under results/metrics/.
#
# Usage:
#   bash scripts/eval_timeout_parkour.sh [all|easy|medium|hard ...]
#
# Environment overrides:
#   NUM_EPISODES=100
#   NUM_ENVS=32
#   CHECKPOINT_EASY=/path/to/model.pt
#   CHECKPOINT_MEDIUM=/path/to/model.pt
#   CHECKPOINT_HARD=/path/to/model.pt
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=_env.sh
source "${SCRIPT_DIR}/_env.sh"

usage() {
  cat <<'EOF'
Usage: bash scripts/eval_timeout_parkour.sh [LEVEL ...]

  LEVEL: all | easy | medium | hard  (default: all)

Examples:
  bash scripts/eval_timeout_parkour.sh
  NUM_EPISODES=50 bash scripts/eval_timeout_parkour.sh easy hard
  CHECKPOINT_HARD=/path/to/model.pt bash scripts/eval_timeout_parkour.sh hard
EOF
}

SCRIPT_ARGS=("$@")
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

find_latest_checkpoint() {
  local level="$1"
  local search_root="${HUMANOID_PARKOUR_RUNS_ROOT}/parkour_${level}/logs/rsl_rl/g1_parkour_${level}"
  if [[ ! -d "${search_root}" ]]; then
    return 1
  fi
  # shellcheck disable=SC2012
  ls -1 "${search_root}"/*/model_*.pt 2>/dev/null | sort -V | tail -n 1
}

checkpoint_for_level() {
  local level="$1"
  local var_name="CHECKPOINT_$(echo "${level}" | tr '[:lower:]' '[:upper:]')"
  local manual="${!var_name:-}"
  if [[ -n "${manual}" ]]; then
    echo "${manual}"
    return 0
  fi
  find_latest_checkpoint "${level}"
}

task_for_level() {
  case "$1" in
    easy) echo "Isaac-Velocity-Parkour-G1-Easy-Play-v0" ;;
    medium) echo "Isaac-Velocity-Parkour-G1-Medium-Play-v0" ;;
    hard) echo "Isaac-Velocity-Parkour-G1-Hard-Play-v0" ;;
    *) return 1 ;;
  esac
}

eval_one_level() {
  local level="$1"
  local task ckpt out_csv append_flag

  task="$(task_for_level "${level}")"
  ckpt="$(checkpoint_for_level "${level}" || true)"
  if [[ -z "${ckpt}" ]]; then
    echo "ERROR: no checkpoint found for ${level}" >&2
    exit 1
  fi

  out_csv="${HUMANOID_PARKOUR_ROOT}/results/metrics/parkour_timeout_eval.csv"
  append_flag="--append"

  echo ""
  echo "============================================================"
  echo "  Parkour EVAL — ${level}"
  echo "============================================================"
  echo "Task: ${task}"
  echo "Checkpoint: ${ckpt}"
  echo "Output: ${out_csv}"

  run_isaaclab_entrypoint "${SCRIPT_DIR}/eval_timeout_parkour.py" \
    --task="${task}" \
    --eval_name="parkour_${level}" \
    --checkpoint="${ckpt}" \
    --output_csv="${out_csv}" \
    --num_episodes="${NUM_EPISODES:-100}" \
    --num_envs="${NUM_ENVS:-32}" \
    --headless \
    ${append_flag}

  if ! grep -q "^parkour_${level}," "${out_csv}"; then
    echo "ERROR: evaluation for ${level} did not write a CSV row" >&2
    exit 1
  fi
}

LEVELS=()
resolve_levels LEVELS

activate_conda
ensure_package_installed

# Start from a fresh combined CSV for default/all evaluations.
if [[ ${#LEVELS[@]} -gt 1 ]]; then
  rm -f "${HUMANOID_PARKOUR_ROOT}/results/metrics/parkour_timeout_eval.csv"
fi

for level in "${LEVELS[@]}"; do
  eval_one_level "${level}"
done

echo ""
echo "Parkour evaluation finished: ${LEVELS[*]}"
echo "CSV: ${HUMANOID_PARKOUR_ROOT}/results/metrics/parkour_timeout_eval.csv"
