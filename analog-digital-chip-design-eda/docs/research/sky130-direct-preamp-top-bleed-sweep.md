# Sky130 Direct-Preamp Top-Plate Bleed Sweep

The direct-preamp handoff left the split-DAC top plate floating enough to
overshoot the 1.8 V supply. This experiment added a resistor from the top
plate to `VDD` and measured the adjacent high-code decisions (7 and 8).

| Top-to-VDD resistor | Code 7 top V | Code 8 top V | Polarity | Bottom-plate legality |
|---:|---:|---:|---:|---|
| 100 kΩ | 2.020 | 2.142 | 2/2 | fail |
| 10 kΩ | 2.021 | 2.147 | 2/2 | fail |
| 100 Ω | 1.876 | 1.959 | 2/2 | fail |

The stronger resistor begins to reduce the top-plate excursion, but it still
does not bring either high-code result into the legal range. It also creates
negative bottom-plate excursions (about −26.8 mV for code 7 and −12.4 mV for
code 8 at 100 Ω). The 10 kΩ and 100 kΩ values are too slow to materially
discharge the sampled capacitor before the decision boundary.

This is therefore rejected as a converter repair. A passive bleed is not a
local common-mode regulator: it either arrives too late or loads the charge
redistribution enough to violate the bottom-plate constraint. The next
revision should use an explicitly timed, isolated common-mode clamp or a
dedicated split-DAC sense buffer, followed by an all-code and PVT sweep.

Evidence:

- `evidence/aimc-simulator-adapters/sky130-direct-preamp-top-bleed-100k.json`
- `evidence/aimc-simulator-adapters/sky130-direct-preamp-top-bleed-10k.json`
- `evidence/aimc-simulator-adapters/sky130-direct-preamp-top-bleed-100r.json`
