# Sky130 Continuous SAR Copy-Node Reset Diagnostic

After the capacitive sample-copy branch isolated the DAC storage nodes, this
experiment reset only the copied preamp-side nodes to `VDD/2` before each
sample. The intent was to remove preamp history without disturbing DAC charge.

## Result

The one-conversion code-2 diagnostic produced comparator decisions
`[0, 1, 0, 1]`, corresponding to code `10` rather than code `2`. It also
reintroduced an illegal bottom-plate excursion. Thus, clearing the copied
nodes does not preserve the required DAC/reference relationship.

Evidence:

- `evidence/aimc-simulator-adapters/sky130-continuous-copy-reset-code2-diagnostic.json`

## Decision

The copy-side reset is rejected. The evidence now separates three effects:
DAC storage history, copied-node history, and comparator regeneration. They
cannot be corrected independently by forcing either storage domain to a fixed
common mode. The next revision must use a genuinely phase-controlled sample
and hold with a matched reference path and a defined transfer instant.
