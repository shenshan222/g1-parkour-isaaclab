# Copyright (c) Humanoid Parkour Course Project.
# SPDX-License-Identifier: BSD-3-Clause

"""RSL-RL PPO configs — one experiment name per difficulty tier."""

from __future__ import annotations

from isaaclab.utils import configclass

from isaaclab_tasks.manager_based.locomotion.velocity.config.g1.agents.rsl_rl_ppo_cfg import (
    G1RoughPPORunnerCfg,
)


@configclass
class G1ParkourEasyPPORunnerCfg(G1RoughPPORunnerCfg):
    experiment_name = "g1_parkour_easy"


@configclass
class G1ParkourMediumPPORunnerCfg(G1RoughPPORunnerCfg):
    experiment_name = "g1_parkour_medium"


@configclass
class G1ParkourHardPPORunnerCfg(G1RoughPPORunnerCfg):
    experiment_name = "g1_parkour_hard"
