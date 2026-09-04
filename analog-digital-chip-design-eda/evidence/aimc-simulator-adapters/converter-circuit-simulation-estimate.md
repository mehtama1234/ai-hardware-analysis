# Converter Circuit-Simulation Estimate

This file is the next proof layer after the local converter estimate. It does not pretend to be layout or silicon. It asks a narrower question: if the ADC is 12 bits and the row drive is 10 bits, do the simple circuit terms point in the same direction as the simulator target?

- status: `circuit_simulation_complete_not_replacement_ready`
- claim-ready to replace break-even: `False`
- ADC bits: `12`
- DAC bits: `10`
- output noise budget: `0.004`
- modeled output noise RMS: `0.000851121`
- meets output noise budget: `True`
- conversion time: `12.0` ns
- settling time: `4.0` ns
- rows served: `64`
- outputs sharing converter cost: `16`
- measurement CSV: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/converter-circuit-simulation-estimate.csv`

## First-Principles Reading

An analog tile is useful only if a small voltage error stays small after it becomes a number. The converter is where that question becomes precise. The row driver chooses an input voltage. The array turns conductance and voltage into current. The readout circuit waits for that current or voltage to settle. The ADC turns the settled value into a code. Each step adds a bounded error.

The model uses five error terms. Quantization error comes from the finite ADC step. Row-drive quantization comes from the finite DAC step. Settling error comes from the fact that a capacitor does not move instantly; after time `t`, a first-order residue is `exp(-t/tau)`. Comparator noise is the uncertainty in the ADC decision. Row-driver noise is the uncertainty in the voltage applied to the selected row.

These errors are combined by root-sum-square because the model treats them as independent small errors. That is not a claim that real silicon will behave this cleanly. It is a clear test: if this clean model failed the `0.004` output-noise budget, the converter target would be too weak even before layout. Here the clean model passes the noise budget, so the target remains worth carrying into a stronger circuit run.

## Cost Meaning

The ADC cost grows with the number of decision levels. A 12-bit SAR ADC makes 12 timed comparisons. The DAC cost grows with the number of row-drive levels and the number of rows that must be driven. Sharing matters because one expensive conversion can serve several useful outputs. Without sharing, the converter eats the advantage of doing multiply-add work in the array.

## Refused Claim

does not replace break-even assumptions, post-layout parasitics, extracted area, measured converter energy, measured silicon noise, or board power

The schema rule is still binding: only `post_layout_simulation` or `measured_silicon` can replace the break-even assumptions. This behavioral circuit estimate narrows the target. It does not close the evidence loop.
