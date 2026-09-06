# Sky130 Continuous SAR Auto-Zero Integration

The nominal extracted-frontend auto-zero interface passes both target
polarities, so it was exercised in the continuous physical SAR deck as an
optional per-decision capacitive interface. The branch connects the SAR
preamp nodes to latch-side nodes through matched capacitors, restores their
common mode, and uses the latch precharge clock as the temporary equalization
control.

## Result

The first `100 fF` run measured one continuous conversion but resolved code
`0` instead of expected code `2`; all four comparator decisions were identical
and the bottom-plate voltages were outside the legal range. Reducing the
coupling to `10 fF` produced the same code `0` and identical decisions, with
larger preamp excursions. The failure is therefore not explained by excessive
coupling alone.

The control was then corrected to use a dedicated behavioral auto-zero waveform
that is high during each DAC trial's `3.5 ns` settling interval and low before
the corresponding sample/decision point. This removes the earlier `clkb`
phase ambiguity, but the measured result remained the same as the baseline:
final code `0`, all four comparator decisions `1`, and illegal bottom-plate
voltages. The timing correction therefore does not repair the converter; it
also shows that the auto-zero branch is not the dominant source of the current
continuous-SAR failure.

Evidence:

- `evidence/aimc-simulator-adapters/sky130-continuous-physical-sar-autozero-timed-single-diagnostic.json`

Earlier coupling evidence:

- `evidence/aimc-simulator-adapters/sky130-continuous-physical-sar-autozero-single-diagnostic.json`
- `evidence/aimc-simulator-adapters/sky130-continuous-physical-sar-autozero-10f-diagnostic.json`

## Decision

The optional branch is not promoted into the accepted continuous-SAR path.
The frontend auto-zero proof remains valid, but its timing cannot be reused
by simply attaching it to the SAR latch `clkb`. The next integration revision
needs a conversion-boundary-specific reset/equalization waveform coordinated
with DAC redistribution and comparator sampling. Continuous-SAR acceptance,
bottom-plate legality, PVT, mismatch, noise, layout, board, and silicon gates
remain open.
