# Sky130 Active Isolation Preamp Target

- status: `active_isolation_preamp_target_ready_after_passive_and_source_follower_failures`
- passive lower-waste measured cases: `2`
- passive lower-waste margin pass count: `0`
- passive combined measured cases: `2`
- passive combined margin pass count: `0`
- source-follower measured cases: `2`
- source-follower sign pass count: `0`
- source-follower margin pass count: `0`
- best passive output to target ratio: `0.139000`
- attached sense loss current x: `9.543`
- attached sense loss target x: `2.000`
- accepted post-layout written: `False`

## First Principle

The frontend is not failing because the sign is unknowable. It is failing because the next circuit stage asks too much from a tiny stored charge.

Passive capacitance edits helped define the problem, but they did not create enough output margin. The simple source follower also failed because its output did not carry the small differential voltage forward. The next active isolation stage must therefore do two jobs at once: touch the frontend lightly, then drive the preamp strongly.

## Acceptance Requirements

| requirement | plain meaning | measurement |
|---|---|---|
| `low_input_capacitance` | the isolation input must not reduce the frontend sense voltage by more than 2x | compare frontend sense voltage with and without isolation input attached |
| `differential_preservation` | both input polarities must keep the correct sign through the isolation output | two reset-pulse transient cases, one positive and one negative input difference |
| `usable_output_margin` | the preamp output difference must reach at least 0.5 mV in both polarities | same attached frontend, same Sky130 device models, same output-margin gate |
| `bounded_power_cost` | the isolation stage must report its bias current before any system break-even claim changes | integrate or record supply current for the same run that measures margin |

## Next Artifact

- script: `run_sky130_active_isolation_preamp_candidate.py`
- page: `docs/research/sky130-active-isolation-preamp-candidate.md`

## Refused Claim

does not prove an active isolation circuit, latch decision, SAR conversion, DRC/LVS, post-layout converter energy, or accepted converter evidence
