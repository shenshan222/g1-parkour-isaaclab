# Copyright (c) Humanoid Parkour Course Project.
# SPDX-License-Identifier: BSD-3-Clause

"""Parkour terrain presets — three difficulty tiers using Isaac Lab TerrainGeneratorCfg.

Only terrain composition lives here; no reward or training logic.
"""

from __future__ import annotations

# TODO: build from Isaac Lab terrain sub-terrain APIs, e.g.:
# from isaaclab.terrains.config.rough import ROUGH_TERRAINS_CFG
# from isaaclab.terrains import TerrainGeneratorCfg

# Placeholder types until Isaac Lab is importable.
PARKOUR_EASY_TERRAINS_CFG = None
"""Stairs + mild slopes; curriculum row 0."""

PARKOUR_MEDIUM_TERRAINS_CFG = None
"""Gaps, platforms, mixed roughness; curriculum row 1."""

PARKOUR_HARD_TERRAINS_CFG = None
"""Narrow gaps, higher steps, steeper slopes; curriculum row 2."""

# Unified export for curriculum that ramps difficulty by row index.
PARKOUR_TERRAINS_BY_LEVEL = {
    0: PARKOUR_EASY_TERRAINS_CFG,
    1: PARKOUR_MEDIUM_TERRAINS_CFG,
    2: PARKOUR_HARD_TERRAINS_CFG,
}
