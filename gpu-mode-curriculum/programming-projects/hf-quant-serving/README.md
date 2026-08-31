# Hugging Face serving baseline: Quantization / low-precision numerics path

Query: `hugging face transformers quantization tgi inference`

## Build Target

Suspect memory savings versus numerical drift, dequantization overhead, or unsupported low-precision kernels.

## Starter Files

- `starter.py`: local harness that runs or classifies the starter source.
- `hf_baseline.py`: first source file to modify.
- `measure.py`: experiment harness that writes `measurements.json`.
- `tasks.json`: concrete reading, programming, measurement, and comparison tasks.
- `measurements.json`: durable local starter measurement after `python3 measure.py`.
- `measurement-contract.json`: expected evidence shape for this project.
- `project.json`: generated metadata linking lessons, sources, papers, labs, and measurements.

## Existing Lab To Compare Against

- `gpu-kernels-serving-lab/21-gpumode-quantized-kernels`
- `cd ../gpu-kernels-serving-lab/21-gpumode-quantized-kernels && python3 run.py && python3 build_page.py`
- measurement: `21-gpumode-quantized-kernels/out_gpumode_quantized_kernels.json`

## Lessons
- Lesson 4: [Lecture 110: The 4-bitter lesson: Balancing Stability and Performance in NVFP4 RL](https://www.youtube.com/watch?v=wiaUh82NEoE)
- Lesson 41: [Lecture 73: [ScaleML Series] Quantization in Large Models](https://www.youtube.com/watch?v=6Cxnnvv3DnY)
- Lesson 12: [Lecture 102: quartet v2](https://www.youtube.com/watch?v=E0G3hf4DneA)
- Lesson 88: [GPU MODE IRL 2024 Keynotes](https://www.youtube.com/watch?v=FH5wiwOyPX4)

## External Tutorials
- Hugging Face: [Transformers Quantization](https://huggingface.co/docs/transformers/en/quantization/overview)

## Paper Cross-Checks
- DAC: Precon: A Precision-Convertible Architecture for Accelerating Quantized Deep Learning Models across Various Domains Including LLMs
  - `analysis/per-paper/dac-2025-273.json`
- ISCA: LUT Tensor Core: A Software-Hardware Co-Design for LUT-Based Low-Bit LLM Inference
  - `analysis/per-paper/isca-2025-079.json`
- MICRO: MCBP: A Memory-Compute Efficient LLM Inference Accelerator Leveraging Bit-Slice-enabled Sparsity and Repetitiveness
  - `analysis/per-paper/micro-2025-096.json`
- MLSYS 2025: TurboAttention: Efficient Attention Approximation for High Throughput LLMs
  - `analysis/per-paper/mlsys-2025-025.json`

## Local Run

```bash
python3 starter.py
python3 measure.py
```
