"""Build Session 21 GPUMODE quantized-kernels page."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.report import esc, load_json, page


HERE = Path(__file__).resolve().parent
DATA = load_json(HERE / "out_gpumode_quantized_kernels.json")
Q = DATA["quantized_matmul"]


def rows() -> str:
    return "\n".join(
        "<tr>"
        f"<td>{esc(row['scheme'])}</td>"
        f"<td>{esc(row['seconds'])}</td>"
        f"<td>{esc(row['effective_gflops'])}</td>"
        f"<td>{esc(row['modeled_bytes']['total_mb'])}</td>"
        f"<td>{esc(row['memory_reduction_vs_fp16_pct'])}%</td>"
        f"<td>{esc(row['relative_error_pct'])}%</td>"
        f"<td>{esc(row['cosine'])}</td>"
        "</tr>"
        for row in Q["rows"]
    )


def runtime_rows() -> str:
    return "\n".join(
        "<tr>"
        f"<td>{esc(name)}</td>"
        f"<td>{esc(row['status'])}</td>"
        f"<td>{esc(row['reason'])}</td>"
        f"<td>{esc(row['next'])}</td>"
        "</tr>"
        for name, row in DATA["runtime_paths"].items()
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
  <div class="kick">GPU kernels and LLM serving lab - Session 21</div>
  <h1>GPUMODE quantized matmul kernel ladder.</h1>
  <p class="dek">This session moves past stored-weight compression into executable
  matmul paths: fp16, int8, int4 groupwise, and MXFP4-like dequantization are compared
  for runtime, modeled memory traffic, and numerical drift.</p>
</header>

<section>
  <div class="eye">Quantized matmul</div>
  <h2>Smaller weights still need the right kernel</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>scheme</th><th>seconds</th><th>GFLOP/s</th><th>modeled MB</th><th>memory reduction</th><th>relative error</th><th>cosine</th></tr>
      {rows()}
    </table>
  </div>
  <div class="why"><h3>Finding</h3><p>{esc(Q["finding"])}</p></div>
  <div class="why"><h3>Correctness</h3><p>{esc(DATA["correctness"])}</p></div>
</section>

<section>
  <div class="eye">GPU kernel boundary</div>
  <h2>CUDA and Triton path status</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>path</th><th>status</th><th>reason</th><th>next</th></tr>
      {runtime_rows()}
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
(HERE / "out" / "index.html").write_text(page("GPU Serving Lab - 21 GPUMODE Quantized Kernels", body), encoding="utf-8")
print("wrote out/index.html")
