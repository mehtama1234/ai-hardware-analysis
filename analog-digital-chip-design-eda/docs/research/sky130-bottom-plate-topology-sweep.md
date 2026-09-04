# Sky130 Bottom-Plate Topology Sweep

This page records the comparison between the current rail-contention cell and single-rail bottom-plate alternatives. The measured evidence is in `evidence/aimc-simulator-adapters/sky130-bottom-plate-topology-sweep.md`.

The follow-up gate-headroom diagnostic is in
`evidence/aimc-simulator-adapters/sky130-pmos-gate-overdrive-diagnostic.md`.
Driving the selected PMOS gate to `-0.6 V` during redistribution completes
both high-code trials, but code `14 -> 15` spacing is only `17.118 mV` versus
the `56.25 mV` 4-bit half-LSB target. Gate overdrive alone is therefore rejected
as the topology repair; the charge-transfer path or bottom-plate waveform must
change.

A follow-up strength sweep is in
`evidence/aimc-simulator-adapters/sky130-bottom-switch-strength-diagnostic.md`.
Increasing the PMOS bottom-plate switch to `2x` and `4x` completes both
high-code trials, but produces only `17.265 mV` and `17.250 mV` of code
`14 -> 15` spacing. Stronger devices alone are therefore also rejected as the
repair.

An isolated `4x` LSB-capacitor ratio test is recorded in
`evidence/aimc-simulator-adapters/sky130-lsb-ratio-diagnostic.md`. It measures
all codes `12-15`, but produces adjacent spacings of `293.782 mV`,
`-104.561 mV`, and `144.058 mV`; the transfer is non-monotonic. Increasing
only the LSB capacitor is therefore rejected too. The next design must
rebalance the complete charge-transfer network and validate all codes.

A full-array `8x` capacitor-scale diagnostic is recorded in
`evidence/aimc-simulator-adapters/sky130-full-array-cap-scale-diagnostic.md`.
It measures codes `12-15` with monotonic spacings of `263.548 mV`,
`208.063 mV`, and `96.855 mV`, exceeding the `56.25 mV` half-LSB target.
However, the top plate reaches `2.544 V`, above the legal `1.8 V` supply.
This confirms that charge-transfer ratio is involved, but the simple full-array
scale is rejected as a physical implementation.

The follow-up zero-common-mode all-code run is recorded in
`evidence/aimc-simulator-adapters/sky130-cap-scale-common-mode-all-code.md`.
Although it measures `16/16` codes and preserves all comparator signs, the
transfer is non-monotonic: code `3 -> 4` is `-123.557 mV`, code `7 -> 8` is
`-855.492 mV`, and code `11 -> 12` is `-160.534 mV`. The focused upper-code
result was therefore not sufficient. The common-mode change is rejected and
the charge-transfer network still needs a complete redesign.

The MSB timing check is recorded in
`evidence/aimc-simulator-adapters/sky130-msb-transfer-timing-diagnostic.md`.
Extending redistribution from `5 ns` to `20 ns` changes code `7 -> 8` from
`-855.492 mV` to `-94.577 mV`, but does not restore monotonicity. Timing alone
is rejected; the next candidate must change the MSB charge-transfer topology.

The MSB capacitor-ratio sweep is recorded in
`evidence/aimc-simulator-adapters/sky130-msb-cap-ratio-diagnostic.md`.
Ratios from `0.125x` through `2x` leave code `7 -> 8` reversed, from
`-1269.695 mV` to `-841.235 mV`, while comparator polarity remains correct.
Ratio-only sizing is rejected; the next candidate needs explicit MSB
precharge/isolation or a different DAC architecture.

The targeted MSB-switch scale check is recorded in
`evidence/aimc-simulator-adapters/sky130-msb-switch-scale-diagnostic.md`.
At `4x`, code `7 -> 8` remains reversed by `-224.255 mV`; at `2x`, code 7
does not converge. Selected-device sizing is rejected as well.

The thermometer-coded equal-unit-capacitor candidate is recorded in
`evidence/aimc-simulator-adapters/sky130-thermometer-dac-comparator-summary.md`. It
uses sixteen equal unit capacitors and selects one additional unit per code,
avoiding a binary MSB capacitor. With `1 pF` units, `2x` bottom-switch sizing,
zero-volt sampled input, and the existing long-acquisition comparator fixture,
the bounded `90 s` full run measures `12/16` codes: codes `0`, `1`, `14`, and
`15` exceed that convergence budget. The converged interior sequence, codes
`2-13`, is monotonic with approximately `56.85 mV` adjacent spacing and
correct comparator polarity. Separate endpoint reruns with the original
`240 s` budget converge all four endpoint codes; code `0` reaches `-1.438 mV`
and the upper pair measures `56.862 mV` spacing. The focused `7,8` probe also
passes, but the full candidate still fails the practical convergence and legal
range contract. This is evidence that equal-unit charge transfer can restore
local spacing, not a physical converter or SAR acceptance result. The next
topology must improve endpoint initialization/headroom and runtime while
retaining the measured interior spacing, then repeat one bounded all-code run
before calibration.

A source-acquisition cutoff of `2.59 ns` then produces a complete `16/16` run:
minimum spacing is `56.299 mV` versus the `56.25 mV` target, maximum top plate
is `0.851292 V`, the transfer is monotonic, and all polarities are correct.
However, code 15 must reach approximately `1.6875 V` for full 4-bit range;
logical codes `8-15` collapse in the calibration map. This is only a
local-spacing candidate, not a full-range converter. A 32-unit, two-units-per-
code range extension was also rejected at `48.71 mV` (`2x` switches) and
`52.75 mV` (`4x` switches). The summary is recorded in
`evidence/aimc-simulator-adapters/sky130-thermometer-dac-comparator-summary.md`.

A `0.25x` source-switch sizing trial preserved polarity and legal range but
reduced code `0 -> 1` spacing to `29.92 mV` and the maximum measured top plate
to `0.253 V`. Smaller source switches therefore fail acquisition drive; the
next full-range design needs a split or bootstrapped charge-transfer path.

A bootstrapped source-gate diagnostic (`0.5x` source switches with `+0.6 V`
overdrive) converged at all four endpoints and preserved legal range, but
minimum spacing was `55.59 mV` and code 15 remained `0.891 V`. Gate drive alone
is rejected; the source interface needs architectural isolation or a different
charge-transfer ratio.

A split odd/even boundary trial with eight coarse units and one half-size fine
capacitor converged at all four endpoints and preserved polarity, but minimum
spacing was `50.38 mV`, code 15 reached only `0.759 V`, and the low endpoint
violated the legal range. This split encoding is rejected; it does not provide
the required full-scale 4-bit transfer.

A complementary differential implementation with sixteen positive and sixteen
negative unit capacitors was then isolated at code 0. It did not converge within
`120 s`, so no threshold, range, or polarity claim is made for that branch. It
is rejected as currently implemented; any differential redesign needs a simpler
explicitly initialized fixture before another sweep.

At `0.9 V` source common mode, the differential fixture converged for codes
`0,1`, but both plates moved together (`0.722317 V` and `0.722305 V`), giving
`0 mV` differential spacing. The complementary control wiring is rejected as
non-opposing and cannot support a range claim.

The differential cell was then corrected to a true break-before-make sequence:
each bottom plate is precharged to its opposite rail and switched to its final
rail after redistribution. The corrected fixture converged on boundary codes
`0,1,14,15` with correct polarity. At both `1x` and `2x` bottom-switch sizing,
however, endpoint plates crossed the legal `0..1.8 V` range (`-113 mV` at code 0
for `1x`, `-44 mV` for `2x`). The strong differential movement is therefore
mechanism evidence that the earlier zero-motion result was a netlist bug, not
converter acceptance. The next cell needs explicit endpoint headroom control,
such as level-shifted gate drive or a redesigned charge-transfer ratio, before
an all-code SAR run is meaningful.

The next dummy-capacitance sweep produced a materially better nominal result.
With `4x` top-plate dummy capacitance, `1x` bottom switches, and `0.9 V` source
common mode, the corrected break-before-make differential DAC measured all
`16/16` codes. It had `83.5273 mV` minimum spacing, `1.7651 V` total span,
legal plate voltages, and correct polarity for every nonzero differential
case. This is a nominal DAC candidate, not yet a converter acceptance result:
the coupled calibrated SAR run measured `16/16` calibration codes and
`20/20` conversion comparisons at the stable `0.8x` level-shift setting, but
only `2/5` correct conversions. A `0.9x` setting worsened low-end convergence
to `12/14` comparisons and `1/5` correct conversions. The source
common-mode/input-range contract is therefore not yet closed.

A separate bounded endpoint probe of the same differential dummy-capacitor
family tested codes `0, 1, 14, 15` with `4x` top-plate dummy capacitance and
`2.59 ns` source acquisition. All four cases timed out before producing a
threshold. This is recorded in
`evidence/aimc-simulator-adapters/sky130-differential-dummy-endpoint-diagnostic.md`.
It is a convergence and initialization failure, not evidence of missing code
spacing; the next revision must simplify endpoint initialization and control
source common mode before another calibrated SAR run.

Adding `+0.6 V` source-switch gate overdrive did not resolve the convergence
problem: a separate `0, 15` endpoint probe measured `0/2` cases and timed out
at both endpoints. The result is recorded in
`evidence/aimc-simulator-adapters/sky130-differential-dummy-boosted-source-endpoints.md`.
Source gate overdrive alone is therefore rejected; the next revision needs a
different initialized charge-transfer cell or an explicit isolated endpoint
precharge path.

A lower-common-mode probe then tested the same PMOS-only coupled topology with a
`0.6 V` source and `0.9 V` reference at code `15`. The run still timed out after
`20 s`. This rejects scalar source/reference remapping as the repair: the next
candidate must change endpoint initialization or the charge-transfer ratio.
The bounded result is recorded in
`evidence/aimc-simulator-adapters/sky130-coupled-common-mode-headroom-probe.json`.

The same cases were rerun with the full `180 s` simulator budget to separate
slow convergence from electrical failure. Code `14` measured `2.466102 V` and
code `15` measured `2.473010 V` at the nominal map; both comparator signs were
correct, but the spacing was only `6.908 mV` and the top plate exceeded the
`1.8 V` supply. With the lower `0.6 V`/`0.9 V` map, code `15` still measured
`2.315697 V`. The authoritative range probe is recorded in
`evidence/aimc-simulator-adapters/sky130-pmos-only-high-code-range-probe.json`.
This confirms that the PMOS-only topology needs a new charge-transfer ratio,
not another scalar common-mode adjustment.

An opt-in temporary NMOS top-plate clamp was then tested on codes `0,1`. It
reduced the code-0 undershoot to `-0.215 mV`, but code `0 -> 1` spacing fell to
`12.54 mV` even when the clamp was released earlier. The clamp is rejected
because it loads source acquisition; endpoint initialization must be isolated
from the acquisition and redistribution paths.

An explicit top-plate dummy capacitor was then added to the coupled diagnostic
deck and tested at `8 pF` and `32 pF` for code `15`. Both cases timed out. This
rejects capacitance-only scaling as the endpoint repair; the next design must
change endpoint initialization, switch operating region, or charge-transfer
control. The result is recorded in
`evidence/aimc-simulator-adapters/sky130-coupled-top-dummy-cap-headroom-probe.json`.

The first explicit break-before-make top-plate reset was also tested: source
acquisition, an NMOS reset phase, then bottom-plate redistribution. Codes `0`
and `15` both timed out. This implementation is rejected as currently
controlled; endpoint isolation still needs a solver-friendly precharge and
device-bias design. The result is recorded in
`evidence/aimc-simulator-adapters/sky130-coupled-top-reset-probe.json`.

A minimum-width, longer-channel clamp (`W=0.42 um`, `L=1.0 um`) recovered
`57.70 mV` code `0 -> 1` spacing, but code 0 remained at `-1.387 mV`. It
therefore clears spacing but fails the legal-range gate; the clamp family is
not promoted to the converter path.
