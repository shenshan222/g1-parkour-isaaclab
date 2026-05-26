# Setup

## 1. Install Isaac Lab (external)

Clone Isaac Lab outside this repository, for example:

```bash
export ISAACLAB_ROOT=/root/autodl-tmp/isaac_workspace/IsaacLab
# Follow official Isaac Lab + Isaac Sim install docs for your platform
```

Do **not** copy Isaac Lab into `g1-parkour-isaaclab`.

## 2. Install this package

```bash
export HUMANOID_PARKOUR_ROOT=/path/to/g1-parkour-isaaclab
conda activate env_isaaclab   # your Isaac Lab environment name
pip install -e "${HUMANOID_PARKOUR_ROOT}"
```

## 3. Environment variables

| Variable | Purpose |
|----------|---------|
| `ISAACLAB_ROOT` | Path to Isaac Lab clone |
| `HUMANOID_PARKOUR_ROOT` | This repo (optional; auto-detected from package) |
| `HUMANOID_PARKOUR_RUNS_ROOT` | Logs & checkpoints (gitignored, use large disk) |
| `OMNI_KIT_ALLOW_ROOT` | Required on some cloud GPUs |
| `VK_ICD_FILENAMES` | Vulkan ICD for rendering |

Edit defaults in `scripts/_env.sh` for your server.

## 4. Verify registration

```bash
python -c "
import gymnasium as gym
import humanoid_parkour
ids = [
    'Isaac-Velocity-Parkour-G1-Easy-v0',
    'Isaac-Velocity-Parkour-G1-Easy-Play-v0',
    'Isaac-Velocity-Parkour-G1-Medium-v0',
    'Isaac-Velocity-Parkour-G1-Medium-Play-v0',
    'Isaac-Velocity-Parkour-G1-Hard-v0',
    'Isaac-Velocity-Parkour-G1-Hard-Play-v0',
]
print('registered:', all(i in gym.registry for i in ids))
"
```

Requires Isaac Lab / `isaaclab` on `PYTHONPATH`.
