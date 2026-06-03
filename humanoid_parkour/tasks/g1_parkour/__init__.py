# Copyright (c) Humanoid Parkour Course Project.
# SPDX-License-Identifier: BSD-3-Clause

"""Register G1 parkour tasks — independent train/play per difficulty tier."""

import gymnasium as gym

_AGENTS = f"{__name__}.agents"

##
# EASY
##

gym.register(
    id="Isaac-Velocity-Parkour-G1-Easy-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.parkour_env_cfg:G1ParkourEasyEnvCfg",
        "rsl_rl_cfg_entry_point": f"{_AGENTS}.rsl_rl_ppo_cfg:G1ParkourEasyPPORunnerCfg",
    },
)

gym.register(
    id="Isaac-Velocity-Parkour-G1-Easy-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.parkour_env_cfg:G1ParkourEasyEnvCfg_PLAY",
        "rsl_rl_cfg_entry_point": f"{_AGENTS}.rsl_rl_ppo_cfg:G1ParkourEasyPPORunnerCfg",
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
        "rsl_rl_cfg_entry_point": f"{_AGENTS}.rsl_rl_ppo_cfg:G1ParkourMediumPPORunnerCfg",
    },
)

gym.register(
    id="Isaac-Velocity-Parkour-G1-Medium-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.parkour_env_cfg:G1ParkourMediumEnvCfg_PLAY",
        "rsl_rl_cfg_entry_point": f"{_AGENTS}.rsl_rl_ppo_cfg:G1ParkourMediumPPORunnerCfg",
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
        "rsl_rl_cfg_entry_point": f"{_AGENTS}.rsl_rl_ppo_cfg:G1ParkourHardPPORunnerCfg",
    },
)

gym.register(
    id="Isaac-Velocity-Parkour-G1-Hard-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.parkour_env_cfg:G1ParkourHardEnvCfg_PLAY",
        "rsl_rl_cfg_entry_point": f"{_AGENTS}.rsl_rl_ppo_cfg:G1ParkourHardPPORunnerCfg",
    },
)

# Hard fine-tune — same env config (now includes parkour MDP terms),
# but reduced learning rate for safe MDP-switch resume training.
gym.register(
    id="Isaac-Velocity-Parkour-G1-Hard-FineTune-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.parkour_env_cfg:G1ParkourHardEnvCfg",
        "rsl_rl_cfg_entry_point": f"{_AGENTS}.rsl_rl_ppo_cfg:G1ParkourHardFineTunePPORunnerCfg",
    },
)

##
# ROUGH MDP
##

gym.register(
    id="Isaac-Velocity-Rough-G1-MDP-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.parkour_env_cfg:G1ParkourRoughMDPEnvCfg",
        "rsl_rl_cfg_entry_point": f"{_AGENTS}.rsl_rl_ppo_cfg:G1RoughMDPPPORunnerCfg",
    },
)

gym.register(
    id="Isaac-Velocity-Rough-G1-MDP-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.parkour_env_cfg:G1ParkourRoughMDPEnvCfg_PLAY",
        "rsl_rl_cfg_entry_point": f"{_AGENTS}.rsl_rl_ppo_cfg:G1RoughMDPPPORunnerCfg",
    },
)

##
# HARD MDP
##

gym.register(
    id="Isaac-Velocity-Parkour-G1-Hard-MDP-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.parkour_env_cfg:G1ParkourHardMDPEnvCfg",
        "rsl_rl_cfg_entry_point": f"{_AGENTS}.rsl_rl_ppo_cfg:G1ParkourHardMDPPPORunnerCfg",
    },
)

gym.register(
    id="Isaac-Velocity-Parkour-G1-Hard-MDP-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.parkour_env_cfg:G1ParkourHardMDPEnvCfg_PLAY",
        "rsl_rl_cfg_entry_point": f"{_AGENTS}.rsl_rl_ppo_cfg:G1ParkourHardMDPPPORunnerCfg",
    },
)

##
# EXTREME RANDOM (evaluation-only)
##

gym.register(
    id="Isaac-Velocity-Parkour-G1-ExtremeRandom-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.parkour_env_cfg:G1ParkourExtremeRandomEnvCfg_PLAY",
        "rsl_rl_cfg_entry_point": f"{_AGENTS}.rsl_rl_ppo_cfg:G1ParkourHardPPORunnerCfg",
    },
)
