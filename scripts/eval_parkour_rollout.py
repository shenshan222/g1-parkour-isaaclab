#!/usr/bin/env python3
# Copyright (c) Humanoid Parkour Course Project.
# SPDX-License-Identifier: BSD-3-Clause

"""Evaluate trained G1 policies with timeout or semantic obstacle metrics."""

from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path

isaaclab_root = Path(os.environ.get("ISAACLAB_ROOT", "/root/autodl-tmp/isaac_workspace/IsaacLab"))
rsl_rl_script_dir = isaaclab_root / "scripts" / "reinforcement_learning" / "rsl_rl"
sys.path.insert(0, str(rsl_rl_script_dir))

from isaaclab.app import AppLauncher  # noqa: E402

import cli_args  # noqa: E402

parser = argparse.ArgumentParser(description="Evaluate a trained G1 checkpoint with timeout or semantic metrics.")
parser.add_argument("--metric", choices=("timeout", "semantic"), default="timeout", help="Evaluation metric family to write.")
parser.add_argument("--task", required=True, type=str, help="Isaac Lab Gym task id, usually a *-Play-v0 task.")
parser.add_argument("--agent", type=str, default="rsl_rl_cfg_entry_point", help="RL agent config entry point.")
parser.add_argument("--eval_name", required=True, type=str, help="Name written into the CSV row.")
parser.add_argument("--checkpoint_source", type=str, default="", help="Source label for cross-terrain eval checkpoints.")
parser.add_argument("--eval_env", type=str, default="", help="Evaluation environment label for cross-terrain eval.")
parser.add_argument("--output_csv", required=True, type=str, help="CSV file to create/update.")
parser.add_argument("--num_episodes", type=int, default=64, help="Number of finished episodes to collect.")
parser.add_argument("--num_envs", type=int, default=32, help="Number of parallel environments.")
parser.add_argument("--terrain_num_rows", type=int, default=10, help="Override terrain generator row count for eval.")
parser.add_argument("--terrain_num_cols", type=int, default=10, help="Override terrain generator column count for eval.")
parser.add_argument("--terrain_sampling", type=str, default="", help="Terrain sampling label written to CSV metadata.")
parser.add_argument("--terrain_fixed_row", type=int, default=None, help="Fix all envs to one terrain difficulty row.")
parser.add_argument("--terrain_fixed_col", type=int, default=None, help="Optionally fix all envs to one terrain type column.")
parser.add_argument("--stress_mode", type=str, default="", help="Stress-test mode label written to CSV metadata.")
parser.add_argument("--pass_distance_m", type=float, default=4.0, help="Minimum max forward distance for semantic pass.")
parser.add_argument("--strong_pass_distance_m", type=float, default=6.0, help="Minimum max forward distance for strong semantic pass.")
parser.add_argument(
    "--max_steps",
    type=int,
    default=None,
    help="Safety cap for environment steps. Defaults to 4x enough steps for requested episodes.",
)
parser.add_argument("--append", action="store_true", help="Append/update one row instead of replacing the CSV.")
parser.add_argument("--seed", type=int, default=42, help="Evaluation seed.")
parser.add_argument("--disable_fabric", action="store_true", default=False, help="Disable fabric and use USD I/O operations.")
parser.add_argument("--real-time", action="store_true", default=False, help="Accepted for parity with play.py; unused.")
cli_args.add_rsl_rl_args(parser)
AppLauncher.add_app_launcher_args(parser)
args_cli, hydra_args = parser.parse_known_args()

sys.argv = [sys.argv[0]] + hydra_args

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import importlib.metadata as metadata  # noqa: E402

from packaging import version  # noqa: E402

installed_version = metadata.version("rsl-rl-lib")

import gymnasium as gym  # noqa: E402
import torch  # noqa: E402
from rsl_rl.runners import DistillationRunner, OnPolicyRunner  # noqa: E402

from isaaclab.envs import DirectMARLEnv, DirectMARLEnvCfg, DirectRLEnvCfg, ManagerBasedRLEnvCfg, multi_agent_to_single_agent  # noqa: E402
from isaaclab.utils.assets import retrieve_file_path  # noqa: E402
from isaaclab_rl.rsl_rl import RslRlBaseRunnerCfg, RslRlVecEnvWrapper, handle_deprecated_rsl_rl_cfg  # noqa: E402
from isaaclab_tasks.utils.hydra import hydra_task_config  # noqa: E402

import humanoid_parkour.tasks.g1_parkour  # noqa: F401,E402
from humanoid_parkour.evaluation.semantic_obstacles import SemanticObstacleCriteria, evaluate_semantic_pass  # noqa: E402

TIMEOUT_FIELDNAMES = [
    "run_name",
    "fall_rate",
    "timeout_rate",
    "mean_velocity_tracking_error",
    "mean_yaw_tracking_error",
    "mean_episode_length",
    "num_episodes",
    "checkpoint_source",
    "eval_env",
    "terrain_num_rows",
    "terrain_num_cols",
    "terrain_sampling",
    "stress_mode",
    "terrain_fixed_row",
    "terrain_fixed_col",
    "seed",
    "checkpoint",
    "task",
    "num_envs",
    "timeout_definition",
]

SEMANTIC_FIELDNAMES = [
    "run_name",
    "semantic_pass_rate",
    "strong_pass_rate",
    "fall_rate",
    "timeout_rate",
    "mean_forward_distance_m",
    "mean_max_forward_distance_m",
    "mean_velocity_tracking_error",
    "mean_yaw_tracking_error",
    "mean_episode_length",
    "num_episodes",
    "checkpoint_source",
    "eval_env",
    "terrain_num_rows",
    "terrain_num_cols",
    "terrain_sampling",
    "stress_mode",
    "terrain_fixed_row",
    "terrain_fixed_col",
    "pass_distance_m",
    "strong_pass_distance_m",
    "seed",
    "checkpoint",
    "task",
    "num_envs",
    "semantic_definition",
    "strong_definition",
]


def _apply_fixed_terrain_selection(raw_env, fixed_row: int | None, fixed_col: int | None) -> bool:
    if fixed_row is None and fixed_col is None:
        return False

    terrain = getattr(raw_env.scene, "terrain", None)
    required_attrs = ("terrain_origins", "terrain_levels", "terrain_types", "env_origins")
    if terrain is None or any(not hasattr(terrain, attr) for attr in required_attrs):
        raise RuntimeError("Fixed terrain selection requires generated terrain origins and terrain level/type tensors.")
    if terrain.terrain_origins is None:
        raise RuntimeError("Fixed terrain selection requires terrain.terrain_origins, but this terrain has none.")

    num_rows, num_cols = terrain.terrain_origins.shape[:2]
    if fixed_row is not None and not 0 <= fixed_row < num_rows:
        raise ValueError(f"--terrain_fixed_row={fixed_row} is out of range for terrain rows [0, {num_rows - 1}].")
    if fixed_col is not None and not 0 <= fixed_col < num_cols:
        raise ValueError(f"--terrain_fixed_col={fixed_col} is out of range for terrain cols [0, {num_cols - 1}].")

    env_ids = torch.arange(raw_env.num_envs, device=terrain.terrain_levels.device)
    if fixed_row is not None:
        terrain.terrain_levels[env_ids] = fixed_row
    if fixed_col is not None:
        terrain.terrain_types[env_ids] = fixed_col
    terrain.env_origins[env_ids] = terrain.terrain_origins[terrain.terrain_levels[env_ids], terrain.terrain_types[env_ids]]
    return True


def _write_row(output_csv: Path, row: dict[str, object], fieldnames: list[str], append: bool) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    if append and output_csv.exists() and output_csv.stat().st_size > 0:
        with output_csv.open(newline="") as f:
            rows = list(csv.DictReader(f))
        rows = [existing for existing in rows if existing.get("run_name") != row["run_name"]]
    rows.append(row)

    with output_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for existing in rows:
            writer.writerow({key: existing.get(key, "") for key in fieldnames})


def _rate(episodes: list[dict[str, object]], key: str) -> float:
    return sum(float(ep[key]) for ep in episodes) / len(episodes)


def _mean(episodes: list[dict[str, object]], key: str) -> float:
    return sum(float(ep[key]) for ep in episodes) / len(episodes)


def _metadata(checkpoint: str, num_envs: int) -> dict[str, object]:
    return {
        "checkpoint_source": args_cli.checkpoint_source,
        "eval_env": args_cli.eval_env,
        "terrain_num_rows": args_cli.terrain_num_rows if args_cli.terrain_num_rows is not None else "",
        "terrain_num_cols": args_cli.terrain_num_cols if args_cli.terrain_num_cols is not None else "",
        "terrain_sampling": args_cli.terrain_sampling,
        "stress_mode": args_cli.stress_mode,
        "terrain_fixed_row": args_cli.terrain_fixed_row if args_cli.terrain_fixed_row is not None else "",
        "terrain_fixed_col": args_cli.terrain_fixed_col if args_cli.terrain_fixed_col is not None else "",
        "seed": args_cli.seed,
        "checkpoint": checkpoint,
        "task": args_cli.task,
        "num_envs": num_envs,
    }


def _timeout_row(episodes: list[dict[str, object]], checkpoint: str, num_envs: int) -> dict[str, object]:
    row: dict[str, object] = {
        "run_name": args_cli.eval_name,
        "fall_rate": f"{_rate(episodes, 'fell'):.4f}",
        "timeout_rate": f"{_rate(episodes, 'timeout'):.4f}",
        "mean_velocity_tracking_error": f"{_mean(episodes, 'xy_error'):.4f}",
        "mean_yaw_tracking_error": f"{_mean(episodes, 'yaw_error'):.4f}",
        "mean_episode_length": f"{_mean(episodes, 'length'):.2f}",
        "num_episodes": len(episodes),
        "timeout_definition": "timeout_without_base_contact; tracking_error_direct_pre_step_mean",
    }
    row.update(_metadata(checkpoint, num_envs))
    return row


def _semantic_row(episodes: list[dict[str, object]], checkpoint: str, num_envs: int) -> dict[str, object]:
    row: dict[str, object] = {
        "run_name": args_cli.eval_name,
        "semantic_pass_rate": f"{_rate(episodes, 'semantic_pass'):.4f}",
        "strong_pass_rate": f"{_rate(episodes, 'strong_pass'):.4f}",
        "fall_rate": f"{_rate(episodes, 'fell'):.4f}",
        "timeout_rate": f"{_rate(episodes, 'timeout'):.4f}",
        "mean_forward_distance_m": f"{_mean(episodes, 'forward_distance_m'):.4f}",
        "mean_max_forward_distance_m": f"{_mean(episodes, 'max_forward_distance_m'):.4f}",
        "mean_velocity_tracking_error": f"{_mean(episodes, 'xy_error'):.4f}",
        "mean_yaw_tracking_error": f"{_mean(episodes, 'yaw_error'):.4f}",
        "mean_episode_length": f"{_mean(episodes, 'length'):.2f}",
        "num_episodes": len(episodes),
        "pass_distance_m": f"{args_cli.pass_distance_m:.2f}",
        "strong_pass_distance_m": f"{args_cli.strong_pass_distance_m:.2f}",
        "semantic_definition": f"no_fall_and_max_forward_distance_ge_{args_cli.pass_distance_m:g}m",
        "strong_definition": f"no_fall_and_max_forward_distance_ge_{args_cli.strong_pass_distance_m:g}m",
    }
    row.update(_metadata(checkpoint, num_envs))
    return row


@hydra_task_config(args_cli.task, args_cli.agent)
def main(env_cfg: ManagerBasedRLEnvCfg | DirectRLEnvCfg | DirectMARLEnvCfg, agent_cfg: RslRlBaseRunnerCfg):
    agent_cfg = cli_args.update_rsl_rl_cfg(agent_cfg, args_cli)
    agent_cfg = handle_deprecated_rsl_rl_cfg(agent_cfg, installed_version)

    env_cfg.scene.num_envs = args_cli.num_envs
    env_cfg.seed = args_cli.seed
    env_cfg.sim.device = args_cli.device if args_cli.device is not None else env_cfg.sim.device
    terrain_generator = getattr(getattr(env_cfg.scene, "terrain", None), "terrain_generator", None)
    if terrain_generator is not None:
        if args_cli.terrain_num_rows is not None:
            terrain_generator.num_rows = args_cli.terrain_num_rows
        if args_cli.terrain_num_cols is not None:
            terrain_generator.num_cols = args_cli.terrain_num_cols
        terrain_generator.curriculum = False

    checkpoint = retrieve_file_path(args_cli.checkpoint)
    env_cfg.log_dir = os.path.dirname(checkpoint)

    env = gym.make(args_cli.task, cfg=env_cfg, render_mode=None)
    if isinstance(env.unwrapped, DirectMARLEnv):
        env = multi_agent_to_single_agent(env)
    env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)

    if agent_cfg.class_name == "OnPolicyRunner":
        runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=None, device=agent_cfg.device)
    elif agent_cfg.class_name == "DistillationRunner":
        runner = DistillationRunner(env, agent_cfg.to_dict(), log_dir=None, device=agent_cfg.device)
    else:
        raise ValueError(f"Unsupported runner class: {agent_cfg.class_name}")
    runner.load(checkpoint)
    policy = runner.get_inference_policy(device=env.unwrapped.device)

    if _apply_fixed_terrain_selection(env.unwrapped, args_cli.terrain_fixed_row, args_cli.terrain_fixed_col):
        obs, _ = env.reset()
    else:
        obs = env.get_observations()

    raw_env = env.unwrapped
    robot = raw_env.scene["robot"]
    num_envs = raw_env.num_envs
    device = raw_env.device
    max_episode_length = int(raw_env.max_episode_length)
    max_steps = args_cli.max_steps or max(max_episode_length * 4, int(args_cli.num_episodes / max(1, num_envs) * max_episode_length * 4))

    episode_lengths = torch.zeros(num_envs, dtype=torch.long, device=device)
    episode_xy_error = torch.zeros(num_envs, dtype=torch.float32, device=device)
    episode_yaw_error = torch.zeros(num_envs, dtype=torch.float32, device=device)
    start_x = robot.data.root_pos_w[:, 0].detach().clone()
    max_forward = torch.zeros(num_envs, dtype=torch.float32, device=device)
    criteria = SemanticObstacleCriteria(args_cli.pass_distance_m, args_cli.strong_pass_distance_m)

    completed: list[dict[str, object]] = []
    steps = 0

    while simulation_app.is_running() and len(completed) < args_cli.num_episodes and steps < max_steps:
        raw_env = env.unwrapped
        robot = raw_env.scene["robot"]
        root_x = robot.data.root_pos_w[:, 0]
        forward = root_x - start_x
        if args_cli.metric == "semantic":
            max_forward = torch.maximum(max_forward, forward)

        command = raw_env.command_manager.get_command("base_velocity")
        xy_error = torch.linalg.norm(command[:, :2] - robot.data.root_lin_vel_b[:, :2], dim=-1)
        yaw_error = torch.abs(command[:, 2] - robot.data.root_ang_vel_b[:, 2])
        episode_lengths += 1
        episode_xy_error += xy_error
        episode_yaw_error += yaw_error

        with torch.inference_mode():
            actions = policy(obs)
            obs, _, dones, _ = env.step(actions)
            if version.parse(installed_version) >= version.parse("4.0.0"):
                policy.reset(dones)

        done_ids = torch.nonzero(dones.to(dtype=torch.bool), as_tuple=False).flatten()
        if len(done_ids) > 0:
            terminated = raw_env.reset_terminated[done_ids].detach().cpu().tolist()
            timed_out = raw_env.reset_time_outs[done_ids].detach().cpu().tolist()
            for local_index, env_id_tensor in enumerate(done_ids):
                env_id = int(env_id_tensor.item())
                length = max(1, int(episode_lengths[env_id].item()))
                fell = bool(terminated[local_index])
                timeout = bool(timed_out[local_index])
                ep: dict[str, object] = {
                    "fell": int(fell),
                    "timeout": int(timeout),
                    "xy_error": float((episode_xy_error[env_id] / length).item()),
                    "yaw_error": float((episode_yaw_error[env_id] / length).item()),
                    "length": length,
                }
                if args_cli.metric == "semantic":
                    forward_distance = float(forward[env_id].detach().cpu().item())
                    max_forward_distance = float(max_forward[env_id].detach().cpu().item())
                    semantic_pass, strong_pass = evaluate_semantic_pass(
                        max_forward_distance_m=max_forward_distance,
                        fell=fell,
                        criteria=criteria,
                    )
                    ep.update(
                        {
                            "forward_distance_m": forward_distance,
                            "max_forward_distance_m": max_forward_distance,
                            "semantic_pass": int(semantic_pass),
                            "strong_pass": int(strong_pass),
                        }
                    )
                completed.append(ep)
                episode_lengths[env_id] = 0
                episode_xy_error[env_id] = 0.0
                episode_yaw_error[env_id] = 0.0
                max_forward[env_id] = 0.0

            start_x[done_ids] = robot.data.root_pos_w[done_ids, 0].detach()

        steps += 1

    env.close()

    if len(completed) == 0:
        raise RuntimeError("Evaluation finished without completed episodes. Increase --max_steps or reduce --num_episodes.")

    episodes = completed[: args_cli.num_episodes]
    output_csv = Path(args_cli.output_csv).resolve()
    if args_cli.metric == "timeout":
        row = _timeout_row(episodes, checkpoint, num_envs)
        fieldnames = TIMEOUT_FIELDNAMES
    else:
        row = _semantic_row(episodes, checkpoint, num_envs)
        fieldnames = SEMANTIC_FIELDNAMES
    _write_row(output_csv, row, fieldnames, append=args_cli.append)

    print("[INFO] Evaluation complete")
    print(f"[INFO] Metric: {args_cli.metric}")
    print(f"[INFO] Run: {args_cli.eval_name}")
    print(f"[INFO] Episodes: {len(episodes)}")
    if args_cli.metric == "timeout":
        print(f"[INFO] Timeout rate: {row['timeout_rate']}")
    else:
        print(f"[INFO] Semantic pass rate: {row['semantic_pass_rate']}")
        print(f"[INFO] Strong pass rate: {row['strong_pass_rate']}")
    print(f"[INFO] Fall rate: {row['fall_rate']}")
    print(f"[INFO] Wrote: {output_csv}")


if __name__ == "__main__":
    main()
    simulation_app.close()
