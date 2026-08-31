# Compiler Runtime Inspection

## First Question

A kernel source file can hide runtime risks before it is compiled: missing bounds masks, high shared memory, barriers, launch indexing mistakes, or tensor core claims without shape proof. This lane asks what can be checked from source before a GPU run.

## What The Code Does

- `compiler-runtime-inspection/compiler_runtime_inspection/inspector.py scans source features when present.`
- `scripts/run_compiler_runtime_inspection.py writes the source report.`
- `site/compiler-runtime-inspection.html lists feature and risk counts.`

## What The Measurement Proves

The measurement proves the curriculum can inspect CUDA, Triton, HIP, and custom op source through one source-level contract.

## What It Does Not Prove

It does not prove the compiled kernel is fast. Source inspection catches early risks; profiler evidence is still required for runtime claims.

## Read Next

- `site/compiler-runtime-inspection.html`
- `site/gpu-promotion.html`
