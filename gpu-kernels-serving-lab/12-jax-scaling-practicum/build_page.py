"""Build Session 12 from JAX scaling practicum JSON."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.report import esc, load_json, page


HERE = Path(__file__).resolve().parent
DATA = load_json(HERE / "out_jax_scaling.json")
R = DATA["result"]


def result_block() -> str:
    if R["status"] != "ran":
        return f'<div class="card"><table><tr><th>status</th><td class="warn">{esc(R["status"])}</td></tr><tr><th>reason</th><td>{esc(R.get("reason"))}</td></tr></table></div>'
    kv = R["kv_cache_estimate"]
    devices = ", ".join(f"{d['platform']}:{d['kind']}" for d in R["devices"])
    return f"""
    <div class="card" style="overflow-x:auto">
      <table>
        <tr><th>JAX</th><td>{esc(R["jax_version"])}</td></tr>
        <tr><th>devices</th><td>{esc(devices)}</td></tr>
        <tr><th>matmul</th><td>{esc(R["matmul_n"])} x {esc(R["matmul_n"])}</td></tr>
        <tr><th>compile + first run</th><td>{esc(R["compile_plus_run_ms"])} ms</td></tr>
        <tr><th>cached run</th><td>{esc(R["cached_run_ms"])} ms / {esc(R["cached_tflops"])} TFLOP/s</td></tr>
        <tr><th>KV-cache estimate</th><td>{esc(kv["kv_cache_mb"])} MB for batch {esc(kv["batch"])}, seq {esc(kv["sequence"])}, layers {esc(kv["layers"])}, hidden {esc(kv["hidden"])}</td></tr>
        <tr><th>multi-device</th><td>{esc(R["multi_device_status"])}</td></tr>
      </table>
    </div>
    """


body = f"""
<header>
  <div class="kick">GPU kernels and LLM serving lab - Session 12</div>
  <h1>Scaling estimates need profiler reality.</h1>
  <p class="dek">This session makes the JAX Scaling Book concrete: compile a matrix multiply,
  time the cached execution, list available JAX devices, and compute an explicit KV-cache
  memory estimate.</p>
</header>

<section>
  <div class="eye">Measured JAX run</div>
  <h2>JIT, devices, and KV-cache math</h2>
  {result_block()}
  <div class="why"><h3>Boundary</h3><p>{esc(R["boundary"])}</p></div>
</section>

<section>
  <div class="eye">Why this matters</div>
  <p class="next">The scaling-book habit is to predict the cost first, then compare it with
  a real trace. This page starts that loop locally; later multi-device work can extend it
  to all-reduce, all-gather, and sharded attention.</p>
</section>
"""

(HERE / "out").mkdir(exist_ok=True)
(HERE / "out" / "index.html").write_text(page("GPU Serving Lab - 12 JAX Scaling", body), encoding="utf-8")
print("wrote out/index.html")

