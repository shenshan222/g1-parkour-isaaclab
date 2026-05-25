# Copyright (c) Humanoid Parkour Course Project.
# SPDX-License-Identifier: BSD-3-Clause

"""Play / visualization environment for parkour task recording."""

from __future__ import annotations

from isaaclab.utils import configclass

from humanoid_parkour.terrains.parkour_terrain_cfg import PARKOUR_EASY_TERRAINS_CFG

from .parkour_env_cfg import G1ParkourEnvCfg


@configclass
class G1ParkourPlayEnvCfg(G1ParkourEnvCfg):
    """Smaller scene, fixed forward speed, no observation corruption — mirrors ``G1RoughEnvCfg_PLAY``."""

    def __post_init__(self):
        super().__post_init__()

        self.scene.num_envs = 50
        self.scene.env_spacing = 2.5
        self.episode_length_s = 40.0

        self.scene.terrain.max_init_terrain_level = None
        self.scene.terrain.terrain_generator = PARKOUR_EASY_TERRAINS_CFG.replace(
            num_rows=5,
            num_cols=5,
            curriculum=False,
        )

        self.commands.base_velocity.ranges.lin_vel_x = (1.0, 1.0)
        self.commands.base_velocity.ranges.lin_vel_y = (0.0, 0.0)
        self.commands.base_velocity.ranges.ang_vel_z = (-1.0, 1.0)
        self.commands.base_velocity.ranges.heading = (0.0, 0.0)

        self.observations.policy.enable_corruption = False
        self.events.base_external_force_torque = None
        self.events.push_robot = None
