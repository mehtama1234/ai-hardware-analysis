# Sky130 Two-Stage Preamp To Latch Width Sweep

After the two-stage extracted-front-end preamp passed its isolated calibrated margin gate, it was connected to the transistor latch with same-run zero-input trim. The latch input-pair width was then reduced to test whether latch loading was the main failure.

| latch input width | same-run zero offset | correct target-edge decisions |
|---:|---:|---:|
| `10 µm` | approximately `-125.7 mV` | `1/2` |
| `1 µm` | approximately `-5.7 mV` | `1/2` |
| `0.5 µm` | approximately `+16.4 mV` | `1/2` |

The artifacts are [1 µm](../../evidence/aimc-simulator-adapters/sky130-two-stage-preamp-latch-w1.json) and [0.5 µm](../../evidence/aimc-simulator-adapters/sky130-two-stage-preamp-latch-w05.json). The original `10 µm` result is [here](../../evidence/aimc-simulator-adapters/sky130-two-stage-preamp-latch-handoff.json).

A source follower was then inserted after the offset-trimmed two-stage preamp and its own zero-input differential was calibrated in the connected deck. That branch also resolved only `1/2` target-edge polarities. Its evidence is [here](../../evidence/aimc-simulator-adapters/sky130-two-stage-preamp-buffered-latch-calibrated.json).

The latch precharge phase was also corrected so the PMOS precharge devices are active before evaluation and off during the high evaluation phase. This produced full-rail regeneration, but still only `1/2` correct target-edge polarities: [correct-precharge evidence](../../evidence/aimc-simulator-adapters/sky130-two-stage-preamp-latch-correct-precharge.json).

Evaluation-delay tests at `2 ns`, `3 ns`, and `4 ns` produced the same `1/2` result, so allowing the extracted preamp more settling time does not repair the polarity. The delay artifacts are `sky130-preamp-latch-delay2.json`, `sky130-preamp-latch-delay3.json`, and `sky130-preamp-latch-delay4.json` under `evidence/aimc-simulator-adapters/`.

Reducing the latch tail/evaluation device width to `2 µm`, `5 µm`, and `10 µm` also produced `1/2` in every case. The tail-current artifacts are `sky130-preamp-latch-tail2.json`, `sky130-preamp-latch-tail5.json`, and `sky130-preamp-latch-tail10.json`. Latch current sizing alone is therefore not the repair.

A fixed latch-input trim sweep at `-100 mV`, `0 mV`, and `+100 mV` found no usable calibration window. The negative and zero trims drove both cases to the positive output rail; the positive trim drove both cases to the negative output rail. The trim artifacts are `sky130-preamp-latch-trim-neg100mv.json`, `sky130-preamp-latch-trim-zero.json`, and `sky130-preamp-latch-trim-pos100mv.json`. The latch’s effective input-referred offset is therefore larger than the target-edge differential.

## Interpretation

Smaller latch devices change the loading and the offset substantially, but neither tested width preserves both polarities. This rules out simply shrinking the latch input pair as a complete repair. The preamp output needs a better-defined common-mode and larger differential dominance at the latch interface, likely through a dedicated output buffer, reset sequencing, or a fully differential active-load stage.

## Boundary

This is a connected transistor transient diagnostic with ideal sample-side sources and a fixed trim derived from a same-run zero-input probe. It does not prove statistical offset, noise, mismatch, physical preamp layout, DRC/LVS, SAR bit cycling, or accepted converter evidence.
