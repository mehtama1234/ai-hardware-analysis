"""Build Session 03 from CUDA vector/reduction JSON."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.report import esc, load_json, page


HERE = Path(__file__).resolve().parent
DATA = load_json(HERE / "out_cuda_vector_reduce.json")
R = DATA["result"]
K = R.get("kernel") or {}


def result_block() -> str:
    if R["status"] != "ran":
        return f"""
        <div class="card">
          <table>
            <tr><th>status</th><td class="warn">{esc(R["status"])}</td></tr>
            <tr><th>reason</th><td>{esc(R.get("reason") or R.get("stderr") or "not available")}</td></tr>
            <tr><th>source</th><td><span class="mono">vector_reduce.cu</span></td></tr>
          </table>
        </div>
        """
    return f"""
    <div class="card">
      <table>
        <tr><th>device</th><td>{esc(K.get("device"))}</td></tr>
        <tr><th>elements</th><td>{esc(K.get("n"))}</td></tr>
        <tr><th>vector add</th><td>{esc(K.get("vector_add_ms"))} ms / {esc(K.get("vector_add_gbps"))} GB/s</td></tr>
        <tr><th>block reduction</th><td>{esc(K.get("reduce_ms"))} ms / {esc(K.get("reduce_gbps"))} GB/s</td></tr>
        <tr><th>sample error</th><td>{esc(K.get("sample_max_error"))}</td></tr>
      </table>
    </div>
    """


body = f"""
<header>
  <div class="kick">GPU kernels and LLM serving lab - Session 03</div>
  <h1>The first CUDA kernels are memory lessons.</h1>
  <p class="dek">Vector add and reduction are intentionally simple. They expose the CUDA
  execution model, coalesced global memory access, block-level cooperation, and event timing
  before attention or matmul adds complexity.</p>
</header>

<section>
  <div class="eye">Compile/run result</div>
  <h2>CUDA source is part of the tutorial contract</h2>
  {result_block()}
  <div class="why"><h3>Boundary</h3><p>{esc(R["boundary"])}</p></div>
</section>

<section>
  <div class="eye">What the code teaches</div>
  <h2>One thread per element, then one block per partial sum</h2>
  <p>The vector-add kernel maps contiguous threads to contiguous floats, which is the first
  memory-coalescing rule every AI kernel depends on. The reduction kernel uses shared memory
  and synchronization to combine values inside a block. Later attention kernels use the same
  ideas, but with tiles of Q, K, and V instead of one-dimensional arrays.</p>
</section>

<section>
  <div class="eye">Next slice</div>
  <p class="next">Next CUDA session: shared-memory tiled matrix multiply, then attention.</p>
</section>
"""

(HERE / "out").mkdir(exist_ok=True)
(HERE / "out" / "index.html").write_text(page("GPU Serving Lab - 03 CUDA Vector Reduce", body), encoding="utf-8")
print("wrote out/index.html")

