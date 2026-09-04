# AIMC End-To-End Proof Explanation

This page explains what the project is trying to prove in plain language.

The goal is not to say that analog compute is good in general. The goal is to prove a chain:

```text
model operation
  -> analog array signal
  -> sampled voltage
  -> comparator decision
  -> digital value
  -> model-level accept or fallback
```

Every arrow in that chain can fail. A useful page should therefore explain the object being moved, what can damage it, what evidence says it survived, and what evidence is still missing.

## The Simple Question

The simple question is:

Can part of a foundation model use analog in-memory compute without corrupting the model state?

That question has two sides.

The analog side asks whether the physical circuit can produce a usable measured value. The digital side asks whether that measured value is safe to use in the model. Both sides are needed. A good analog waveform is not enough if the model is sensitive to the error. A good digital controller is not enough if the analog readout cannot produce a reliable code.

## What The Analog Array Gives Us

A digital matrix multiply stores weights in memory, moves them to arithmetic units, multiplies, adds, rounds, and stores the result again.

An analog in-memory array tries to collapse some of that movement. The weight is stored as a physical conductance. The input is driven as a voltage. The column adds current because currents naturally sum on a wire.

That is the useful idea:

```text
stored conductance x input voltage = current contribution
many current contributions on one column = analog sum
```

The cost is that the answer is now a physical signal. It has noise, offset, drift, wire loss, device mismatch, limited voltage range, and converter error. The project cannot treat it as a normal number until it is measured and checked.

## Why The Converter Is The Hard Boundary

The analog array does not hand the model a number. It hands the next circuit a voltage or current.

The converter is the boundary where that physical signal becomes a digital code. That boundary is hard because it asks a very small signal to survive several things at once:

- sampling error
- charge injection
- capacitance loading
- latch kickback
- comparator offset
- comparator noise
- layout parasitics

If the signal is smaller than these disturbances, the digital code can be wrong even if the array math was conceptually right.

That is why the current work has focused on the Sky130 frontend. We are not adding circuit pages for decoration. We are asking whether the voltage difference that represents the analog result can reach the comparator input strongly enough to be decided.

## What Is Proven Today

The current extracted Sky130 frontend work proves a narrow statement.

The balanced frontend fixed the old sign problem. The extracted sense nodes now preserve the direction of the input difference in all four checked cases.

The strong and ultra sense candidates increased useful sample-to-sense coupling. The latest ultra candidate has:

- direct sample-to-sense capacitance: `0.8 fF`
- direct coupling improvement over the first balanced starter: `9.11x`
- minimum measured sample-to-sense transfer ratio: `0.437908`
- sign preservation: `4/4` cases

This means the signal is no longer being flipped by the extracted frontend. It also means the layout change is helping.

## What Is Not Proven Today

The current result does not yet prove an accepted converter.

The transfer target before latch proof is `1.0`. The current best measured transfer is `0.437908`. That leaves about `2.28x` improvement still needed.

In simple terms: the signal arrives with the right sign, but not with enough strength.

That is why the pages must not claim latch resolution, ADC correctness, offset margin, noise margin, DRC/LVS completion, SAR conversion, or accepted post-layout converter evidence.

## Why Stronger Coupling Did Not Fully Solve It

Increasing coupling helps only if the extra coupling becomes useful voltage at the sense node.

A sense node is like a small bucket for charge. If the bucket gets larger while the signal pipe also gets larger, the final voltage may not rise as much as expected. The useful quantity is not only direct sample-to-sense capacitance. It is useful coupling divided by all the capacitance that must be moved.

That is why the sense-efficiency audit matters. It compares the balanced, strong, and ultra candidates and asks a simple physical question: how much of the added coupling becomes useful voltage at the sense node, and how much is lost into extra capacitance.

It should show:

- how much direct coupling each layout added
- how much total sense capacitance each layout carried
- how much voltage transfer actually improved
- why the transfer gain slowed down
- whether the next move should be lower wasted capacitance or an active preamp/buffer

## How This Fits The Digital System

The digital controller is not a backup paragraph. It is part of the proof.

Once the converter produces a code, the digital side must still decide whether to trust it. The mixed-signal trust boundary receives the raw code, zero point, gain, bias, residual estimate, residual budget, calibration age, and tile health. It then returns either a valid corrected value or a fallback request.

That is the full meaning of the digital governor:

```text
analog path proposes a measured value
digital boundary checks whether the value is safe
model state changes only if the check passes
```

So the project is not trying to replace digital logic with analog compute. It is trying to build a mixed system where analog does the dense repeated work only when the physical evidence and model evidence say it is safe.

## How The HTML Pages Should Flow Now

The reader should be able to move through the site in this order:

1. [Cross-Repo Loop Proof](cross-repo-aimc-loop-proof.html)
2. [Current AIMC System State](current-aimc-system-state.html)
3. [ONNX Fixture Inventory](onnx-fixture-inventory.html)
4. [Simulator To Placement Decision Boundary](simulator-to-placement-decision-boundary.html)
5. [AIHWKIT Current Tile Boundary Replay](aihwkit-current-tile-boundary-replay.html)
6. [AIHWKIT Converter Upgrade Target](aihwkit-converter-upgrade-target.html)
7. [AIHWKIT Converter Break-Even](aihwkit-converter-break-even.html)
8. [Converter Circuit Evidence Contract](converter-circuit-evidence-contract.html)
9. [Simulator To Post-Layout Gap Audit](simulator-to-post-layout-gap-audit.html)
10. [Analog Converter Layout Work Order](analog-converter-layout-work-order.html)
11. [Converter Post-Layout Evidence Contract](converter-post-layout-evidence-contract.html)
12. [Converter Post-Layout Strict Intake](converter-post-layout-strict-intake.html)
13. [First Real Converter Candidate Execution Plan](first-real-converter-candidate-execution-plan.html)
14. [First Real Converter Candidate Packet](first-real-converter-candidate-packet.html)
15. [First Real Converter Candidate Loop Strict Readiness](first-real-converter-candidate-loop-strict-readiness.html)
16. [Sky130 Balanced Frontend Sign Preservation](sky130-balanced-frontend-sign-preservation.html)
17. [Sky130 Ultra Sense Frontend Candidate](sky130-ultra-sense-frontend-candidate.html)
18. [Sky130 Frontend Sense Efficiency Audit](sky130-frontend-sense-efficiency-audit.html)
19. [Comparator Decision Margin From First Principles](comparator-decision-margin-from-first-principles.html)
20. [Passive Frontend Vs Active Preamp](passive-frontend-vs-active-preamp.html)
21. [Sky130 Frontend Input-Stage Handoff Candidate](sky130-frontend-input-stage-handoff-candidate.html)
22. [From Active Macro To Real Transistor Handoff](from-active-macro-to-real-transistor-handoff.html)
23. [Sky130 Transistor Handoff Replacement Work Order](sky130-transistor-handoff-replacement-work-order.html)
24. [Sky130 Frontend Transistor Input-Stage Handoff Candidate](sky130-frontend-transistor-input-stage-handoff-candidate.html)
25. [Final Accepted Converter Gate](final-accepted-converter-gate.html)
26. [Analog-To-Digital-To-Model Error Flow](analog-to-digital-to-model-error-flow.html)

The first pages explain why analog might be useful. The middle pages explain why the converter is the blocking physical object. The later pages explain how the digital system refuses unsafe analog results and what evidence is still missing.

The newest result is important: the active-macro handoff passes as a same-deck check, but the replacement with a real Sky130 transistor input stage currently fails or times out. That means the project has not merely said "we need a transistor handoff." It has built the handoff test and shown that the current transistor version is still not ready.

## What Has Been Written

The deeper connector pages now exist. They are the pages that make the hardware story readable across the small circuit measurements:

1. **Sky130 Frontend Sense Efficiency Audit**

   This explains why balanced, strong, and ultra frontend layouts changed transfer the way they did. The first principle is that voltage transfer improves only when useful coupling rises faster than the total capacitance that must be moved.

2. **Comparator Decision Margin From First Principles**

   This explains that a comparator is not checking an abstract positive or negative number. It resolves two physical nodes. The page connects input difference, offset, noise, kickback, latch gain, decision time, and wrong-code risk.

3. **Converter Evidence Ladder**

   This separates schematic SPICE, extracted RC, extracted transistor netlist, DRC/LVS, post-layout measurement, and accepted evidence. It stops a partial artifact from being treated as final proof.

4. **Analog-To-Digital-To-Model Error Flow**

   This explains how a physical readout error becomes a model residual, how the residual is compared to a budget, and why some model locations are allowed to use analog while others must stay digital.

5. **Final Accepted Converter Gate**

   This defines exactly what one accepted converter package must contain: one named physical object, one extracted netlist, one model setup, one rerun source, energy, latency, noise, area, sharing rule, DRC/LVS status, and same-run break-even rerun.

6. **Sky130 Frontend Input-Stage Handoff Candidate**

   This records the active-macro handoff. It proves the extracted frontend signal can be handed to a gain block in one deck, but it does not prove that a real transistor input stage can do the same job.

7. **Sky130 Frontend Transistor Input-Stage Handoff Candidate**

   This records the current failed transistor handoff. It is useful because it turns the next gap into a measured object instead of a vague task: the real input pair must preserve sign, make enough output margin, avoid timeout, and then feed the latch.

8. **From Active Macro To Real Transistor Handoff**

   This explains why the active macro was useful, why it is not enough, and what changes when the next block becomes real Sky130 transistors with loading, bias, offset, noise, timing, and convergence risk.

## The Current Big Picture

The project is past broad planning. It has a real local workflow, simulator adapters, RTL checks, synthesis, OpenLane evidence, Magic extraction, ngspice runs, frontend candidates, strict evidence gates, and a site that records what each artifact proves.

The remaining work is sharper:

```text
make the frontend signal strong enough
prove the comparator decision
package the converter evidence
feed the measured converter numbers back into simulator and placement decisions
show the final claim boundary in the frontend/backend workbench
```

Until that happens, the honest statement is:

The AIMC workbench can show a connected local proof path and several real hardware-adjacent measurements. It cannot yet claim accepted post-layout converter evidence or full foundation-model execution on analog hardware.
