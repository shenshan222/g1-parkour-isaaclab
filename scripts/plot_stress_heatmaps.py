#!/usr/bin/env python3
# Copyright (c) Humanoid Parkour Course Project.
# SPDX-License-Identifier: BSD-3-Clause

"""Plot fixed-row stress evaluation figures for report use."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


SOURCE_ORDER = ["rough", "easy", "medium", "hard", "rough_mdp", "hard_mdp"]
EVAL_ORDER = ["rough", "easy", "medium", "hard"]
EXTREME_SOURCE_ORDER = ["hard", "hard_mdp"]


@dataclass(frozen=True)
class HeatmapSpec:
    input_csv: Path
    metric: str
    title: str
    output_png: Path


SPECS = [
    HeatmapSpec(
        input_csv=Path("results/metrics/timeout_cross_terrain_stress_eval.csv"),
        metric="timeout_rate",
        title="Timeout Rate (Fixed-Row Stress)",
        output_png=Path("results/figures/timeout_stress_heatmap.png"),
    ),
    HeatmapSpec(
        input_csv=Path("results/metrics/traversal_progress_cross_terrain_stress_eval.csv"),
        metric="progress_pass_rate",
        title="Progress Pass Rate (Fixed-Row Stress)",
        output_png=Path("results/figures/progress_stress_heatmap.png"),
    ),
    HeatmapSpec(
        input_csv=Path("results/metrics/obstacle_crossing_cross_terrain_stress_eval.csv"),
        metric="obstacle_pass_rate",
        title="Obstacle Pass Rate (Fixed-Row Stress)",
        output_png=Path("results/figures/obstacle_stress_heatmap.png"),
    ),
]


def _load_matrix(spec: HeatmapSpec) -> pd.DataFrame:
    if not spec.input_csv.exists():
        raise FileNotFoundError(f"Input CSV does not exist: {spec.input_csv}")

    df = pd.read_csv(spec.input_csv)
    required = {"checkpoint_source", "eval_env", spec.metric}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"{spec.input_csv} is missing columns: {sorted(missing)}")

    df = df[df["checkpoint_source"].isin(SOURCE_ORDER) & df["eval_env"].isin(EVAL_ORDER)].copy()
    matrix = df.pivot(index="checkpoint_source", columns="eval_env", values=spec.metric)
    matrix = matrix.reindex(index=SOURCE_ORDER, columns=EVAL_ORDER)
    if matrix.isna().any().any():
        missing_cells = [
            f"{source}->{env}"
            for source in SOURCE_ORDER
            for env in EVAL_ORDER
            if pd.isna(matrix.loc[source, env])
        ]
        raise ValueError(f"{spec.input_csv} is missing heatmap cells: {missing_cells}")
    return matrix.astype(float) * 100.0


def _plot_heatmap(spec: HeatmapSpec) -> None:
    matrix = _load_matrix(spec)
    spec.output_png.parent.mkdir(parents=True, exist_ok=True)

    sns.set_theme(style="white", context="paper", font_scale=1.1)
    fig, ax = plt.subplots(figsize=(8.4, 5.2), constrained_layout=True)
    sns.heatmap(
        matrix,
        ax=ax,
        cmap="YlGnBu",
        vmin=0,
        vmax=100,
        annot=True,
        fmt=".1f",
        linewidths=0.7,
        linecolor="white",
        cbar_kws={"label": "Rate (%)"},
    )
    ax.set_title(spec.title, pad=12, fontsize=14, weight="bold")
    ax.set_xlabel("Evaluation Terrain")
    ax.set_ylabel("Checkpoint Source")
    ax.set_xticklabels([label.replace("_", " ") for label in EVAL_ORDER], rotation=0)
    ax.set_yticklabels([label.replace("_", " ") for label in SOURCE_ORDER], rotation=0)
    fig.savefig(spec.output_png, dpi=300)
    plt.close(fig)
    print(f"Wrote: {spec.output_png}")


def _read_extreme_metric(csv_path: Path, metric: str) -> dict[str, float]:
    if not csv_path.exists():
        raise FileNotFoundError(f"Input CSV does not exist: {csv_path}")
    df = pd.read_csv(csv_path)
    required = {"checkpoint_source", "eval_env", metric}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"{csv_path} is missing columns: {sorted(missing)}")

    df = df[(df["checkpoint_source"].isin(EXTREME_SOURCE_ORDER)) & (df["eval_env"] == "extreme")]
    values = dict(zip(df["checkpoint_source"], df[metric].astype(float) * 100.0))
    missing_sources = [source for source in EXTREME_SOURCE_ORDER if source not in values]
    if missing_sources:
        raise ValueError(f"{csv_path} is missing extreme rows for: {missing_sources}")
    return values


def _plot_extreme_comparison() -> None:
    metrics = [
        (
            "Timeout",
            _read_extreme_metric(Path("results/metrics/extreme_random_timeout_stress_eval.csv"), "timeout_rate"),
        ),
        (
            "Progress",
            _read_extreme_metric(
                Path("results/metrics/extreme_random_progress_stress_eval.csv"), "progress_pass_rate"
            ),
        ),
        (
            "Strong Progress",
            _read_extreme_metric(
                Path("results/metrics/extreme_random_progress_stress_eval.csv"), "strong_progress_pass_rate"
            ),
        ),
        (
            "Obstacle",
            _read_extreme_metric(
                Path("results/metrics/extreme_random_obstacle_stress_eval.csv"), "obstacle_pass_rate"
            ),
        ),
        (
            "Gap",
            _read_extreme_metric(Path("results/metrics/extreme_random_obstacle_stress_eval.csv"), "gap_pass_rate"),
        ),
        (
            "Stairs",
            _read_extreme_metric(Path("results/metrics/extreme_random_obstacle_stress_eval.csv"), "stairs_pass_rate"),
        ),
    ]

    rows = [
        {"Metric": label, "Checkpoint Source": source.replace("_", " "), "Rate (%)": values[source]}
        for label, values in metrics
        for source in EXTREME_SOURCE_ORDER
    ]
    df = pd.DataFrame(rows)

    output_png = Path("results/figures/extreme_hard_vs_hard_mdp_bar.png")
    output_png.parent.mkdir(parents=True, exist_ok=True)

    sns.set_theme(style="whitegrid", context="paper", font_scale=1.1)
    fig, ax = plt.subplots(figsize=(10.0, 5.4), constrained_layout=True)
    sns.barplot(
        data=df,
        x="Metric",
        y="Rate (%)",
        hue="Checkpoint Source",
        palette=["#4C72B0", "#55A868"],
        ax=ax,
    )
    ax.set_title("Hard vs Hard-MDP on ExtremeRandom Stress", pad=12, fontsize=14, weight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Rate (%)")
    ax.set_ylim(0, 100)
    ax.legend(title="Checkpoint Source", loc="upper right")
    ax.bar_label(ax.containers[0], fmt="%.1f", padding=3, fontsize=9)
    ax.bar_label(ax.containers[1], fmt="%.1f", padding=3, fontsize=9)
    fig.savefig(output_png, dpi=300)
    plt.close(fig)
    print(f"Wrote: {output_png}")


def main() -> None:
    for spec in SPECS:
        _plot_heatmap(spec)
    _plot_extreme_comparison()


if __name__ == "__main__":
    main()
