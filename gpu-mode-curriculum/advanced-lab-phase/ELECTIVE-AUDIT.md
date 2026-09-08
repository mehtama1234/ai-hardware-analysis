# Specialist elective inventory

Initial local-artifact audit, not acceptance of these research topics. Six
`lab.py` programs listed below were executed directly with Python; all returned
`ran-cpu-proxy`. Topic 8 now also has a separate deterministic vectorized
grid-world artifact with a scalar oracle and an accepted single-T4 CUDA run;
that evidence is intentionally narrower than Isaac Gym or policy-quality
claims. The other lesson proxies below still do not launch their named external
systems or device kernels.

| Handbook topic | Closest inspected starting point | Observed behavior | Required end-to-end extension |
|---|---|---|---|
| 8: accelerated RL | [OpenEnv-titled lesson](../lesson-labs/lesson-023-mega-lecture-91-reinforcement-learning-agents-openenv/lab.py), [vectorized CUDA rollout](../rl-gpu-simulation/README.md) | Proxy lesson remains modeled; vectorized grid-world passes scalar transition and goal-directed policy/termination/reset oracles, and a fixed supervised policy reaches 100% held-out episodic success on a Tesla T4 | Physics/environment fidelity, zero-copy policy integration, trained RL optimization, and broader hardware evidence |
| 10: formal layouts | [CuTe algebra lesson](../lesson-labs/lesson-011-lecture-103-fundamentals-of-cute-layout-algebra-and-category-the/lab.py), [layout-algebra contract lab](../layout-algebra/README.md) | Host bijection/inverse checks, exact blocked/XOR offset emission from Triton CUDA on Tesla T4, and a native CUDA shared-memory probe showing 32-way-conflict versus XOR bank-spread timing | Version-pinned CuTe execution, richer layout composition and alias counterexamples, profiler-level bank/occupancy attribution; proof scope remains distinct from mapping correctness |
| 11: video/analytics | [FastVideo-titled lesson](../lesson-labs/lesson-055-lecture-59-fastvideo/lab.py) | Stride model, softmax, fixed KV-size formula | Real bounded video or dataframe workload, reference outputs, representative inputs and measured pipeline stages |
| 17: CXL/disaggregated memory | [Topology model](../distributed-topology/distributed_topology/planner.py) is adjacent work only | Analytical capacity/communication model reviewed in the distributed audit; no CXL execution established | Explicit memory-tier model versus real fabric evidence, placement/migration correctness, transfer-inclusive cache access and application timing |
| 19: edge/consumer hardware | [WebGPU-titled lesson](../lesson-labs/lesson-091-lecture-27-gpu-cpp-portable-gpu-compute-using-webgpu/lab.py), [Metal-titled lesson](../lesson-labs/lesson-068-lecture-49-low-bit-metal-kernels/lab.py) | WebGPU proxy emits stride/KV formulas; Metal proxy emits stride and INT4 level constants | Compile/execute a native consumer-platform operation, compare identical outputs, account for transfers and device memory; no portability inferred from names |
| 22: multimodal routing | [Cornserve-titled lesson](../lesson-labs/lesson-021-lecture-93-cornserve-easy-fast-and-scalable-multimodal-ai/lab.py) | Four-value softmax and KV-size formula | Actual modality inputs/encoders, alignment and request-identity tests, routed stage execution, bounded backpressure and stage-level latency |
| 23: GPU physics/worlds | OpenEnv proxy above is only an adjacent starting point | No physics integration, collision, state transition or world rollout in that program | Bounded physical system with declared integration method, scalar/state invariants, batched equivalence and device-resident rollout measurements |
| 24: career companion | [Existing advanced exercises](EXERCISES.md) | Written derivations and executable reference links, not a hiring-market study | Role-to-lab portfolio rubric, timed debugging/optimization exercises, reviewed solutions; current hiring/compensation claims require separately dated primary evidence |

The OpenEnv lesson's inspected `measure.py` calls its starter and marks correctness
passed when the process succeeds and emits a nonempty `checks` payload. It does
not assert that the output implements environment transitions or any other
title-specific behavior. Generated lesson metadata and proxy checks must not be
used to infer specialist implementation coverage.

Search scope: filenames and Python text in `gpu-mode-curriculum` and
`gpu-kernels-serving-lab`, followed by inspection/execution of the concrete files
above. No repository-wide absence claim follows from this bounded search.
The external projects named by the handbook were not audited in this pass.
Primary sources, complete prerequisite chains and acceptance tests remain open.

## Dependency order

Lay out mathematical and scalar references before native implementations. Reuse
the tested primitives and provenance utilities where applicable. RL and physics
share state-transition infrastructure; video and multimodal serving share request
identity, staging and backpressure requirements. Consumer-platform execution and
real CXL measurements require suitable approved hardware; local models must stay
explicitly separate. Career exercises should cite accepted labs, not scaffold
counts or hypothetical performance claims.
