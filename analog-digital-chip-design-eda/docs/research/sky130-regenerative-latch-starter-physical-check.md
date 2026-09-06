# Sky130 Regenerative Latch Starter Physical Check

The first real-device latch physical slice is now present in
`layout-workbench/cells/sky130_regenerative_latch_starter.mag`.

The cell contains four Sky130 `nfet_01v8` transistor geometries and named
sense-P, sense-N, output, and common-tail ports. Magic extracts four NMOS
devices and reports zero DRC errors. The generated artifact is recorded at
`evidence/aimc-simulator-adapters/sky130-regenerative-latch-starter-physical-check.json`.

Magic extraction now shows the two feedback devices share the opposite output
domains (`out_p` and `out_n`) and that each feedback gate is driven by
the opposite output label. This closes the geometry-to-extraction feedback
step, not the comparator step. Extracted transient regeneration, latch
kickback, noise, mismatch, and LVS against a matching schematic remain to be
proven.
The analog converter gate therefore remains guarded.

## Next gate

Create a matching schematic netlist, add clocked reset/precharge behavior, and
run bounded extracted transient polarity tests with the Sky130 model. Only then
compare regeneration time and kickback against the converter timing/error
budget.

The first structural extracted transient is recorded in
`evidence/aimc-simulator-adapters/sky130-extracted-regenerative-latch-starter-transient.json`.
Using the exact extracted connectivity and parasitic capacitors with a bounded
level-1 MOS model, all four cases regenerate to roughly 1.05--1.09 V output
differential, but only 2/4 input polarities resolve correctly. The negative
input cases fall into the same polarity, so startup symmetry and polarity are
not closed. This is structural evidence, not Sky130-model, noise, mismatch, or
converter signoff.

A matched physical PMOS precharge pair is now also present in
`layout-workbench/cells/sky130_pmos_precharge_pair_starter.mag`. Magic extracts
two PMOS devices with zero DRC errors and named `precharge_p`, `precharge_n`,
`vdd`, and `reset` nets. Its evidence is recorded in
`sky130-pmos-precharge-pair-physical-check.json`. The pair is intentionally
still separate from the latch until the integrated parent route and extracted
Sky130 transient are proven.

The flat integrated parent is now DRC-clean and extracts four NMOS feedback
devices plus two PMOS precharge devices on one `reset` net. Its structural
transient is recorded in
`sky130-flat-latch-precharge-extracted-transient.json`: all four cases
converge and regenerate, but only 2/4 resolve the requested input polarity.
The reset phase is therefore physically integrated but the post-reset decision
is not yet robust.

The follow-up input/feedback strength sweep is recorded in
`sky130-flat-latch-input-strength-sweep.json`. In the structural model, an
approximately 6x sense-device strength with 0.75--1x feedback strength reaches
3/4 cases, but still misses the smallest positive `+0.5 mV` decision. This is
a sizing target for a physical revision, not evidence that the current layout
has those widths.

The first physical sizing candidate, with both sense diffusions widened to a
5x height while retaining the feedback/precharge geometry, is recorded in
`sky130-wide-input-latch-precharge-extracted-transient.json`. It remains
DRC-clean and extracts correctly, but the integrated structural transient
still passes only 2/4 polarities. Widening the sense pair alone is therefore
not sufficient; feedback weakening or a clocked tail/evaluation stage is still
required.

A real clocked-tail NMOS has now been integrated into a seven-device flat
parent. Magic extraction reports five NMOS devices, two PMOS precharge devices,
zero DRC errors, and distinct `tail`, `eval`, `vss`, `reset`, `out_p`, and
`out_n` nets. The extracted structural transient with the widened tail was
extended to 10 ns; it remained below 0.1 V differential and resolved only one
polarity. This candidate is therefore rejected as an evaluation-strength fix,
despite passing geometry and extraction.

Two physical co-tuning candidates were then extracted and tested. The 5x sense
pair with 2x feedback gate length is DRC-clean but passes only 1/4 transient
decisions. The intermediate 1.33x feedback-length version is also DRC-clean
and returns 2/4, with the fixed bias direction reversed. These results rule
out simple width/length tuning as sufficient; a clocked tail/evaluation path
or explicit offset cancellation is now required.

A precharge experiment and a 0--10 fF output-balance sweep are also recorded
in `sky130-extracted-latch-precharge-transient.json`. Precharge equalizes both
outputs to within microvolts, but the latch still resolves only 2/4 polarities;
every tested compensation value has the same 2/4 result. The next revision
therefore needs physical clocked reset/precharge and matched evaluation
strength, not just an added output capacitor.
