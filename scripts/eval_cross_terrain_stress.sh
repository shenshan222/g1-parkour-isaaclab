#!/usr/bin/env bash
# Run fixed-row 4x4 cross-terrain stress evaluation rollouts with timeout or semantic metrics.
#
# Usage:
#   bash scripts/eval_cross_terrain_stress.sh [--metric timeout|semantic] [all|SOURCE [EVAL_ENV]]
#
# SOURCE/EVAL_ENV: rough | easy | medium | hard
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
        echo "ERROR: --metric requires timeout or semantic" >&2
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
  timeout | semantic) ;;
  *)
    echo "ERROR: EVAL_METRIC/--metric must be timeout or semantic" >&2
    exit 1
    ;;
esac

if [[ "${EVAL_METRIC}" == "timeout" ]]; then
  OUT_CSV="${STRESS_EVAL_CSV:-${HUMANOID_PARKOUR_ROOT}/results/metrics/timeout_cross_terrain_stress_eval.csv}"
else
  OUT_CSV="${SEMANTIC_STRESS_EVAL_CSV:-${HUMANOID_PARKOUR_ROOT}/results/metrics/semantic_obstacle_cross_terrain_stress_eval.csv}"
fi
TERRAIN_NUM_ROWS="${TERRAIN_NUM_ROWS:-10}"
TERRAIN_NUM_COLS="${TERRAIN_NUM_COLS:-10}"
TERRAIN_SAMPLING="${TERRAIN_SAMPLING:-fixed_row_all_types}"
STRESS_MODE="${STRESS_MODE:-max}"
STRESS_ROW="${STRESS_ROW:-9}"
STRESS_COL="${STRESS_COL:-}"
PASS_DISTANCE_M="${PASS_DISTANCE_M:-4.0}"
STRONG_PASS_DISTANCE_M="${STRONG_PASS_DISTANCE_M:-6.0}"

usage() {
  cat <<'EOF'
Usage: bash scripts/eval_cross_terrain_stress.sh [--metric timeout|semantic] [all|SOURCE [EVAL_ENV]]

  SOURCE/EVAL_ENV: rough | easy | medium | hard
  Metric can also be set with EVAL_METRIC=timeout|semantic.

Examples:
  bash scripts/eval_cross_terrain_stress.sh --metric timeout all
  bash scripts/eval_cross_terrain_stress.sh --metric semantic all
  NUM_EPISODES=4 NUM_ENVS=4 bash scripts/eval_cross_terrain_stress.sh --metric semantic hard easy

Environment overrides:
  EVAL_METRIC=timeout
  NUM_EPISODES=64
  NUM_ENVS=32
  SEED=42
  TERRAIN_NUM_ROWS=10
  TERRAIN_NUM_COLS=10
  TERRAIN_SAMPLING=fixed_row_all_types
  STRESS_MODE=max
  STRESS_ROW=9
  STRESS_COL=
  STRESS_EVAL_CSV=/path/to/timeout_cross_terrain_stress_eval.csv
  SEMANTIC_STRESS_EVAL_CSV=/path/to/semantic_obstacle_cross_terrain_stress_eval.csv
  PASS_DISTANCE_M=4.0
  STRONG_PASS_DISTANCE_M=6.0
  CHECKPOINT_ROUGH=/path/to/model.pt
  CHECKPOINT_EASY=/path/to/model.pt
  CHECKPOINT_MEDIUM=/path/to/model.pt
  CHECKPOINT_HARD=/path/to/model.pt
EOF
}

is_level() {
  case "$1" in
    rough | easy | medium | hard) return 0 ;;
    *) return 1 ;;
  esac
}

find_latest_checkpoint() {
  local source="$1" search_root
  case "${source}" in
    rough) search_root="${HUMANOID_PARKOUR_RUNS_ROOT}/rough_baseline/logs/rsl_rl/g1_rough" ;;
    easy | medium | hard) search_root="${HUMANOID_PARKOUR_RUNS_ROOT}/parkour_${source}/logs/rsl_rl/g1_parkour_${source}" ;;
    *) return 1 ;;
  esac
  if [[ ! -d "${search_root}" ]]; then
    return 1
  fi
  # shellcheck disable=SC2012
  ls -1 "${search_root}"/*/model_*.pt 2>/dev/null | sort -V | tail -n 1
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
          if ! is_level "${SCRIPT_ARGS[0]}"; then
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
      if ! is_level "${SCRIPT_ARGS[0]}" || ! is_level "${SCRIPT_ARGS[1]}"; then
        echo "ERROR: SOURCE and EVAL_ENV must be one of: ${ORDER[*]}" >&2
        usage >&2
        exit 1
      fi
      _sources=("${SCRIPT_ARGS[0]}")
      _envs=("${SCRIPT_ARGS[1]}")
      ;;
    *)
      echo "ERROR: expected zero, one, or two positional arguments" >&2
      usage >&2
      exit 1
      ;;
  esac
}

run_name_for_pair() {
  if [[ "${EVAL_METRIC}" == "timeout" ]]; then
    echo "stress_${STRESS_MODE}_$1_to_$2"
  else
    echo "semantic_stress_${STRESS_MODE}_$1_to_$2"
  fi
}

eval_one_pair() {
  local source="$1" eval_env="$2" task ckpt run_name
  local stress_col_arg
  task="$(task_for_env "${eval_env}")"
  ckpt="$(checkpoint_for_source "${source}" || true)"
  if [[ -z "${ckpt}" ]]; then
    echo "ERROR: no checkpoint found for source '${source}'" >&2
    exit 1
  fi
  run_name="$(run_name_for_pair "${source}" "${eval_env}")"

  echo ""
  echo "============================================================"
  echo "  ${EVAL_METRIC} cross-terrain STRESS EVAL - ${run_name}"
  echo "============================================================"
  echo "Task: ${task}"
  echo "Checkpoint: ${ckpt}"
  echo "Terrain grid: ${TERRAIN_NUM_ROWS}x${TERRAIN_NUM_COLS}"
  echo "Fixed row: ${STRESS_ROW}"
  echo "Fixed col: ${STRESS_COL:-all terrain-type columns}"
  echo "Output: ${OUT_CSV}"

  stress_col_arg=()
  if [[ -n "${STRESS_COL}" ]]; then
    stress_col_arg=(--terrain_fixed_col="${STRESS_COL}")
  fi

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
    --stress_mode="${STRESS_MODE}" \
    --terrain_fixed_row="${STRESS_ROW}" \
    "${stress_col_arg[@]}" \
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
echo "${EVAL_METRIC} cross-terrain stress evaluation finished."
echo "CSV: ${OUT_CSV}"
