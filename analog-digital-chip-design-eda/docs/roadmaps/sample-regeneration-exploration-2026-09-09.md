# Separating acquisition and regeneration: bounded schematic results

The phase-separated schematic resolves large inputs correctly with sufficient
output margin, but fails the small-input requirement. It is a new schematic
experiment, not an extracted-layout upgrade or qualified converter.

## Design change

Starting from the DRC/LVS-checked macro, the input transistor pair receives a
separate switched tail. Regenerative feedback uses the existing tail switch
and a new PFET supply header, enabled after acquisition ends. This adds two
devices (15 total). A second experiment adds transmission gates at both input
pair drains (19 devices total), attempting to remove a residual differential
load during regeneration.

The inherited parasitics are provisional because connectivity changed and
the added devices have no layout. Each output preserves the source extraction,
modified schematic, source snapshots, raw decks and ngspice logs. These
experiments cannot inherit the predecessor's DRC or LVS pass.

## Results

Supply is 1.8 V, input common mode 0.9 V, sense load 100 kΩ, and decision sample
18 ns. Regeneration starts 0.1 ns after the nominal acquisition pulse width.
Pulse transitions take 20 ps and are explicit in every deck.

| Variant | Acquisition window | ±100 mV: polarity and ≥0.9 V margin | ±0.152971 mV: polarity and ≥0.9 V margin |
| --- | ---: | ---: | ---: |
| Separate input tail and regenerative supply | 0.1 ns | 2/2 | 0/2 |
| Same | 0.3 ns | 2/2 | 0/2 |
| Same | 1.0 ns | 2/2 | 0/2 |
| Additional drain transmission gates | 0.1 ns | 1/2 | 1/2 |

The direct phase-separated variant produces about ±1.27 V for the large inputs.
Small-input outputs remain around ±0.59 V and exhibit a sampling-window-dependent
bias. In the transmission-gate experiment, every tested input produces −1.8 V:
its positive-input passes reflect a stuck decision, not a valid bipolar response.
All 16 cases completed; no paired small-input setting qualified.

The results establish that phase control can improve the large-input behavior
under these schematic assumptions. They do not establish the needed small-signal
gain, offset, noise, clock-feedthrough tolerance or 12-bit converter performance.
The drain-isolation variant is rejected at its tested timing.

## Artifacts and reproduction

All paths below are under `evidence/aimc-simulator-adapters/recovery-20260909/`:

- `separated-sample-regeneration-v1/result.json`: 12 cases, 15-device variant.
- `separated-sample-drain-isolation/result.json`: four cases, 19-device variant.
- `sample_regeneration_design_exploration.json`: source-hashed comparison.

From the EDA project, using new output directories:

```bash
AIMC_SENSE_LOAD_OHM=100000 python3 scripts/test_separated_sample_regeneration.py --netlist evidence/aimc-simulator-adapters/recovery-20260909/contact-rebuild-v3/aimc_converter_macro_active_candidate_extracted.spice --output evidence/aimc-simulator-adapters/recovery-20260909/new-phase-test
AIMC_SENSE_LOAD_OHM=100000 python3 scripts/test_separated_sample_regeneration.py --netlist evidence/aimc-simulator-adapters/recovery-20260909/contact-rebuild-v3/aimc_converter_macro_active_candidate_extracted.spice --output evidence/aimc-simulator-adapters/recovery-20260909/new-isolation-test --isolate-drains --sample-durations-ns 0.1
```

The physical gate continues to reference the unchanged DRC/LVS-checked layout
and its failed electrical margin. No favorable schematic row is promoted into
that gate. Further hardware work needs gain/offset/clock-feedthrough analysis
and a selected topology before another physical build. Representative
real-model dataset validation, calibrated array/error/cost binding and actual
target execution remain independent end-to-end program requirements.
