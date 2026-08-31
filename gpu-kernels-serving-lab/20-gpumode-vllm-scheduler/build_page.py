"""Build Session 20 GPUMODE vLLM scheduler page."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.report import esc, load_json, page


HERE = Path(__file__).resolve().parent
DATA = load_json(HERE / "out_gpumode_vllm_scheduler.json")
SCHED = DATA["scheduler"]


def policy_rows() -> str:
    rendered = []
    for row in SCHED["policies"]:
        rendered.append(
            "<tr>"
            f"<td>{esc(row['name'])}</td>"
            f"<td>{esc(row['completed_requests'])}</td>"
            f"<td>{esc(row['makespan_ms'])}</td>"
            f"<td>{esc(row['tokens_per_second'])}</td>"
            f"<td>{esc(row['mean_ttft_ms'])}</td>"
            f"<td>{esc(row['p95_ttft_ms'])}</td>"
            f"<td>{esc(row['mean_tpot_ms'])}</td>"
            f"<td>{esc(row['peak_kv_blocks'])}</td>"
            "</tr>"
        )
    return "\n".join(rendered)


def comparison_rows() -> str:
    return "\n".join(
        "<tr>"
        f"<td>{esc(key)}</td>"
        f"<td>{esc(value)}</td>"
        "</tr>"
        for key, value in SCHED["comparison"].items()
    )


def workload_rows() -> str:
    return "\n".join(
        "<tr>"
        f"<td>{esc(row['id'])}</td>"
        f"<td>{esc(row['arrival_ms'])}</td>"
        f"<td>{esc(row['prompt_tokens'])}</td>"
        f"<td>{esc(row['output_tokens'])}</td>"
        f"<td>{esc(row['prefix_group'])}</td>"
        f"<td>{esc(row['shared_prefix_tokens'])}</td>"
        "</tr>"
        for row in SCHED["workload"]
    )


def lesson_rows() -> str:
    lessons = DATA["source"]["gpumode_lessons"]
    if not lessons:
        return '<tr><td colspan="5" class="warn">No GPUMODE lesson-intelligence artifact found.</td></tr>'
    return "\n".join(
        "<tr>"
        f"<td>{esc(row['index'])}</td>"
        f'<td><a href="{esc(row["url"])}">{esc(row["title"])}</a></td>'
        f"<td>{esc(', '.join(row['topics'][:5]))}</td>"
        f"<td>{esc(', '.join(row['concepts'][:5]))}</td>"
        f"<td>{esc('; '.join(row['exercise_candidates'][:2]))}</td>"
        "</tr>"
        for row in lessons
    )


body = f"""
<header>
  <div class="kick">GPU kernels and LLM serving lab - Session 20</div>
  <h1>GPUMODE vLLM scheduler and KV-cache pressure.</h1>
  <p class="dek">This session turns serving lessons into a deterministic scheduler lab:
  compare static FCFS batches with continuous batching, account for paged prefix-cache
  blocks, and report TTFT, TPOT, throughput, and memory pressure.</p>
</header>

<section>
  <div class="eye">Scheduler policies</div>
  <h2>Continuous batching changes the latency shape</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>policy</th><th>requests</th><th>makespan ms</th><th>tok/s</th><th>mean TTFT</th><th>P95 TTFT</th><th>mean TPOT</th><th>peak KV blocks</th></tr>
      {policy_rows()}
    </table>
  </div>
  <div class="why"><h3>Finding</h3><p>{esc(SCHED["finding"])}</p></div>
  <div class="why"><h3>Correctness</h3><p>{esc(DATA["correctness"])}</p></div>
</section>

<section>
  <div class="eye">Comparison</div>
  <h2>Measured scheduler deltas</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>metric</th><th>value</th></tr>
      {comparison_rows()}
    </table>
  </div>
</section>

<section>
  <div class="eye">Workload</div>
  <h2>Deterministic request mix</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>id</th><th>arrival ms</th><th>prompt</th><th>output</th><th>prefix group</th><th>shared prefix</th></tr>
      {workload_rows()}
    </table>
  </div>
</section>

<section>
  <div class="eye">GPUMODE links</div>
  <h2>Transcript-derived lesson anchors</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>#</th><th>lesson</th><th>topics</th><th>concepts</th><th>exercise candidates</th></tr>
      {lesson_rows()}
    </table>
  </div>
</section>

<section>
  <div class="eye">Evidence boundary</div>
  <p>{esc(DATA["boundary"])}</p>
</section>
"""

(HERE / "out").mkdir(exist_ok=True)
(HERE / "out" / "index.html").write_text(page("GPU Serving Lab - 20 GPUMODE vLLM Scheduler", body), encoding="utf-8")
print("wrote out/index.html")
