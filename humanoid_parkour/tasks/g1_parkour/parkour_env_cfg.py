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

        # --- Terrain ---
        # .replace() avoids sharing one mutable cfg with play/eval code paths.
        self.scene.terrain.terrain_generator = PARKOUR_EASY_TERRAINS_CFG.replace(curriculum=True)

@configclass
class G1ParkourEnvCfg_PLAY(G1ParkourEnvCfg):
    """Parkour play environment: smaller scene, fixed speed, no observation corruption."""

    def __post_init__(self):
        super().__post_init__()

        self.scene.num_envs = 50
        self.scene.env_spacing = 2.5
        self.episode_length_s = 40.0
        self.scene.terrain.terrain_generator = PARKOUR_EASY_TERRAINS_CFG.replace()
        self.scene.terrain.max_init_terrain_level = None
        # reduce the number of terrains to save memory
        if self.scene.terrain.terrain_generator is not None:
            self.scene.terrain.terrain_generator.num_rows = 5
            self.scene.terrain.terrain_generator.num_cols = 5
            self.scene.terrain.terrain_generator.curriculum = False

        self.commands.base_velocity.ranges.lin_vel_x = (1.0, 1.0)
        self.commands.base_velocity.ranges.lin_vel_y = (0.0, 0.0)
        self.commands.base_velocity.ranges.ang_vel_z = (-1.0, 1.0)
        self.commands.base_velocity.ranges.heading = (0.0, 0.0)
        # disable randomization for play
        self.observations.policy.enable_corruption = False
        # remove random pushing
        self.events.base_external_force_torque = None
        self.events.push_robot = None