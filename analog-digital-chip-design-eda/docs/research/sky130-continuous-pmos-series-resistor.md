# Sky130 Continuous SAR PMOS Series-Resistance Diagnostic

The continuous SAR candidate has two coupled problems: high-side PMOS charge
transfer can create later `>1.8 V` samples, while low-side switching can create
small negative bottom-plate excursions. This diagnostic inserted the same
series resistor between each continuous PMOS source and `VDD`, leaving the
PMOS device and decision waveforms otherwise unchanged.

| PMOS source series resistance | Result | Bottom-plate gate | Conversion result |
|---:|---|---|---|
| none | baseline | fail | `0→0, 2→1, 4→4, 6→6, 7→7` |
| 100 Ω | measured | fail | `0→0, 2→1, 4→4, 6→6, 7→8` |

The 100 Ω resistor does not isolate the retained charge-transfer state. It
still produces negative bottom-plate samples and raises the largest sampled
top plate to about `2.048 V`. It also changes the highest-code decision. The
variant is rejected as a complete repair.

This result narrows the design requirement: the continuous switch network
needs explicit phase isolation and a defined common-mode/precharge state. A
passive series element on the high-side path is insufficient. The next
implementation should separate acquisition, redistribution, and decision
loading at the switch topology level, then re-run the five-conversion,
legal-range, PVT, and layout gates.

Evidence:

- `evidence/aimc-simulator-adapters/sky130-continuous-pmos-series100-full.json`
