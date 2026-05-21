# Copyright (c) Humanoid Parkour Course Project.
# SPDX-License-Identifier: BSD-3-Clause

"""Definitions of parkour success for consistent experiments across train/eval/report."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ParkourSuccessCriteria:
    """Configurable thresholds for episode success."""

    min_forward_distance_m: float = 2.0
    max_base_tilt_rad: float = 0.8
    max_velocity_tracking_error: float = 0.5
    require_no_fall: bool = True


def evaluate_episode_success(
    *,
    forward_distance_m: float,
    base_tilt_rad: float,
    velocity_tracking_error: float,
    fell: bool,
    criteria: ParkourSuccessCriteria | None = None,
) -> bool:
    """Return True if the episode meets all success conditions."""
    c = criteria or ParkourSuccessCriteria()
    if c.require_no_fall and fell:
        return False
    if forward_distance_m < c.min_forward_distance_m:
        return False
    if base_tilt_rad > c.max_base_tilt_rad:
        return False
    if velocity_tracking_error > c.max_velocity_tracking_error:
        return False
    return True
