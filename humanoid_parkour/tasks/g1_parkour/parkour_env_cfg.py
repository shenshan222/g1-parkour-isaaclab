# Copyright (c) Humanoid Parkour Course Project.
# SPDX-License-Identifier: BSD-3-Clause

"""Training environment configuration for G1 parkour velocity tracking.

Inherits ``G1RoughEnvCfg`` (G1 robot, height scanner, rough-style rewards/events).
Primary override for Phase 2: swap in ``PARKOUR_EASY_TERRAINS_CFG``.
"""

from __future__ import annotations

from isaaclab.utils import configclass

from isaaclab_tasks.manager_based.locomotion.velocity.config.g1.rough_env_cfg import G1RoughEnvCfg

from humanoid_parkour.terrains.parkour_terrain_cfg import PARKOUR_EASY_TERRAINS_CFG


@configclass
class G1ParkourEnvCfg(G1RoughEnvCfg):
    """Parkour training: rough G1 stack + easy parkour terrain preset."""

    def __post_init__(self):
        super().__post_init__()

        # --- Terrain (Phase 2 core) ---
        # .replace() avoids sharing one mutable cfg with play/eval code paths.
        self.scene.terrain.terrain_generator = PARKOUR_EASY_TERRAINS_CFG.replace()

        # Easy tier: fixed generator difficulty (no row-wise curriculum in terrain mesh).
        # Disable env terrain-level curriculum so spawn difficulty does not ramp like full rough.
        self.curriculum.terrain_levels = None

        # Optional later: reward / command tweaks for parkour (keep rough defaults until easy trains).
        # self.commands.base_velocity.ranges.lin_vel_x = (0.0, 1.0)
        # self.rewards.feet_air_time.weight = 0.5
