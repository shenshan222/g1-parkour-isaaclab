# Copyright (c) Humanoid Parkour Course Project.
# SPDX-License-Identifier: BSD-3-Clause

"""Register G1 parkour tasks — independent train/play per difficulty tier."""

import gymnasium as gym

from . import agents

##
# EASY
##

gym.register(
    id="Isaac-Velocity-Parkour-G1-Easy-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.parkour_env_cfg:G1ParkourEasyEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:G1ParkourEasyPPORunnerCfg",
    },
)

gym.register(
    id="Isaac-Velocity-Parkour-G1-Easy-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.parkour_env_cfg:G1ParkourEasyEnvCfg_PLAY",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:G1ParkourEasyPPORunnerCfg",
    },
)

##
# MEDIUM
##

gym.register(
    id="Isaac-Velocity-Parkour-G1-Medium-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.parkour_env_cfg:G1ParkourMediumEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:G1ParkourMediumPPORunnerCfg",
    },
)

gym.register(
    id="Isaac-Velocity-Parkour-G1-Medium-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.parkour_env_cfg:G1ParkourMediumEnvCfg_PLAY",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:G1ParkourMediumPPORunnerCfg",
    },
)

##
# HARD
##

gym.register(
    id="Isaac-Velocity-Parkour-G1-Hard-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.parkour_env_cfg:G1ParkourHardEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:G1ParkourHardPPORunnerCfg",
    },
)

gym.register(
    id="Isaac-Velocity-Parkour-G1-Hard-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.parkour_env_cfg:G1ParkourHardEnvCfg_PLAY",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:G1ParkourHardPPORunnerCfg",
    },
)
