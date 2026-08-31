"""Build Session 08 from quantization JSON."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.report import esc, load_json, page


HERE = Path(__file__).resolve().parent
DATA = load_json(HERE / "out_quantized_inference.json")


def rows() -> str:
    out = []
    for r in DATA["rows"]:
        out.append(
            "<tr>"
            f"<td>{esc(r['scheme'])}</td>"
            f"<td>{esc(r['bits_per_param'])}</td>"
            f"<td>{esc(r['memory_mb'])}</td>"
            f"<td>{esc(r['relative_error_pct'])}%</td>"
            f"<td>{esc(r['cosine'])}</td>"
            "</tr>"
        )
    return "\n".join(out)


fallback = ""
if DATA.get("fallback_reason"):
    fallback = f'<div class="why"><h3>Fallback reason</h3><p>{esc(DATA["fallback_reason"])}</p></div>'


body = f"""
<header>
  <div class="kick">GPU kernels and LLM serving lab - Session 08</div>
  <h1>Quantization starts as a memory trade.</h1>
  <p class="dek">Before optimized int4 kernels enter the story, the first question is simple:
  how many bytes did we save, and how far did the stored numbers move?</p>
</header>

<section>
  <div class="eye">Measured source</div>
  <h2>{esc(DATA["source"])}</h2>
  <p>Loaded in {esc(DATA["load_seconds"])} seconds. The table below is generated from
  `out_quantized_inference.json`.</p>
  {fallback}
  <div class="why"><h3>Boundary</h3><p>{esc(DATA["boundary"])}</p></div>
</section>

<section>
  <div class="eye">Quantization table</div>
  <h2>Memory down, numerical drift up</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>scheme</th><th>bits/param</th><th>MB for sampled values</th><th>relative error</th><th>cosine</th></tr>
      {rows()}
    </table>
  </div>
</section>

<section>
  <div class="eye">Serving implication</div>
  <p class="next">Quantization reduces the bytes that must be stored and streamed. It only
  speeds serving when the runtime has kernels that can exploit the smaller format without
  wasting the savings on dequantization overhead.</p>
</section>
"""

(HERE / "out").mkdir(exist_ok=True)
(HERE / "out" / "index.html").write_text(page("GPU Serving Lab - 08 Quantized Inference", body), encoding="utf-8")
print("wrote out/index.html")

