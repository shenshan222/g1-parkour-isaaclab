# Copyright (c) Humanoid Parkour Course Project.
# SPDX-License-Identifier: BSD-3-Clause

"""Training environment configuration for G1 parkour velocity tracking.

Inherit from Isaac Lab G1 rough locomotion and override:
- terrain generator (see ``humanoid_parkour.terrains.parkour_terrain_cfg``)
- reward weights / MDP terms (see ``mdp_overrides``)
- command ranges, terminations, curriculum
"""

from __future__ import annotations

from isaaclab.utils import configclass

# TODO: uncomment when Isaac Lab is available in the runtime environment
# from isaaclab_tasks.manager_based.locomotion.velocity.config.g1.rough_env_cfg import (
#     G1RoughEnvCfg,
# )
# from humanoid_parkour.terrains.parkour_terrain_cfg import PARKOUR_MEDIUM_TERRAINS_CFG


@configclass
class G1ParkourEnvCfg:
    """Parkour training env cfg — extend ``G1RoughEnvCfg`` and apply parkour overrides."""

    # Placeholder: replace with ``class G1ParkourEnvCfg(G1RoughEnvCfg):`` after Isaac Lab import works.
    #
    # Example overrides:
    #   scene.terrain.terrain_generator = PARKOUR_MEDIUM_TERRAINS_CFG
    #   rewards.* = mdp_overrides custom terms
    #   curriculum.terrain_levels = ...
    pass


@configclass
class G1ParkourEnvCfg_PLAY(G1ParkourEnvCfg):
    """Play variant with fewer envs and reduced randomization — use parkour_env_cfg_play instead."""

    pass
