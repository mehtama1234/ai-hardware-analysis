# Converter contact/routing rebuild: full-cell DRC passes

The rebuilt macro passes the completed full-cell Magic DRC audit with zero
rule-region reports. It preserves the repaired preamp connections and all 13
extracted transistor instances, including their node connections, models and
geometry parameters. This is progress on the same physical candidate, not a
replacement with an ideal netlist.

The electrical margin still fails. The physical analog gate remains false.

## What changed

The rebuild corrects poly/local-interconnect/contact enclosure, tap enclosure,
metal contact landing, and via enclosure across the existing cells. It replaces
undersized via4 cuts and metal5 wires, moves the long preamp input route away
from latch gate escapes, and shifts one starter-column stripe away from the
latch source bus. Each revision is an isolated copy; source and generated
layout hashes and generator snapshots are preserved.

| Candidate | Full-cell DRC rule-region reports |
| --- | ---: |
| Original macro, before preamp connection repair | 1,918 |
| Physical preamp connection repair | 1,951 |
| Contact enclosure rebuild v1 | 217 |
| Rebuild v2, corrected one-direction metal1 enclosure | 73 |
| Rebuild v3, corrected remaining route spacing/enclosures | 0 |

These are rule-region reports, not independent defect counts. The checker
records `drc listall why` after `drc catchup`; it does not rely on the historical
zero summary count. Passing this check is not foundry signoff or density/LVS
qualification.

## Exact artifacts and measured result

The layout and extraction are in
`evidence/aimc-simulator-adapters/recovery-20260909/contact-rebuild-v3/`.
The full-cell audit is in `contact-rebuild-v3-drc/result.json` beside that
directory. Audit input hashes match the generated layout hashes.

The extracted netlist SHA-256 is
`d94c84fa2534bd92e0c763ec9dd58de6a7f236a5c5fafa20a3ba6abd3673bcc5`.
`device_preservation.json` compares every transistor line against the repaired
predecessor. It does not substitute for independent schematic LVS. Routing
parasitics change, as expected.

The same-netlist transient is
`active-converter-macro-transient/20260909T170213704860Z/result.json`:

| Input differential | Output differential at 18 ns | Correct sign | ≥0.9 V margin |
| --- | ---: | --- | --- |
| −100 mV | +0.222409 V | Yes | No |
| +100 mV | −0.321264 V | Yes | No |

Conditions: 1.8 V supply, 0.9 V input common mode, 100 kΩ sense loads, nominal
TT models. The completed rerun used a 60-second per-case process timeout. The
earlier run `20260909T170050134872Z` preserves one 20-second timeout and one
completed case. No timed-out case was counted as passing.

`physical_readiness.json` in the rebuilt directory freezes the joined result.
`evidence/aimc-simulator-adapters/converter-physical-repair-current.json` points
to the same evidence for the software importer. It records DRC and connectivity
passed, electrical margin failed, and physical analog authorization false.

## Reproduction

From the EDA project, use new directories:

```bash
python3 scripts/rebuild_converter_contact_enclosures.py --source evidence/aimc-simulator-adapters/recovery-20260909/physical-preamp-route-repair-v4 --output evidence/aimc-simulator-adapters/recovery-20260909/new-contact-rebuild
python3 scripts/audit_converter_layout_drc.py --source evidence/aimc-simulator-adapters/recovery-20260909/new-contact-rebuild --output evidence/aimc-simulator-adapters/recovery-20260909/new-contact-drc
python3 scripts/extract_rebuilt_converter.py --candidate-dir evidence/aimc-simulator-adapters/recovery-20260909/new-contact-rebuild
AIMC_SENSE_LOAD_OHM=100000 python3 scripts/run_active_converter_macro_extracted_transient.py --candidate-dir evidence/aimc-simulator-adapters/recovery-20260909/new-contact-rebuild --input-diffs-mv -100 100 --timeout-seconds 60
```

## Remaining end-to-end work

The next electrical question is whether the loaded preamp/latch topology can
meet the actual converter resolution and decision-time contract. The ±100 mV
probe is far from a 12-bit threshold qualification. Gain, sampling, regeneration,
full SAR behavior, PVT/noise/mismatch and matched converter/array costs remain
open. The broader program still needs a representative task dataset and
acceptance contract, qualified array mapping, controller/target binding and a
measured analog-versus-digital hardware comparison. DRC closure alone does not
make the provisional GPT-2 array model physically valid.
