# Sky130 Single-Device Charge Injection Ngspice

- status: `sky130_single_device_charge_injection_characterized_not_converter_proof`
- topology: `single_sky130_nfet_sample_path_to_hold_capacitor`
- PDK model library: `/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice`
- generated deck: `labs/analog/analog-in-memory-foundation-model-hardware/spice/sky130_single_device_charge_injection.sp`
- case count: `3`
- measured case count: `0`
- timed out case count: `3`
- half LSB 12b V: `2.197265625e-04`
- worst edge abs delta V: `not measured`
- pass count: `0` of `3`
- candidate post-layout written: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-single-device-charge-injection-ngspice.csv`

## First Principle

A MOS gate is separated from the held node by capacitance. When the gate voltage moves, some charge is pushed through that capacitance. The held node is a capacitor, so the pushed charge becomes a voltage step.

This fixture keeps the signal path but makes it as small as possible. One Sky130 nfet connects a DC input to the hold capacitor. The gate then falls from high to low. The measured voltage step after turn-off is the smallest normal-switch unit behind clock feedthrough and charge injection.

This is not a sample-and-hold proof. It is a device-level measurement that tells us whether the next differential or bootstrapped switch deck is working from a measured disturbance size instead of a guess.

## Results

| case | input V | Wn um | Csample pF | before edge V | after edge V | edge delta V | sample error before edge V | inferred charge C | pass |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| mid_0p2p_1x | `0.900000000` | `1.000` | `0.200` | timeout | timeout | timeout | timeout | timeout | `False` |
| mid_1p0p_1x | `0.900000000` | `1.000` | `1.000` | timeout | timeout | timeout | timeout | timeout | `False` |
| mid_1p0p_2x | `0.900000000` | `2.000` | `1.000` | timeout | timeout | timeout | timeout | timeout | `False` |

## Refused Claim

does not prove a complete sampling switch, differential matching, comparator behavior, SAR conversion, extracted layout, DRC/LVS signoff, or accepted replacement economics
