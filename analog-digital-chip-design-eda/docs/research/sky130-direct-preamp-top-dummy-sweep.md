# Sky130 Direct-Preamp Top-Dummy Sweep

The direct high-impedance preamp still drove the physical DAC top plate above
the 1.8 V supply at high codes. This diagnostic adds a top-plate dummy
capacitor and measures the critical adjacent code boundary.

| Top dummy | Code 7 top V | Code 7 polarity | Code 8 top V | Code 8 polarity |
|---:|---:|---|---:|---|
| 4 pF | 2.308 | pass | not run | — |
| 20 pF | 2.010 | pass | not run | — |
| 40 pF | 1.745 | pass | 1.367 | fail |

The 40 pF value brings code 7 into the legal range, but reverses the code-8
comparator polarity. It changes the DAC transfer rather than merely absorbing
overshoot, so it is rejected as a converter repair. Evidence is stored in:

- `sky130-direct-preamp-topdummy-4p-code7.json`
- `sky130-direct-preamp-topdummy-20p-code7.json`
- `sky130-direct-preamp-topdummy-40p-code7.json`
- `sky130-direct-preamp-topdummy-40p-code8.json`

The next design should control the split-DAC common mode locally, instead of
adding a large capacitor directly to the shared top plate.
