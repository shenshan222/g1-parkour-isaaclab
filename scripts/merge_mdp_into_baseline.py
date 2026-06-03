#!/usr/bin/env python3
# Copyright (c) Humanoid Parkour Course Project.
# SPDX-License-Identifier: BSD-3-Clause

"""Merge separate MDP ablation CSVs into the main cross-terrain result CSVs."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

SOURCE_ORDER = ("rough", "easy", "medium", "hard", "rough_mdp", "hard_mdp")
EVAL_ORDER = ("rough", "easy", "medium", "hard")

MERGE_SPECS = (
    (
        "timeout_cross_terrain_eval.csv",
        ("mdp_ablation_timeout_eval.csv", "hard_mdp_ablation_timeout_eval.csv"),
    ),
    (
        "timeout_cross_terrain_stress_eval.csv",
        ("mdp_ablation_timeout_stress_eval.csv", "hard_mdp_ablation_timeout_stress_eval.csv"),
    ),
    (
        "traversal_progress_cross_terrain_eval.csv",
        ("mdp_ablation_progress_eval.csv", "hard_mdp_ablation_progress_eval.csv"),
    ),
    (
        "traversal_progress_cross_terrain_stress_eval.csv",
        ("mdp_ablation_progress_stress_eval.csv", "hard_mdp_ablation_progress_stress_eval.csv"),
    ),
    (
        "obstacle_crossing_cross_terrain_stress_eval.csv",
        ("mdp_ablation_obstacle_stress_eval.csv", "hard_mdp_ablation_obstacle_stress_eval.csv"),
    ),
)


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def _union_fields(field_groups: list[list[str]]) -> list[str]:
    fields: list[str] = []
    for group in field_groups:
        for field in group:
            if field not in fields:
                fields.append(field)
    return fields


def _sort_key(row: dict[str, str]) -> tuple[int, int, str]:
    source = row.get("checkpoint_source", "")
    eval_env = row.get("eval_env", "")
    source_idx = SOURCE_ORDER.index(source) if source in SOURCE_ORDER else len(SOURCE_ORDER)
    eval_idx = EVAL_ORDER.index(eval_env) if eval_env in EVAL_ORDER else len(EVAL_ORDER)
    return source_idx, eval_idx, row.get("run_name", "")


def _merge_one(metrics_dir: Path, output_name: str, input_names: tuple[str, ...]) -> int:
    output_path = metrics_dir / output_name
    if not output_path.exists():
        raise FileNotFoundError(f"Missing baseline CSV: {output_path}")

    field_groups: list[list[str]] = []
    all_rows: list[dict[str, str]] = []

    base_fields, base_rows = _read_csv(output_path)
    field_groups.append(base_fields)
    all_rows.extend(row for row in base_rows if row.get("checkpoint_source") not in {"rough_mdp", "hard_mdp"})

    for input_name in input_names:
        input_path = metrics_dir / input_name
        if not input_path.exists():
            raise FileNotFoundError(f"Missing MDP CSV: {input_path}")
        fields, rows = _read_csv(input_path)
        field_groups.append(fields)
        all_rows.extend(rows)

    fields = _union_fields(field_groups)
    all_rows.sort(key=_sort_key)

    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in all_rows:
            writer.writerow({field: row.get(field, "") for field in fields})

    return len(all_rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics_dir", type=Path, default=Path("results/metrics"))
    args = parser.parse_args()

    for output_name, input_names in MERGE_SPECS:
        row_count = _merge_one(args.metrics_dir, output_name, input_names)
        print(f"Merged {output_name}: {row_count} rows")


if __name__ == "__main__":
    main()
