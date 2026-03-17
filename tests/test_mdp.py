"""Tests for mjswan.mdp observation config serialization.

Factory names match mjlab.envs.mdp.observations exactly (snake_case).
The emitted JSON names must match the JS registry keys in
template/src/core/mdp/observations.ts.
"""

import json

import pytest

from mjswan.mdp.observations import (
    ObsTerm,
    base_ang_vel,
    base_lin_vel,
    joint_pos_rel,
    projected_gravity,
    root_height,
)


# ---------------------------------------------------------------------------
# ObsTerm
# ---------------------------------------------------------------------------


def test_obsterm_to_dict_name_only():
    t = ObsTerm("projected_gravity")
    assert t.to_dict() == {"name": "projected_gravity"}


def test_obsterm_to_dict_with_params():
    t = ObsTerm("joint_pos_rel", {"scale": 0.5})
    d = t.to_dict()
    assert d == {"name": "joint_pos_rel", "scale": pytest.approx(0.5)}


def test_obsterm_json_roundtrip():
    t = ObsTerm("joint_pos_rel", {"scale": 0.5})
    parsed = json.loads(json.dumps(t.to_dict()))
    assert parsed == {"name": "joint_pos_rel", "scale": 0.5}


# ---------------------------------------------------------------------------
# Factory names match mjlab exactly
# ---------------------------------------------------------------------------


def test_base_lin_vel_name():
    assert base_lin_vel().name == "base_lin_vel"


def test_base_ang_vel_name():
    assert base_ang_vel().name == "base_ang_vel"


def test_projected_gravity_name():
    assert projected_gravity().name == "projected_gravity"


def test_root_height_name():
    assert root_height().name == "root_height"


def test_joint_pos_rel_name():
    assert joint_pos_rel().name == "joint_pos_rel"


# ---------------------------------------------------------------------------
# Parameter serialization
# ---------------------------------------------------------------------------


def test_base_lin_vel_no_params():
    assert base_lin_vel().to_dict() == {"name": "base_lin_vel"}


def test_projected_gravity_no_params():
    assert projected_gravity().to_dict() == {"name": "projected_gravity"}


def test_root_height_no_params():
    assert root_height().to_dict() == {"name": "root_height"}


def test_joint_pos_rel_default_scale_omitted():
    d = joint_pos_rel().to_dict()
    assert d == {"name": "joint_pos_rel"}


def test_joint_pos_rel_scale():
    d = joint_pos_rel(scale=0.5).to_dict()
    assert d["scale"] == pytest.approx(0.5)


def test_kwargs_pass_through():
    d = base_lin_vel(extra_param=True).to_dict()
    assert d["extra_param"] is True


# ---------------------------------------------------------------------------
# Proposal usage example — round-trips through JSON
# ---------------------------------------------------------------------------


def test_proposal_example():
    """Validates the exact usage pattern from the issue proposal."""
    obs = [
        base_lin_vel(),
        projected_gravity(),
        joint_pos_rel(scale=0.5),
        root_height(),
    ]
    obs_config = {"policy": [o.to_dict() for o in obs]}

    assert obs_config["policy"] == [
        {"name": "base_lin_vel"},
        {"name": "projected_gravity"},
        {"name": "joint_pos_rel", "scale": 0.5},
        {"name": "root_height"},
    ]

    # Verify it serializes cleanly to JSON
    raw = json.dumps(obs_config)
    parsed = json.loads(raw)
    assert parsed["policy"][0]["name"] == "base_lin_vel"
    assert parsed["policy"][2]["scale"] == pytest.approx(0.5)
