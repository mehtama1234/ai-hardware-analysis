# Sky130 Two-Phase Transistor Full PVT Matrix

- status: `full_pvt_matrix_measured_not_noise_or_mismatch_proof`
- matrix: `3 process x 3 temperature x 3 supply`
- cases: `54`
- measured cases: `53`
- timed-out cases: `1`
- sign passes: `53` of `53`
- preamp-margin passes: `39` of `53`
- margin target: `5.000000000e-04 V`
- worst preamp magnitude: `1.550000000e-05 V`

## First-Principles Reading

The preamp differential is the signal that must survive before the latch can make a reliable decision. Process changes transistor gain, temperature changes mobility and leakage, and supply changes headroom. Sweeping them independently prevents a favorable process-temperature-supply combination from hiding the operating limit.

A sign pass is only directional evidence. The amplitude-margin pass is the service rule: any measured row below the target must be redesigned, derated, or sent to digital fallback.

## Worst Case

- corner: `ss_-20c_1.62v`
- preamp magnitude: `1.550000000e-05 V`

## Next Gate

Add mismatch and transistor noise at the worst independent corners, then repeat the same margin rule at every SAR transition.

## Refused Claim

does not prove random noise, mismatch distributions, SAR conversion, extracted layout, board behavior, or silicon yield
