"""Build Session 19 GPUMODE torch.compile page."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.report import esc, load_json, page


HERE = Path(__file__).resolve().parent
DATA = load_json(HERE / "out_gpumode_torch_compile.json")
COMP = DATA["torch_compile"]
GRAPH = COMP["graph_analysis"]


def rows() -> str:
    rendered = []
    for row in COMP["rows"]:
        detail = row.get("reason", "")
        if row.get("backend"):
            detail = f"{row.get('backend')} {detail}".strip()
        rendered.append(
            "<tr>"
            f"<td>{esc(row['name'])}</td>"
            f"<td>{esc(row['status'])}</td>"
            f"<td>{esc(row.get('seconds', ''))}</td>"
            f"<td>{esc(row.get('tflops', ''))}</td>"
            f"<td>{esc(row.get('max_abs_error', ''))}</td>"
            f"<td>{esc(detail)}</td>"
            "</tr>"
        )
    return "\n".join(rendered)


def graph_rows() -> str:
    rendered = []
    for name, result in GRAPH.items():
        rendered.append(
            "<tr>"
            f"<td>{esc(name)}</td>"
            f"<td>{esc(result['status'])}</td>"
            f"<td>{esc(result.get('graph_count', ''))}</td>"
            f"<td>{esc(result.get('graph_break_count', ''))}</td>"
            f"<td>{esc(result.get('op_count', ''))}</td>"
            f"<td>{esc('; '.join(result.get('break_reasons', [])) or result.get('reason', ''))}</td>"
            "</tr>"
        )
    return "\n".join(rendered)


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
  <div class="kick">GPU kernels and LLM serving lab - Session 19</div>
  <h1>GPUMODE torch.compile fusion and graph breaks.</h1>
  <p class="dek">This session turns PyTorch compiler lessons into a measured workflow:
  benchmark eager tensor code, compile the same function, inspect graph capture, and make
  data-dependent Python control flow visible as a graph-break risk.</p>
</header>

<section>
  <div class="eye">Eager vs compiled</div>
  <h2>Compiler capture is a runtime fact, not a promise</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>path</th><th>status</th><th>seconds</th><th>TFLOP/s</th><th>max error</th><th>detail</th></tr>
      {rows()}
    </table>
  </div>
  <div class="why"><h3>Finding</h3><p>{esc(COMP["finding"])}</p></div>
  <div class="why"><h3>Correctness</h3><p>{esc(DATA["correctness"])}</p></div>
</section>

<section>
  <div class="eye">Graph analysis</div>
  <h2>Captured graphs and breaks</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>function</th><th>status</th><th>graphs</th><th>breaks</th><th>ops</th><th>reason</th></tr>
      {graph_rows()}
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
(HERE / "out" / "index.html").write_text(page("GPU Serving Lab - 19 GPUMODE torch.compile", body), encoding="utf-8")
print("wrote out/index.html")
