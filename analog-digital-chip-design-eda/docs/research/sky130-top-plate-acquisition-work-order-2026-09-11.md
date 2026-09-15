# Sky130 top-plate acquisition work order

## Objective

Make the four-bit capacitor DAC produce legal, bit-weighted top-plate samples
at the comparator input while retaining the known fixed-state rail pattern.
This work order follows the 2026-09-11 screens: bottom-plate isolation and a
timed rail handoff preserve per-bit rails, while broad clamps, extra top
capacitance, and early sampling do not preserve the top node.

## Required configuration

- Start from the pinned Sky130 model and source bundles.
- Use the two-control sequential deck with the phase window ending at each
  trial's end.
- Keep the 100 fF capacitive copy as the comparator interface.
- Run fixed retained states first, then the live closed-loop sequence.
- Record `post_trial_db_v`, `v(top)`, `v(sp)`, `v(sn)`, preamp differential,
  raw decision, and comparator decision for every bit.

## Experiment sequence

1. **Charge-preserving handoff:** isolate each capacitor plate during the trial,
   open the trial switch, then connect the selected rail through a finite 100 Ω
   path. Confirm the post-trial rows retain the expected mixed pattern.
2. **Top-node isolation:** keep the top plate disconnected from the preamp until
   after redistribution; transfer it through the 100 fF copy only after the
   post-trial probe. Do not add a top clamp during this step.
3. **Acquisition timing sweep:** measure at `trial_end + 0.5 ns`, `+1.0 ns`,
   and `+2.0 ns`. Keep the comparator disabled until each measurement point.
4. **Closed-loop replay:** run five conversions with the best fixed-state
   timing, then repeat at FS and FF corners in Colab.

## Promotion gates

Promote a candidate only if all four post-trial plate values and all four
sampled top-node values stay in `0..1.8 V`, the fixed-state preamp signs match
the known pattern, and the five-conversion live run produces the contracted
code sequence. Any failed case remains diagnostic and routes to the digital
fallback.

Receipts must include the experiment-control manifest and the complete waveform
probe set. No energy, PVT yield, silicon, or analog speedup claim is allowed
until those gates and the existing robustness gates close.
