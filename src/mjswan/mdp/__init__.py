"""mjlab-style MDP component configuration for mjswan.

Provides Python factory functions that mirror mjlab's MDP vocabulary.
Each function returns an ObsTerm that emits the correct JS observation
class name into the policy config JSON at build time.

Example:
    from mjswan.mdp import observations as Obs

    policy = scene.add_policy(
        name="velocity",
        policy=onnx_model,
        observations=[
            Obs.projected_gravity(history_steps=3),
            Obs.joint_pos(subtract_default=True, scale=0.5),
            Obs.joint_vel(scale=0.05),
            Obs.prev_actions(history_steps=4),
            Obs.velocity_command(),
        ],
    )
"""

from . import observations

__all__ = ["observations"]
