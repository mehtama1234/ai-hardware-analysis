"""Build Session 04 from CUDA tiled matmul JSON."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.report import esc, load_json, page


HERE = Path(__file__).resolve().parent
DATA = load_json(HERE / "out_cuda_tiled_matmul.json")
R = DATA["result"]
K = R.get("kernel") or {}


def result_block() -> str:
    if R["status"] != "ran":
        return f"""
        <div class="card" style="overflow-x:auto">
          <table>
            <tr><th>status</th><td class="warn">{esc(R["status"])}</td></tr>
            <tr><th>reason</th><td>{esc(R.get("reason") or R.get("stderr"))}</td></tr>
            <tr><th>source</th><td><span class="mono">tiled_matmul.cu</span></td></tr>
          </table>
        </div>
        """
    return f"""
    <div class="card" style="overflow-x:auto">
      <table>
        <tr><th>device</th><td>{esc(K.get("device"))}</td></tr>
        <tr><th>matrix</th><td>{esc(K.get("n"))} x {esc(K.get("n"))}</td></tr>
        <tr><th>tile</th><td>{esc(K.get("tile"))} x {esc(K.get("tile"))}</td></tr>
        <tr><th>naive</th><td>{esc(K.get("naive_ms"))} ms / {esc(K.get("naive_tflops"))} TFLOP/s</td></tr>
        <tr><th>tiled</th><td>{esc(K.get("tiled_ms"))} ms / {esc(K.get("tiled_tflops"))} TFLOP/s</td></tr>
        <tr><th>speedup</th><td>{esc(K.get("speedup"))}x</td></tr>
        <tr><th>sample error</th><td>{esc(K.get("sample_max_error"))}</td></tr>
      </table>
    </div>
    """


body = f"""
<header>
  <div class="kick">GPU kernels and LLM serving lab - Session 04</div>
  <h1>Fast matmul is mostly data reuse.</h1>
  <p class="dek">This CUDA session puts the roofline lesson into code: a naive matrix
  multiply rereads global memory constantly, while a tiled kernel stages chunks through
  shared memory so each loaded value does more work.</p>
</header>

<section>
  <div class="eye">Compile/run result</div>
  <h2>Naive global-memory matmul vs shared-memory tiled matmul</h2>
  {result_block()}
  <div class="why"><h3>Boundary</h3><p>{esc(R["boundary"])}</p></div>
</section>

<section>
  <div class="eye">What this teaches</div>
  <h2>The tile is a small cache you control</h2>
  <p>Each block loads a square tile of A and B into shared memory, synchronizes, and then
  reuses those values for many multiply-adds before loading the next tile. This is the
  same memory-locality idea behind tensor-core GEMM, attention tiling, and fused kernels.</p>
</section>
"""

(HERE / "out").mkdir(exist_ok=True)
(HERE / "out" / "index.html").write_text(page("GPU Serving Lab - 04 CUDA Tiled Matmul", body), encoding="utf-8")
print("wrote out/index.html")

