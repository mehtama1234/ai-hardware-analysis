# Compiler inspection: source hints versus executed generated code

The original `compiler_runtime_inspection/inspector.py` searches source text for
compiler/runtime patterns. Its report is static inspection, not proof of a
compiled kernel, fusion, or speedup. The separate experiment below executes CPU
Inductor compilation of the existing bias–tanh-GELU–residual operation.

## Reproduce

Use the [hash-locked CPU environment](../advanced-lab-phase/ENVIRONMENT.md) with
`g++` available, then run from the repository root:

```bash
python gpu-mode-curriculum/compiler-runtime-inspection/run_cpu_compile.py
```

The runner uses a temporary Inductor cache and a 300-second worker timeout.
It requests `backend="inductor", fullgraph=True`; compilation errors fail instead
of becoming an eager timing result. Code capture uses the private PyTorch 2.4.1
`run_and_get_code` hook inspected in the installed package. Other releases may
require adaptation. The wheel lock does not pin the host C++ toolchain.

[The raw report](reports/cpu-compile.json) includes generated Python wrappers
with embedded C++ source, source hashes, compiler version, input strides,
correctness errors, first-call times, and every steady-state sample.
Temporary include paths in captured code no longer exist after cleanup: the
capture is inspection evidence, not a self-contained distributable binary or
rebuild archive. Reproduce by running the source experiment again.

## What this execution showed

The initial recorded run used PyTorch 2.4.1+cpu. Every candidate and held-out
value check passed against FP64 eager evaluation rounded to FP32, with tolerances
`atol=2e-6, rtol=2e-5`. The held-out inputs multiply the original inputs by -3.25;
they do not establish general numerical robustness or a broad workload holdout.

| Shape | Input stride | Eager median | Compiled median |
|---|---|---:|---:|
| 7 × 33 | (33, 1) | 10.94 µs | 30.14 µs |
| 7 × 33 | (66, 2) | 9.81 µs | 25.68 µs |
| 32 × 128 | (128, 1) | 41.18 µs | 63.97 µs |

These are one run's ten host-wall samples after three warmups, not stable
cross-machine performance guarantees. First-call times were approximately
16.38, 5.74 and 6.92 seconds and are excluded from that table. Each first call
includes compiler/runtime setup and execution; the three cases share one worker
and are not independently cold process launches.

The captured wrapper calls one `cpp_fused_add_gelu_0` operation and allocates an
output buffer. For contiguous width 33, the generated C++ has eight-lane vector
loads through column 31 followed by a scalar tail. The strided case uses
`2*x1 + 66*x0` input addressing and a different gather construction; the wrapper
guards stride `(66,2)`. Inspect the code rather than inferring layout support
from output shape alone. Generated source is not disassembly or profiler proof.

Fusion did **not** produce a measured speedup in these cases. The samples include
compiled-call wrapper overhead and output allocation, so they do not identify
the isolated native kernel cost. Larger workloads, repeated sessions, randomized
measurement order and profiler traces are needed to explain performance robustly.

## Exercise and remaining gates

### Primary references and version boundaries

| Reference | What it supports here | What it does not establish |
|---|---|---|
| [PyTorch 2.4.1 compile implementation](https://github.com/pytorch/pytorch/blob/v2.4.1/torch/__init__.py) | Version-specific API used by this environment; inspect alongside the installed package | Compatibility with later compiler APIs or a speedup on our shapes |
| [PyTorch 2.4.1 Inductor utilities](https://github.com/pytorch/pytorch/blob/v2.4.1/torch/_inductor/utils.py) | The private `run_and_get_code` hook used to capture generated modules | A stable public code-capture API or a complete toolchain archive |
| [PyTorch maintainer explanation of AOTAutograd](https://dev-discuss.pytorch.org/t/how-does-torch-compile-work-with-autograd/1621/2) | Joint forward/backward tracing, partitioning and saved-versus-recomputed values | Evidence that our particular operation is faster or that an optimizer step was compiled |

The maintainer explanation describes AOTAutograd tracing a joint computation and
partitioning it into forward and backward graphs. Our captured modules provide
local execution evidence for that structure. This experiment does not enable the
separate experimental feature named **Compiled Autograd**; it uses AOTAutograd
through ordinary `torch.compile`. Do not confuse those names or infer that the
entire Python training loop is compiled from two captured native modules.

Locate the bias broadcast, residual addition, vector path, scalar tail and
stride guards in the first two captured wrappers. Predict what changing width
33 to 32 removes; run a separate experiment to test that prediction. Do not
replace recorded evidence with the prediction.

The initial evidence above is forward-only CPU compilation. The runner now also
requests first-order backward compilation, captures the generated forward and
backward modules, and checks input, bias and residual derivatives against FP64
eager autograd using a seeded nonuniform upstream gradient. Its separate training
samples include forward plus `autograd.grad`, not optimizer updates. Acceptance
of this extension requires a successful regenerated report containing `training`
results for every row; the initial forward-only report cannot establish it.

The subsequent backward run passed all three cases and captured separate
`forward` and `backward` AOT modules for each. Largest recorded absolute errors
were approximately `1.67e-6` for the input derivative, `2.86e-6` for the bias
derivative and zero for the residual derivative; elementwise combined absolute
and relative tolerances passed. Compiled forward/backward median times were
approximately 295, 250 and 251 µs versus eager 220, 170 and 177 µs for the three
rows. This is another measured loss on small CPU operations, not a training
speedup. The report is regenerated on reruns, so consult its current samples
rather than treating these historical observations as fixed performance.

Graph-break examples, application integration, CUDA/Triton comparison, PTX/SASS capture, architecture
layouts and bounded kernel synthesis remain open. The runner is now registered
in the aggregate advanced checkpoint. The expanded isolated CPU run subsequently
passed all 64 tests and ten CPU experiments, including this compiler runner.
It does not complete the compiler package.
