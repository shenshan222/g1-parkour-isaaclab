# Copyright (c) Humanoid Parkour Course Project.
# SPDX-License-Identifier: BSD-3-Clause

"""RSL-RL PPO runner configuration for parkour training.

Start from Isaac Lab G1 rough PPO cfg and tune learning rate, horizon, and network size.
"""

from __future__ import annotations

from isaaclab.utils import configclass

# TODO: inherit from official cfg when Isaac Lab is on PYTHONPATH
# from isaaclab_tasks.manager_based.locomotion.velocity.config.g1.agents.rsl_rl_ppo_cfg import (
#     G1RoughPPORunnerCfg,
# )


@configclass
class G1ParkourPPORunnerCfg:
    """PPO runner for ``Isaac-Velocity-Parkour-G1-v0``."""

    # Placeholder fields — mirror G1RoughPPORunnerCfg after import works.
    seed = 42
    device = "cuda:0"
    num_steps_per_env = 24
    max_iterations = 3000
    empirical_normalization = False

    # class PolicyCfg: ...
    # class AlgorithmCfg: ...
