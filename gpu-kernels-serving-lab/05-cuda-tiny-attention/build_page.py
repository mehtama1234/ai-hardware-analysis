"""Build Session 05 from tiny attention JSON."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.report import esc, load_json, page


HERE = Path(__file__).resolve().parent
DATA = load_json(HERE / "out_cuda_tiny_attention.json")


def prefill_rows() -> str:
    return "\n".join(
        "<tr>"
        f"<td>{esc(r['sequence'])}</td>"
        f"<td>{esc(r['attention_matrix_mb'])}</td>"
        f"<td>{esc(r['materialized_ms'])}</td>"
        f"<td>{esc(r['sdpa_ms'])}</td>"
        f"<td>{esc(r['sdpa_speedup'])}x</td>"
        f"<td>{esc(r['max_abs_error'])}</td>"
        "</tr>"
        for r in DATA["prefill_rows"]
    )


def decode_rows() -> str:
    return "\n".join(
        "<tr>"
        f"<td>{esc(r['context'])}</td>"
        f"<td>{esc(r['kv_cache_mb'])}</td>"
        f"<td>{esc(r['decode_ms_per_token'])}</td>"
        "</tr>"
        for r in DATA["decode_rows"]
    )


body = f"""
<header>
  <div class="kick">GPU kernels and LLM serving lab - Session 05</div>
  <h1>Attention becomes expensive when you write down the whole table.</h1>
  <p class="dek">This session measures the reference attention path before custom CUDA
  fusion: materialized causal attention, PyTorch SDPA, and one-token decode over a growing
  KV cache.</p>
</header>

<section>
  <div class="eye">Measured reference</div>
  <h2>{esc(DATA["device"])} / {esc(DATA["dtype"])}</h2>
  <div class="why"><h3>Boundary</h3><p>{esc(DATA["boundary"])}</p></div>
</section>

<section>
  <div class="eye">Prefill</div>
  <h2>The attention matrix grows quadratically</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>sequence</th><th>attention matrix MB</th><th>materialized ms</th><th>SDPA ms</th><th>SDPA speedup</th><th>max error</th></tr>
      {prefill_rows()}
    </table>
  </div>
</section>

<section>
  <div class="eye">Decode</div>
  <h2>The KV cache grows with context</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>context</th><th>KV cache MB</th><th>ms/token</th></tr>
      {decode_rows()}
    </table>
  </div>
</section>

<section>
  <div class="eye">CUDA target</div>
  <p class="next">The custom-kernel goal is now concrete: avoid writing the full attention
  matrix, keep tiles local, and reduce HBM traffic while matching the reference output.</p>
</section>
"""

(HERE / "out").mkdir(exist_ok=True)
(HERE / "out" / "index.html").write_text(page("GPU Serving Lab - 05 Tiny Attention", body), encoding="utf-8")
print("wrote out/index.html")

