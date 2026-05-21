# Copyright (c) Humanoid Parkour Course Project.
# SPDX-License-Identifier: BSD-3-Clause

"""Metrics exported to ``results/metrics/*.csv`` for the final report."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class EpisodeMetrics:
    """Per-episode statistics."""

    success: bool
    fell: bool
    velocity_tracking_error: float
    terrain_level: int
    episode_length: int


def compute_episode_metrics(
    *,
    success: bool,
    fell: bool,
    velocity_tracking_error: float,
    terrain_level: int,
    episode_length: int,
) -> EpisodeMetrics:
    """Build metrics for one finished episode."""
    return EpisodeMetrics(
        success=success,
        fell=fell,
        velocity_tracking_error=velocity_tracking_error,
        terrain_level=terrain_level,
        episode_length=episode_length,
    )


def aggregate_run_metrics(episodes: list[EpisodeMetrics]) -> dict[str, Any]:
    """Aggregate a list of episodes into report-ready scalars."""
    if not episodes:
        return {
            "success_rate": 0.0,
            "fall_rate": 0.0,
            "mean_velocity_tracking_error": 0.0,
            "mean_episode_length": 0.0,
            "pass_rate_by_level": {},
        }
    n = len(episodes)
    success_rate = sum(e.success for e in episodes) / n
    fall_rate = sum(e.fell for e in episodes) / n
    mean_vte = sum(e.velocity_tracking_error for e in episodes) / n
    mean_len = sum(e.episode_length for e in episodes) / n

    by_level: dict[int, list[bool]] = {}
    for e in episodes:
        by_level.setdefault(e.terrain_level, []).append(e.success)
    pass_rate_by_level = {lvl: sum(s) / len(s) for lvl, s in by_level.items()}

    return {
        "success_rate": success_rate,
        "fall_rate": fall_rate,
        "mean_velocity_tracking_error": mean_vte,
        "mean_episode_length": mean_len,
        "pass_rate_by_level": pass_rate_by_level,
        "num_episodes": n,
    }


def metrics_to_csv_row(aggregated: dict[str, Any], run_name: str) -> dict[str, Any]:
    """Flatten aggregates for CSV export."""
    return {"run_name": run_name, **aggregated}
