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


def reward_foothold_safety(
    env,
    sensor_cfg,
    asset_cfg,
    slide_scale: float = 1.0,
    support_drop_scale: float = 2.0,
    height_mismatch_scale: float = 0.5,
    max_base_to_foot_height: float = 1.05,
    max_contact_height_mismatch: float = 0.35,
) -> torch.Tensor:
    """Penalize unsafe footholds using existing contact and ankle state.

    This is a lightweight Hiking-in-the-Wild-inspired safety term. It does not
    add depth cameras, edge maps, or foot-volume sensors; instead it uses the
    signals already present in the Isaac Lab G1 rough task:

    - foot sliding while an ankle link is in contact,
    - support points that drop far below the base, which approximates stepping
      into gaps or off platform edges,
    - large height mismatch between simultaneously contacting feet.

    The term returns a positive cost and should be used with a negative reward
    weight.
    """
    contact_sensor = env.scene.sensors[sensor_cfg.name]
    asset = env.scene[asset_cfg.name]

    contacts = contact_sensor.data.net_forces_w_history[:, :, sensor_cfg.body_ids, :].norm(dim=-1).max(dim=1)[0] > 1.0
    foot_pos_z = asset.data.body_pos_w[:, asset_cfg.body_ids, 2]
    foot_vel_xy = asset.data.body_lin_vel_w[:, asset_cfg.body_ids, :2].norm(dim=-1)

    slide_cost = torch.sum(foot_vel_xy * contacts, dim=1)

    root_z = asset.data.root_pos_w[:, 2].unsqueeze(1)
    base_to_foot_height = root_z - foot_pos_z
    support_drop = torch.clamp(base_to_foot_height - max_base_to_foot_height, min=0.0)
    support_drop_cost = torch.sum(support_drop * contacts, dim=1)

    contact_count = torch.sum(contacts.int(), dim=1)
    masked_min = torch.where(contacts, foot_pos_z, torch.full_like(foot_pos_z, float("inf"))).min(dim=1)[0]
    masked_max = torch.where(contacts, foot_pos_z, torch.full_like(foot_pos_z, float("-inf"))).max(dim=1)[0]
    height_mismatch = torch.clamp(masked_max - masked_min - max_contact_height_mismatch, min=0.0)
    height_mismatch_cost = torch.where(contact_count >= 2, height_mismatch, torch.zeros_like(height_mismatch))

    return (
        slide_scale * slide_cost
        + support_drop_scale * support_drop_cost
        + height_mismatch_scale * height_mismatch_cost
    )


def termination_fall(env, minimum_height: float = 0.3) -> torch.Tensor:
    """Terminate when the robot base drops below ``minimum_height``.

    Provides an earlier termination signal for gap/edge falls than the
    inherited ``base_contact`` termination alone.
    """
    root_height = env.scene["robot"].data.root_pos_w[:, 2]
    return root_height < minimum_height
