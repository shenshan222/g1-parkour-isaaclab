# Copyright (c) Humanoid Parkour Course Project.
# SPDX-License-Identifier: BSD-3-Clause

"""Task ID registry for scripts and experiment docs."""

from __future__ import annotations

from dataclasses import dataclass

_CFG = "humanoid_parkour.tasks.g1_parkour.parkour_env_cfg"
_AGENTS = "humanoid_parkour.tasks.g1_parkour.agents.rsl_rl_ppo_cfg"


@dataclass(frozen=True)
class TaskSpec:
    """Metadata for a registered Gym task."""

    gym_id: str
    env_cfg_entry: str
    rsl_rl_cfg_entry: str
    description: str
    log_subdir: str
    experiment_name: str


def _parkour_specs(
    tier: str,
    tier_label: str,
    env_train: str,
    env_play: str,
    ppo_cfg: str,
) -> dict[str, TaskSpec]:
    log_subdir = f"parkour_{tier}"
    experiment_name = f"g1_parkour_{tier}"
    return {
        f"parkour_{tier}_train": TaskSpec(
            gym_id=f"Isaac-Velocity-Parkour-G1-{tier_label}-v0",
            env_cfg_entry=f"{_CFG}:{env_train}",
            rsl_rl_cfg_entry=f"{_AGENTS}:{ppo_cfg}",
            description=f"Parkour {tier} — training",
            log_subdir=log_subdir,
            experiment_name=experiment_name,
        ),
        f"parkour_{tier}_play": TaskSpec(
            gym_id=f"Isaac-Velocity-Parkour-G1-{tier_label}-Play-v0",
            env_cfg_entry=f"{_CFG}:{env_play}",
            rsl_rl_cfg_entry=f"{_AGENTS}:{ppo_cfg}",
            description=f"Parkour {tier} — play / video",
            log_subdir=log_subdir,
            experiment_name=experiment_name,
        ),
    }


TASK_IDS: dict[str, TaskSpec] = {
    **_parkour_specs(
        "easy",
        "Easy",
        "G1ParkourEasyEnvCfg",
        "G1ParkourEasyEnvCfg_PLAY",
        "G1ParkourEasyPPORunnerCfg",
    ),
    **_parkour_specs(
        "medium",
        "Medium",
        "G1ParkourMediumEnvCfg",
        "G1ParkourMediumEnvCfg_PLAY",
        "G1ParkourMediumPPORunnerCfg",
    ),
    **_parkour_specs(
        "hard",
        "Hard",
        "G1ParkourHardEnvCfg",
        "G1ParkourHardEnvCfg_PLAY",
        "G1ParkourHardPPORunnerCfg",
    ),
    "flat_baseline": TaskSpec(
        gym_id="Isaac-Velocity-Flat-G1-v0",
        env_cfg_entry="isaaclab_tasks...g1.flat_env_cfg:G1FlatEnvCfg",
        rsl_rl_cfg_entry="isaaclab_tasks...g1.agents.rsl_rl_ppo_cfg:G1FlatPPORunnerCfg",
        description="Official Isaac Lab flat G1 baseline",
        log_subdir="flat_baseline",
        experiment_name="g1_flat",
    ),
    "rough_baseline": TaskSpec(
        gym_id="Isaac-Velocity-Rough-G1-v0",
        env_cfg_entry="isaaclab_tasks...g1.rough_env_cfg:G1RoughEnvCfg",
        rsl_rl_cfg_entry="isaaclab_tasks...g1.agents.rsl_rl_ppo_cfg:G1RoughPPORunnerCfg",
        description="Official Isaac Lab rough G1 baseline",
        log_subdir="rough_baseline",
        experiment_name="g1_rough",
    ),
}


def get_task_spec(key: str) -> TaskSpec:
    """Look up a task by registry key."""
    if key not in TASK_IDS:
        raise KeyError(f"Unknown task key '{key}'. Available: {list(TASK_IDS)}")
    return TASK_IDS[key]
