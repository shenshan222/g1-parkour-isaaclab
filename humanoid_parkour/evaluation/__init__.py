"""Evaluation helpers for course reporting."""

from .obstacle_crossing import (
    ObstacleBoundaryCriteria,
    compute_obstacle_boundary_x_m,
    evaluate_obstacle_boundary_pass,
    obstacle_group_for_terrain_type,
)
from .traversal_progress import TraversalProgressCriteria, evaluate_progress_pass, terrain_type_by_column

__all__ = [
    "ObstacleBoundaryCriteria",
    "TraversalProgressCriteria",
    "compute_obstacle_boundary_x_m",
    "evaluate_obstacle_boundary_pass",
    "evaluate_progress_pass",
    "obstacle_group_for_terrain_type",
    "terrain_type_by_column",
]
