# Sky130 Continuous SAR Isolated Sample-Copy Diagnostic

The continuous SAR failure was traced to comparator storage nodes retaining
prior-cycle charge. This branch inserts matched NMOS source followers between
the DAC storage nodes (`sp`, `sn`) and the dynamic preamp gates. The source
followers are biased by matched finite resistors, so the preamp/latch cannot
directly kick the DAC storage capacitors.

## Result

The one-conversion branch is electrically measurable and keeps the DAC
bottom plates legal. With `4 um` followers and `100 kOhm` source bias, the
reference-side copied node remains approximately `0.695 V` through the later
cycles, demonstrating the intended isolation. The representative code-2
conversion nevertheless resolves as code `0`, not code `2`.

The five-conversion replay does not produce a valid map: ngspice encounters a
timestep failure at the first conversion's late LSB control transition. The
branch therefore cannot be used as acceptance evidence.

Evidence:

- `evidence/aimc-simulator-adapters/sky130-continuous-isolated-copy-code2-diagnostic.json`
- `evidence/aimc-simulator-adapters/sky130-continuous-isolated-copy-nmos64-bank8-full-diagnostic.json`

## Decision

The source-follower copy stage is retained as a rejected architectural
diagnostic. It confirms that storage-node isolation is physically meaningful,
but it does not solve the decision convention and introduces a repeated-run
convergence boundary. A future sample-and-copy stage must include explicit
sample timing, common-mode restoration, and a latch interface designed as one
coupled cell rather than adding always-on followers to the existing path.
