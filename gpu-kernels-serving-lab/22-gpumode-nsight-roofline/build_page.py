"""Build Session 22 GPUMODE Nsight-to-roofline page."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.report import esc, load_json, page


HERE = Path(__file__).resolve().parent
DATA = load_json(HERE / "out_gpumode_nsight_roofline.json")
P = DATA["profiler_roofline"]


def classification_rows() -> str:
    return "\n".join(
        "<tr>"
        f"<td>{esc(row['operation'])}</td>"
        f"<td>{esc(row['bottleneck'])}</td>"
        f"<td>{esc(row['evidence']['arithmetic_intensity_flop_per_byte'])}</td>"
        f"<td>{esc(row['evidence']['dram_pct_proxy'])}</td>"
        f"<td>{esc(row['evidence']['sm_pct_proxy'])}</td>"
        f"<td>{esc(row['evidence']['barrier_stall_proxy'])}</td>"
        f"<td>{esc(row['next_action'])}</td>"
        "</tr>"
        for row in P["classifications"]
    )


def counter_rows() -> str:
    rendered = []
    for row in P["rows"]:
        counters = row["counters"]
        rendered.append(
            "<tr>"
            f"<td>{esc(row['operation'])}</td>"
            f"<td>{esc(counters['dram__throughput.avg.pct_of_peak_sustained_elapsed'])}</td>"
            f"<td>{esc(counters['sm__throughput.avg.pct_of_peak_sustained_elapsed'])}</td>"
            f"<td>{esc(counters['smsp__average_warps_issue_stalled_barrier_per_issue_active.ratio'])}</td>"
            f"<td>{esc(counters['launch__occupancy_limit_registers.pct'])}</td>"
            f"<td>{esc(counters['kernel__launch_count'])}</td>"
            "</tr>"
        )
    return "\n".join(rendered)


def map_rows() -> str:
    return "\n".join(
        "<tr>"
        f"<td>{esc(name)}</td>"
        f"<td>{esc(meaning)}</td>"
        "</tr>"
        for name, meaning in P["counter_map"].items()
    )


def imported_rows() -> str:
    imported = P.get("imported_reports", {})
    rows = imported.get("classifications", [])
    if not rows:
        return '<tr><td colspan="7">No imported Nsight report rows found.</td></tr>'
    return "\n".join(
        "<tr>"
        f"<td>{esc(row['operation'])}</td>"
        f"<td>{esc(row['bottleneck'])}</td>"
        f"<td>{esc(row['evidence']['arithmetic_intensity_flop_per_byte'])}</td>"
        f"<td>{esc(row['evidence']['dram_pct_proxy'])}</td>"
        f"<td>{esc(row['evidence']['sm_pct_proxy'])}</td>"
        f"<td>{esc(row['evidence']['barrier_stall_proxy'])}</td>"
        f"<td>{esc(row['next_action'])}</td>"
        "</tr>"
        for row in rows
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
  <div class="kick">GPU kernels and LLM serving lab - Session 22</div>
  <h1>GPUMODE Nsight counters to roofline decisions.</h1>
  <p class="dek">This session turns profiler vocabulary into an optimization workflow:
  map counters to memory, compute, synchronization, and launch overhead, then connect
  each classification back to the local roofline measurements.</p>
</header>

<section>
  <div class="eye">Profiler availability</div>
  <h2>{esc(P["profiler"]["status"])}</h2>
  <div class="why"><h3>Reason</h3><p>{esc(P["profiler"]["reason"])}</p></div>
  <div class="why"><h3>Finding</h3><p>{esc(P["finding"])}</p></div>
  <div class="why"><h3>Correctness</h3><p>{esc(DATA["correctness"])}</p></div>
</section>

<section>
  <div class="eye">Classifications</div>
  <h2>Counter rows become next actions</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>operation</th><th>bottleneck</th><th>FLOP/byte</th><th>DRAM %</th><th>SM %</th><th>barrier stall</th><th>next action</th></tr>
      {classification_rows()}
    </table>
  </div>
</section>

<section>
  <div class="eye">Counter proxies</div>
  <h2>Nsight-shaped measurements</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>operation</th><th>DRAM % peak</th><th>SM % peak</th><th>barrier stall</th><th>register limit</th><th>launches</th></tr>
      {counter_rows()}
    </table>
  </div>
</section>

<section>
  <div class="eye">Imported reports</div>
  <h2>{esc(P.get("imported_reports", {}).get("status", "empty"))}</h2>
  <div class="why"><h3>Finding</h3><p>{esc(P.get("imported_reports", {}).get("finding", ""))}</p></div>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>kernel</th><th>bottleneck</th><th>FLOP/byte</th><th>DRAM %</th><th>SM %</th><th>barrier stall</th><th>next action</th></tr>
      {imported_rows()}
    </table>
  </div>
</section>

<section>
  <div class="eye">Counter map</div>
  <h2>Profiler terms used by this lab</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>counter</th><th>meaning</th></tr>
      {map_rows()}
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
(HERE / "out" / "index.html").write_text(page("GPU Serving Lab - 22 GPUMODE Nsight To Roofline", body), encoding="utf-8")
print("wrote out/index.html")
