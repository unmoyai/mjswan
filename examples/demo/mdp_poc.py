"""POC: mjlab MDP observation config via mjswan.mdp.

Demonstrates the Python → JS mapping proposed in issue #32.

mjlab MDP functions implemented in JS (core/mdp/observations.ts):
  - joint_pos_rel    — asset.data.joint_pos - asset.data.default_joint_pos
  - base_lin_vel     — asset.data.root_link_lin_vel_b  (body frame)
  - projected_gravity — asset.data.projected_gravity_b
  - root_height      — asset.data.root_pos_w[:, 2:3]

Python factories use the exact same names as mjlab:

    from mjswan.mdp import observations as Obs

    policy = scene.add_policy(
        name="velocity",
        policy=onnx_model,
        observations=[
            Obs.base_lin_vel(),
            Obs.projected_gravity(),
            Obs.joint_pos_rel(scale=0.5),
            Obs.root_height(),
        ],
    )

The observations are emitted as obs_config.monitor in the policy JSON.
The vanilla Go2 policy provides obs_config.policy (required by the ONNX
model) via config_path.  The browser collects both groups; the Observations
panel shows the monitor group live.

Usage:
    uv run python examples/demo/mdp_poc.py
"""

import mujoco
import onnx

import mjswan
from mjswan.mdp import observations as Obs

go2_xml = "examples/demo/assets/unitree_go2/scene.xml"
go2_onnx = "examples/demo/assets/unitree_go2/vanilla.onnx"
go2_cfg = "examples/demo/assets/unitree_go2/vanilla.json"

spec = mujoco.MjSpec.from_file(go2_xml)
model = onnx.load(go2_onnx)

builder = mjswan.Builder()
project = builder.add_project(name="Go2 MDP POC")
scene = project.add_scene(spec=spec, name="Velocity Flat")

scene.add_policy(
    name="vanilla",
    policy=model,
    config_path=go2_cfg,
    observations=[
        Obs.base_lin_vel(),
        Obs.projected_gravity(),
        Obs.joint_pos_rel(scale=0.5),
        Obs.root_height(),
    ],
).add_velocity_command()

app = builder.build()
app.launch()
