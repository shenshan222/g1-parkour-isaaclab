# Copyright (c) Humanoid Parkour Course Project.
# SPDX-License-Identifier: BSD-3-Clause

"""G1 parkour env cfgs — one train + one play class per difficulty tier."""

from __future__ import annotations

from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.terrains.terrain_generator_cfg import TerrainGeneratorCfg
from isaaclab.utils import configclass

from isaaclab_tasks.manager_based.locomotion.velocity.config.g1.rough_env_cfg import G1Rewards, G1RoughEnvCfg

from humanoid_parkour.tasks.g1_parkour.mdp_overrides import reward_parkour_progress
from humanoid_parkour.terrains.parkour_terrain_cfg import (
    PARKOUR_EASY_TERRAINS_CFG,
    PARKOUR_MEDIUM_TERRAINS_CFG,
    PARKOUR_HARD_TERRAINS_CFG,
)


@configclass
class G1ParkourRewards(G1Rewards):
    """Reward terms for parkour locomotion."""

    parkour_progress = RewTerm(
        func=reward_parkour_progress,
        weight=0.5,
        params={},
    )


def _terrain_copy(preset: TerrainGeneratorCfg, *, curriculum: bool) -> TerrainGeneratorCfg:
    return preset.replace(curriculum=curriculum)


def _apply_play_settings(cfg: G1RoughEnvCfg, preset: TerrainGeneratorCfg) -> None:
    """Shared play overrides (mirrors ``G1RoughEnvCfg_PLAY``)."""
    cfg.scene.num_envs = 50
    cfg.scene.env_spacing = 2.5
    cfg.episode_length_s = 40.0
    cfg.scene.terrain.max_init_terrain_level = None
    cfg.scene.terrain.terrain_generator = _terrain_copy(preset, curriculum=False)
    if cfg.scene.terrain.terrain_generator is not None:
        cfg.scene.terrain.terrain_generator.num_rows = 5
        cfg.scene.terrain.terrain_generator.num_cols = 5
    cfg.curriculum.terrain_levels = None

    cfg.commands.base_velocity.ranges.lin_vel_x = (1.0, 1.0)
    cfg.commands.base_velocity.ranges.lin_vel_y = (0.0, 0.0)
    cfg.commands.base_velocity.ranges.ang_vel_z = (-1.0, 1.0)
    cfg.commands.base_velocity.ranges.heading = (0.0, 0.0)

    cfg.observations.policy.enable_corruption = False
    cfg.events.base_external_force_torque = None
    cfg.events.push_robot = None


# -----------------------------------------------------------------------------
# EASY
# -----------------------------------------------------------------------------


@configclass
class G1ParkourEasyEnvCfg(G1RoughEnvCfg):
    rewards: G1ParkourRewards = G1ParkourRewards()

    def __post_init__(self):
        super().__post_init__()
        self.scene.terrain.terrain_generator = _terrain_copy(PARKOUR_EASY_TERRAINS_CFG, curriculum=True)


@configclass
class G1ParkourEasyEnvCfg_PLAY(G1ParkourEasyEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        _apply_play_settings(self, PARKOUR_EASY_TERRAINS_CFG)


# -----------------------------------------------------------------------------
# MEDIUM
# -----------------------------------------------------------------------------


@configclass
class G1ParkourMediumEnvCfg(G1RoughEnvCfg):
    rewards: G1ParkourRewards = G1ParkourRewards()

    def __post_init__(self):
        super().__post_init__()
        self.scene.terrain.terrain_generator = _terrain_copy(PARKOUR_MEDIUM_TERRAINS_CFG, curriculum=True)


@configclass
class G1ParkourMediumEnvCfg_PLAY(G1ParkourMediumEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        _apply_play_settings(self, PARKOUR_MEDIUM_TERRAINS_CFG)


# -----------------------------------------------------------------------------
# HARD
# -----------------------------------------------------------------------------


@configclass
class G1ParkourHardEnvCfg(G1RoughEnvCfg):
    rewards: G1ParkourRewards = G1ParkourRewards()

    def __post_init__(self):
        super().__post_init__()
        self.scene.terrain.terrain_generator = _terrain_copy(PARKOUR_HARD_TERRAINS_CFG, curriculum=True)


@configclass
class G1ParkourHardEnvCfg_PLAY(G1ParkourHardEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        _apply_play_settings(self, PARKOUR_HARD_TERRAINS_CFG)
