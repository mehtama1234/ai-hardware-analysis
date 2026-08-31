"""Build Session 17 GPUMODE Triton autotune page."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.report import esc, load_json, page


HERE = Path(__file__).resolve().parent
DATA = load_json(HERE / "out_gpumode_triton_autotune.json")
CONFIG = DATA["config_model"]
CPU = DATA["cpu_baseline"]
TRITON = DATA["triton"]


def config_rows() -> str:
    return "\n".join(
        "<tr>"
        f"<td>{esc(row['block_m'])}x{esc(row['block_n'])}x{esc(row['block_k'])}</td>"
        f"<td>{esc(row['num_warps'])}</td>"
        f"<td>{esc(row['programs'])}</td>"
        f"<td>{esc(row['k_tiles'])}</td>"
        f"<td>{esc(row['arithmetic_intensity_flop_per_byte'])}</td>"
        f"<td>{esc(row['fit_signal'])}</td>"
        "</tr>"
        for row in CONFIG["rows"]
    )


def triton_rows() -> str:
    if TRITON["status"] == "ran":
        return "\n".join(
            "<tr>"
            f"<td>{esc(row['block_m'])}x{esc(row['block_n'])}x{esc(row['block_k'])}</td>"
            f"<td>{esc(row['num_warps'])}</td>"
            f"<td>{esc(row['milliseconds'])}</td>"
            f"<td>{esc(row['tflops'])}</td>"
            f"<td>{esc(row['max_abs_error'])}</td>"
            "</tr>"
            for row in TRITON["rows"]
        )
    return (
        "<tr>"
        f"<td>{esc(TRITON['status'])}</td>"
        f"<td colspan=\"4\">{esc(TRITON.get('reason', TRITON.get('boundary', '')))}</td>"
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
        f"<td>{esc('; '.join(row['exercise_candidates'][:2]))}</td>"
        "</tr>"
        for row in lessons
    )


body = f"""
<header>
  <div class="kick">GPU kernels and LLM serving lab - Session 17</div>
  <h1>GPUMODE Triton matmul autotuning workbench.</h1>
  <p class="dek">This session turns GPUMODE Triton/autotuning lessons into a concrete tile
  search problem: model candidate block shapes, record a CPU baseline, and run a Triton
  sweep when CUDA is visible.</p>
</header>

<section>
  <div class="eye">Config model</div>
  <h2>Before timing, reason about tile reuse</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>block MxNxK</th><th>warps</th><th>programs</th><th>K tiles</th><th>AI FLOP/byte</th><th>signal</th></tr>
      {config_rows()}
    </table>
  </div>
  <div class="why"><h3>Finding</h3><p>{esc(CONFIG["finding"])}</p></div>
</section>

<section>
  <div class="eye">CPU baseline</div>
  <h2>Correctness and portability baseline</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>shape M,N,K</th><th>seconds</th><th>TFLOP/s</th><th>max abs error</th></tr>
      <tr><td>{esc(CPU["shape"])}</td><td>{esc(CPU["seconds"])}</td><td>{esc(CPU["tflops"])}</td><td>{esc(CPU["max_abs_error"])}</td></tr>
    </table>
  </div>
  <div class="why"><h3>Finding</h3><p>{esc(CPU["finding"])}</p></div>
</section>

<section>
  <div class="eye">Triton sweep</div>
  <h2>{esc(TRITON["status"])}</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>block/status</th><th>warps</th><th>milliseconds</th><th>TFLOP/s</th><th>max error</th></tr>
      {triton_rows()}
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
(HERE / "out" / "index.html").write_text(page("GPU Serving Lab - 17 GPUMODE Triton Autotune", body), encoding="utf-8")
print("wrote out/index.html")
