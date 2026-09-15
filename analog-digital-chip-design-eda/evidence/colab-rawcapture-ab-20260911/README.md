# Colab raw-capture A/B — 2026-09-11

This directory contains the first Sky130 FS sequential run after separating
retention control from the phase-safe trial driver.

## Receipt

- `sequential-raw.json` — completed five-conversion FS transient
- `online-schedule-audit.md` — raw comparator, held-state, and gate-ownership summary
- `envelope.json` — Colab runner envelope with return codes and stdout/stderr

The raw comparator decisions reached valid 0/1.8 V rails. Held state remained
intermediate and the decoded sequence was `[15, 0, 6, 14, 5]`, so this run is
diagnostic evidence only. It does not qualify the converter or authorize the
analog path.

The next run must use the corrected generator and the pinned bundle builder,
then compare the same probes before and after retention hold.
