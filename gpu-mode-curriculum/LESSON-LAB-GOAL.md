# GPUMODE 118-Lesson Lab Coverage Goal

Build a lab coverage layer that treats every GPUMODE lesson as an implementable programming unit.

The end state is not just a list of ideas. The repo must produce:

- a gap analysis for all 118 lessons;
- one generated lab directory per lesson;
- runnable `starter.py` and `measure.py` files for every lesson lab;
- `measurement-contract.json`, `tasks.json`, `lab.json`, and `measurements.json` for every lesson;
- a consolidated lesson-lab index and run report;
- site pages that expose coverage and links from lessons to their generated lab;
- verification that fails if any lesson lacks a lab, measurement, task list, or contract.

Local runtime caveat: these lesson labs start as CPU proxy programs because this machine does not expose CUDA/HIP compilers or a visible GPU runtime. The contract for each lab requires an explicit promotion task to replace or extend the proxy with CUDA, Triton, HIP, JAX, profiler, or serving-runtime code on a GPU host.
