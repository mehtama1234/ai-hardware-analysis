# Sky130 Transistor Comparator SAR Cycle

- status: `transistor_comparator_sar_cycle_failed_or_incomplete`
- bits: `4`
- conversions: `3`
- comparator decisions: `3`
- measured decisions: `0`
- timed-out decisions: `3`
- correct conversions: `0` of `3`

## What Is Real

The controller performs a genuine most-significant-bit-first SAR update. For every trial code it computes the signed input difference, runs the transistor preamp/latch, reads the regenerated output, and uses that result to decide whether to retain the trial bit.

The DAC reference in this first loop is an ideal numerical threshold. That keeps the experiment focused on the transistor comparator/controller boundary and prevents an ideal capacitor overlay from being mistaken for a physical DAC result.

## Next Physical Gate

Replace the numerical threshold with a switched capacitor-DAC network, measure its settling and reference loading, then repeat the exact same trace with mismatch and noise applied at each decision.

## Refused Claim

does not prove a capacitor-DAC network, DAC settling, capacitor mismatch, comparator noise yield, extracted layout, board behavior, or silicon
