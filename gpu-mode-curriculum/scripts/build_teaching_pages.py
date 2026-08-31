#!/usr/bin/env python3
"""Build first-principles teaching notes beside the GPU curriculum code."""

from __future__ import annotations

import html
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
TEACHING = ROOT / "teaching"
SITE = ROOT / "site"


LANES = [
    {
        "id": "cuda-memory-kernel",
        "title": "CUDA Memory Kernel",
        "problem": "A GPU can issue many loads at once, but slow address patterns waste memory bandwidth. This lane asks a small question: do adjacent threads read adjacent data, and how much does that change time per byte?",
        "code": [
            "programming-projects/cuda-memory-kernel/kernel.cu defines the CUDA source shape.",
            "programming-projects/cuda-memory-kernel/measure.py records the local contract result.",
            "kernel-benchmarks/kernels/cuda/memory.cu is the promotion source for a GPU host.",
        ],
        "proof": "The measurement proves that the benchmark harness can separate contiguous, strided, and gathered access patterns and preserve the result as JSON. On Colab T4 it also proves the CUDA path can see an NVIDIA GPU.",
        "not_proof": "It does not prove peak bandwidth for every GPU. It does not prove that a larger model is memory-bound. It proves the smaller claim first: address pattern changes measured memory behavior.",
        "read_next": ["site/kernel-benchmarks.html", "programming-projects/cuda-memory-kernel/README.md"],
    },
    {
        "id": "triton-fused-softmax",
        "title": "Triton Fused Softmax",
        "problem": "Softmax reads a row, finds a maximum, computes exponentials, sums them, and writes normalized values. If each step writes a full temporary tensor, memory traffic grows. This lane asks whether one program can keep the row state close to the compute units.",
        "code": [
            "programming-projects/triton-fused-softmax/kernel.py holds the Triton source.",
            "kernel-benchmarks/kernels/triton/softmax_layernorm.py gives the benchmark promotion path.",
            "scripts/run_kernel_benchmarks.py records correctness and timing fields.",
        ],
        "proof": "The measurement proves the fused path returns the expected values for the tested shapes and records timing in the same format as other kernel families.",
        "not_proof": "It does not prove the selected block size is optimal. It does not replace a profiler trace. It proves that fusion can be tested with a fixed contract.",
        "read_next": ["site/project-triton-fused-softmax.html", "site/autotune-db.html"],
    },
    {
        "id": "jax-scaling-roofline",
        "title": "JAX Scaling Roofline",
        "problem": "A workload is limited by the slowest required resource. Roofline analysis compares math work with bytes moved. This lane asks whether a kernel or model shape has enough math per byte to use the compute units well.",
        "code": [
            "programming-projects/jax-scaling-roofline/roofline_model.py computes arithmetic intensity and bottleneck class.",
            "programming-projects/jax-scaling-roofline/measure.py writes the project measurement.",
            "programming-projects/jax-scaling-roofline/jax-scaling-roofline.ipynb gives the notebook path.",
        ],
        "proof": "The measurement proves the model can classify test shapes using explicit FLOP, byte, bandwidth, and compute assumptions. It connects the JAX Scaling Book reading to local code.",
        "not_proof": "It does not prove hardware counters match the model. A profiler run is needed for that. It proves that the cost model is written down and can be checked.",
        "read_next": ["site/project-jax-scaling-roofline.html", "https://jax-ml.github.io/scaling-book/roofline/"],
    },
    {
        "id": "attention-serving-stack",
        "title": "Attention Serving Stack",
        "problem": "Attention can spend memory on materialized score matrices and on cached keys and values. Serving also cares about first token delay and time per output token. This lane asks how tiling, online softmax, batching, and KV reuse change those numbers.",
        "code": [
            "attention-serving-stack/attention_serving_stack/analyzer.py builds the scenario metrics.",
            "serving-traces/serving_traces/replay.py simulates request scheduling.",
            "kv-cache-paged-attention/kv_cache_paged_attention/simulator.py handles block-table style KV accounting.",
        ],
        "proof": "The measurement proves the scenarios track HBM reduction, shared memory size, prefix reuse, and serving policy fields under one contract.",
        "not_proof": "It does not prove production vLLM throughput. It proves the serving variables are exposed and testable before a real serving engine run.",
        "read_next": ["site/attention-serving-stack.html", "site/serving-traces.html", "site/kv-cache-paged-attention.html"],
    },
    {
        "id": "speculative-decoding-serving",
        "title": "Speculative Decoding Serving",
        "problem": "A small draft model can propose tokens faster than a large target model. The target model still must verify the tokens. This lane asks when accepted draft tokens reduce total decode work and when rejected tokens add waste.",
        "code": [
            "speculative-decoding-serving/speculative_decoding_serving/analyzer.py computes acceptance, rollback, wasted draft tokens, and speedup.",
            "scripts/run_speculative_decoding_serving.py writes the report.",
            "gpu-runs/gpu_runs/collector.py imports the Colab measured status for this step.",
        ],
        "proof": "The measurement proves the system records both the good case and the bad case. It accepts high speedup only when acceptance and waste are visible.",
        "not_proof": "It does not prove a specific draft model is the best choice. It proves the scheduler can be judged by acceptance rate, wasted work, and output speed.",
        "read_next": ["site/speculative-decoding-serving.html", "lesson-labs/lesson-096-lecture-22-hacker-s-guide-to-speculative-decoding-in-vllm/README.md"],
    },
    {
        "id": "fused-training-kernels",
        "title": "Fused Training Kernels",
        "problem": "Training does forward math, backward math, and optimizer updates. If each small operation launches its own kernel and writes full tensors to memory, time is lost to launches and memory traffic. This lane asks which groups of operations can share one pass over data.",
        "code": [
            "fused-training-kernels/fused_training_kernels/analyzer.py models the fused training cases.",
            "custom-ops/custom_ops/fused_bias_gelu_residual.py gives a concrete fused operator path.",
            "model-integration/model_integration/tiny_transformer.py connects the operator to a transformer-shaped block when present.",
        ],
        "proof": "The measurement proves each training case has a correctness bound, a launch reduction estimate, an HBM reduction estimate, and a promotion path.",
        "not_proof": "It does not prove numerical safety for every model size or optimizer. It proves each fused choice states the saved work and the error bound.",
        "read_next": ["site/fused-training-kernels.html", "site/custom-ops.html", "site/model-integration.html"],
    },
    {
        "id": "quantization-memory-formats",
        "title": "Quantization And Memory Formats",
        "problem": "Lower precision stores fewer bits per value. That can reduce memory traffic and fit larger models, but it can also add dequantization work and numerical error. This lane asks which formats pass error checks for specific serving and training cases.",
        "code": [
            "quantization-memory-formats/quantization_memory_formats/analyzer.py compares the formats.",
            "numerical-reproducibility/numerical_reproducibility/analyzer.py records tolerance rules.",
            "programming-projects/hf-quant-serving/hf_baseline.py gives the Hugging Face serving baseline path.",
        ],
        "proof": "The measurement proves each format is judged by compression, error, cosine similarity, dequantization cost, and serving fit.",
        "not_proof": "It does not prove one format is always better. It proves a format must pass a stated error contract for a stated workload.",
        "read_next": ["site/quantization-memory-formats.html", "site/numerical-reproducibility.html", "site/project-hf-quant-serving.html"],
    },
    {
        "id": "compiler-runtime-inspection",
        "title": "Compiler Runtime Inspection",
        "problem": "A kernel source file can hide runtime risks before it is compiled: missing bounds masks, high shared memory, barriers, launch indexing mistakes, or tensor core claims without shape proof. This lane asks what can be checked from source before a GPU run.",
        "code": [
            "compiler-runtime-inspection/compiler_runtime_inspection/inspector.py scans source features when present.",
            "scripts/run_compiler_runtime_inspection.py writes the source report.",
            "site/compiler-runtime-inspection.html lists feature and risk counts.",
        ],
        "proof": "The measurement proves the curriculum can inspect CUDA, Triton, HIP, and custom op source through one source-level contract.",
        "not_proof": "It does not prove the compiled kernel is fast. Source inspection catches early risks; profiler evidence is still required for runtime claims.",
        "read_next": ["site/compiler-runtime-inspection.html", "site/gpu-promotion.html"],
    },
    {
        "id": "distributed-training-optimizer",
        "title": "Distributed Training Optimizer",
        "problem": "Large training splits weights, gradients, optimizer state, and activations across devices. Splitting saves memory but adds communication. This lane asks which split has enough memory headroom and how much communication remains exposed after overlap.",
        "code": [
            "distributed-training-optimizer/distributed_training_optimizer/analyzer.py models the strategies.",
            "distributed-topology/distributed_topology/planner.py compares device and link layouts when present.",
            "distributed-collectives/distributed_collectives/analyzer.py supplies collective cost estimates.",
        ],
        "proof": "The measurement proves each strategy records memory per GPU, communication time, pipeline bubble time, optimizer-state savings, and pass or review status.",
        "not_proof": "It does not prove a full cluster run completed. The Colab T4 run proves the code path; true collective bandwidth needs a multi-GPU host.",
        "read_next": ["site/distributed-training-optimizer.html", "site/distributed-topology.html", "site/distributed-collectives.html"],
    },
    {
        "id": "moe-routing-all-to-all",
        "title": "MoE Routing And All-To-All",
        "problem": "A mixture-of-experts layer sends each token to a small number of experts. If many tokens choose the same expert, some devices overload while others wait. This lane asks how routing balance, capacity drops, and all-to-all payload affect the step.",
        "code": [
            "moe-routing-all-to-all/moe_routing_all_to_all/simulator.py computes routing outcomes.",
            "distributed-collectives/distributed_collectives/analyzer.py supplies the communication context.",
            "hardware-capacity-planning/hardware_capacity_planning/planner.py connects the result to hardware choice.",
        ],
        "proof": "The measurement proves each scenario records load balance, dropped tokens, payload size, communication time, and the bottleneck label.",
        "not_proof": "It does not prove a real MoE model was trained. It proves the routing failure modes are made measurable.",
        "read_next": ["site/moe-routing-all-to-all.html", "site/hardware-capacity.html"],
    },
    {
        "id": "gpu-evidence",
        "title": "GPU Evidence And Acceptance",
        "problem": "A local CPU result, a generated source file, and a real GPU measurement are different kinds of evidence. This lane asks whether the repo can keep those claims separate.",
        "code": [
            "gpu-runs/gpu_runs/collector.py writes host evidence from local or Colab runs.",
            "gpu-measurement-queue/gpu_measurement_queue/builder.py checks each step against its required metrics.",
            "capstone-acceptance/capstone_acceptance/evaluator.py turns the evidence state into a score.",
        ],
        "proof": "The Colab T4 import proves the system can ingest a real GPU run and mark 18 of 18 tasks measured. It accepts 15 tasks and keeps 3 failed because the required hardware or tools were absent.",
        "not_proof": "It does not hide missing Nsight, ROCm, or multi-GPU evidence. The failed rows are the point: they stop the report from claiming more than the hardware proved.",
        "read_next": ["site/gpu-runs.html", "site/gpu-measurement-queue.html", "site/capstone-acceptance.html"],
    },
]


def esc(value: object) -> str:
    return html.escape(str(value))


def md_for_lane(lane: dict[str, object]) -> str:
    code = "\n".join(f"- `{item}`" for item in lane["code"])
    read_next = "\n".join(f"- `{item}`" if not str(item).startswith("http") else f"- {item}" for item in lane["read_next"])
    return "\n".join(
        [
            f"# {lane['title']}",
            "",
            "## First Question",
            "",
            str(lane["problem"]),
            "",
            "## What The Code Does",
            "",
            code,
            "",
            "## What The Measurement Proves",
            "",
            str(lane["proof"]),
            "",
            "## What It Does Not Prove",
            "",
            str(lane["not_proof"]),
            "",
            "## Read Next",
            "",
            read_next,
            "",
        ]
    )


def html_for_lane(lane: dict[str, object]) -> str:
    code = "".join(f"<li><code>{esc(item)}</code></li>" for item in lane["code"])
    read_next = "".join(
        f'<li><a href="{esc(item)}">{esc(item)}</a></li>' if str(item).startswith("site/") or str(item).startswith("http") else f"<li><code>{esc(item)}</code></li>"
        for item in lane["read_next"]
    )
    return dedent(
        f"""\
        <meta charset="utf-8">
        <title>{esc(lane["title"])} - Teaching Note</title>
        {style()}
        <div class="wrap">
          <div class="kick">First-principles teaching note</div>
          <h1>{esc(lane["title"])}</h1>
          <section><h2>First Question</h2><p>{esc(lane["problem"])}</p></section>
          <section><h2>What The Code Does</h2><ul>{code}</ul></section>
          <section><h2>What The Measurement Proves</h2><p>{esc(lane["proof"])}</p></section>
          <section><h2>What It Does Not Prove</h2><p>{esc(lane["not_proof"])}</p></section>
          <section><h2>Read Next</h2><ul>{read_next}</ul></section>
          <p class="small"><a href="teaching.html">Back to teaching notes</a> / <a href="index.html">Back to curriculum index</a></p>
        </div>
        """
    )


def style() -> str:
    return """<style>
:root{--bg:#0E1420;--bg2:#141D2C;--ink:#EAEEF4;--soft:#B4BFD0;--dim:#8493A8;--line:rgba(150,170,205,.14);--accent:#4FA8B8;--serif:"Iowan Old Style",Palatino,Georgia,serif;--sans:-apple-system,system-ui,"Segoe UI",Roboto,Arial,sans-serif;--mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);line-height:1.65}.wrap{max-width:980px;margin:0 auto;padding:56px 24px 80px}.kick{font-family:var(--mono);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--accent)}h1{font-family:var(--serif);font-size:clamp(34px,6vw,56px);line-height:1.05;margin:14px 0 28px;color:#fff}h2{font-family:var(--serif);font-size:26px;margin:0 0 12px;color:#fff}section{padding:28px 0;border-top:1px solid var(--line)}p,li{color:var(--soft);font-size:17px;max-width:78ch}code{font-family:var(--mono);color:#fff}.small{font-size:13px;color:var(--dim)}a{color:var(--accent);text-decoration:none}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px}.card{background:var(--bg2);border:1px solid var(--line);border-radius:8px;padding:16px}.card h2{font-size:20px;margin:0 0 8px}.card p{font-size:14px;margin:0;color:var(--dim)}
</style>"""


def index_page() -> str:
    cards = []
    for lane in LANES:
        href = f"teaching-{lane['id']}.html"
        cards.append(
            f'<div class="card"><h2><a href="{esc(href)}">{esc(lane["title"])}</a></h2>'
            f'<p>{esc(lane["problem"])}</p></div>'
        )
    return dedent(
        f"""\
        <meta charset="utf-8">
        <title>GPUMODE Teaching Notes</title>
        {style()}
        <div class="wrap">
          <div class="kick">Code beside explanation</div>
          <h1>First-principles notes for the GPU curriculum.</h1>
          <section>
            <h2>How To Read This</h2>
            <p>Each note starts with the smallest question the code can answer. It then names the files, the measured claim, and the claim that is still not proven.</p>
          </section>
          <section>
            <h2>Notes</h2>
            <div class="grid">{''.join(cards)}</div>
          </section>
          <p class="small"><a href="index.html">Back to curriculum index</a></p>
        </div>
        """
    )


def main() -> None:
    TEACHING.mkdir(parents=True, exist_ok=True)
    SITE.mkdir(parents=True, exist_ok=True)
    links = []
    for lane in LANES:
        md_path = TEACHING / f"{lane['id']}.md"
        html_path = SITE / f"teaching-{lane['id']}.html"
        md_path.write_text(md_for_lane(lane), encoding="utf-8")
        html_path.write_text(html_for_lane(lane), encoding="utf-8")
        links.append(f"- [{lane['title']}]({md_path.name})")
    (TEACHING / "README.md").write_text(
        "# First-Principles Teaching Notes\n\n" + "\n".join(links) + "\n",
        encoding="utf-8",
    )
    (SITE / "teaching.html").write_text(index_page(), encoding="utf-8")
    print(f"wrote {len(LANES)} teaching notes and site/teaching.html")


if __name__ == "__main__":
    main()
