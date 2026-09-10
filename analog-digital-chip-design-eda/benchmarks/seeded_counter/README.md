# Seeded counter end-to-end benchmark

This benchmark is the executable proof slice for the verification platform. It
intentionally removes the counter's `enable` guard, then exercises planning,
procedural-check generation, Icarus compilation, VVP simulation, VCD evidence,
logic-aware triage, human-approved repair, retest, and closure.

Run the complete flow from this directory:

```bash
python3 run_end_to_end.py
```

The expected baseline result is a classified failure. The retest applies the
bounded repair only to `runs/retest/counter_repaired.sv`; the original
`counter.sv` remains unchanged. The summary, session ledger, closure report,
and proof artifacts are written below `runs/`.
