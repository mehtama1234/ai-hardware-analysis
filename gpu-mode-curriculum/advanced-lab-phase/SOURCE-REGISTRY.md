# Primary-source registry — topic inventory complete, source review staged

This registry connects each of the handbook's 24 topics to a canonical starting
source, local artifacts, evidence classification, prerequisites, and an open
acceptance gate. The machine-readable inventory is
[source-registry.json](source-registry.json), validated by
`python scripts/verify_source_registry.py`. A topic entry is not a claim that
the source was fully reviewed or that local hardware execution was accepted.
The handbook's stated 145 sources and 74 audio artifacts have not been provided
as an individually identified bibliography; those counts remain unverified.
The original handbook is unchanged.

## Core entries

| ID / handbook topics | Primary source and review scope | Local connection | Remaining verification |
|---|---|---|---|
| ATT-001 / 1, 21 | [FlashAttention, arXiv 2205.14135v2](https://arxiv.org/html/2205.14135v2); section 3.1, B.2 and selected B.4 text reviewed | [Paper-to-code mapping](../flash-attention-backward/PAPER-MAPPING.md) | Complete implementation correspondence, fused GPU execution and hardware evidence remain open |
| GEM-001 / 3, 5, 14 | [Official Triton matmul tutorial](https://triton-lang.org/main/getting-started/tutorials/03-matrix-multiplication.html); blocked algorithm, stride arithmetic, program ordering and autotuning sections located/reviewed | [GEMM lab](../../gpu-kernels-serving-lab/23-gpumode-shared-memory-gemm/README.md) supplies the numerical/timing baseline for a future common-workload comparison | Pin a Triton revision, execute on suitable hardware, compare identical shapes/dtypes; tutorial results are not local measurements |
| DSL-001 / 3, 10 | [NVIDIA CuTe DSL programming model](https://docs.nvidia.com/cutlass/latest/media/docs/pythonDSL/cute_dsl.html); official documentation located, landing page inspected | Compiler/layout work package; no CuTe DSL execution accepted by the current checkpoint | Choose a supported version/architecture, inspect relevant layout APIs, then compile and test; `latest` is a moving reference |
| NUM-001 / 2 | [OCP Microscaling Formats v1.0 specification](https://www.opencompute.org/documents/ocp-microscaling-formats-mx-v1-0-spec-final-pdf); retry succeeded; sections 4, 5.1–5.3.3 reviewed for format boundaries | [Local packed INT4](../../gpu-kernels-serving-lab/common/packed_int4.py) uses integer elements and FP32 scales, not MXFP4 | Complete scale/conversion/operation review and conformance vectors before claiming an MX implementation |
| CMP-001 / 5, 21 | [PyTorch maintainer AOTAutograd explanation](https://dev-discuss.pytorch.org/t/how-does-torch-compile-work-with-autograd/1621/2); reviewed joint tracing, partitioning and compiled function integration | [CPU compiler experiment](../compiler-runtime-inspection/run_cpu_compile.py) captures forward/backward modules and checks gradients | Broader shapes, numerical adversaries, graph breaks, profiler evidence and GPU execution |
| CMP-002 / 5, 12 | [PyTorch v2.4.1 Inductor utilities](https://github.com/pytorch/pytorch/blob/v2.4.1/torch/_inductor/utils.py); installed version's `run_and_get_code` implementation inspected directly | Generated-module capture in compiler and compiled-training experiments | Private API is version-specific; temporary wrapper include paths are not a self-contained native build archive |

## MoE entries

| ID / topics | Primary source and review scope | Local connection | Remaining verification |
|---|---|---|---|
| MOE-001 / 4, 15 | [Shazeer et al., arXiv 1701.06538v1](https://arxiv.org/html/1701.06538v1); sections 2–3.2 and balancing discussion inspected | Weighted expert sum, selected-logit normalization and expert ownership in [our reference](../moe-routing-all-to-all/REFERENCE.md) | Noise, balancing objectives, trained model and hardware performance are not reproduced |
| MOE-002 / 15 | [Fedus et al., JMLR 23(120), 2022](https://www.jmlr.org/papers/volume23/21-0998/21-0998.pdf); PDF retry succeeded; section 2.2 and router/distributed pseudocode in figures 15–16 inspected | Explicit contrast between Switch's full-softmax top-1 gate and our selected-logit gate; local capacity/residual differences documented | Full architecture/training correspondence and quality evaluation remain open; local top-1 is not Switch |

## Required completion work

The topic-level inventory is now complete. Remaining source work is staged rather
than hidden: upgrade `source_status` from identified to reviewed where needed,
record revisions before depending on moving upstream code, and expand entries
into claim-level citations. Separate external published performance from local
results. Paper abstracts and landing pages establish only the narrow review
scope recorded in each entry, not full-paper review, implementation equivalence,
or hardware acceptance.
