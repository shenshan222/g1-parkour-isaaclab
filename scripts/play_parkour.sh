#!/usr/bin/env bash
# Play G1 parkour velocity task (visualization / video).
#
# Usage:
#   bash scripts/play_parkour.sh [all|easy|medium|hard ...]
#
# Examples:
#   bash scripts/play_parkour.sh          # same as "all"
#   bash scripts/play_parkour.sh easy
#   bash scripts/play_parkour.sh medium hard
#
# Per-tier checkpoint override:
#   CHECKPOINT_EASY=/path/to/model.pt
#   CHECKPOINT_MEDIUM=...
#   CHECKPOINT_HARD=...
#
# If unset, uses the latest model_*.pt under:
#   $HUMANOID_PARKOUR_RUNS_ROOT/parkour_{level}/logs/rsl_rl/g1_parkour_{level}/
#
# Skip tiers with no checkpoint (default). To fail instead:
#   PARKOUR_PLAY_REQUIRE_CHECKPOINT=1 bash scripts/play_parkour.sh all
#
# Extra args after "--" are forwarded to Isaac Lab play.py.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=_env.sh
source "${SCRIPT_DIR}/_env.sh"

usage() {
  cat <<'EOF'
Usage: bash scripts/play_parkour.sh [LEVEL ...] [-- extra play.py args]

  LEVEL: all | easy | medium | hard  (default: all)

Per-tier checkpoints (optional):
  CHECKPOINT_EASY, CHECKPOINT_MEDIUM, CHECKPOINT_HARD

Examples:
  bash scripts/play_parkour.sh
  bash scripts/play_parkour.sh all
  bash scripts/play_parkour.sh easy
  CHECKPOINT_MEDIUM=/path/to/model.pt bash scripts/play_parkour.sh medium
EOF
}

SCRIPT_ARGS=()
PLAY_EXTRA=()
while [[ $# -gt 0 ]]; do
  if [[ "$1" == "--" ]]; then
    shift
    PLAY_EXTRA=("$@")
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

find_latest_checkpoint() {
  local log_dir="$1"
  local experiment_name="$2"
  local search_root="${log_dir}/logs/rsl_rl/${experiment_name}"
  if [[ ! -d "${search_root}" ]]; then
    return 1
  fi
  # shellcheck disable=SC2012
  ls -1 "${search_root}"/*/model_*.pt 2>/dev/null | sort -V | tail -n 1
}

checkpoint_for_level() {
  local level="$1"
  local log_dir="${HUMANOID_PARKOUR_RUNS_ROOT}/parkour_${level}"
  local experiment_name="g1_parkour_${level}"
  local var_name="CHECKPOINT_$(echo "${level}" | tr '[:lower:]' '[:upper:]')"
  local manual="${!var_name:-}"

  if [[ -n "${manual}" ]]; then
    echo "${manual}"
    return 0
  fi
  find_latest_checkpoint "${log_dir}" "${experiment_name}"
}

play_one_level() {
  local level="$1"
  local task

  case "${level}" in
    easy)
      task="Isaac-Velocity-Parkour-G1-Easy-Play-v0"
      ;;
    medium)
      task="Isaac-Velocity-Parkour-G1-Medium-Play-v0"
      ;;
    hard)
      task="Isaac-Velocity-Parkour-G1-Hard-Play-v0"
      ;;
    *)
      echo "ERROR: internal unknown level '${level}'" >&2
      exit 1
      ;;
  esac

  local ckpt
  ckpt="$(checkpoint_for_level "${level}" || true)"
  if [[ -z "${ckpt}" ]]; then
    if [[ "${PARKOUR_PLAY_REQUIRE_CHECKPOINT:-0}" == "1" ]]; then
      echo "ERROR: no checkpoint for ${level}. Train first: bash scripts/train_parkour.sh ${level}" >&2
      exit 1
    fi
    echo "WARN: no checkpoint for ${level}, skipping play."
    return 0
  fi

  echo "Checkpoint: ${ckpt}"

  local play_args=(--task="${task}" --num_envs=16 --checkpoint="${ckpt}")
  run_isaaclab_entrypoint "${ISAACLAB_PLAY}" "${play_args[@]}" "${PLAY_EXTRA[@]}"
  echo "Task: ${task}"
}

LEVELS=()
resolve_levels LEVELS

activate_conda
ensure_package_installed

for level in "${LEVELS[@]}"; do
  echo ""
  echo "============================================================"
  echo "  Parkour PLAY — ${level}"
  echo "============================================================"
  play_one_level "${level}"
done

echo ""
echo "Parkour play finished: ${LEVELS[*]}"
