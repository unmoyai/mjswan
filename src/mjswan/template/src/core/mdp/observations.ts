/**
 * mjlab MDP observation mirrors.
 *
 * Each class mirrors a function from mjlab.envs.mdp.observations, using the
 * exact same snake_case name so the policy JSON can reference them directly:
 *
 *   {"name": "joint_pos_rel", "scale": 0.5}
 *   {"name": "base_lin_vel"}
 *   {"name": "projected_gravity"}
 *   {"name": "root_height"}
 *
 * The JS implementation follows the same pattern shown in the proposal:
 * a simple function over PolicyState with no batching or history.
 */

import { ObservationBase } from '../observation/ObservationBase';
import type { ObservationConfig } from '../observation/ObservationBase';
import { normalizeQuat, quatApplyInv } from '../observation/math';
import type { PolicyState } from '../policy/types';
import type { PolicyRunner } from '../policy/PolicyRunner';

// ---------------------------------------------------------------------------
// joint_pos_rel
// mjlab: asset.data.joint_pos - asset.data.default_joint_pos
//
// JS equivalent of the proposal:
//   function joint_pos_rel(state, opts = {}) {
//     const pos = state.jointPos;
//     const def = state.defaultJointPos;
//     const scale = opts.scale ?? 1.0;
//     const out = new Float32Array(pos.length);
//     for (let i = 0; i < pos.length; i++) out[i] = (pos[i] - def[i]) * scale;
//     return out;
//   }
// ---------------------------------------------------------------------------
class JointPosRel extends ObservationBase {
  private scale: number;

  constructor(runner: PolicyRunner, config: ObservationConfig) {
    super(runner, config);
    this.scale = typeof config.scale === 'number' ? config.scale : 1.0;
  }

  get size(): number {
    return this.runner.getNumActions();
  }

  compute(state: PolicyState): Float32Array {
    const pos = state.jointPos;
    const def = this.runner.getDefaultJointPos();
    const out = new Float32Array(pos.length);
    for (let i = 0; i < pos.length; i++) {
      out[i] = (pos[i] - def[i]) * this.scale;
    }
    return out;
  }
}

// ---------------------------------------------------------------------------
// base_lin_vel
// mjlab: asset.data.root_link_lin_vel_b  (body frame)
// ---------------------------------------------------------------------------
class BaseLinVel extends ObservationBase {
  get size(): number {
    return 3;
  }

  compute(state: PolicyState): Float32Array {
    const vel = state.rootLinVel ?? new Float32Array(3);
    const quat = normalizeQuat(state.rootQuat ?? [1, 0, 0, 0]);
    return new Float32Array(quatApplyInv(quat, vel));
  }
}

// ---------------------------------------------------------------------------
// base_ang_vel
// mjlab: asset.data.root_link_ang_vel_b  (body frame)
// ---------------------------------------------------------------------------
class BaseAngVel extends ObservationBase {
  get size(): number {
    return 3;
  }

  compute(state: PolicyState): Float32Array {
    return new Float32Array(state.rootAngVel ?? new Float32Array(3));
  }
}

// ---------------------------------------------------------------------------
// projected_gravity
// mjlab: asset.data.projected_gravity_b
// ---------------------------------------------------------------------------
class ProjectedGravity extends ObservationBase {
  get size(): number {
    return 3;
  }

  compute(state: PolicyState): Float32Array {
    const quat = normalizeQuat(state.rootQuat ?? [1, 0, 0, 0]);
    return new Float32Array(quatApplyInv(quat, [0, 0, -1]));
  }
}

// ---------------------------------------------------------------------------
// root_height
// mjlab: asset.data.root_pos_w[:, 2:3]
// ---------------------------------------------------------------------------
class RootHeight extends ObservationBase {
  get size(): number {
    return 1;
  }

  compute(state: PolicyState): Float32Array {
    return new Float32Array([state.rootPos?.[2] ?? 0]);
  }
}

// ---------------------------------------------------------------------------
// Registry — names match mjlab function names exactly (snake_case)
// ---------------------------------------------------------------------------
type ObsCtor = new (runner: PolicyRunner, config: ObservationConfig) => ObservationBase;

export const MdpObservations: Record<string, ObsCtor> = {
  joint_pos_rel: JointPosRel,
  base_lin_vel: BaseLinVel,
  base_ang_vel: BaseAngVel,
  projected_gravity: ProjectedGravity,
  root_height: RootHeight,
};
