#!/usr/bin/env bash
# Run cross-terrain evaluation rollouts with timeout, progress, or obstacle metrics.
#
# Usage:
#   bash scripts/eval_cross_terrain.sh [--metric timeout|progress|obstacle] [all|SOURCE [EVAL_ENV]]
#
# SOURCE: rough | easy | medium | hard | rough_mdp | hard_mdp
# EVAL_ENV: rough | easy | medium | hard | rough_mdp | hard_mdp | extreme
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=_env.sh
source "${SCRIPT_DIR}/_env.sh"

ORDER=(rough easy medium hard)
EVAL_METRIC="${EVAL_METRIC:-timeout}"
SCRIPT_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --metric)
      if [[ $# -lt 2 ]]; then
        echo "ERROR: --metric requires timeout, progress, or obstacle" >&2
        exit 1
      fi
      EVAL_METRIC="$2"
      shift 2
      ;;
    --metric=*)
      EVAL_METRIC="${1#--metric=}"
      shift
      ;;
    *)
      SCRIPT_ARGS+=("$1")
      shift
      ;;
  esac
done

case "${EVAL_METRIC}" in
  timeout | progress | obstacle) ;;
  *)
    echo "ERROR: EVAL_METRIC/--metric must be timeout, progress, or obstacle" >&2
    exit 1
    ;;
esac

if [[ "${EVAL_METRIC}" == "timeout" ]]; then
  OUT_CSV="${CROSS_EVAL_CSV:-${HUMANOID_PARKOUR_ROOT}/results/metrics/timeout_cross_terrain_eval.csv}"
elif [[ "${EVAL_METRIC}" == "progress" ]]; then
  OUT_CSV="${PROGRESS_CROSS_EVAL_CSV:-${HUMANOID_PARKOUR_ROOT}/results/metrics/traversal_progress_cross_terrain_eval.csv}"
else
  OUT_CSV="${OBSTACLE_CROSS_EVAL_CSV:-${HUMANOID_PARKOUR_ROOT}/results/metrics/obstacle_crossing_cross_terrain_eval.csv}"
fi
TERRAIN_NUM_ROWS="${TERRAIN_NUM_ROWS:-10}"
TERRAIN_NUM_COLS="${TERRAIN_NUM_COLS:-10}"
TERRAIN_SAMPLING="${TERRAIN_SAMPLING:-random_uniform_difficulty}"
PASS_DISTANCE_M="${PASS_DISTANCE_M:-4.0}"
STRONG_PASS_DISTANCE_M="${STRONG_PASS_DISTANCE_M:-6.0}"

usage() {
  cat <<'EOF'
Usage: bash scripts/eval_cross_terrain.sh [--metric timeout|progress|obstacle] [all|SOURCE [EVAL_ENV]]

  SOURCE: rough | easy | medium | hard | rough_mdp | hard_mdp
  EVAL_ENV: rough | easy | medium | hard | rough_mdp | hard_mdp | extreme
  Metric can also be set with EVAL_METRIC=timeout|progress|obstacle.

  "all" selects rough/easy/medium/hard and excludes MDP/extreme.

Examples:
  bash scripts/eval_cross_terrain.sh --metric timeout all
  bash scripts/eval_cross_terrain.sh --metric progress all
  bash scripts/eval_cross_terrain.sh --metric obstacle all
  NUM_EPISODES=4 NUM_ENVS=4 bash scripts/eval_cross_terrain.sh --metric progress hard easy
  bash scripts/eval_cross_terrain.sh --metric timeout rough_mdp all
  bash scripts/eval_cross_terrain.sh --metric obstacle hard_mdp extreme

Environment overrides:
  EVAL_METRIC=timeout
  NUM_EPISODES=64
  NUM_ENVS=32
  SEED=42
  TERRAIN_NUM_ROWS=10
  TERRAIN_NUM_COLS=10
  TERRAIN_SAMPLING=random_uniform_difficulty
  CHECKPOINT_ROUGH=/path/to/model.pt
  CHECKPOINT_EASY=/path/to/model.pt
  CHECKPOINT_MEDIUM=/path/to/model.pt
  CHECKPOINT_HARD=/path/to/model.pt
  CHECKPOINT_ROUGH_MDP=/path/to/model.pt
  CHECKPOINT_HARD_MDP=/path/to/model.pt
  MDP_ABLATION_TIMEOUT_CSV=/path/to/mdp_ablation_timeout_eval.csv
  MDP_ABLATION_PROGRESS_CSV=/path/to/mdp_ablation_progress_eval.csv
  MDP_ABLATION_OBSTACLE_CSV=/path/to/mdp_ablation_obstacle_eval.csv
  EXTREME_RANDOM_TIMEOUT_CSV=/path/to/extreme_random_timeout_eval.csv
  EXTREME_RANDOM_PROGRESS_CSV=/path/to/extreme_random_progress_eval.csv
  EXTREME_RANDOM_OBSTACLE_CSV=/path/to/extreme_random_obstacle_eval.csv
EOF
}

is_source() {
  case "$1" in
    rough | easy | medium | hard | rough_mdp | hard_mdp) return 0 ;;
    *) return 1 ;;
  esac
}

is_eval_env() {
  case "$1" in
    rough | easy | medium | hard | rough_mdp | hard_mdp | extreme) return 0 ;;
    *) return 1 ;;
  esac
}

is_mdp_source() {
  case "$1" in
    rough_mdp | hard_mdp) return 0 ;;
    *) return 1 ;;
  esac
}

find_latest_checkpoint() {
  local source="$1" search_root
  local candidates=()
  local selected=""
  case "${source}" in
    rough) search_root="${HUMANOID_PARKOUR_RUNS_ROOT}/rough_baseline/logs/rsl_rl/g1_rough" ;;
    easy | medium | hard) search_root="${HUMANOID_PARKOUR_RUNS_ROOT}/parkour_${source}/logs/rsl_rl/g1_parkour_${source}" ;;
    rough_mdp) search_root="${HUMANOID_PARKOUR_RUNS_ROOT}/rough_mdp/logs/rsl_rl/g1_rough_mdp" ;;
    hard_mdp) search_root="${HUMANOID_PARKOUR_RUNS_ROOT}/parkour_hard_mdp/logs/rsl_rl/g1_parkour_hard_mdp" ;;
    *) return 1 ;;
  esac
  if [[ ! -d "${search_root}" ]]; then
    return 1
  fi

  shopt -s nullglob
  candidates=("${search_root}"/*/model_2999.pt)
  if [[ ${#candidates[@]} -gt 0 ]]; then
    printf '%s\n' "${candidates[@]}" | sort -V | tail -n 1
    return 0
  fi

  candidates=("${search_root}"/*/model_*.pt)
  if [[ ${#candidates[@]} -gt 0 ]]; then
    selected="$(printf '%s\n' "${candidates[@]}" | grep -Ev '/model_0\.pt$' | sort -V | tail -n 1 || true)"
    if [[ -n "${selected}" ]]; then
      echo "${selected}"
      return 0
    fi
  fi
  return 1
}

checkpoint_for_source() {
  local source="$1"
  local var_name="CHECKPOINT_$(echo "${source}" | tr '[:lower:]' '[:upper:]')"
  local manual="${!var_name:-}"
  if [[ -n "${manual}" ]]; then
    echo "${manual}"
    return 0
  fi
  find_latest_checkpoint "${source}"
}

task_for_env() {
  case "$1" in
    rough) echo "Isaac-Velocity-Rough-G1-Play-v0" ;;
    easy) echo "Isaac-Velocity-Parkour-G1-Easy-Play-v0" ;;
    medium) echo "Isaac-Velocity-Parkour-G1-Medium-Play-v0" ;;
    hard) echo "Isaac-Velocity-Parkour-G1-Hard-Play-v0" ;;
    rough_mdp) echo "Isaac-Velocity-Rough-G1-MDP-Play-v0" ;;
    hard_mdp) echo "Isaac-Velocity-Parkour-G1-Hard-MDP-Play-v0" ;;
    extreme) echo "Isaac-Velocity-Parkour-G1-ExtremeRandom-Play-v0" ;;
    *) return 1 ;;
  esac
}

resolve_pairs() {
  local -n _sources=$1
  local -n _envs=$2
  _sources=()
  _envs=()

  case "${#SCRIPT_ARGS[@]}" in
    0)
      _sources=("${ORDER[@]}")
      _envs=("${ORDER[@]}")
      ;;
    1)
      case "${SCRIPT_ARGS[0]}" in
        all)
          _sources=("${ORDER[@]}")
          _envs=("${ORDER[@]}")
          ;;
        -h | --help)
          usage
          exit 0
          ;;
        *)
          if ! is_source "${SCRIPT_ARGS[0]}"; then
            echo "ERROR: unknown source '${SCRIPT_ARGS[0]}'" >&2
            usage >&2
            exit 1
          fi
          _sources=("${SCRIPT_ARGS[0]}")
          _envs=("${ORDER[@]}")
          ;;
      esac
      ;;
    2)
      if ! is_source "${SCRIPT_ARGS[0]}"; then
        echo "ERROR: unknown source '${SCRIPT_ARGS[0]}'" >&2
        usage >&2
        exit 1
      fi
      if [[ "${SCRIPT_ARGS[1]}" == "all" ]]; then
        _envs=("${ORDER[@]}")
      elif is_eval_env "${SCRIPT_ARGS[1]}"; then
        _envs=("${SCRIPT_ARGS[1]}")
      else
        echo "ERROR: unknown eval env '${SCRIPT_ARGS[1]}'" >&2
        usage >&2
        exit 1
      fi
      _sources=("${SCRIPT_ARGS[0]}")
      ;;
    *)
      echo "ERROR: expected zero, one, or two positional arguments" >&2
      usage >&2
      exit 1
      ;;
  esac
}

_detect_output_csv() {
  local e s
  for e in "${EVAL_ENVS[@]}"; do
    if [[ "${e}" == "extreme" ]]; then
      case "${EVAL_METRIC}" in
        timeout) OUT_CSV="${EXTREME_RANDOM_TIMEOUT_CSV:-${HUMANOID_PARKOUR_ROOT}/results/metrics/extreme_random_timeout_eval.csv}" ;;
        progress) OUT_CSV="${EXTREME_RANDOM_PROGRESS_CSV:-${HUMANOID_PARKOUR_ROOT}/results/metrics/extreme_random_progress_eval.csv}" ;;
        obstacle) OUT_CSV="${EXTREME_RANDOM_OBSTACLE_CSV:-${HUMANOID_PARKOUR_ROOT}/results/metrics/extreme_random_obstacle_eval.csv}" ;;
      esac
      return 0
    fi
  done
  for s in "${SOURCES[@]}"; do
    if is_mdp_source "${s}"; then
      case "${EVAL_METRIC}" in
        timeout) OUT_CSV="${MDP_ABLATION_TIMEOUT_CSV:-${HUMANOID_PARKOUR_ROOT}/results/metrics/mdp_ablation_timeout_eval.csv}" ;;
        progress) OUT_CSV="${MDP_ABLATION_PROGRESS_CSV:-${HUMANOID_PARKOUR_ROOT}/results/metrics/mdp_ablation_progress_eval.csv}" ;;
        obstacle) OUT_CSV="${MDP_ABLATION_OBSTACLE_CSV:-${HUMANOID_PARKOUR_ROOT}/results/metrics/mdp_ablation_obstacle_eval.csv}" ;;
      esac
      return 0
    fi
  done
}

run_name_for_pair() {
  if [[ "${EVAL_METRIC}" == "timeout" ]]; then
    echo "$1_to_$2"
  elif [[ "${EVAL_METRIC}" == "progress" ]]; then
    echo "progress_$1_to_$2"
  else
    echo "obstacle_$1_to_$2"
  fi
}

eval_one_pair() {
  local source="$1" eval_env="$2" task ckpt run_name
  task="$(task_for_env "${eval_env}")"
  ckpt="$(checkpoint_for_source "${source}" || true)"
  if [[ -z "${ckpt}" ]]; then
    echo "ERROR: no checkpoint found for source '${source}'" >&2
    echo "Set CHECKPOINT_$(echo "${source}" | tr '[:lower:]' '[:upper:]') to evaluate an explicit checkpoint." >&2
    exit 1
  fi
  run_name="$(run_name_for_pair "${source}" "${eval_env}")"

  echo ""
  echo "============================================================"
  echo "  ${EVAL_METRIC} cross-terrain EVAL - ${run_name}"
  echo "============================================================"
  echo "Task: ${task}"
  echo "Checkpoint: ${ckpt}"
  echo "Terrain grid: ${TERRAIN_NUM_ROWS}x${TERRAIN_NUM_COLS}"
  echo "Output: ${OUT_CSV}"

  run_isaaclab_entrypoint "${SCRIPT_DIR}/eval_parkour_rollout.py" \
    --metric="${EVAL_METRIC}" \
    --task="${task}" \
    --eval_name="${run_name}" \
    --checkpoint_source="${source}" \
    --eval_env="${eval_env}" \
    --checkpoint="${ckpt}" \
    --output_csv="${OUT_CSV}" \
    --num_episodes="${NUM_EPISODES:-64}" \
    --num_envs="${NUM_ENVS:-32}" \
    --seed="${SEED:-42}" \
    --terrain_num_rows="${TERRAIN_NUM_ROWS}" \
    --terrain_num_cols="${TERRAIN_NUM_COLS}" \
    --terrain_sampling="${TERRAIN_SAMPLING}" \
    --pass_distance_m="${PASS_DISTANCE_M}" \
    --strong_pass_distance_m="${STRONG_PASS_DISTANCE_M}" \
    --headless \
    --append

  if ! grep -q "^${run_name}," "${OUT_CSV}"; then
    echo "ERROR: evaluation for ${run_name} did not write a CSV row" >&2
    exit 1
  fi
}

SOURCES=()
EVAL_ENVS=()
resolve_pairs SOURCES EVAL_ENVS
_detect_output_csv

activate_conda
ensure_package_installed

if [[ ${#SOURCES[@]} -gt 1 || ${#EVAL_ENVS[@]} -gt 1 ]]; then
  rm -f "${OUT_CSV}"
fi

for source in "${SOURCES[@]}"; do
  for eval_env in "${EVAL_ENVS[@]}"; do
    eval_one_pair "${source}" "${eval_env}"
  done
done

echo ""
echo "${EVAL_METRIC} cross-terrain evaluation finished."
echo "CSV: ${OUT_CSV}"
