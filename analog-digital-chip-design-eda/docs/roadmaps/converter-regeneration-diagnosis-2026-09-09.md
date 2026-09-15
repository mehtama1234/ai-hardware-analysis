# Active schematic LVS and bounded regeneration diagnosis

The DRC-clean macro now passes Netgen LVS against the intended active-transistor
schematic. The electrical diagnostic shows that extra settling/precharge time
does not resolve the observed margin/polarity failures under the tested loads.

## Active-transistor LVS

The reference uses the existing independently written 11-transistor latch
schematic plus the intended two-transistor preamp. Netgen reports
`Final result: Circuits match uniquely.` for the 13-transistor macro. Extracted
MOS lines and ports were retained unchanged; 75 parasitic capacitor lines were
excluded from the schematic comparison. This does not check complete converter
function: starter DAC/SAR/mux regions still lack functional devices.

The report is
`evidence/aimc-simulator-adapters/recovery-20260909/contact-rebuild-v3-schematic-lvs/result.json`.
It binds the extraction, independent latch reference, PDK setup and command.
A negative control doubles one preamp width in the reference while leaving
extraction unchanged; the acceptance check rejects it. That evidence is in
`schematic-lvs-negative-control/result.json` beside the positive run.

## Regeneration diagnosis on the same extraction

All cases use the same netlist hash
`d94c84fa2534bd92e0c763ec9dd58de6a7f236a5c5fafa20a3ba6abd3673bcc5`.
The test keeps reset released and evaluation enabled for a single extended
window. It records output, latch-input and tail nodes before and after clock
release. It does not represent normal multicycle operation or throughput.

| Protocol | −100 mV input | +100 mV input | Finding |
| --- | ---: | ---: | --- |
| 100 kΩ load, sample at 98 ns | +0.214958 V | −0.214958 V | Correct signs, insufficient 0.9 V margin |
| 300 kΩ load, sample at 98 ns | −1.415216 V | −1.800000 V | Strong regeneration, wrong negative-input decision |
| 300 kΩ load, release delayed to 80 ns, sample at 170 ns | −1.415216 V | −1.800000 V | Longer precharge does not correct the biased decision |

At ±0.152971 mV input, the 100 kΩ case produces only about ±0.2302 mV output
at 98 ns. The 300 kΩ case produces approximately −1.796 V for both input signs.
Neither load passes correct polarity and sufficient margin for both signs.
Polarity results from one load cannot be combined with margin from another.

The 100 kΩ node probes show high latch-input common mode (about 1.4 V for the
small differential), consistent with sustained input-transistor pull-down.
The 300 kΩ condition lowers that common mode to about 0.6 V and permits strong
regeneration, but the incorrect decision remains after longer precharge. These
observations narrow the next design work to input/feedback strength, common-mode
interface and clock-coupling behavior; they do not uniquely prove a root cause.

Joined evidence: `recovery-20260909/regeneration_diagnosis.json`. Raw decks,
logs, samples and source snapshots are in `regeneration-hold-diagnostic`,
`regeneration-hold-load300k`, and `regeneration-precharge80-load300k`.

## Gate and next work

The current physical record and software importer now distinguish full-cell
DRC pass, active-transistor LVS pass, complete-converter LVS missing, and
electrical qualification failed. Physical analog authorization remains false.

The next electrical change needs an explicit sampling/regeneration interface
and a matched operating contract. More nominal timing/load sweeps alone cannot
close the converter. Full SAR transfer, noise/mismatch/PVT, model-level error
binding, actual array/target access and the measured end-to-end comparison
remain program requirements.

Reproduce with new output directories from the EDA project:

```bash
python3 scripts/check_active_macro_schematic_lvs.py --netlist evidence/aimc-simulator-adapters/recovery-20260909/contact-rebuild-v3/aimc_converter_macro_active_candidate_extracted.spice --output evidence/aimc-simulator-adapters/recovery-20260909/new-active-lvs
AIMC_SENSE_LOAD_OHM=100000 python3 scripts/diagnose_converter_regeneration.py --netlist evidence/aimc-simulator-adapters/recovery-20260909/contact-rebuild-v3/aimc_converter_macro_active_candidate_extracted.spice --output evidence/aimc-simulator-adapters/recovery-20260909/new-hold
AIMC_SENSE_LOAD_OHM=300000 python3 scripts/diagnose_converter_regeneration.py --netlist evidence/aimc-simulator-adapters/recovery-20260909/contact-rebuild-v3/aimc_converter_macro_active_candidate_extracted.spice --output evidence/aimc-simulator-adapters/recovery-20260909/new-delayed-hold --release-ns 80 --input-diffs-mv -100 100
```
