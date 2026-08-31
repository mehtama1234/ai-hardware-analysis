"""Build Session 06 from Triton matmul JSON."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.report import esc, load_json, page


HERE = Path(__file__).resolve().parent
DATA = load_json(HERE / "out_triton_matmul.json")
R = DATA["result"]


def result_block() -> str:
    if R["status"] != "ran":
        return f"""
        <div class="card">
          <table>
            <tr><th>status</th><td class="warn">{esc(R["status"])}</td></tr>
            <tr><th>reason</th><td>{esc(R.get("reason"))}</td></tr>
          </table>
        </div>
        """
    return f"""
    <div class="card">
      <table>
        <tr><th>size</th><td>{esc(R.get("n"))} x {esc(R.get("n"))}</td></tr>
        <tr><th>block</th><td>{esc(R.get("block"))}</td></tr>
        <tr><th>Triton</th><td>{esc(R.get("triton_ms"))} ms / {esc(R.get("triton_tflops"))} TFLOP/s</td></tr>
        <tr><th>PyTorch</th><td>{esc(R.get("torch_ms"))} ms / {esc(R.get("torch_tflops"))} TFLOP/s</td></tr>
        <tr><th>max error</th><td>{esc(R.get("max_abs_error"))}</td></tr>
      </table>
    </div>
    """


body = f"""
<header>
  <div class="kick">GPU kernels and LLM serving lab - Session 06</div>
  <h1>Triton is the practical middle layer.</h1>
  <p class="dek">This session introduces a blocked matrix multiplication written in Python
  with Triton. It keeps the CUDA idea of tiles and SRAM reuse, but removes most C++ boilerplate.
  On this machine the runner records whether a CUDA-visible device exists before launching.</p>
</header>

<section>
  <div class="eye">Run result</div>
  <h2>Blocked matmul</h2>
  {result_block()}
  <div class="why"><h3>Boundary</h3><p>{esc(R["boundary"])}</p></div>
</section>

<section>
  <div class="eye">Why this belongs after CUDA</div>
  <h2>Same memory idea, faster iteration</h2>
  <p>CUDA Session 04 will teach shared-memory tiling from the metal up. Triton uses the
  same structure: each program instance owns a tile, loads blocks of A and B, accumulates
  locally, and writes C. That is the shape behind fused attention and quantized matmul too.</p>
</section>
"""

(HERE / "out").mkdir(exist_ok=True)
(HERE / "out" / "index.html").write_text(page("GPU Serving Lab - 06 Triton Matmul", body), encoding="utf-8")
print("wrote out/index.html")

