# Sky130 Balanced Frontend Work Order

- status: `ready_to_build_balanced_extracted_frontend_candidate`
- target cell: `sky130_balanced_capacitive_isolation_frontend`
- required wrong-sign bias reduction: `144.33x`
- maximum wrong-sign gate bias: `0.076485 mV`
- missing post-layout objects: `offset_noise_record, drc_lvs_record`

## First Principle

The analog frontend has one job before the latch fires: keep the sign of the sampled voltage difference. It does not need to understand the model, the token, or the layer. It only needs to make `gp - gn` carry the same sign as `sample_p - sample_n` while keeping kickback below the ADC boundary.

The failed extracted cell tells us what broke. The physical metal and node loading made a preferred latch-gate direction that was much larger than the signal. So the next cell must be built as a balance problem first and a latch problem second.

## Build Object

Create `sky130_balanced_capacitive_isolation_frontend` beside the current starter cell. Keep the same external role, but add explicit balance and reset structure instead of relying on accidental symmetry.

| port | role | rule |
|---|---|---|
| `vss` | quiet reference | route symmetrically near both latch-gate sides |
| `vdd` | supply reference | do not let one latch-gate side see a different supply plate area |
| `sample_p` | positive held sample | couple only to the positive measuring node before latch fire |
| `sense_p` | positive balanced measuring node | reset to common-mode before sampling and isolate from regeneration |
| `clk_sample` | sample handoff clock | must not share a large unbalanced plate with one sense node |
| `vcm_reset` | common-mode reset | forces sense_p and sense_n to the same voltage before handoff |
| `clk_latch` | regeneration clock | fires only after the sense nodes have formed the sign |
| `sense_n` | negative balanced measuring node | match sense_p total extracted capacitance within the bias target |
| `sample_n` | negative held sample | mirror the positive sample path in metal length, area, and neighbors |

## Required Design Moves

- split the old latch_gate_p/latch_gate_n nodes into sense_p/sense_n and later latch inputs
- add matched reset devices from sense_p and sense_n to vcm_reset
- keep sample_p-to-sense_p and sample_n-to-sense_n plates mirrored in drawn area and neighboring conductors
- route clk_sample and clk_latch as separate controls so sampling disturbance is not mixed with regeneration disturbance
- shield sense_p and sense_n with symmetric vss or vcm neighbors before either node approaches vdd or substrate plates
- extract the new cell and compute total sense_p and sense_n capacitance before running the latch proof

## Acceptance Checks

- extracted netlist exists for the new balanced cell name
- normal port mapping preserves both signs for the target positive and negative input differences
- absolute wrong-sign gate bias is below the redesign target before latch fire
- sample-node kickback remains below the hard half-LSB limit from the comparator acceptance fixture
- offset/noise record exists and combines with the static target by root-sum-square
- DRC/LVS record exists for the same cell name used in the extracted rerun
- accepted evidence remains false until all checks come from the same extracted physical candidate

## Rejected Shortcuts

- do not accept an ideal capacitor overlay as physical evidence
- do not swap ports to hide a one-direction extracted bias
- do not use a schematic-only pass after layout parasitics have contradicted it
- do not write accepted post-layout evidence while offset/noise or DRC/LVS is missing

## End-To-End Fit

This work order is the next physical object in the chain from analog tile output to digital code. The model and simulator path can only trust an analog readout if this frontend first preserves the sign of the tiny sampled voltage. Once the balanced frontend passes extraction, it can feed the comparator acceptance fixture, then the converter post-layout payload, then the digital governor that decides whether an analog result is safe to use.

## Refused Claim

does not create the new layout, does not prove the comparator works, does not run DRC/LVS, and does not write accepted post-layout evidence
