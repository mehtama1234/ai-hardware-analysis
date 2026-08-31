#!/usr/bin/env python3
"""Build worked walkthroughs for the core GPU curriculum paths."""

from __future__ import annotations

import html
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WALKTHROUGHS = ROOT / "worked-walkthroughs"
SITE = ROOT / "site"


WALKTHROUGHS_DATA = [
    {
        "id": "cuda-memory",
        "title": "CUDA Memory Access",
        "claim": "Adjacent threads should read adjacent addresses when the goal is high bandwidth.",
        "files": [
            "programming-projects/cuda-memory-kernel/kernel.cu",
            "programming-projects/cuda-memory-kernel/measure.py",
            "kernel-benchmarks/reports/kernel-benchmark-report.json",
        ],
        "predict": "Before running the code, predict that contiguous reads finish faster than strided or gathered reads for the same number of values.",
        "run": [
            "python3 programming-projects/cuda-memory-kernel/measure.py",
            "python3 scripts/run_kernel_benchmarks.py",
        ],
        "change": "Change the stride or gathered index pattern in the measurement code. Keep the element count fixed. Run the same command again.",
        "explain": "If time changes while the element count stays fixed, the address pattern changed the memory work seen by the hardware. The claim is not that the GPU reached peak bandwidth. The claim is that layout is a measured variable.",
    },
    {
        "id": "triton-softmax",
        "title": "Triton Fused Softmax",
        "claim": "Softmax can avoid extra memory traffic by keeping row state inside one fused program.",
        "files": [
            "programming-projects/triton-fused-softmax/kernel.py",
            "programming-projects/triton-fused-softmax/measure.py",
            "programming-projects/triton-fused-softmax/measurements.json",
        ],
        "predict": "Predict that a fused row operation should write fewer intermediate values than a step-by-step version.",
        "run": [
            "python3 programming-projects/triton-fused-softmax/measure.py",
            "python3 scripts/run_kernel_benchmarks.py",
        ],
        "change": "Change the row length or block size. Do not change the expected output. Run the measurement again.",
        "explain": "The useful result is not a single fastest number. The useful result is whether the same correctness check survives while the block shape changes timing.",
    },
    {
        "id": "jax-roofline",
        "title": "JAX Roofline Model",
        "claim": "A workload is compute-limited only when it has enough arithmetic work for each byte moved.",
        "files": [
            "programming-projects/jax-scaling-roofline/roofline_model.py",
            "programming-projects/jax-scaling-roofline/measure.py",
            "programming-projects/jax-scaling-roofline/measurements.json",
        ],
        "predict": "Pick one shape and predict whether bytes or FLOPs limit it. Write down the arithmetic intensity before running the code.",
        "run": [
            "python3 programming-projects/jax-scaling-roofline/measure.py",
        ],
        "change": "Double the hidden size, then double the sequence length. Compare which change moves the bottleneck label.",
        "explain": "The model proves only the math of the estimate. Hardware counters are a separate test. A good answer names both the estimate and the missing counter evidence.",
    },
    {
        "id": "kv-cache",
        "title": "KV Cache Blocks",
        "claim": "Serving long prompts becomes memory work unless cached key and value blocks are reused and accounted for.",
        "files": [
            "kv-cache-paged-attention/kv_cache_paged_attention/simulator.py",
            "kv-cache-paged-attention/kv-cache-report.json",
            "serving-traces/reports/serving-trace-report.json",
        ],
        "predict": "Predict that prefix-heavy requests reuse more blocks than unrelated short requests.",
        "run": [
            "python3 scripts/run_kv_cache_paged_attention.py",
            "python3 scripts/run_serving_traces.py",
        ],
        "change": "Increase the shared prefix length in a serving fixture. Keep the number of requests fixed. Rebuild the reports.",
        "explain": "The proof is block accounting: peak blocks, reused blocks, and admitted requests. It is not a claim about a production server until a real serving engine produces the same fields.",
    },
    {
        "id": "speculative-decoding",
        "title": "Speculative Decoding",
        "claim": "A draft model helps only when accepted tokens save more target-model work than rejected tokens waste.",
        "files": [
            "speculative-decoding-serving/speculative_decoding_serving/analyzer.py",
            "speculative-decoding-serving/speculative-decoding-report.json",
            "lesson-labs/lesson-096-lecture-22-hacker-s-guide-to-speculative-decoding-in-vllm/measurements.json",
        ],
        "predict": "Predict that low acceptance raises wasted draft work even if the draft model is cheap.",
        "run": [
            "python3 scripts/run_speculative_decoding_serving.py",
            "python3 scripts/verify_speculative_decoding_serving.py",
        ],
        "change": "Lower one scenario's acceptance rate. Keep the target model cost fixed. Check whether the scenario moves to review.",
        "explain": "The measurement proves the scheduler records acceptance, rollback, waste, and speedup together. It does not prove one draft model is always best.",
    },
    {
        "id": "quantization",
        "title": "Quantization Format Choice",
        "claim": "Fewer bits reduce storage, but the result is useful only if error and dequantization cost stay inside the workload limit.",
        "files": [
            "quantization-memory-formats/quantization_memory_formats/analyzer.py",
            "quantization-memory-formats/quantization-report.json",
            "numerical-reproducibility/numerical-reproducibility-report.json",
            "programming-projects/hf-quant-serving/measure.py",
        ],
        "predict": "Predict that smaller formats improve compression but do not all pass the same error check.",
        "run": [
            "python3 scripts/run_quantization_memory_formats.py",
            "python3 scripts/run_numerical_reproducibility.py",
            "python3 programming-projects/hf-quant-serving/measure.py",
        ],
        "change": "Tighten the cosine or max-error threshold. Run the report again and see which formats move from pass to calibration-needed.",
        "explain": "The measured claim is format-by-format: compression, error, cosine similarity, and dequantization tax. There is no single best format without a workload and a tolerance.",
    },
    {
        "id": "distributed-collectives",
        "title": "Distributed Collectives",
        "claim": "A training step can wait on communication even when each GPU has enough compute.",
        "files": [
            "distributed-collectives/distributed_collectives/analyzer.py",
            "distributed-collectives/distributed_collectives/benchmark.py",
            "distributed-collectives/reports/collective-benchmark-run.json",
            "programming-projects/distributed-collectives/collective_model.py",
        ],
        "predict": "Predict that larger payloads care more about bandwidth, while smaller payloads care more about latency.",
        "run": [
            "python3 scripts/run_distributed_collectives.py",
            "python3 scripts/run_distributed_collectives_benchmark.py",
        ],
        "change": "Change payload bytes in the benchmark command. On a multi-GPU host, run with torch distributed and compare all-reduce with all-gather.",
        "explain": "The local code proves the communication model and artifact schema. A single-GPU Colab run cannot prove multi-GPU bandwidth; the failed gate records that limit.",
    },
    {
        "id": "gpu-evidence",
        "title": "GPU Evidence Gate",
        "claim": "A project should not claim real accelerator proof unless the measurement came from a real accelerator host and passed the metric contract.",
        "files": [
            "gpu-runs/gpu_runs/collector.py",
            "gpu-measurement-queue/gpu_measurement_queue/builder.py",
            "gpu-runs/imports/colab-advanced-phase.json",
            "capstone-acceptance/capstone-acceptance.json",
        ],
        "predict": "Predict that Colab T4 accepts CUDA and Triton checks but fails ROCm, full profiler, and true multi-GPU checks.",
        "run": [
            "python3 scripts/build_gpu_runs.py",
            "python3 scripts/build_gpu_provenance.py",
            "python3 scripts/build_gpu_measurement_queue.py",
            "python3 scripts/verify_gpu_measurement_queue.py",
        ],
        "change": "Import a run from a different host class. Compare accepted, failed, and queued counts.",
        "explain": "The proof is separation of evidence types. The report can accept 15 T4-backed claims while refusing the 3 claims that require other hardware.",
    },
]


def esc(value: object) -> str:
    return html.escape(str(value))


def style() -> str:
    return """<style>
:root{--bg:#0E1420;--bg2:#141D2C;--ink:#EAEEF4;--soft:#B4BFD0;--dim:#8493A8;--line:rgba(150,170,205,.14);--accent:#4FA8B8;--serif:"Iowan Old Style",Palatino,Georgia,serif;--sans:-apple-system,system-ui,"Segoe UI",Roboto,Arial,sans-serif;--mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);line-height:1.65}.wrap{max-width:980px;margin:0 auto;padding:56px 24px 80px}.kick{font-family:var(--mono);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--accent)}h1{font-family:var(--serif);font-size:clamp(34px,6vw,56px);line-height:1.05;margin:14px 0 28px;color:#fff}h2{font-family:var(--serif);font-size:26px;margin:0 0 12px;color:#fff}section{padding:28px 0;border-top:1px solid var(--line)}p,li{color:var(--soft);font-size:17px;max-width:78ch}code{font-family:var(--mono);color:#fff}pre{background:var(--bg2);border:1px solid var(--line);border-radius:8px;padding:14px;overflow:auto}.small{font-size:13px;color:var(--dim)}a{color:var(--accent);text-decoration:none}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px}.card{background:var(--bg2);border:1px solid var(--line);border-radius:8px;padding:16px}.card h2{font-size:20px;margin:0 0 8px}.card p{font-size:14px;margin:0;color:var(--dim)}
</style>"""


def md_for_walkthrough(item: dict[str, object]) -> str:
    files = "\n".join(f"- `{path}`" for path in item["files"])
    commands = "\n".join(str(cmd) for cmd in item["run"])
    return "\n".join(
        [
            f"# {item['title']}",
            "",
            "## Claim",
            "",
            str(item["claim"]),
            "",
            "## Read The Code",
            "",
            files,
            "",
            "## Predict",
            "",
            str(item["predict"]),
            "",
            "## Run",
            "",
            "```bash",
            commands,
            "```",
            "",
            "## Change One Thing",
            "",
            str(item["change"]),
            "",
            "## Explain The Result",
            "",
            str(item["explain"]),
            "",
        ]
    )


def html_for_walkthrough(item: dict[str, object]) -> str:
    files = "".join(f"<li><code>{esc(path)}</code></li>" for path in item["files"])
    commands = "\n".join(str(cmd) for cmd in item["run"])
    return f"""<meta charset="utf-8">
<title>{esc(item['title'])} - Worked Walkthrough</title>
{style()}
<div class="wrap">
  <div class="kick">Worked walkthrough</div>
  <h1>{esc(item['title'])}</h1>
  <section><h2>Claim</h2><p>{esc(item['claim'])}</p></section>
  <section><h2>Read The Code</h2><ul>{files}</ul></section>
  <section><h2>Predict</h2><p>{esc(item['predict'])}</p></section>
  <section><h2>Run</h2><pre><code>{esc(commands)}</code></pre></section>
  <section><h2>Change One Thing</h2><p>{esc(item['change'])}</p></section>
  <section><h2>Explain The Result</h2><p>{esc(item['explain'])}</p></section>
  <p class="small"><a href="worked-walkthroughs.html">Back to walkthroughs</a> / <a href="index.html">Back to curriculum index</a></p>
</div>
"""


def index_html() -> str:
    cards = []
    for item in WALKTHROUGHS_DATA:
        href = f"walkthrough-{item['id']}.html"
        cards.append(f'<div class="card"><h2><a href="{esc(href)}">{esc(item["title"])}</a></h2><p>{esc(item["claim"])}</p></div>')
    return f"""<meta charset="utf-8">
<title>GPUMODE Worked Walkthroughs</title>
{style()}
<div class="wrap">
  <div class="kick">Predict, run, change, explain</div>
  <h1>Worked walkthroughs for the core GPU labs.</h1>
  <section><h2>How To Use These</h2><p>Read the claim, inspect the named files, predict the result, run the command, change one variable, and explain the measured change.</p></section>
  <section><h2>Walkthroughs</h2><div class="grid">{''.join(cards)}</div></section>
  <p class="small"><a href="index.html">Back to curriculum index</a></p>
</div>
"""


def main() -> None:
    WALKTHROUGHS.mkdir(parents=True, exist_ok=True)
    SITE.mkdir(parents=True, exist_ok=True)
    links = []
    for item in WALKTHROUGHS_DATA:
        md = WALKTHROUGHS / f"{item['id']}.md"
        page = SITE / f"walkthrough-{item['id']}.html"
        md.write_text(md_for_walkthrough(item), encoding="utf-8")
        page.write_text(html_for_walkthrough(item), encoding="utf-8")
        links.append(f"- [{item['title']}]({item['id']}.md)")
    (WALKTHROUGHS / "README.md").write_text("# Worked Walkthroughs\n\n" + "\n".join(links) + "\n", encoding="utf-8")
    (SITE / "worked-walkthroughs.html").write_text(index_html(), encoding="utf-8")
    print(f"wrote {len(WALKTHROUGHS_DATA)} worked walkthroughs and site/worked-walkthroughs.html")


if __name__ == "__main__":
    main()
