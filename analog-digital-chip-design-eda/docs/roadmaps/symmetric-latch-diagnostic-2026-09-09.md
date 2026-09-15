# Symmetric-capacitance latch diagnostic

A schematic with synthetic symmetric parasitics and input-drain isolation now
passes both input signs at ±100 mV and ±0.1529705854 mV in a single-cycle nominal
test. It is a design lead, not a qualified converter or repaired layout.

The source is the same 13-MOS extracted macro used by the physical gate. The
diagnostic leaves its MOS lines unchanged and replaces every parasitic capacitor
with half the original capacitance plus half its side-mirrored counterpart.
The mirror exchanges decision nodes, latch sense nodes, and the two signal input
ports. All 75 original entries were checked against the 150 synthetic entries.
This transformation is not a physical extraction; it asks what the circuit
would do with a symmetric capacitance network.

The existing acquisition/regeneration experiment then adds a separate input tail
and regenerative supply header (15 MOS). Its drain-isolation option adds four
transmission-gate devices (19 MOS). Supply, nominal TT transistor models, input
common mode, 100 kΩ sense loads and 0.1 ns acquisition are unchanged from the
earlier phase-separation experiment. Decision is sampled at 18 ns.

| Synthetic-capacitance schematic | ±100 mV paired polarity/margin | ±0.15297 mV paired polarity/margin |
| --- | --- | --- |
| Separated sample/regeneration, no drain isolation | 2/2 | 0/2 |
| Same, with drain isolation | 2/2 | 2/2 |

Without drain isolation, small-input outputs are approximately ±0.585 V,
below the existing 0.9 V margin criterion. With drain isolation they are
approximately ±1.79986 V; large-input outputs are ±1.8 V. All eight single-cycle
cases exited successfully, and the measurements/polarity/margin classifications
were rechecked against raw simulator logs.

Capacitance symmetry alone is insufficient in this experiment. Together with
drain isolation it restores the tested nominal small-input decision. These
observations do not uniquely identify all offset sources or prove noise
robustness, 12-bit precision, full SAR transfer or a manufacturable layout.
The existing physical gate remains unchanged and disallows analog execution.

Evidence is under
`evidence/aimc-simulator-adapters/recovery-20260909/symmetric-capacitance-diagnostic/`:
`derivation.json`, `synthetic_symmetric_caps.spice`, `phase-test/`,
`drain-isolation-test/`, and `single_cycle_comparison.json`. The comparison hashes
34 completed sources and evidence files. It excludes the running repeated test.

## Repeated-decision failure

`scripts/test_symmetric_latch_repeated_decisions.py` runs eight cycles with
alternating and repeated large/small input signs. All phase clocks share a
60 ns period, inputs change over 1 ns at cycle boundaries, and each decision is
sampled 18 ns into its cycle. This exercises reset/history behavior that the
single-cycle results do not establish.

The output `repeated-decisions-v2/` completed with exit code zero, but only
7/8 decisions have correct polarity. Cycle 2 applies −0.1529705854 mV after
the prior cycle's +100 mV input and produces approximately −1.8 V output,
the wrong sign. All eight cycles have sufficient magnitude. The failure is
therefore a decision failure, not insufficient output swing. The later small
negative input in cycle 5 decides correctly, indicating history dependence
under this protocol. It does not uniquely identify the storage node responsible.

The saved waveforms verify the applied input values and output measurements;
the wrong polarity persists through a 2 ns window after the decision sample.
No repeated-decision process remains active. An earlier `repeated-decisions/`
preparation attempt failed before creating a valid circuit deck and is not a
circuit result.

Before physical redesign, the isolated input nodes and reset/acquisition
protocol need investigation to remove history-dependent wrong decisions.
Only after that should a selected topology and capacitance balance be built in
actual layout and checked through extraction, DRC/LVS and electrical tests.
Synthetic symmetry must not be carried forward as an achieved layout property.
