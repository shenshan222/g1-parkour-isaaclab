"""Humanoid Parkour — Isaac Lab external task package."""

__version__ = "0.1.0"

# Import tasks so Gym registrations run after editable install.
from . import tasks as _tasks  # noqa: F401
