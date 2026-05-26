# Copyright (c) Humanoid Parkour Course Project.
# SPDX-License-Identifier: BSD-3-Clause

"""Register G1 parkour velocity-tracking environments with Gymnasium."""

import gymnasium as gym

from . import agents

##
# Register Gym environments (Isaac Lab manager-based RL).
##

gym.register(
    id="Isaac-Velocity-Parkour-G1-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.parkour_env_cfg:G1ParkourEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:G1ParkourPPORunnerCfg",
    },
)

gym.register(
    id="Isaac-Velocity-Parkour-G1-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.parkour_env_cfg:G1ParkourEnvCfg_PLAY",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:G1ParkourPPORunnerCfg",
    },
)
