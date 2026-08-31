"""Build Session 16 GPUMODE warp reductions page."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.report import esc, load_json, page


HERE = Path(__file__).resolve().parent
DATA = load_json(HERE / "out_gpumode_warp_reductions.json")
CPU = DATA["cpu_proxy"]
CUDA = DATA["cuda"]


def cpu_rows() -> str:
    return "\n".join(
        "<tr>"
        f"<td>{esc(row['pattern'])}</td>"
        f"<td>{esc(row['primitive'])}</td>"
        f"<td>{esc(row['semantic'])}</td>"
        f"<td>{esc(row['seconds'])}</td>"
        f"<td>{esc(row['effective_gbps'])}</td>"
        f"<td>{esc(row['abs_error'])}</td>"
        "</tr>"
        for row in CPU["rows"]
    )


def cuda_rows() -> str:
    if CUDA["status"] == "ran" and isinstance(CUDA.get("result"), dict):
        rows = CUDA["result"].get("rows", [])
        if rows:
            return "\n".join(
                "<tr>"
                f"<td>{esc(row['pattern'])}</td>"
                f"<td>{esc(row['milliseconds'])}</td>"
                f"<td>{esc(row['effective_gbps'])}</td>"
                f"<td>{esc(row['abs_error'])}</td>"
                "</tr>"
                for row in rows
            )
    return (
        "<tr>"
        f"<td>{esc(CUDA.get('source', 'reductions.cu'))}</td>"
        f"<td>{esc(CUDA.get('reason', CUDA.get('stderr', '')))}</td>"
        f"<td>{esc(CUDA.get('boundary', ''))}</td>"
        f"<td></td>"
        "</tr>"
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
        f"<td>{esc(', '.join(row['prerequisites'][:4]))}</td>"
        "</tr>"
        for row in lessons
    )


body = f"""
<header>
  <div class="kick">GPU kernels and LLM serving lab - Session 16</div>
  <h1>GPUMODE warp reductions and scans.</h1>
  <p class="dek">This session turns GPUMODE warp-execution and shared-memory themes into
  a concrete reduction/scan lab with CPU evidence and CUDA implementations for shared-memory
  and warp-shuffle block reductions.</p>
</header>

<section>
  <div class="eye">CPU proxy measurement</div>
  <h2>Reduction and scan are different synchronization stories</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>pattern</th><th>primitive</th><th>semantic</th><th>seconds</th><th>GB/s</th><th>abs error</th></tr>
      {cpu_rows()}
    </table>
  </div>
  <div class="why"><h3>Finding</h3><p>{esc(CPU["finding"])}</p></div>
  <div class="why"><h3>Correctness</h3><p>{esc(DATA["correctness"])}</p></div>
</section>

<section>
  <div class="eye">CUDA path</div>
  <h2>{esc(CUDA["status"])}</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>pattern/source</th><th>milliseconds/reason</th><th>GB/s/boundary</th><th>abs error</th></tr>
      {cuda_rows()}
    </table>
  </div>
</section>

<section>
  <div class="eye">GPUMODE links</div>
  <h2>Transcript-derived lesson anchors</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>#</th><th>lesson</th><th>topics</th><th>concepts</th><th>prerequisites</th></tr>
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
(HERE / "out" / "index.html").write_text(page("GPU Serving Lab - 16 GPUMODE Warp Reductions", body), encoding="utf-8")
print("wrote out/index.html")
