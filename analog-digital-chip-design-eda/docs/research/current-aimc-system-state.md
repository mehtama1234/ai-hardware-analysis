# Current AIMC System State

This page is the short review page for the current analog in-memory compute workbench.

It answers three questions:

1. What works now?
2. What is still only needs-review?
3. What is still blocked?

The generated source summary is:

- `evidence/aimc-hardware-lab/current-aimc-system-state.json`
- `evidence/aimc-hardware-lab/current-aimc-system-state.md`

## Object

The object is package `pkg-e931662a01293df2` moving through the combined old workbench and new hardware lab.

The current proof starts with a backend model graph, turns that graph into hardware placement, runs lab checks, exports evidence, imports the evidence back into the backend, and refreshes claim readiness.

The browser entry points are:

- lab hub: `http://127.0.0.1:8023/`
- old workbench: `http://127.0.0.1:8024/analog-in-memory-ai-inference/software-architecture/master-review-path.html`
- backend claim readiness: `http://127.0.0.1:8025/deployment-packages/pkg-e931662a01293df2/claim-readiness`

## Current Supported Claims

The current proof supports three narrow lab claims.

`C1` is supported because the backend emits model-to-hardware placement evidence. The package has five backend operators, two structural analog candidates, converter boundaries, and fallback points.

`C4` is supported because analog error evidence and task-sensitivity evidence are attached. This is a local simulator-backed accuracy and sensitivity claim, not a full pretrained-model claim.

`C5` is supported because the digital control path has RTL, synthesis, and exploratory OpenLane physical-flow evidence. This is a bounded digital-control implementation claim, not full-chip signoff.

## Current Needs-Review Claims

`C2` latency is still needs-review.

The current runtime record is useful because it carries local RTL/runtime behavior, generated governor cases, fallback events, synthesis context, and OpenLane context. It is still not a measured board trace.

`C3` energy is still needs-review.

The current power record is useful because it carries local OpenLane-derived power and thermal context. It is still not meter-backed measured power, and measured energy requires runtime and power evidence tied to the same runtime trace ID, package, workload, board, start time, and end time.

## Current Blocked Claim

Production readiness is blocked.

That is correct. The current system does not yet prove calibrated silicon, analog macro layout, package reliability, thermal envelope, repeated-board behavior, manufacturing yield, test insertion, customer operating limits, or tapeout signoff.

## Simulator State

AIHWKIT and CrossSim are installed and exercised through the bridge.

The current executable result is:

- AIHWKIT adapter: available
- CrossSim adapter: available
- small fixture payloads: both wrote payloads
- tensor-shaped backend MatMul payloads: both wrote payloads
- trained-weight and larger model-shaped AIHWKIT payloads: ran but exceeded the positive-claim residual threshold
- trained-weight and larger model-shaped CrossSim payloads: wrote passing payloads

This does not mean the whole model is proven. It means the simulator path works and the guarded importer separates passing evidence from threshold-fail evidence.

## Placement State

Structural placement and residual-aware placement are separate.

The backend has five operators:

- `dense1.matmul`
- `dense1.bias`
- `dense1.relu`
- `dense2.matmul`
- `dense2.bias`

Only the two MatMul rows are structural analog candidates.

After residual-aware filtering, the two MatMul rows remain analog-allowed. The selected evidence source is `deep_transformer_mlp_stack`, using the `fixed_weight_matmul_family_match` policy. The accepted tool is CrossSim. Bias and ReLU stay digital because simulator evidence for fixed-weight MatMul does not prove non-MatMul operations.

## What The 50-Gate Proof Checks

The broad proof command is:

```bash
./scripts/check_aimc_bridge.sh
```

The latest passing run checks:

- backend hardware placement import
- SPICE and analog-tile evidence
- model-impact governor requests
- generated RTL traces
- Yosys synthesis
- OpenLane readiness
- AIHWKIT and CrossSim status
- simulator payload generation
- guarded simulator payload import
- calibrated residual governor bridge
- residual-aware placement
- hardware-lab evidence export
- strict analog simulator/tool evidence export
- site build
- project validation
- cross-repo backend proof
- residual-aware placement API
- residual-aware placement archive

## Allowed Claim

The system can say:

The combined AIMC workbench has a passing local evidence loop from backend model graph to analog/digital placement, simulator payloads, RTL checks, evidence import, residual-aware placement, archive, and claim readiness. Selected fixed-weight MatMul rows can request analog service under the current local CrossSim-backed residual policy.

## Refused Claim

The system cannot say:

- the whole foundation model runs correctly on analog hardware
- AIHWKIT and CrossSim agree on the whole model
- threshold-fail AIHWKIT payloads support positive analog placement
- local RTL timing is measured board latency
- OpenLane power is measured energy
- measured runtime and measured power can be mixed across different runtime trace IDs
- analog macro layout is complete
- silicon is calibrated
- production readiness is achieved
- tapeout is ready

## Next Handoff

The next meaningful work is stronger evidence, not broader wording.

The clearest next upgrade is now the converter handoff, not more prose.

For the short end-to-end map of how the current circuit evidence ties back to model placement and the strict accepted converter gate, read `aimc-remaining-proof-spine.html`.

1. Keep the passing active-macro handoff as a bounded result: the extracted frontend can hand a signed signal to a gain block in one deck.
2. Fix the Sky130 transistor input-stage handoff. The direct gate-ramp check passes, and the assisted extracted-frontend gate-startup deck now runs, but only one polarity preserves sign and output margin. A targeted passive coupling sweep found no passing passive setting. A bare source follower runs but collapses the tiny differential signal. After fixing the too-short runner timeout, the same preamp bias passes with measured sense-voltage sources, the bias sweep finds one passing setting, and the OP map finds one valid DC point. The exact known-good input-stage deck also reproduces at both the old target input and the smaller measured frontend input. The extracted-frontend preamp now runs and preserves sign, but the output margin is too small; a gain sweep finds no simple setting that reaches the margin. The capacitance budget says the physical target is about `1.64x` better useful coupling or about `1.64x` less wasted sense capacitance. A lower-waste-only scaled-RC candidate preserves both signs but still misses margin. A combined useful-coupling plus lower-waste scaled-RC candidate also preserves both signs but still reaches only about `69.5 uV`, below the `500 uV` output target. An ideal low-input-capacitance active-isolation macro shows enough raw output margin, but raw output keeps a one-sided sign bias. With zero-input offset subtraction, the unity low-cap active-isolation macro passes both signs with at least about `610 uV` corrected margin. The first Sky130 transistor isolation-pair replacement now measures every case and reaches enough corrected magnitude in the small and medium settings, but its corrected sign is inverted. A direct output swap of the prior best setting does not solve the handoff; both signal cases time out. Re-reading the stable transistor measurements with an explicit converter polarity contract gives two schematic-level passing settings, because the sign error is deterministic inversion rather than random ambiguity.
3. Carry the polarity contract into the latch/SAR input definition. The joined latch-risk page says the best transistor handoff has about `1.59x` the required output margin, but the best existing latch sizing still has about `2.99x` too much kickback relative to the 12-bit half-LSB line. The isolated-latch work order now names the next circuit target: preserve the polarity contract, keep both signs resolving, reduce kickback by about `3.0x` to reach the hard half-LSB line or about `6.0x` for a cleaner design target, and then measure offset, noise, decision time, and wrong-code risk. The first source-follower isolated-latch candidate did not produce usable measurements; all four targeted signal cases timed out. The sampled internal decision-capacitor candidate also did not produce a usable branch; it measured zero cases and timed out on most cases. The two-phase preamp-then-latch candidate also timed out on both target-edge cases. The isolated-latch debug ladder now records the pattern: three candidate branches, zero measured candidate cases, and nine timed-out cases. The first preamp-alone transient debug also timed out on both signs with the latch removed. The first OP-only preamp debug used too short a timeout. The old known-good OP reproduction still passes, and the current known-good-shape OP rerun now passes both signs after matching that timeout. The known-good-shape transient from the measured OP initial point also passes both signs with margin and settling. The first latch-alone run from those measured preamp voltages measured both cases without timeout but resolved with inverted polarity. Swapping the measured preamp voltages into the latch input fixes latch-alone polarity: both cases measure and both resolve. The clock-timing sweep with that swapped mapping measures all six delayed-clock cases without timeout, but every case fails under the old `outn - outp` signed-output definition. Reinterpreting those same measured rails shows the real convention: the source contract is matched by `outp - outn`, with six of six cases correct. Carrying that convention into the direct coupled sample-hold/latch fixture still does not pass: both signs measure without timeout, but the sampled differential is only about `49 uV` before latch fire, the latch kickback moves it by about `12.0 mV`, no case stays below the 12-bit half-LSB line, and no case resolves with the required source polarity. Tiny capacitive latch-input isolation is the first coupled schematic branch that does pass this narrow gate: `0.1 fF` and `0.2 fF` coupling capacitors both resolve both signs, all four cases measure without timeout, worst sampled differential kickback is about `202 uV`, and the 12-bit half-LSB line is about `220 uV`. The input-range stress keeps that branch alive: both caps pass both signs at one, two, and five times the target-edge differential, for `12/12` measured and passing schematic cases, with worst kickback still about `202 uV`. This is still only schematic-level converter-readout evidence. The next executable move is to stress clock timing and then offset/noise before extracted layout, SAR logic, or accepted post-layout economics can be claimed.
4. Only then fill the strict post-layout payload with same-run energy, latency, noise, area, sharing, netlist, model, and rerun evidence.
5. Feed that accepted converter package back into break-even and residual-aware placement.

Until those upgrades exist, the correct current state is: local placement and local accuracy evidence are supported; the active-macro handoff is supported; the transistor readout can amplify measured sense voltages in controlled tests; the extracted frontend still does not reliably drive the real transistor gates; latency and energy need review; production remains blocked.
