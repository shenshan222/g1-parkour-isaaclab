# Copyright (c) Humanoid Parkour Course Project.
# SPDX-License-Identifier: BSD-3-Clause

"""Geometry-boundary obstacle crossing metrics for gap and stairs terrain."""

from __future__ import annotations

from dataclasses import dataclass

from .traversal_progress import terrain_type_by_column


@dataclass(frozen=True)
class ObstacleBoundaryCriteria:
    """Geometry-boundary settings for obstacle crossing success."""

    boundary_margin_m: float = 0.20
    use_conservative_gap_width: bool = True


OBSTACLE_GROUPS: dict[str, tuple[str, ...]] = {
    "gap": ("gap",),
    "stairs": ("pyramid_stairs", "pyramid_stairs_inv"),
}


def obstacle_group_for_terrain_type(terrain_type: str) -> str:
    """Return the obstacle group used by the official obstacle metric."""
    for group, names in OBSTACLE_GROUPS.items():
        if terrain_type in names:
            return group
    return "unsupported"


def difficulty_from_row(row: int, num_rows: int) -> float:
    """Return a conservative nominal difficulty for a terrain row."""
    if row < 0 or num_rows <= 0:
        return 1.0
    return min(1.0, max(0.0, (row + 1) / num_rows))


def sub_terrain_cfg_for_type(terrain_generator_cfg, terrain_type: str):
    """Return the sub-terrain cfg for a terrain type name, if present."""
    if terrain_generator_cfg is None or not hasattr(terrain_generator_cfg, "sub_terrains"):
        return None
    return terrain_generator_cfg.sub_terrains.get(terrain_type)


def compute_obstacle_boundary_x_m(
    *,
    terrain_type: str,
    sub_terrain_cfg,
    terrain_row: int,
    num_rows: int,
    criteria: ObstacleBoundaryCriteria | None = None,
) -> float | None:
    """Return the local +x pass boundary for gap/stairs terrain, or None if unsupported."""
    c = criteria or ObstacleBoundaryCriteria()
    group = obstacle_group_for_terrain_type(terrain_type)
    if group == "gap":
        if sub_terrain_cfg is None or not hasattr(sub_terrain_cfg, "gap_width_range"):
            return None
        if c.use_conservative_gap_width:
            gap_width = float(sub_terrain_cfg.gap_width_range[1])
        else:
            difficulty = difficulty_from_row(terrain_row, num_rows)
            low, high = sub_terrain_cfg.gap_width_range
            gap_width = float(low + difficulty * (high - low))
        return float(sub_terrain_cfg.platform_width) / 2.0 + gap_width + c.boundary_margin_m
    if group == "stairs":
        if sub_terrain_cfg is None or not hasattr(sub_terrain_cfg, "size"):
            return None
        border_width = float(getattr(sub_terrain_cfg, "border_width", 0.0))
        return float(sub_terrain_cfg.size[0]) / 2.0 - border_width - c.boundary_margin_m
    return None


def evaluate_obstacle_boundary_pass(
    *,
    max_local_x_m: float,
    fell: bool,
    boundary_x_m: float | None,
) -> tuple[bool | None, bool | None]:
    """Return obstacle pass and fall-before-obstacle flags for one episode."""
    if boundary_x_m is None:
        return None, None
    obstacle_pass = (not fell) and max_local_x_m >= boundary_x_m
    fall_before_obstacle = fell and max_local_x_m < boundary_x_m
    return obstacle_pass, fall_before_obstacle
