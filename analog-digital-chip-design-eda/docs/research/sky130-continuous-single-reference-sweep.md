# Sky130 Continuous SAR Single-Reference Sweep

This sweep repeats the same one-conversion continuous transistor-level SAR
fixture at three reference values. Each run uses a separate output stem so
that evidence cannot be overwritten by concurrent diagnostics.

| Reference | Final code | Decisions | Bottom plate legal |
|---:|---:|---|---|
| 0.55 V | 0 | `[1, 1, 1, 1]` | no |
| 0.60 V | 0 | `[1, 1, 1, 1]` | no |
| 0.65 V | 0 | `[1, 1, 1, 1]` | no |

At `0.695 V`, using the eight-finger bank, the result is also code `0` with
`[1, 1, 1, 1]`; the cycle DAC samples are `[1.5219, 1.0596, 0.8219,
0.7091] V`. This confirms that the banked circuit does not yet realize a
correct retained-bit sequence at the intended reference window.

The DAC threshold samples are almost unchanged across this range:
`[1.2311, 0.8258, 0.8214, 0.7107] V`. The result therefore does not support
a reference-window repair. The failure is upstream in the continuous
charge-transfer/control state: the bottom plate still leaves the legal range
and the latch sees the same decision sequence.

## Banked continuous follow-up

An eight-device PMOS bank was then carried into the actual repeated
continuous-SAR transient. It improves selected-plate charging to roughly
`1.80 V`, but the run still returns code `0` with decisions `[1,1,1,1]`.
Unselected plates undershoot below ground by up to about `5.6 mV`, so the
banked cell does not pass the legal-range gate. High-side drive strength helps,
but the control waveform still needs explicit bottom-plate isolation or
clamping and a corrected charge-transfer sequence before the bank can be used
in the binary array.

Evidence: `sky130-continuous-bank8.json`.

The explicit dead-time NMOS clamp reduces the worst undershoot from about
`-5.6 mV` to `-4.8 mV`, but does not restore legal range or correct the
decision sequence. It is therefore characterized and rejected as a complete
repair; the remaining error is not only a floating-node transient. Evidence:
`sky130-continuous-bank8-dead-clamp.json`.

The full five-conversion run with the eight-device PMOS bank is also rejected:
`0→0`, `2→1`, `4→3`, `6→5`, and `7→7`. The bank improves rail charging in the
isolated cell but changes the continuous retained-bit trajectory and still
produces about `-5.6 mV` bottom-plate undershoot. Evidence:
`sky130-continuous-bank8-full.json`.

An explicit 2 ns ground-precharge transistor at each conversion boundary is
also rejected. It changes the sequence to `0→0`, `2→4`, `4→5`, `6→8`, and
`7→8`, while some internal nodes rise to about `2.00 V`. The extra device is
therefore injecting enough charge to disturb the DAC transfer; state reset
cannot be added as an unisolated parallel clamp. Evidence:
`sky130-continuous-precharged-full.json`.

A shared top-plate reset transistor is rejected as well. The full run returns
`0→1`, `2→8`, `4→13`, `6→15`, and `7→15`, with internal excursions reaching
about `1.89 V`. Resetting the shared node changes the sampled input itself and
does not repair the retained-bit transfer. Evidence:
`sky130-continuous-top-reset-full.json`.

Evidence files:

- `sky130-continuous-single-ref-055.json`
- `sky130-continuous-single-ref-060.json`
- `sky130-continuous-single-ref-065.json`

The runner now accepts `AIMC_CONTINUOUS_OUTPUT_STEM` for reproducible named
diagnostics. This remains circuit diagnostic evidence, not SAR acceptance.
