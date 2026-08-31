# vLLM-style serving: vLLM scheduler / TTFT and batching bottleneck

Query: `vllm scheduler kv cache ttft batching`

## Build Target

Suspect batching policy, chunked prefill, prefix-cache reuse, admission control, or SLA-driven decode scheduling.

## Starter Files

- `starter.py`: local harness that runs or classifies the starter source.
- `scheduler.py`: first source file to modify.
- `measure.py`: experiment harness that writes `measurements.json`.
- `tasks.json`: concrete reading, programming, measurement, and comparison tasks.
- `measurements.json`: durable local starter measurement after `python3 measure.py`.
- `measurement-contract.json`: expected evidence shape for this project.
- `project.json`: generated metadata linking lessons, sources, papers, labs, and measurements.

## Existing Lab To Compare Against

- `gpu-kernels-serving-lab/20-gpumode-vllm-scheduler`
- `cd ../gpu-kernels-serving-lab/20-gpumode-vllm-scheduler && python3 run.py && python3 build_page.py`
- measurement: `20-gpumode-vllm-scheduler/out_gpumode_vllm_scheduler.json`

## Lessons
- Lesson 14: [Lecture 100: InferenceX Continuous OSS Inference Benchmarking](https://www.youtube.com/watch?v=kPBTBl7xvEY)
- Lesson 16: [Lecture 98: GPU Observability](https://www.youtube.com/watch?v=-6FlMJ-AP74)
- Lesson 88: [GPU MODE IRL 2024 Keynotes](https://www.youtube.com/watch?v=FH5wiwOyPX4)
- Lesson 2: [Lecture 112: Production Megakernels for Real-World Inference](https://www.youtube.com/watch?v=loZ4xQ5RZuU)

## External Tutorials
- JAX Scaling Book: [All About Transformer Inference](https://jax-ml.github.io/scaling-book/inference/)
- Hugging Face: [LLM Course: Optimized Inference Deployment](https://huggingface.co/learn/llm-course/chapter2/8)
- Hugging Face: [Text Generation Inference Documentation](https://huggingface.co/docs/text-generation-inference/index)
- JAX Scaling Book: [Serving LLaMA 3-70B on TPUs](https://jax-ml.github.io/scaling-book/applied-inference/)

## Paper Cross-Checks
- ASPLOS: Past-Future Scheduler for LLM Serving under SLA Guarantees
  - `analysis/per-paper/asplos-2025-049.json`
- MLSYS 2025: FlashInfer: Efficient and Customizable Attention Engine for LLM Inference Serving
  - `analysis/per-paper/mlsys-2025-000.json`
- MLSYS 2025: NEO: Saving GPU Memory Crisis with CPU Offloading for Online LLM Inference
  - `analysis/per-paper/mlsys-2025-024.json`
- ISCA: WindServe: Efficient Phase-Disaggregated LLM Serving with Stream-based Dynamic Scheduling
  - `analysis/per-paper/isca-2025-034.json`

## Local Run

```bash
python3 starter.py
python3 measure.py
```
