"""Build Session 18 GPUMODE online softmax page."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.report import esc, load_json, page


HERE = Path(__file__).resolve().parent
DATA = load_json(HERE / "out_gpumode_online_softmax.json")
ONLINE = DATA["online_softmax"]
TRITON = DATA["triton"]


def online_rows() -> str:
    return "\n".join(
        "<tr>"
        f"<td>{esc(row['seq'])}</td>"
        f"<td>{esc(row['dim'])}</td>"
        f"<td>{esc(row['block'])}</td>"
        f"<td>{esc(row['materialized_seconds'])}</td>"
        f"<td>{esc(row['online_seconds'])}</td>"
        f"<td>{esc(row['estimated_memory_saved_pct'])}%</td>"
        f"<td>{esc(row['max_abs_error'])}</td>"
        "</tr>"
        for row in ONLINE["rows"]
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
  <div class="kick">GPU kernels and LLM serving lab - Session 18</div>
  <h1>GPUMODE online softmax for attention.</h1>
  <p class="dek">This session derives the core FlashAttention-style idea at tutorial scale:
  keep row-wise max, denominator, and output state while streaming K/V blocks instead of
  materializing the full attention matrix.</p>
</header>

<section>
  <div class="eye">Online softmax measurement</div>
  <h2>Same answer, smaller live state</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>seq</th><th>dim</th><th>block</th><th>materialized s</th><th>online s</th><th>estimated memory saved</th><th>max error</th></tr>
      {online_rows()}
    </table>
  </div>
  <div class="why"><h3>Finding</h3><p>{esc(ONLINE["finding"])}</p></div>
  <div class="why"><h3>Correctness</h3><p>{esc(DATA["correctness"])}</p></div>
</section>

<section>
  <div class="eye">Triton fused-kernel path</div>
  <h2>{esc(TRITON["status"])}</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>field</th><th>value</th></tr>
      <tr><td>extends</td><td>{esc(TRITON.get("extends"))}</td></tr>
      <tr><td>reason</td><td>{esc(TRITON.get("reason", ""))}</td></tr>
      <tr><td>boundary</td><td>{esc(TRITON.get("boundary", ""))}</td></tr>
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
(HERE / "out" / "index.html").write_text(page("GPU Serving Lab - 18 GPUMODE Online Softmax", body), encoding="utf-8")
print("wrote out/index.html")
