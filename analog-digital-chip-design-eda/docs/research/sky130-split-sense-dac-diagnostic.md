# Sky130 Split-Sense DAC Diagnostic

This diagnostic inserts a separate capacitive sense node between the physical
DAC top plate and the transistor comparator. The purpose is to test whether
comparator loading and kickback can be isolated without changing the physical
DAC redistribution node.

| Isolation capacitor | Code 7/8 measured | Correct polarity | Sense-node result |
|---:|---:|---:|---|
| 0.1 pF | 0/2 | 0/2 | timeout |
| 0.2 pF | 0/2 | 0/2 | timeout |
| 0.5 pF | 2/2 | 2/2 | code 7 reaches 2.089 V |
| 1.0 pF | 0/2 | 0/2 | timeout |

The 0.5 pF case preserves the sign at the critical code-7/code-8 boundary,
but the isolated sense node exceeds the 1.8 V supply. The other coupling
values do not converge within the bounded transistor simulation. Capacitive
isolation by itself is therefore not an accepted repair.

Adding the existing passive diode rail clamp to the 0.5 pF sense node keeps
both critical polarities correct, but only reduces the code-7 sense value from
`2.089 V` to `2.048 V`. It does not enforce the legal range and is rejected as
an effective clamp. Evidence: `sky130-split-sense-05p-rail-clamp.json`.

Increasing the modeled diode area to `100x` reduces the code-7 sense value to
`1.967 V`, still above the supply. At `1000x`, code 7 becomes incomplete while
code 8 converges. The passive clamp-area tradeoff is therefore rejected as
well. Evidence: `sky130-split-sense-05p-area-100.json` and
`sky130-split-sense-05p-area-1000.json`.

Evidence files:

- `sky130-split-sense-01p.json`
- `sky130-split-sense-02p.json`
- `sky130-split-sense-05p.json`
- `sky130-split-sense-1p.json`

The experiment remains useful as a design boundary: the next split-DAC
candidate needs a defined common-mode clamp and a real sampling switch or
precharge phase, rather than a floating capacitor connected directly to the
comparator.
