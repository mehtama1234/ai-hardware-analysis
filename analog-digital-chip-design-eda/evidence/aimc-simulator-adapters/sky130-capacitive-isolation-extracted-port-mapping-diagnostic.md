# Sky130 Capacitive Isolation Extracted Port-Mapping Diagnostic

- status: `no_port_mapping_preserves_both_signs`
- rows: `6`
- mappings with both signs preserved: `none`
- extracted frontend: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/sky130_capacitive_isolation_frontend_extracted.spice`

## First Principle

Before blaming the latch, check what the extracted frontend hands to the latch. A comparator can only decide correctly if the sign of the sampled difference reaches the latch input with the same sign or with a known intentional inversion.

This diagnostic removes the latch. It drives the extracted frontend with a positive and negative sample difference, then measures `gp - gn`. If a mapping gives the same sign for both inputs, the physical connection is not a valid differential handoff.

## Results

| mapping | input diff mV | gate diff before V | gate diff after V | expected sign | measured sign | sign preserved |
|---|---:|---:|---:|---:|---:|---|
| `normal` | `-0.152971` | `-1.266000000e-03` | `1.103900000e-02` | `-1` | `1` | `False` |
| `normal` | `0.152971` | `-1.213000000e-03` | `1.109300000e-02` | `1` | `1` | `True` |
| `swap_latch_gates` | `-0.152971` | `1.266000000e-03` | `-1.103900000e-02` | `-1` | `-1` | `True` |
| `swap_latch_gates` | `0.152971` | `1.213000000e-03` | `-1.109300000e-02` | `1` | `-1` | `False` |
| `swap_samples` | `-0.152971` | `-1.213000000e-03` | `1.109300000e-02` | `-1` | `1` | `False` |
| `swap_samples` | `0.152971` | `-1.266000000e-03` | `1.103900000e-02` | `1` | `1` | `True` |

## Refused Claim

does not prove latch resolution, comparator offset, comparator noise, DRC/LVS, SAR conversion, or accepted converter replacement
