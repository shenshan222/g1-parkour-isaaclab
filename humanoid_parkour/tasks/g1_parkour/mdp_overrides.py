# Copyright (c) Humanoid Parkour Course Project.
# SPDX-License-Identifier: BSD-3-Clause

"""Custom MDP terms: rewards and terminations for parkour.

Reference these callables from ``parkour_env_cfg`` reward/termination config entries.
"""

from __future__ import annotations

import torch


def reward_parkour_progress(env) -> torch.Tensor:
    """Reward forward base motion in the world x-axis.

    Complementary to the inherited base-frame velocity-tracking reward: this
    term directly rewards world-space forward progress regardless of robot
    orientation, and saturates rather than penalising imperfect tracking.
    """
    root_vel_w = env.scene["robot"].data.root_lin_vel_w
    return torch.clamp(root_vel_w[:, 0] * 0.5, min=0.0, max=0.75)


def reward_foothold_safety(env) -> torch.Tensor:
    """Optional: penalise unsafe footholds on gaps/edges (Hiking-in-the-Wild style)."""
    raise NotImplementedError


def termination_fall(env, minimum_height: float = 0.3) -> torch.Tensor:
    """Terminate when the robot base drops below ``minimum_height``.

    Provides an earlier termination signal for gap/edge falls than the
    inherited ``base_contact`` termination alone.
    """
    root_height = env.scene["robot"].data.root_pos_w[:, 2]
    return root_height < minimum_height


def check_obstacle_passed(env, checkpoint_x: float) -> torch.Tensor:
    """Return True if the robot passed a terrain checkpoint (for metrics)."""
    raise NotImplementedError
