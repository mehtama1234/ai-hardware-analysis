# Layout algebra and bijection checks

This lab makes the indexing contract behind tiled GPU kernels executable. It
implements row-major, tile-major blocked, and XOR-swizzled 2-D layouts and
checks bounds, bijection, and inverse lookup by exhaustive enumeration.

These are host-side layout contracts, not CuTe DSL execution or a bank-conflict
measurement. The output is useful before writing a CUDA/Triton kernel because a
layout with aliases or dropped coordinates cannot be correct on any backend.

```bash
python layout-algebra/run_layout_checks.py
python -m unittest discover -s layout-algebra/tests -v
```
