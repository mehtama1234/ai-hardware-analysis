# PyTorch Custom Op Lab

This lab connects kernel work to model integration by implementing and testing a
transformer-style fused `bias + GELU + residual` operator.

The local path uses a Python `torch.autograd.Function` so the forward and
backward contracts are testable on CPU. The `csrc/` files provide the
source-ready C++/CUDA extension boundary for promotion on a CUDA host.

## Run

```bash
python3 scripts/run_custom_ops.py
python3 scripts/verify_custom_ops.py
```

The report records randomized forward/backward correctness, shape coverage,
CPU timing, accelerator readiness, and whether the compiled CUDA extension is
ready or source-only on the current machine.
