# Sky130 Thermometer DAC Comparator Summary

- status: `differential_nominal_dac_candidate_sar_pending`
- topology: `complementary differential break-before-make thermometer DAC`
- configuration: `1 pF unit capacitors`, `4x` top-plate dummy capacitance, `1x` bottom switches, `0.9 V` source common mode

## Bounded Full Sweep

The `90 s` per-code all-code run measured `12/16` codes. Codes `0`, `1`, `14`,
and `15` exceeded the convergence budget. Codes `2-13` converged with correct
polarity and approximately `56.8501 mV` interior adjacent spacing.

## Endpoint Follow-Ups

With the original `240 s` per-code budget, codes `0` and `1` converged and
preserved polarity, but code `0` measured `-1.438451 mV`, outside the legal
`0-1.8 V` range. Codes `14` and `15` also converged and preserved polarity,
with `56.8622 mV` spacing.

## Conclusion

The initial bounded run did not satisfy the full convergence contract, but a
source-acquisition timing revision at `2.59 ns` now measures all `16/16` codes.
The minimum spacing is `56.298975 mV` versus the `56.25 mV` half-LSB target,
the maximum top plate is `0.851292 V`, the transfer is monotonic, and all
comparator polarities are correct. However, code 15 reaches only `0.851292 V`
while a full 4-bit range requires approximately `1.6875 V`; logical codes
`8-15` therefore collapse in the calibration map. This promotes the topology
only to a local-spacing candidate, not a full-range physical converter or SAR
acceptance result.

The result is narrowly above the spacing threshold, so it must still pass
repeatability, PVT, mismatch, noise, settling, SAR, extraction, area, energy,
and system-level gates. A 32-unit, two-units-per-code range extension was also
tested: boundary spacing was `48.71 mV` with `2x` switches and `52.75 mV` with
`4x` switches, both below the `56.25 mV` threshold. That range extension is
rejected and the full-scale architecture remains open.

A `0.25x` source-switch sizing trial was also measured at codes `0,1`. It
preserved polarity and legal range, but spacing fell to `29.92 mV` and the
maximum measured top plate was `0.253 V`; the smaller source interface does not
acquire the DAC strongly enough and is rejected.

A bootstrapped source-gate diagnostic (`0.5x` source switches with `+0.6 V`
gate overdrive) converged at all four endpoints and preserved legal range, but
minimum spacing was `55.59 mV` and code 15 remained only `0.891 V`. Gate drive
alone is rejected; the source interface needs architectural isolation or a
different charge-transfer ratio.

A split odd/even boundary trial with eight coarse units and one half-size fine
capacitor converged at all four endpoints and preserved polarity, but minimum
spacing was `50.38 mV`, code 15 reached only `0.759 V`, and the low endpoint
violated the legal range. This split encoding is rejected; it does not provide
the required full-scale 4-bit transfer.

A complementary differential implementation with sixteen positive and sixteen
negative unit capacitors was then isolated at code 0. It did not converge within
`120 s`, so no threshold, range, or polarity claim is made for that branch; it
is rejected as currently implemented and requires a simpler, explicitly
initialized differential fixture before further sweep work.

## Initialization Clamp Diagnostic

An opt-in temporary NMOS clamp on the top plate was tested for codes `0,1`.
With the clamp released before redistribution, both cases converged and kept
the correct comparator polarity, but spacing fell to `12.54 mV`; code 0 still
measured `-0.215 mV`. The clamp is rejected because it loads the source
acquisition path rather than acting as an isolated initialization device.

A minimum-width, longer-channel variant (`W=0.42 um`, `L=1.0 um`) reduced the
added capacitance: code `0 -> 1` spacing recovered to `57.70 mV`, but code 0
still measured `-1.387 mV`. It clears spacing but fails the legal-range gate,
so this clamp family is not promoted to the converter path.

## Current Differential Candidate

The corrected break-before-make differential cell with `4x` top-plate dummy
capacitance is the first nominal full-range candidate in this sweep. Its
complete run measured `16/16` codes, `83.5273 mV` minimum spacing, `1.7651 V`
span, legal plate range, and correct nonzero comparator polarity. The coupled
SAR follow-up measured `16/16` calibration codes but only `6/10` conversion
comparisons before bounded simulator timeouts and `0/5` correct conversions.
The DAC gate is therefore open for further qualification, while the SAR gate
remains blocked by the source common-mode and input-range contract.
