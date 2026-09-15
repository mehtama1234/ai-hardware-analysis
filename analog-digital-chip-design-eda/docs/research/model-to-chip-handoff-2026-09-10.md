# Model-to-Chip Handoff

**Snapshot:** 2026-09-11  
**Owner:** ongoing shared lab work  
**Status:** active; analog path is not authorized

## What this handoff is for

This document lets the next work session resume without reconstructing the
investigation. It records what is proven, what failed, where the artifacts are,
and the next experiment. It is intentionally conservative: a completed SPICE
transient does not equal a qualified converter, and a model match does not
equal a hardware speedup claim.

## Current decision

Keep native digital GPU execution as the authoritative path. The analog/hybrid
path remains an experiment until the exact-map, robustness, energy, and matched
workload gates close.

## Proven reference

The fixed-decision Sky130 FS diagnostic repeatedly reproduces:

```text
[0, 2, 4, 6, 7]
```

The transient completes and the fixed arm is the reference for every sequential
experiment. This is a fixed-control diagnostic, not closed-loop qualification.

## Current sequential result

The latest stable two-control run uses:

- raw comparator decision capture;
- separate trial override and retained-state switches;
- break-before-make timing;
- trial and retained PMOS/NMOS edge probes; and
- a completed five-conversion FS transient.

The raw-capture version reached real state rails and produced `[0, 0, 15, 0,
0]`. A later sample-reset test returned `[0, 0, 0, 0, 0]`, and a fixed-state
two-control isolation returned `[8, 0, 8, 0, 0]`. These results prove useful
parts of the handoff but do not qualify the converter.

The most recent reference-calibration screen used sequential references
`[1.1, 1.4, 1.1, 1.4, 1.75]` and still returned all zeros. This rules out a
simple reference-window mismatch as the primary repair.

## Local retention-fix diagnostic

The corrected generator was also exercised against the pinned local Sky130
models in `evidence/aimc-simulator-adapters/local-retention-fix.json`. All five
conversions completed, and the retained state now reaches near-rail values for
the first two conversions (`0.078/1.717/1.715/0.077 V`, then
`0.000/0.161/1.800/0.000 V`). This confirms that separating the trial override
from the retained-state driver repaired the state-storage ownership defect.

The same run remains rejected: later DAC nodes leave the legal range and the
decoded sequence is not the expected `[0, 2, 4, 6, 7]`. The result is a local
diagnostic only; the next Colab receipt must reproduce these probes with the
pinned bundle before the repair is treated as portable physical evidence.
The one-conversion DAC legality comparison is recorded in
`docs/research/continuous-sar-dac-legality-screen-2026-09-11.md`.
The runner now also records `post_trial_db_v` probes for all four plates after
each trial, making the rail-handoff timing observable in both local and Colab
receipts.
The fixed-state handoff receipt confirms the per-bit rail polarity follows a
known pattern; the live loop's all-low capture therefore points upstream to
decision capture and state restore.
The raw decision sources have now been corrected to use `V(outn)-V(outp)`, the
same polarity as the accepted comparator measurement. Static deck inspection
confirms the correction. A one-conversion run capturing at the decision edge
now converges and records rail-valued raw/state nodes in
`evidence/aimc-simulator-adapters/local-raw-latecapture1-100ps.json`; the DAC
trajectory remains rejected and requires a full Colab reproduction.

## Evidence locations

Authoritative raw receipts are under:

```text
analog-digital-chip-design-eda/evidence/colab-fixedtwocontrol-ab-20260910/comparison.json
analog-digital-chip-design-eda/evidence/colab-rawcapture-ab-20260910/comparison.json
analog-digital-chip-design-eda/evidence/colab-owner-ab-20260910/comparison.json
analog-digital-chip-design-eda/evidence/colab-refcal-ab-20260910/comparison.json
analog-digital-chip-design-eda/evidence/colab-resetboundary-ab-20260910/comparison.json
analog-digital-chip-design-eda/evidence/colab-edgeprobe-ab-20260910/comparison.json
analog-digital-chip-design-eda/evidence/colab-rawcapture-ab-20260910/online-schedule-audit.md
```

The qualification ledger is:

```text
analog-in-memory-ai-inference/software-architecture/experiments/gpt2-hybrid-v1/qualification/matrix.json
```

The isolated one-bit Sky130 bottom-plate fixture is measured but not accepted in
`analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/sky130-bottom-plate-cell.json`.
It covers four nominal cases with non-overlap control; it is the starting cell
for the required two-cell and four-bit reconstruction, not converter proof.

The first shared-top-plate two-cell reconstruction is now measured in
`analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/sky130-two-bottom-plate-cells.json`.
All four code combinations converge, but selected high rails settle near
`1.171 V` rather than `1.8 V` after correcting the original enable waveform.
The fixture is therefore explicitly marked
`two_cell_fixture_measured_not_accepted`; the next repair target is high-side
charge transfer and settling margin before reconnecting the four-bit array.
An attempted 64 µm PMOS sizing screen timed out before producing a complete
receipt (`sky130-two-bottom-plate-cells-pmos64-timeout.json`), so brute-force
width increase is rejected as the next fix; isolation and a bounded handoff
remain the preferred redesign.
The complementary NMOS high-side assist screen also timed out before a
complete four-code receipt (`sky130-two-bottom-plate-cells-tg-assist.json`).
This rejects the naive parallel transmission-gate assist and keeps the next
repair focused on isolated, finite-edge charge transfer.
Adding a `1 kΩ` or `10 kΩ` high-side keeper likewise timed out in the shared
two-cell fixture (`sky130-two-bottom-plate-cells-keeper1k.json` and
`sky130-two-bottom-plate-cells-keeper10k.json`). Passive low-value rail keepers
are therefore rejected; the cell needs a sequenced active handoff with a
bounded load.
An isolated timing screen at `3.9 ns` still reached only `1.669 V` on the
selected high rail (code 1), outside the `100 mV` target window. The existing
16 µm PMOS therefore needs either a longer legal acquisition interval or a
different isolated cell topology; the 2.5 ns SAR boundary cannot yet be
claimed.
With the same 16 µm PMOS and corrected controls, extending the isolated
measurement to `7.9 ns` reaches `1.7995 V` (code 1), inside the 100 mV target.
This separates a timing requirement from a topology failure: the next SAR
revision should test a legally extended acquisition phase before changing the
transistor cell again.

The active design notes are:

```text
analog-digital-chip-design-eda/docs/research/sky130-dac-bottom-plate-switch-redesign-work-order.md
analog-digital-chip-design-eda/scripts/run_sky130_continuous_physical_sar.py
analog-digital-chip-design-eda/colab/run_fs_fixed_vs_sequential_ab.py
analog-digital-chip-design-eda/colab/validate_sequential_control_deck.py
```

## Reproduce the structural checks

```bash
python3 analog-digital-chip-design-eda/colab/validate_sequential_control_deck.py
python3 analog-digital-chip-design-eda/scripts/check_sequential_bit_mapping.py
python3 -m py_compile \
  analog-digital-chip-design-eda/scripts/run_sky130_continuous_physical_sar.py \
  analog-digital-chip-design-eda/colab/run_fs_fixed_vs_sequential_ab.py
```

The canonical A/B harness enables `AIMC_CONTINUOUS_STATE_CAPTURE_RAW=1` for
sequential cases, so new receipts include the raw comparator boundary by
default.

The preflight must report `status: ready`, including the explicit
`two_control_timing_contract` check for the four trial starts, pulse widths,
and retention gating. These checks prove deck structure only; they do not
authorize analog execution.

The receipt also records the schedule as data: trial starts at `5, 21, 37,
53 ns`, a `1 ns` break-before-make interval, `14 ns` trial width, and an `80 ns`
conversion period. This is the schedule contract to compare against every
future Colab transient. The structural preflight also requires at least
`6.7 ns` of trial width, based on the isolated 7.9 ns rail screen minus the
1.2 ns high-side enable delay. The current two-control deck provides `14 ns`,
so the remaining online failure is more likely state ownership or capture
alignment than insufficient trial window.

## Next work order

1. Keep retained state independent from plate acquisition reset.
2. Add measurements at each trial edge for `gp_dacN`, `gn_dacN`, bottom plate,
   and the trial/retained switch controls.
3. Compare the online trial schedule with the fixed arm at the same four sample
   times. Resolve whether the candidate bit is actually connected to the DAC
   plate before comparator capture.
4. Correct the conversion-boundary initialization and state-to-bit contract.
5. Rerun the five-conversion FS A/B on Colab T4 and preserve the full JSON.
6. Only after an exact map is repeated should PVT, noise, mismatch, energy, or
   DeepSeek workload integration resume.

The first saved schedule audit is generated with:

```bash
python3 analog-digital-chip-design-eda/colab/analyze_online_schedule.py \
  analog-digital-chip-design-eda/evidence/colab-rawcapture-ab-20260910/comparison.json \
  --output analog-digital-chip-design-eda/evidence/colab-rawcapture-ab-20260910/online-schedule-audit.md
```

It shows the retained-state rails, trial rails, and retained-control rails for
each conversion so the next Colab run can target a specific boundary rather
than infer behavior from the final code alone.
The generator now also records the raw comparator decision at the same capture
sample (`raw_dec_v`), allowing the next receipt to separate comparator polarity
from state-storage or gate-driver failure.

The first Colab T4 rerun with that instrumentation is saved under
`evidence/colab-rawcapture-ab-20260911/`. Raw comparator nodes are clean 0/1.8 V
rails, while captured state nodes sit in intermediate ranges (`~0.09 V` or
`~1.64 V`) and the resulting codes are `[15, 0, 6, 14, 5]`. This localizes the
online defect to state storage/restore or its threshold contract; comparator
polarity is no longer the leading hypothesis.

## Colab operating rule

Use a pinned bundle and upload the repository tarball plus the Sky130 and
dependency bundles. Download the JSON before stopping the session. If Colab
returns `TooManyAssignmentsError`, treat that as an infrastructure condition,
not circuit evidence; keep the goal active and continue structural work.

Build the correctly rooted upload archives with
`colab/build_sky130_colab_bundle.py`; the helper emits the source, ngspice, and
device-model bundles expected by `bootstrap_continuous_sar.py`.

Every continuous-SAR receipt now carries an `experiment_controls` object,
including failed and timed-out runs. This makes the handoff reproducible: the
next session can identify the topology and timing knobs actually exercised.
The provenance smoke receipt
`evidence/aimc-simulator-adapters/local-provenance-failure128b.json` is a
timeout artifact and has no acceptance value.

Run the next Colab handoff in this order:

```bash
python3 colab/validate_sequential_control_deck.py
python3 scripts/validate_aimc_physical_evidence.py
python3 colab/build_sky130_colab_bundle.py
# upload the emitted archives; run the matching bootstrap in Colab T4
# download JSON and Markdown receipts before ending the session
python3 scripts/validate_aimc_physical_evidence.py
```

Use the checked-in campaign contract
`colab/sky130-top-plate-acquisition-settings.json` as
`/content/sky130-campaign-settings.json`; do not recreate its environment by
memory or by filename. Validate it locally with
`python3 colab/validate_top_plate_campaign_settings.py` before uploading.
When the repository is unpacked under `/content`, the campaign can select the
same contract directly with `AIMC_USE_BUNDLED_TOP_PLATE_SETTINGS=1`; the
resulting summary records the settings SHA-256.

Preserve the Colab runtime, GPU, ngspice version, bundle hashes, timeout,
output stem, and `experiment_controls` with every receipt. A timeout is an
infrastructure result and cannot be promoted to analog accuracy evidence.

## Claim boundary

The cross-repository proof was rerun after correcting backend evidence-batch
path resolution and completed with `PASS cross_repo_aimc_loop`. Its saved
record is
`evidence/aimc-hardware-lab/cross-repo-loop-proof.json` (10 governor rows,
6 imported evidence records, RTL pass, and 3 supported / 2 needs-review lab
claims). This proves the software-to-lab evidence loop; it does not promote
the analog converter or production claim.

The current work demonstrates a reproducible digital reference and a growing
set of physical handoff diagnostics. It does not yet demonstrate a qualified
closed-loop analog converter, PVT or mismatch yield, energy advantage, silicon
behavior, or end-to-end DeepSeek acceleration.
The next executable work order is
`docs/research/sky130-top-plate-acquisition-work-order-2026-09-11.md`.
The five-conversion diagnostic with decision-edge capture completes, but the
held state alternates between near-low and near-high values across conversions
and every decoded code is `15`. This is now a repeated-history state-capture
failure, not a simulator timeout; reset/restore sequencing remains the next
hardware repair target.
An isolated one-conversion run with the cross-coupled restore latch disabled
holds a stable low state (`~4 mV` on all bits), strengthening the diagnosis.
The corresponding five-conversion run is numerically stiff, so the next
implementation should use a clocked, damped restore element rather than the
present cross-coupled latch.
The first damped-restore receipt (`evidence/aimc-simulator-adapters/local-damped-restore1-100ps.json`)
reproduces the stable low hold with finite 100 Ω rail paths. A five-conversion
run now completes in `evidence/aimc-simulator-adapters/local-damped-restore5-100ps.json`,
but raw decisions alternate all-low/all-high by conversion and every code is
`15`. The preamp differential has one sign across all four bit decisions within
each conversion, and the comparator follows it. The remaining issue is the
DAC charge trajectory and plate handoff, not only the restore latch.
The PMOS-bank screen (`evidence/aimc-simulator-adapters/local-pmosbank16-100ps.json`)
shows that stronger high-side drive brings the four DAC samples close together
near `0.36 V`, but does not restore bit weighting. The next topology change
must preserve capacitor isolation and binary weighting while improving rail
drive; simply adding more parallel PMOS devices is rejected.
The combined isolated-plate/timed-handoff fixture preserves a mixed per-bit
rail pattern under fixed states in
`evidence/aimc-simulator-adapters/local-isolated-handoff-fixed1-100ps.json`.
This makes the settling and comparator sample interval the next measurable
repair target.
An early-handoff diagnostic with a shortened 3 ns trial still leaves the
sampled DAC out of range (`local-isolated-handoff-early-fixed1-100ps.json`),
so top-plate redistribution and comparator input isolation must be examined
alongside timing.
The 100 fF capacitive copy diagnostic (`local-capcopy-fixed1-100ps.json`)
changes the fixed-pattern preamp signs to `[+,-,-,-]`, showing that input
loading was masking bit information. The DAC plates themselves remain outside
the legal range, so this is an interface improvement rather than acceptance.
Adding 100 fF sense isolation at the comparator boundary does not improve the
trajectory or weighting (`local-senseisolation-fixed1-100ps.json`), so the
preferred interface remains the direct 100 fF capacitive copy without this
extra sense capacitor.
Increasing the top dummy capacitor to 10 pF attenuates the excursion but still
leaves a negative sample and weakens the MSB (`local-capcopy-dummy10p-fixed1-100ps.json`).
This is a damping tradeoff, not a viable weighting fix.
Enabling the top-reset primitive improves selected nodes but still leaves the
top trajectory outside range (`local-capcopy-topreset-fixed1-100ps.json`), so
reset alone is insufficient.
The bootstrapped high-side NMOS diagnostic improves the MSB sample to `0.565 V`
but leaves lower-bit samples negative (`local-bootstrapped-high-fixed1-100ps.json`).
It is a useful charge-transfer direction, but it does not yet preserve the
full binary range or satisfy the gate-oxide claim boundary.
An opt-in 10 pF common-mode top hold attenuates the swing but still leaves
negative samples (`local-top-hold10p-fixed1-100ps.json`), so top capacitance is
not a sufficient charge-preservation fix.
The opt-in post-trial acquisition schedule (`AIMC_CONTINUOUS_POST_TRIAL_SAMPLE=1`)
settles the bottom rails but collapses the top node and preamp signal in the
fixed-pattern test (`local-postsample-fixed1-100ps.json`). The handoff must
therefore preserve top-plate charge, not only clamp the bottom plates.
Increasing the capacitive copy to 1 pF removes nearly all preamp differential
while leaving the DAC out of range (`local-capcopy1p-fixed1-100ps.json`). Keep
the 100 fF copy as the interface baseline; larger capacitance is rejected.
Combining top reset with bottom ground precharge improves the sampled values
slightly but still leaves the top trajectory outside range
(`local-capcopy-reset-precharge-fixed1-100ps.json`). The next design should
replace these broad clamps with a phase-specific acquisition schedule.
The five-conversion live capacitive-copy run completes with bit-dependent
preamp magnitudes but a uniform sign within each conversion; all codes remain
`15`. The interface is less loaded, but the DAC feedback still does not create
per-bit decisions.
The source-follower copy variant gives weaker separation (`+0.068/-0.007/-0.006/-0.004 V`)
than the 100 fF capacitive copy, so the capacitive interface remains the
preferred handoff candidate for the next timing experiment.
