"""Build Session 02 from roofline benchmark JSON."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.report import esc, load_json, page


HERE = Path(__file__).resolve().parent
DATA = load_json(HERE / "out_roofline.json")


def rows() -> str:
    out = []
    for r in DATA["rows"]:
        out.append(
            "<tr>"
            f"<td>{esc(r['operation'])}</td>"
            f"<td>{esc(r['shape'])}</td>"
            f"<td>{esc(r['arithmetic_intensity_flop_per_byte'])}</td>"
            f"<td>{esc(r['effective_gbps'])}</td>"
            f"<td>{esc(r['effective_tflops'])}</td>"
            f"<td>{esc(r['classification'])}</td>"
            "</tr>"
        )
    return "\n".join(out)


def bars() -> str:
    max_t = max(r["effective_tflops"] for r in DATA["rows"]) or 1
    max_b = max(r["effective_gbps"] for r in DATA["rows"]) or 1
    out = []
    for r in DATA["rows"]:
        t_pct = max(2, r["effective_tflops"] / max_t * 100)
        b_pct = max(2, r["effective_gbps"] / max_b * 100)
        out.append(
            f"""<div class="barrow">
  <div class="blabel">{esc(r['operation'])}</div>
  <div class="track"><span style="width:{b_pct:.1f}%;background:var(--accent)"></span></div>
  <div class="track"><span style="width:{t_pct:.1f}%;background:var(--amber)"></span></div>
</div>"""
        )
    return "\n".join(out)


body = f"""
<style>
.barrow{{display:grid;grid-template-columns:170px 1fr 1fr;gap:10px;align-items:center;margin:9px 0;font-family:var(--mono);font-size:12px}}
.blabel{{color:var(--soft)}}.track{{height:18px;background:rgba(150,170,205,.07);border-radius:5px;overflow:hidden}}.track span{{display:block;height:100%}}
@media(max-width:720px){{.barrow{{grid-template-columns:1fr}}}}
</style>
<header>
  <div class="kick">GPU kernels and LLM serving lab - Session 02</div>
  <h1>Classify the work before optimizing it.</h1>
  <p class="dek">The JAX Scaling Book starts from a simple discipline: decide whether a
  workload is limited by math, memory, or communication. This session runs small AI-shaped
  operations and reports arithmetic intensity, bandwidth, and FLOP/s.</p>
</header>

<section>
  <div class="eye">Measured device</div>
  <h2>{esc(DATA["device"])} / {esc(DATA["dtype"])}</h2>
  <div class="why"><h3>Boundary</h3><p>{esc(DATA["boundary"])}</p></div>
</section>

<section>
  <div class="eye">Roofline table</div>
  <h2>Operation shape decides the bottleneck</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>operation</th><th>shape</th><th>FLOP/byte</th><th>GB/s</th><th>TFLOP/s</th><th>classification</th></tr>
      {rows()}
    </table>
  </div>
</section>

<section>
  <div class="eye">Relative picture</div>
  <h2>Bandwidth bars vs compute bars</h2>
  <p>Blue bars are effective bandwidth relative to the best bandwidth in this run. Amber
  bars are effective compute relative to the best compute in this run. The absolute numbers
  are less important than the shape.</p>
  <div class="card">
    <div class="barrow"><div></div><div class="mono">GB/s</div><div class="mono">TFLOP/s</div></div>
    {bars()}
  </div>
</section>

<section>
  <div class="eye">Takeaway</div>
  <p class="next">Vector add and reductions have low arithmetic intensity, so memory traffic
  dominates. Matrix multiply can reuse data enough to become compute-heavy. The KV-cache
  score scan sits in the attention-serving danger zone: it does useful math, but its cost
  grows with context memory.</p>
</section>
"""

(HERE / "out").mkdir(exist_ok=True)
(HERE / "out" / "index.html").write_text(page("GPU Serving Lab - 02 Roofline", body), encoding="utf-8")
print("wrote out/index.html")

