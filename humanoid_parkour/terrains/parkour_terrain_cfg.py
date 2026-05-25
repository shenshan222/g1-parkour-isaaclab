# Copyright (c) Humanoid Parkour Course Project.
# SPDX-License-Identifier: BSD-3-Clause

"""Parkour terrain presets — three difficulty tiers using Isaac Lab TerrainGeneratorCfg.

Difficulty ladder (vs official ``ROUGH_TERRAINS_CFG``):
- EASY: same terrain *types* as rough, capped lower ranges (~85% of rough extremes), no gaps.
- MEDIUM (TODO): add gaps + bump ranges above rough.
- HARD (TODO): large gaps, high steps, parkour-style mixes.

Only terrain composition lives here; no reward or training logic.
"""

from __future__ import annotations

import isaaclab.terrains as terrain_gen
from isaaclab.terrains.terrain_generator_cfg import TerrainGeneratorCfg

# Reference — Isaac Lab ``isaaclab/terrains/config/rough.py``:
#   step_height (0.05, 0.23), boxes height (0.05, 0.20), noise (0.02, 0.10), slope (0.0, 0.4)

PARKOUR_EASY_TERRAINS_CFG = TerrainGeneratorCfg(
    size=(8.0, 8.0),
    border_width=20.0,
    num_rows=10,
    num_cols=20,
    horizontal_scale=0.1,
    vertical_scale=0.005,
    slope_threshold=0.75,
    use_cache=False,
    curriculum=False,
    sub_terrains={
        "pyramid_stairs": terrain_gen.MeshPyramidStairsTerrainCfg(
            proportion=0.2,
            step_height_range=(0.05, 0.17),
            step_width=0.3,
            platform_width=3.0,
            border_width=1.0,
            holes=False,
        ),
        "pyramid_stairs_inv": terrain_gen.MeshInvertedPyramidStairsTerrainCfg(
            proportion=0.2,
            step_height_range=(0.05, 0.17),
            step_width=0.3,
            platform_width=3.0,
            border_width=1.0,
            holes=False,
        ),
        "boxes": terrain_gen.MeshRandomGridTerrainCfg(
            proportion=0.2,
            grid_width=0.45,
            grid_height_range=(0.05, 0.15),
            platform_width=2.0,
        ),
        "random_rough": terrain_gen.HfRandomUniformTerrainCfg(
            proportion=0.2,
            noise_range=(0.02, 0.08),
            noise_step=0.02,
            border_width=0.25,
        ),
        "hf_pyramid_slope": terrain_gen.HfPyramidSlopedTerrainCfg(
            proportion=0.1,
            slope_range=(0.0, 0.30),
            platform_width=2.0,
            border_width=0.25,
        ),
        "hf_pyramid_slope_inv": terrain_gen.HfInvertedPyramidSlopedTerrainCfg(
            proportion=0.1,
            slope_range=(0.0, 0.30),
            platform_width=2.0,
            border_width=0.25,
        ),
    },
)
"""Rough-like mix with reduced extremes; no gaps. Slightly easier than official rough."""

PARKOUR_MEDIUM_TERRAINS_CFG = None
"""TODO: rough-level or above + ``MeshGapTerrainCfg`` (small–medium gaps)."""

PARKOUR_HARD_TERRAINS_CFG = None
"""TODO: high steps, wide gaps, irregular boxes — near real parkour."""

PARKOUR_TERRAINS_BY_LEVEL = {
    0: PARKOUR_EASY_TERRAINS_CFG,
    1: PARKOUR_MEDIUM_TERRAINS_CFG,
    2: PARKOUR_HARD_TERRAINS_CFG,
}
