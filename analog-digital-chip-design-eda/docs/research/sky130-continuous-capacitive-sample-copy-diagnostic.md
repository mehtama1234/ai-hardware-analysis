# Sky130 Continuous SAR Capacitive Sample-Copy Diagnostic

This branch inserts matched capacitors from the comparator storage nodes into
separate preamp-gate nodes, with finite matched common-mode restoration. It
is intended to isolate the DAC sample capacitors from preamp/latch kickback
without adding an always-on source-follower operating point.

## Full measured map

| Expected code | Final code | Bottom plates |
|---:|---:|---|
| 0 | 1 | pass |
| 2 | 3 | pass |
| 4 | 6 | pass |
| 6 | 7 | pass |
| 7 | 8 | fail |

The five-conversion transient completes, and the copied reference-side node
remains well behaved in the one-conversion diagnostic. However, the complete
map is incorrect and the highest representative code still produces an
illegal bottom-plate excursion. The branch is therefore not an acceptance
result.

Evidence:

- `evidence/aimc-simulator-adapters/sky130-continuous-capacitive-copy-code2-diagnostic.json`
- `evidence/aimc-simulator-adapters/sky130-continuous-capacitive-copy-nmos64-bank8-full-diagnostic.json`

## Decision

The capacitive copy stage is retained as a useful isolation mechanism, but it
does not close the SAR. Its systematic positive code error indicates that the
copied-node common-mode/threshold relationship and the retained-bit timing
must be co-designed. The next revision should use an explicit two-phase
sample, copy, and latch interface with a calibrated reference at the copied
node, rather than attaching the copy network to the existing timing schedule.
