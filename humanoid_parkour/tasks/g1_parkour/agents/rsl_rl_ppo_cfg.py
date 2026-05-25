# Copyright (c) Humanoid Parkour Course Project.
# SPDX-License-Identifier: BSD-3-Clause

"""RSL-RL PPO runner configuration for parkour training."""

from __future__ import annotations

from isaaclab.utils import configclass

from isaaclab_tasks.manager_based.locomotion.velocity.config.g1.agents.rsl_rl_ppo_cfg import (
    G1RoughPPORunnerCfg,
)


@configclass
class G1ParkourPPORunnerCfg(G1RoughPPORunnerCfg):
    """Official G1 rough PPO stack; separate TensorBoard / log folder name."""

    experiment_name = "g1_parkour_easy"
