"""Build Session 09 from vLLM readiness JSON."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.report import esc, load_json, page


HERE = Path(__file__).resolve().parent
DATA = load_json(HERE / "out_vllm_serving.json")
R = DATA["result"]


body = f"""
<header>
  <div class="kick">GPU kernels and LLM serving lab - Session 09</div>
  <h1>Serving engines are schedulers and memory managers.</h1>
  <p class="dek">vLLM is the optimized-serving checkpoint in this lab. This first page
  records whether the current machine can run that path before we add a load generator and
  compare it against the Hugging Face baseline.</p>
</header>

<section>
  <div class="eye">Readiness result</div>
  <h2>{esc(R["status"])}</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>reason</th><td>{esc(R["reason"])}</td></tr>
      <tr><th>next</th><td>{esc(R["recommended_next"])}</td></tr>
    </table>
  </div>
  <div class="why"><h3>Boundary</h3><p>{esc(R["boundary"])}</p></div>
</section>

<section>
  <div class="eye">What will be measured here</div>
  <h2>Throughput, TTFT, and batch pressure</h2>
  <p>The real vLLM slice will run the same model/workload as Session 01, then sweep
  concurrency, prompt length, generated tokens, prefix sharing, and memory pressure. The
  target measurements are TTFT, inter-token latency, throughput, P95/P99 latency, and GPU
  memory.</p>
</section>
"""

(HERE / "out").mkdir(exist_ok=True)
(HERE / "out" / "index.html").write_text(page("GPU Serving Lab - 09 vLLM Serving", body), encoding="utf-8")
print("wrote out/index.html")

