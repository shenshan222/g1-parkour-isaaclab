# Copyright (c) Humanoid Parkour Course Project.
# SPDX-License-Identifier: BSD-3-Clause

"""Metrics exported to ``results/metrics/*.csv`` for the final report."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class EpisodeMetrics:
    """Per-episode timeout-evaluation statistics."""

    timeout: bool
    fell: bool
    velocity_tracking_error: float
    episode_length: int


def compute_episode_metrics(
    *,
    timeout: bool,
    fell: bool,
    velocity_tracking_error: float,
    episode_length: int,
) -> EpisodeMetrics:
    """Build metrics for one finished episode."""
    return EpisodeMetrics(
        timeout=timeout,
        fell=fell,
        velocity_tracking_error=velocity_tracking_error,
        episode_length=episode_length,
    )


def aggregate_run_metrics(episodes: list[EpisodeMetrics]) -> dict[str, Any]:
    """Aggregate a list of episodes into report-ready timeout-eval scalars."""
    if not episodes:
        return {
            "timeout_rate": 0.0,
            "fall_rate": 0.0,
            "mean_velocity_tracking_error": 0.0,
            "mean_episode_length": 0.0,
            "num_episodes": 0,
        }
    n = len(episodes)
    timeout_rate = sum(e.timeout for e in episodes) / n
    fall_rate = sum(e.fell for e in episodes) / n
    mean_vte = sum(e.velocity_tracking_error for e in episodes) / n
    mean_len = sum(e.episode_length for e in episodes) / n

    return {
        "timeout_rate": timeout_rate,
        "fall_rate": fall_rate,
        "mean_velocity_tracking_error": mean_vte,
        "mean_episode_length": mean_len,
        "num_episodes": n,
    }


def metrics_to_csv_row(aggregated: dict[str, Any], run_name: str) -> dict[str, Any]:
    """Flatten aggregates for CSV export."""
    return {"run_name": run_name, **aggregated}
