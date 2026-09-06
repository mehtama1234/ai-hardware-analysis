# Sky130 Direct Preamp DAC Handoff

This experiment connects the physical DAC top plate and reference directly to
the gates of the existing transistor preamplifier. The comparator input
storage-switch path is removed, so the DAC is not directly loaded by latch
storage capacitors.

The two-code handoff first passed after correcting the physical input mapping:
both critical code-7/code-8 polarities converged, with preamp differences of
approximately `0.447 V` and `0.281 V`. The required all-code run is weaker:

- `15/16` codes measured;
- `12/15` measured polarities correct;
- top-plate voltage reaches about `2.68 V` at high codes;
- code 0 was incomplete.

The direct preamp removes comparator kickback loading, but it does not repair
the DAC transfer or its legal voltage range. It is rejected as a converter
interface and remains a diagnostic candidate for a future actively regulated
split-DAC design.

Evidence: `evidence/aimc-simulator-adapters/sky130-direct-preamp-all-codes.json`.

The coupled runner exposes this experiment through
`AIMC_COUPLED_DIRECT_PREAMP=1`; the default path remains unchanged and was
rerun successfully after the hook was added.
