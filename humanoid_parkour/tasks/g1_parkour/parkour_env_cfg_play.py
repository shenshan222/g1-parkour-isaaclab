# Copyright (c) Humanoid Parkour Course Project.
# SPDX-License-Identifier: BSD-3-Clause

"""Play / visualization environment — fewer envs, fixed terrain, no domain randomization."""

from __future__ import annotations

from isaaclab.utils import configclass

from .parkour_env_cfg import G1ParkourEnvCfg

# from humanoid_parkour.terrains.parkour_terrain_cfg import PARKOUR_EASY_TERRAINS_CFG


@configclass
class G1ParkourPlayEnvCfg(G1ParkourEnvCfg):
    """Inference-oriented cfg for recording rollout videos."""

    # TODO after inheriting G1RoughEnvCfg:
    #   scene.num_envs = 16  # or fewer for recording
    #   scene.terrain.terrain_generator = PARKOUR_EASY_TERRAINS_CFG
    #   disable push / event randomization for stable demos
    pass
