"""Build Session 13 capstone report page."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.report import esc, load_json, page


HERE = Path(__file__).resolve().parent
DATA = load_json(HERE / "out_capstone_report.json")
D = DATA["diagnosis"]


def blocked_rows() -> str:
    if not D["blocked"]:
        return '<tr><td colspan="3" class="ok">No blocked runtime areas in current report.</td></tr>'
    return "\n".join(
        f"<tr><td>{esc(r['area'])}</td><td class=\"warn\">{esc(r['status'])}</td><td>{esc(r.get('reason'))}</td></tr>"
        for r in D["blocked"]
    )


kv = D["kv_cache_pressure_case"]
serving = D["serving_path_comparison"]
high = serving["high_level"]
opt = serving["optimized"]
body = f"""
<header>
  <div class="kick">GPU kernels and LLM serving lab - Session 13</div>
  <h1>The current end-to-end diagnosis.</h1>
  <p class="dek">This capstone reads the measurement artifacts from the completed sessions
  and turns them into one serving-system report: what ran, what is blocked, and what should
  be optimized next.</p>
</header>

<section>
  <div class="eye">Serving diagnosis</div>
  <h2>{esc(D["main_bottleneck_now"])}</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>current path</th><td>{esc(D["current_serving_path"])}</td></tr>
      <tr><th>device</th><td>{esc(D["device"])}</td></tr>
      <tr><th>throughput</th><td>{esc(D["tokens_per_sec"])} tokens/sec</td></tr>
      <tr><th>strongest signal</th><td>{esc(D["strongest_measured_signal"])}</td></tr>
      <tr><th>next optimization</th><td>{esc(D["next_optimization"])}</td></tr>
    </table>
  </div>
  <div class="why"><h3>Boundary</h3><p>{esc(DATA["boundary"])}</p></div>
</section>

<section>
  <div class="eye">Serving path comparison</div>
  <h2>High-level endpoint versus optimized batch path</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>path</th><th>endpoint</th><th>backend</th><th>tokens/sec</th><th>total latency ms</th><th>prefix reuse</th></tr>
      <tr>
        <td>{esc(high["name"])}</td>
        <td>{esc(high["endpoint"])}</td>
        <td>{esc(high["backend"])}</td>
        <td>{esc(high["tokens_per_sec"])}</td>
        <td>{esc(high["latency_ms_total"])}</td>
        <td>0</td>
      </tr>
      <tr>
        <td>{esc(opt["name"])}</td>
        <td>{esc(opt["endpoint"])}</td>
        <td>{esc(opt["backend"])}</td>
        <td>{esc(opt["tokens_per_sec"])}</td>
        <td>{esc(opt["latency_ms_total"])}</td>
        <td>{esc(opt["prefix_tokens_reused"])} tokens</td>
      </tr>
    </table>
  </div>
  <p>The optimized local path measured a {esc(serving["optimized_latency_speedup"])}x total-latency
  speedup for the same logical prompts. This is a CPU-runnable proxy for the same serving ideas
  used by GPU runtimes: batching, amortized prefill work, and KV/prefix reuse.</p>
</section>

<section>
  <div class="eye">Blocked runtime areas</div>
  <h2>What needs environment work</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>area</th><th>status</th><th>reason</th></tr>
      {blocked_rows()}
    </table>
  </div>
</section>

<section>
  <div class="eye">KV-cache pressure case</div>
  <h2>{esc(kv["name"])}</h2>
  <p>This was the highest block-use scenario in the current simulator: {esc(kv["blocks_with_prefix_cache"])}
  blocks with prefix caching versus {esc(kv["blocks_without_prefix_cache"])} without it, saving
  {esc(kv["saved_pct"])}%.</p>
</section>
"""

(HERE / "out").mkdir(exist_ok=True)
(HERE / "out" / "index.html").write_text(page("GPU Serving Lab - 13 Capstone", body), encoding="utf-8")
print("wrote out/index.html")
