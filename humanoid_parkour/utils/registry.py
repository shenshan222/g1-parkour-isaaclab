# Copyright (c) Humanoid Parkour Course Project.
# SPDX-License-Identifier: BSD-3-Clause

"""Task ID registry for scripts and experiment docs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TaskSpec:
    """Metadata for a registered Gym task."""

    gym_id: str
    env_cfg_entry: str
    rsl_rl_cfg_entry: str
    description: str


TASK_IDS: dict[str, TaskSpec] = {
    "parkour_train": TaskSpec(
        gym_id="Isaac-Velocity-Parkour-G1-v0",
        env_cfg_entry="humanoid_parkour.tasks.g1_parkour.parkour_env_cfg:G1ParkourEnvCfg",
        rsl_rl_cfg_entry="humanoid_parkour.tasks.g1_parkour.agents.rsl_rl_ppo_cfg:G1ParkourPPORunnerCfg",
        description="Parkour velocity tracking — training",
    ),
    "parkour_play": TaskSpec(
        gym_id="Isaac-Velocity-Parkour-G1-Play-v0",
        env_cfg_entry="humanoid_parkour.tasks.g1_parkour.parkour_env_cfg_play:G1ParkourPlayEnvCfg",
        rsl_rl_cfg_entry="humanoid_parkour.tasks.g1_parkour.agents.rsl_rl_ppo_cfg:G1ParkourPPORunnerCfg",
        description="Parkour velocity tracking — play / video",
    ),
    "flat_baseline": TaskSpec(
        gym_id="Isaac-Velocity-Flat-G1-v0",
        env_cfg_entry="isaaclab_tasks...g1.flat_env_cfg:G1FlatEnvCfg",
        rsl_rl_cfg_entry="isaaclab_tasks...g1.agents.rsl_rl_ppo_cfg:G1FlatPPORunnerCfg",
        description="Official Isaac Lab flat G1 baseline",
    ),
    "rough_baseline": TaskSpec(
        gym_id="Isaac-Velocity-Rough-G1-v0",
        env_cfg_entry="isaaclab_tasks...g1.rough_env_cfg:G1RoughEnvCfg",
        rsl_rl_cfg_entry="isaaclab_tasks...g1.agents.rsl_rl_ppo_cfg:G1RoughPPORunnerCfg",
        description="Official Isaac Lab rough G1 baseline",
    ),
}


def get_task_spec(key: str) -> TaskSpec:
    """Look up a task by registry key."""
    if key not in TASK_IDS:
        raise KeyError(f"Unknown task key '{key}'. Available: {list(TASK_IDS)}")
    return TASK_IDS[key]
