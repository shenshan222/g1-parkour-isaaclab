# Copyright (c) Humanoid Parkour Course Project.
# SPDX-License-Identifier: BSD-3-Clause

"""RSL-RL PPO configs — one experiment name per difficulty tier, plus fine-tune variants."""

from __future__ import annotations

from isaaclab.utils import configclass

from isaaclab_tasks.manager_based.locomotion.velocity.config.g1.agents.rsl_rl_ppo_cfg import (
    G1RoughPPORunnerCfg,
)


@configclass
class G1ParkourEasyPPORunnerCfg(G1RoughPPORunnerCfg):
    experiment_name = "g1_parkour_easy"


@configclass
class G1ParkourMediumPPORunnerCfg(G1RoughPPORunnerCfg):
    experiment_name = "g1_parkour_medium"


@configclass
class G1ParkourHardPPORunnerCfg(G1RoughPPORunnerCfg):
    experiment_name = "g1_parkour_hard"


@configclass
class G1RoughNoHeightScanPPORunnerCfg(G1RoughPPORunnerCfg):
    experiment_name = "g1_rough_no_height_scan"


@configclass
class G1ParkourHardNoHeightScanPPORunnerCfg(G1RoughPPORunnerCfg):
    experiment_name = "g1_parkour_hard_no_height_scan"


# -----------------------------------------------------------------------------
# Fine-tune configs (reduced learning rate for MDP-switch resume training)
# -----------------------------------------------------------------------------
# Verify field paths on your Isaac Lab install:
#   python -c "from isaaclab_tasks... import G1RoughPPORunnerCfg; print(G1RoughPPORunnerCfg.__annotations__)"


@configclass
class G1ParkourHardFineTunePPORunnerCfg(G1RoughPPORunnerCfg):
    experiment_name = "g1_parkour_hard_finetune"

    def __post_init__(self):
        super().__post_init__()
        # Halve learning rates to reduce the risk of catastrophic critic updates
        # when the reward landscape changes.
        if hasattr(self, "algorithm"):
            alg = self.algorithm
            if hasattr(alg, "learning_rate"):
                alg.learning_rate = alg.learning_rate * 0.5
            if hasattr(alg, "desired_kl"):
                alg.desired_kl = getattr(alg, "desired_kl", 0.01) * 0.8


# -----------------------------------------------------------------------------
# MDP ablation configs
# -----------------------------------------------------------------------------


@configclass
class G1RoughMDPPPORunnerCfg(G1RoughPPORunnerCfg):
    """Rough locomotion with current reward-only parkour MDP ablation."""

    experiment_name = "g1_rough_mdp"


@configclass
class G1ParkourHardMDPPPORunnerCfg(G1RoughPPORunnerCfg):
    """Hard parkour terrain with current reward-only parkour MDP ablation."""

    experiment_name = "g1_parkour_hard_mdp"
