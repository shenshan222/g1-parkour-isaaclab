# Copyright (c) Humanoid Parkour Course Project.
# SPDX-License-Identifier: BSD-3-Clause

"""Custom MDP terms: rewards, terminations, and success checks for parkour.

Keep experiment logic out of env cfg files; reference these callables from
``parkour_env_cfg`` reward/termination config entries.
"""

from __future__ import annotations

# from isaaclab.envs import ManagerBasedRLEnv
# from isaaclab.managers import SceneEntityCfg


def reward_parkour_progress(env, asset_cfg=None) -> float:
    """Reward forward progress along the commanded velocity direction."""
    # TODO: implement using base linear velocity vs command
    raise NotImplementedError


def reward_foothold_safety(env, sensor_cfg=None) -> float:
    """Optional: penalize unsafe footholds on gaps / edges (Hiking-in-the-Wild style)."""
    raise NotImplementedError


def termination_fall(env, minimum_height: float = 0.3) -> bool:
    """Terminate when the robot base drops below ``minimum_height``."""
    raise NotImplementedError


def check_obstacle_passed(env, checkpoint_x: float) -> bool:
    """Return True if the robot passed a terrain checkpoint (for metrics)."""
    raise NotImplementedError
