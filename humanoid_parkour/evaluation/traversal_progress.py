# Copyright (c) Humanoid Parkour Course Project.
# SPDX-License-Identifier: BSD-3-Clause

"""Helpers for traversal progress evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class _SubTerrainCfg(Protocol):
    proportion: float


class _TerrainGeneratorCfg(Protocol):
    sub_terrains: dict[str, _SubTerrainCfg]


@dataclass(frozen=True)
class TraversalProgressCriteria:
    """Distance thresholds for forward progress success."""

    pass_distance_m: float = 4.0
    strong_pass_distance_m: float = 6.0


def terrain_type_by_column(terrain_cfg: _TerrainGeneratorCfg, num_cols: int) -> list[str]:
    """Map terrain columns to sub-terrain names using Isaac Lab curriculum proportions."""
    if num_cols <= 0:
        raise ValueError("num_cols must be positive.")
    if not terrain_cfg.sub_terrains:
        raise ValueError("terrain_cfg.sub_terrains must not be empty.")

    names = list(terrain_cfg.sub_terrains.keys())
    proportions = [float(cfg.proportion) for cfg in terrain_cfg.sub_terrains.values()]
    total = sum(proportions)
    if total <= 0.0:
        raise ValueError("sum of sub-terrain proportions must be positive.")

    cumulative: list[float] = []
    running = 0.0
    for proportion in proportions:
        running += proportion / total
        cumulative.append(running)

    column_types: list[str] = []
    for col in range(num_cols):
        position = col / num_cols + 0.001
        sub_index = next((idx for idx, upper in enumerate(cumulative) if position < upper), len(names) - 1)
        column_types.append(names[sub_index])
    return column_types


def evaluate_progress_pass(
    *,
    max_forward_distance_m: float,
    fell: bool,
    criteria: TraversalProgressCriteria | None = None,
) -> tuple[bool, bool]:
    """Return progress and strong progress pass flags for one episode."""
    c = criteria or TraversalProgressCriteria()
    progress_pass = (not fell) and max_forward_distance_m >= c.pass_distance_m
    strong_progress_pass = (not fell) and max_forward_distance_m >= c.strong_pass_distance_m
    return progress_pass, strong_progress_pass
