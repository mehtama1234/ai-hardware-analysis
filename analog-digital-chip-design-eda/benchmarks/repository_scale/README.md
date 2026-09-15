# Repository-scale benchmark seed

This directory contains the first runnable task for the next-stage benchmark.
It executes the existing seeded-counter RTL testbench twice: the baseline copy
must fail because `enable` is ignored, and the isolated candidate copy must
pass after the repair. The canonical checkout is snapshotted before and after
the runs, and the result is blocked unless the candidate changed a declared
source file while the canonical source remained unchanged.

Run it with:

```bash
python3 scripts/run_seeded_repository_scale_demo.py
```
