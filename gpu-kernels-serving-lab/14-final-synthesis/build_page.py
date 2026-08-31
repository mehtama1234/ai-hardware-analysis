"""Build Session 14 final synthesis page."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.report import esc, load_json, page


HERE = Path(__file__).resolve().parent
DATA = load_json(HERE / "out_final_synthesis.json")
S = DATA["synthesis"]
SCALING = S["scaling_book_language"]
SERVING = S["serving_language"]
CAP = S["capstone_result"]
CORPUS = S["corpus_bridge"]
GPUMODE = S["gpumode_deep_labs"]


def blocked_rows() -> str:
    rows = CAP["blocked_runtime_areas"]
    if not rows:
        return '<tr><td colspan="3" class="ok">No blocked runtime areas in current report.</td></tr>'
    return "\n".join(
        f"<tr><td>{esc(row['area'])}</td><td class=\"warn\">{esc(row['status'])}</td><td>{esc(row.get('reason'))}</td></tr>"
        for row in rows
    )


def gpumode_rows() -> str:
    return "\n".join(
        "<tr>"
        f"<td>{esc(row['session'])}</td>"
        f"<td>{esc(row['lab_id'])}</td>"
        f"<td>{esc(row['lesson_anchor_count'])}</td>"
        f"<td>{esc(row['cpu_finding'])}</td>"
        f"<td>{esc(row['cuda_status'])}</td>"
        f"<td>{esc(row['correctness'])}</td>"
        "</tr>"
        for row in GPUMODE
    )


body = f"""
<header>
  <div class="kick">GPU kernels and LLM serving lab - Session 14</div>
  <h1>The final synthesis is generated from the evidence.</h1>
  <p class="dek">This page ties the lab back to scaling and serving vocabulary:
  compute, memory, communication, KV cache, batching, prefix reuse, quantization,
  and deployment runtime.</p>
</header>

<section>
  <div class="eye">JAX Scaling Book lens</div>
  <h2>Compute, memory, and communication</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>dimension</th><th>measured interpretation</th></tr>
      <tr><td>compute</td><td>{esc(SCALING["compute"])}</td></tr>
      <tr><td>memory</td><td>{esc(SCALING["memory"])}</td></tr>
      <tr><td>communication</td><td>{esc(SCALING["communication"])}</td></tr>
    </table>
  </div>
</section>

<section>
  <div class="eye">HF and vLLM serving lens</div>
  <h2>Runtime behavior, not just kernels</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>concept</th><th>measured interpretation</th></tr>
      <tr><td>KV cache</td><td>{esc(SERVING["kv_cache"])}</td></tr>
      <tr><td>batching</td><td>{esc(SERVING["batching"])}</td></tr>
      <tr><td>prefix reuse</td><td>{esc(SERVING["prefix_reuse"])}</td></tr>
      <tr><td>quantization</td><td>{esc(SERVING["quantization"])}</td></tr>
      <tr><td>deployment runtime</td><td>{esc(SERVING["deployment_runtime"])}</td></tr>
    </table>
  </div>
</section>

<section>
  <div class="eye">Capstone comparison</div>
  <h2>Two serving paths were measured</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>path</th><th>backend</th><th>tokens/sec</th><th>latency ms</th></tr>
      <tr>
        <td>{esc(CAP["high_level"]["name"])}</td>
        <td>{esc(CAP["high_level"]["backend"])}</td>
        <td>{esc(CAP["high_level"]["tokens_per_sec"])}</td>
        <td>{esc(CAP["high_level"]["latency_ms_total"])}</td>
      </tr>
      <tr>
        <td>{esc(CAP["optimized"]["name"])}</td>
        <td>{esc(CAP["optimized"]["backend"])}</td>
        <td>{esc(CAP["optimized"]["tokens_per_sec"])}</td>
        <td>{esc(CAP["optimized"]["latency_ms_total"])}</td>
      </tr>
    </table>
  </div>
</section>

<section>
  <div class="eye">GPUMODE deep lab</div>
  <h2>Transcript intelligence now drives a runnable kernel microscope</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>session</th><th>lab id</th><th>lesson anchors</th><th>CPU finding</th><th>CUDA status</th><th>correctness</th></tr>
      {gpumode_rows()}
    </table>
  </div>
</section>

<section>
  <div class="eye">Runtime gaps</div>
  <h2>What remains environment-gated</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>area</th><th>status</th><th>reason</th></tr>
      {blocked_rows()}
    </table>
  </div>
  <div class="why"><h3>Final read</h3><p>{esc(S["final_read"])}</p></div>
  <div class="why"><h3>Boundary</h3><p>{esc(DATA["boundary"])}</p></div>
</section>

<section>
  <div class="eye">Conference corpus bridge</div>
  <h2>The lab is the runnable counterpart to the corpus</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>repo synthesis</th><td>{esc(CORPUS["top_level_synthesis"])}</td></tr>
      <tr><th>venue pages found</th><td>{esc(len(CORPUS["venue_bigpicture_pages"]))}</td></tr>
      <tr><th>per-paper JSON files</th><td>{esc(CORPUS["per_paper_json_count"])}</td></tr>
      <tr><th>interpretation</th><td>{esc(CORPUS["interpretation"])}</td></tr>
    </table>
  </div>
</section>
"""

(HERE / "out").mkdir(exist_ok=True)
(HERE / "out" / "index.html").write_text(page("GPU Serving Lab - 14 Final Synthesis", body), encoding="utf-8")
print("wrote out/index.html")
