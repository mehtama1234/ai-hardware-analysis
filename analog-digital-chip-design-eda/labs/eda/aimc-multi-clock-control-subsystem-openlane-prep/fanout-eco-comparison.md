# Fanout ECO comparison

The canonical implementation uses the original signed multiplier, area-oriented
synthesis, and CTS clustering size 8 / diameter 12. All values below come from
completed OpenLane runs using the same sky130A PDK and 10 ns core-clock target.

| Variant | Fanout violations | Extracted timing | Area (µm²) | Decision |
| --- | ---: | --- | ---: | --- |
| Canonical explicit-source run | 38 | WNS/TNS 0 / 0 | 64,348 | Keep |
| Max-fanout limit 20 | 30 | WNS −0.05 ns | — | Reject |
| Narrow ADC arithmetic | 40 | WNS/TNS 0 / 0 | 65,746 | Reject |
| Radix-16 gain decomposition | 27 | WNS −0.19 ns, TNS −1.11 ns | 62,735 | Reject |
| Narrow 20-bit radix decomposition | 34 | Setup violation (WNS −0.0 ns) | 63,080 | Reject |
| CTS cluster 10 / diameter 16 | 32 | WNS/TNS 0 / 0 | 64,348 | Reject: 1 pin + 1 net antenna |

The fanout target is therefore an open implementation warning, not a hidden
waiver. Constraint relaxation and arithmetic restructuring were both tested;
the current timing-clean multiplier is retained. A future successful ECO must
reduce fanout while preserving extracted 10 ns setup/hold, physical checks,
and lint cleanliness.
