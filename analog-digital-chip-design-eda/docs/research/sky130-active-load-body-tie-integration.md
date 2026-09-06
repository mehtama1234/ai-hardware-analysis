# Sky130 Active-Load Body-Tie Integration

The cross-coupled PMOS active-load cell now includes a local Sky130 n-well tap.
The tap uses n-substrate diffusion, the corresponding diffusion contact and
local-interconnect/via stack, and two guarded metal2 supply routes. The routes
connect both PMOS source domains and the well supply without crossing the
metal2 output-to-gate feedback path.

Magic extraction of the standalone cell reports:

- two PMOS devices;
- cross-coupled `out_p`/`out_n` gate and drain connectivity;
- a common `vdd` source supply;
- the PMOS well/body on that same supply; and
- zero DRC errors.

The integrated parent assembler previously discarded the new `nsubdiff`,
`nsubdiffcont`, and `viali` sections. Preserving those sections closes the
same body connection in the flattened parent. The integrated extraction now
reports both active-load PMOS source terminals and both bodies on isolated
`vdd_active`, while the parent `vdd` remains separate. The parent contains
five NMOS and four PMOS devices and remains DRC-clean.

The physical artifact is recorded in
`evidence/aimc-simulator-adapters/sky130-latch-precharge-tail-active-load-physical-check.json`.
The bounded extracted transient rerun measured all 30 cases and regenerated
12. The six large-signal cases for each input polarity regenerate strongly;
the small `+/-10 mV` and zero-differential cases do not meet the current
regeneration threshold.

The follow-up strength sweep was corrected to use the same 4 ns evaluation
point as the main transient gate and to model the sense pair, feedback pair,
and clocked tail separately. All 192 combinations completed, but none
produced a polarity-consistent `0.5 V` evaluation margin. The best small-signal
case reached about `54.7 mV` with a weak tail, but the opposite polarity was
incorrect. This rules out simple strength tuning within the tested range as a
sufficient repair. The corresponding evidence is
`evidence/aimc-simulator-adapters/sky130-active-load-strength-sweep.json`.

## Claim boundary

This closes the active-load body/source extraction gate. It does not prove
Sky130-model convergence, noise, mismatch, kickback, PVT yield, LVS against a
matching schematic, SAR conversion accuracy, or converter acceptance. The
analog converter therefore remains guarded behind the existing digital
fallback.
