"""Build Session 07 from Triton fused attention JSON."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.report import esc, load_json, page


HERE = Path(__file__).resolve().parent
DATA = load_json(HERE / "out_triton_fused_attention.json")
R = DATA["result"]


def result_block() -> str:
    if R["status"] != "ran":
        return f"""
        <div class="card" style="overflow-x:auto">
          <table>
            <tr><th>status</th><td class="warn">{esc(R["status"])}</td></tr>
            <tr><th>reason</th><td>{esc(R.get("reason"))}</td></tr>
          </table>
        </div>
        """
    return f"""
    <div class="card" style="overflow-x:auto">
      <table>
        <tr><th>context</th><td>{esc(R["context"])}</td></tr>
        <tr><th>d_head</th><td>{esc(R["d_head"])}</td></tr>
        <tr><th>Triton</th><td>{esc(R["triton_ms"])} ms</td></tr>
        <tr><th>PyTorch SDPA</th><td>{esc(R["torch_sdpa_ms"])} ms</td></tr>
        <tr><th>speedup</th><td>{esc(R["speedup_vs_sdpa"])}x</td></tr>
        <tr><th>bytes read estimate</th><td>{esc(R["bytes_read_estimate"])}</td></tr>
        <tr><th>max error</th><td>{esc(R["max_abs_error"])}</td></tr>
      </table>
    </div>
    """


body = f"""
<header>
  <div class="kick">GPU kernels and LLM serving lab - Session 07</div>
  <h1>Fused attention keeps the softmax state local.</h1>
  <p class="dek">This session is the Triton counterpart to the attention reference page:
  stream K/V through a single-query decode kernel, update online softmax statistics, and
  avoid storing a full score vector as an intermediate.</p>
</header>

<section>
  <div class="eye">Run result</div>
  <h2>Single-query decode attention</h2>
  {result_block()}
  <div class="why"><h3>Boundary</h3><p>{esc(R["boundary"])}</p></div>
</section>

<section>
  <div class="eye">What this teaches</div>
  <h2>The FlashAttention shape in miniature</h2>
  <p>The production version tiles Q, K, and V, keeps running softmax normalization in fast
  memory, and writes only the final output. This tiny decode kernel teaches that dataflow
  without trying to be a full replacement for vendor attention kernels.</p>
</section>
"""

(HERE / "out").mkdir(exist_ok=True)
(HERE / "out" / "index.html").write_text(page("GPU Serving Lab - 07 Triton Fused Attention", body), encoding="utf-8")
print("wrote out/index.html")

