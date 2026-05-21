# Copyright (c) Humanoid Parkour Course Project.
# SPDX-License-Identifier: BSD-3-Clause

"""Central path resolution — keeps logs/checkpoints off the Git repo."""

from __future__ import annotations

import os
from pathlib import Path


def get_humanoid_parkour_root() -> Path:
    """Repository root (this package's parent directory)."""
    env = os.environ.get("HUMANOID_PARKOUR_ROOT")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parents[2]


def get_isaaclab_root() -> Path:
    """External Isaac Lab installation (not vendored in this repo)."""
    env = os.environ.get("ISAACLAB_ROOT")
    if not env:
        raise EnvironmentError(
            "Set ISAACLAB_ROOT to your Isaac Lab clone, e.g. "
            "export ISAACLAB_ROOT=/root/autodl-tmp/isaac_workspace/IsaacLab"
        )
    return Path(env).resolve()


def get_runs_root() -> Path:
    """Training logs and checkpoints (gitignored)."""
    default = Path(os.environ.get("RUNS_ROOT", "/root/autodl-tmp/humanoid_parkour_runs"))
    path = Path(os.environ.get("HUMANOID_PARKOUR_RUNS_ROOT", str(default)))
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()


def get_results_root() -> Path:
    """Committed summaries under ``results/`` in the repo."""
    return get_humanoid_parkour_root() / "results"
