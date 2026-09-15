# Physical preamp layout repair and full-cell DRC audit

The intended preamp input/output connections now exist in a newly edited
layout and its final extracted netlist. This closes the wiring defect, but
the candidate still fails physical design rules and electrical output margin.

## Reproducible candidate

`evidence/aimc-simulator-adapters/recovery-20260909/physical-preamp-route-repair-v4/`
contains the edited cells, extraction script, Magic logs, source snapshot,
layout hashes, and `repair_result.json`.

The repair adds missing poly contacts, removes an unused metal2 bar crossing
both drains, adds drain via stacks, and routes the outputs on metal5 over the
macro's metal4 supply escape. It changes actual geometry; the extracted SPICE
was not manually reconnected. Both branches pass the final-netlist connectivity
audit. The netlist SHA-256 is
`3eb9d089631f917e2834c27ec07bde167f007db1d5419f016163e358017ce964`.

The failed v1 extraction preserves a PDK setup failure. The v2 candidate exposes
drain/supply shorts. The v3/v4 geometry repairs those shorts; v4 additionally
waits for the DRC queue. These intermediate artifacts remain preserved.

## Electrical result on that exact extraction

`evidence/aimc-simulator-adapters/active-converter-macro-transient/20260909T164810672780Z/result.json`
matches the netlist hash above. With 100 kΩ load, 1.8 V supply, 0.9 V common
mode and an 18 ns decision sample:

| Differential input | Differential output | Correct sign | Required 0.9 V margin |
| --- | ---: | --- | --- |
| −100 mV | +0.223687 V | Yes | Fail |
| +100 mV | −0.282252 V | Yes | Fail |

The 0–20 ns net supply energies are approximately 1.870 and 1.794 pJ,
respectively, excluding input/clock-driver and bias-generation costs. These
are two decision-boundary simulations, not complete ADC conversion costs.
The improved hypothetical netlist result does not transfer to this layout:
actual routing parasitics alter the result.

## The previous DRC zero was not full-cell clearance

Magic emitted `Total DRC errors found: 0` in a run that also emitted a nonzero
cell error-tile count. The new audit waits for completion and records every
`drc listall why` rule/region result for the flattened cell. Under that check:

| Layout | Full-cell rule-region reports | Pass |
| --- | ---: | --- |
| Original `physical-integrated-tail-local-final` | 1,918 | No |
| Repaired v4 | 1,951 | No |

These are rule-region counts, not counts of distinct independent defects.
The reports are in `recovery-20260909/drc-original-full-cell/result.json` and
`recovery-20260909/drc-repaired-full-cell/result.json`. The audit hashes match
the corresponding layout files. Most violations predate this repair: local
interconnect/contact overlap, via landing/enclosure, and spacing requirements.
The repair also introduces metal5/via4 width, enclosure and spacing violations.
Historical zero-count claims for this original macro must not be treated as
full-cell DRC passes. Other historical candidates have not been audited here.

`repair_result.json` preserves the old summary-parser field from the run; its
`drc_count: 0` is superseded by the explicit full-cell audit. The generator now
waits for DRC and refuses to interpret a nonzero error-tile count as zero.

## Connected hardware evidence

`evidence/aimc-simulator-adapters/converter-physical-repair-current.json` binds
the layout repair, transient, original DRC and repaired DRC reports by hashes.
It reports connections repaired, DRC failed, electrical margin failed and
physical analog authorization false. The software physical-gate importer
verifies those hashes and carries the result into the workload evidence.
The runtime distinguishes a repaired connection from failed layout rules;
neither can enable a missing physical analog executor.

The next physical work is a rule-correct primitive/contact/routing rebuild
with a full-cell audit, then gain/loading and full-converter qualification.
Further nominal latch sweeps alone cannot close this failure. Model-level
quality, representative workload validation, matched array/converter costs,
target/controller binding and measured hardware comparison remain program gates.

## Commands

From the EDA project, use new output directories:

```bash
python3 scripts/repair_preamp_layout_connections.py --source evidence/aimc-simulator-adapters/active-converter-macro-candidate/physical-integrated-tail-local-final --output evidence/aimc-simulator-adapters/recovery-20260909/new-repair
python3 scripts/audit_converter_layout_drc.py --source evidence/aimc-simulator-adapters/recovery-20260909/new-repair --output evidence/aimc-simulator-adapters/recovery-20260909/new-drc
AIMC_SENSE_LOAD_OHM=100000 python3 scripts/run_active_converter_macro_extracted_transient.py --candidate-dir evidence/aimc-simulator-adapters/recovery-20260909/new-repair --input-diffs-mv -100 100
python3 scripts/check_full_cell_drc_reporting.py
```
