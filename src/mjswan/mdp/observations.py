"""mjlab MDP observation factories for mjswan.

Each function mirrors a function from mjlab.envs.mdp.observations using the
exact same name.  Calling a factory returns an ObsTerm that emits the
corresponding JSON entry referencing the JS implementation in
core/mdp/observations.ts.

Example:
    from mjswan.mdp import observations as Obs

    scene.add_policy(
        name="velocity",
        policy=onnx_model,
        observations=[
            Obs.base_lin_vel(),
            Obs.projected_gravity(),
            Obs.joint_pos_rel(scale=0.5),
            Obs.root_height(),
        ],
    )

Emits:
    {"obs_config": {"policy": [
        {"name": "base_lin_vel"},
        {"name": "projected_gravity"},
        {"name": "joint_pos_rel", "scale": 0.5},
        {"name": "root_height"}
    ]}}
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ObsTerm:
    """A reference to a JS-side MDP observation function.

    At build time this serializes to a single entry in obs_config[group][].
    The JS PolicyRunner resolves `name` against the Observations registry,
    which includes the MdpObservations from core/mdp/observations.ts.
    """

    name: str
    params: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, **self.params}


# ---------------------------------------------------------------------------
# Root state mirrors
# ---------------------------------------------------------------------------


def base_lin_vel(**kw: Any) -> ObsTerm:
    """Root linear velocity in the body frame.

    mjlab: asset.data.root_link_lin_vel_b
    """
    return ObsTerm("base_lin_vel", dict(kw))


def base_ang_vel(**kw: Any) -> ObsTerm:
    """Root angular velocity in the body frame.

    mjlab: asset.data.root_link_ang_vel_b
    """
    return ObsTerm("base_ang_vel", dict(kw))


def projected_gravity(**kw: Any) -> ObsTerm:
    """Gravity vector projected into the body frame.

    mjlab: asset.data.projected_gravity_b
    """
    return ObsTerm("projected_gravity", dict(kw))


def root_height(**kw: Any) -> ObsTerm:
    """Height of the root body above the ground plane (rootPos.z).

    mjlab: asset.data.root_pos_w[:, 2:3]
    """
    return ObsTerm("root_height", dict(kw))


# ---------------------------------------------------------------------------
# Joint state mirrors
# ---------------------------------------------------------------------------


def joint_pos_rel(*, scale: float = 1.0, **kw: Any) -> ObsTerm:
    """Joint positions relative to default pose.

    mjlab: asset.data.joint_pos - asset.data.default_joint_pos
    """
    p: dict[str, Any] = {}
    if scale != 1.0:
        p["scale"] = scale
    p.update(kw)
    return ObsTerm("joint_pos_rel", p)


__all__ = [
    "ObsTerm",
    "base_lin_vel",
    "base_ang_vel",
    "projected_gravity",
    "root_height",
    "joint_pos_rel",
]
