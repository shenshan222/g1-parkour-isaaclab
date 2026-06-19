#!/usr/bin/env bash
# Run fixed-row stress evaluation for height-scanner ablation checkpoints.
#
# This evaluates no-height-scan policies on no-height-scan play envs whose
# terrain presets match rough/easy/medium/hard. The CSV keeps eval_env as the
# terrain label so rows can be compared directly with scanner-enabled stress CSVs.
#
# Usage:
#   bash scripts/eval_height_scanner_ablation_stress.sh [--metric timeout|progress|obstacle] [all|SOURCE [EVAL_ENV]]
#
# SOURCE: rough_no_height_scan | hard_no_height_scan
# EVAL_ENV: rough | easy | medium | hard
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=_env.sh
source "${SCRIPT_DIR}/_env.sh"

SOURCES_ORDER=(rough_no_height_scan hard_no_height_scan)
EVAL_ORDER=(rough easy medium hard)
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

case "${EVAL_METRIC}" in
  timeout)
    OUT_CSV="${HEIGHT_SCANNER_ABLATION_TIMEOUT_CSV:-${HUMANOID_PARKOUR_ROOT}/results/metrics/height_scanner_ablation_timeout_stress_eval.csv}"
    ;;
  progress)
    OUT_CSV="${HEIGHT_SCANNER_ABLATION_PROGRESS_CSV:-${HUMANOID_PARKOUR_ROOT}/results/metrics/height_scanner_ablation_progress_stress_eval.csv}"
    ;;
  obstacle)
    OUT_CSV="${HEIGHT_SCANNER_ABLATION_OBSTACLE_CSV:-${HUMANOID_PARKOUR_ROOT}/results/metrics/height_scanner_ablation_obstacle_stress_eval.csv}"
    ;;
esac

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
Usage: bash scripts/eval_height_scanner_ablation_stress.sh [--metric timeout|progress|obstacle] [all|SOURCE [EVAL_ENV]]

  SOURCE: rough_no_height_scan | hard_no_height_scan
  EVAL_ENV: rough | easy | medium | hard
  Metric can also be set with EVAL_METRIC=timeout|progress|obstacle.

  "all" selects both no-height-scan sources and rough/easy/medium/hard eval terrains.

Examples:
  bash scripts/eval_height_scanner_ablation_stress.sh --metric timeout all
  bash scripts/eval_height_scanner_ablation_stress.sh --metric progress rough_no_height_scan all
  NUM_EPISODES=4 NUM_ENVS=4 bash scripts/eval_height_scanner_ablation_stress.sh --metric obstacle hard_no_height_scan hard

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
  CHECKPOINT_ROUGH_NO_HEIGHT_SCAN=/path/to/model.pt
  CHECKPOINT_HARD_NO_HEIGHT_SCAN=/path/to/model.pt
  HEIGHT_SCANNER_ABLATION_TIMEOUT_CSV=/path/to/timeout.csv
  HEIGHT_SCANNER_ABLATION_PROGRESS_CSV=/path/to/progress.csv
  HEIGHT_SCANNER_ABLATION_OBSTACLE_CSV=/path/to/obstacle.csv
EOF
}

is_source() {
  case "$1" in
    rough_no_height_scan | hard_no_height_scan) return 0 ;;
    *) return 1 ;;
  esac
}

is_eval_env() {
  case "$1" in
    rough | easy | medium | hard) return 0 ;;
    *) return 1 ;;
  esac
}

find_latest_checkpoint() {
  local source="$1" search_root selected
  local candidates=()
  selected=""
  case "${source}" in
    rough_no_height_scan)
      search_root="${HUMANOID_PARKOUR_RUNS_ROOT}/rough_no_height_scan/logs/rsl_rl/g1_rough_no_height_scan"
      ;;
    hard_no_height_scan)
      search_root="${HUMANOID_PARKOUR_RUNS_ROOT}/parkour_hard_no_height_scan/logs/rsl_rl/g1_parkour_hard_no_height_scan"
      ;;
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
  local source="$1" var_name manual
  var_name="CHECKPOINT_$(echo "${source}" | tr '[:lower:]' '[:upper:]')"
  manual="${!var_name:-}"
  if [[ -n "${manual}" ]]; then
    echo "${manual}"
    return 0
  fi
  find_latest_checkpoint "${source}"
}

task_for_env() {
  case "$1" in
    rough) echo "Isaac-Velocity-Rough-G1-NoHeightScan-Play-v0" ;;
    easy) echo "Isaac-Velocity-Parkour-G1-Easy-NoHeightScan-Play-v0" ;;
    medium) echo "Isaac-Velocity-Parkour-G1-Medium-NoHeightScan-Play-v0" ;;
    hard) echo "Isaac-Velocity-Parkour-G1-Hard-NoHeightScan-Play-v0" ;;
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
      _sources=("${SOURCES_ORDER[@]}")
      _envs=("${EVAL_ORDER[@]}")
      ;;
    1)
      case "${SCRIPT_ARGS[0]}" in
        all)
          _sources=("${SOURCES_ORDER[@]}")
          _envs=("${EVAL_ORDER[@]}")
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
          _envs=("${EVAL_ORDER[@]}")
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
        _envs=("${EVAL_ORDER[@]}")
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

run_name_for_pair() {
  if [[ "${EVAL_METRIC}" == "timeout" ]]; then
    echo "height_scan_ablation_stress_${STRESS_MODE}_$1_to_$2"
  elif [[ "${EVAL_METRIC}" == "progress" ]]; then
    echo "height_scan_ablation_progress_stress_${STRESS_MODE}_$1_to_$2"
  else
    echo "height_scan_ablation_obstacle_stress_${STRESS_MODE}_$1_to_$2"
  fi
}

eval_one_pair() {
  local source="$1" eval_env="$2" task ckpt run_name
  local stress_col_arg
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
  echo "  ${EVAL_METRIC} height-scanner ablation STRESS EVAL - ${run_name}"
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
echo "${EVAL_METRIC} height-scanner ablation stress evaluation finished."
echo "CSV: ${OUT_CSV}"
