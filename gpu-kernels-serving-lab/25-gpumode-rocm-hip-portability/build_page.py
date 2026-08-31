"""Build Session 25 GPUMODE ROCm/HIP portability page."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.report import esc, load_json, page


HERE = Path(__file__).resolve().parent
DATA = load_json(HERE / "out_gpumode_rocm_hip_portability.json")
PORT = DATA["hip_portability"]
CPU = DATA["cpu_semantic_proxy"]
HIP = DATA["hip"]


def translation_rows() -> str:
    return "\n".join(
        "<tr>"
        f"<td>{esc(row['source'])}</td>"
        f"<td>{esc(row.get('translated', ''))}</td>"
        f"<td>{esc(row['status'])}</td>"
        f"<td>{esc(row.get('replacement_count', 0))}</td>"
        f"<td>{esc(', '.join(row.get('hard_boundaries', [])))}</td>"
        f"<td>{esc(', '.join(row.get('remaining_cuda_symbols', [])))}</td>"
        "</tr>"
        for row in PORT["rows"]
    )


def semantic_rows() -> str:
    return "\n".join(
        "<tr>"
        f"<td>{esc(row['operation'])}</td>"
        f"<td>{esc(row['seconds'])}</td>"
        f"<td>{esc(row.get('elements', row.get('shape')))}</td>"
        f"<td>{esc(row['max_abs_error'])}</td>"
        "</tr>"
        for row in CPU["rows"]
    )


def hip_rows() -> str:
    if HIP["status"] == "ran":
        kernel = HIP.get("kernel", {})
        rows = [
            ("status", HIP["status"]),
            ("operations", kernel.get("operations")),
            ("vector max abs error", kernel.get("vector_max_abs_error")),
            ("reduction abs error", kernel.get("reduction_abs_error")),
            ("gemm max abs error", kernel.get("gemm_max_abs_error")),
        ]
    else:
        rows = [
            ("status", HIP["status"]),
            ("reason", HIP.get("reason") or HIP.get("boundary", "")),
            ("source", HIP.get("source", "hip_portability_kernels.hip.cpp")),
        ]
    return "\n".join(f"<tr><th>{esc(key)}</th><td>{esc(value)}</td></tr>" for key, value in rows)


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
        f"<td>{esc(', '.join(row.get('tools', [])[:4]))}</td>"
        "</tr>"
        for row in lessons
    )


body = f"""
<header>
  <div class="kick">GPU kernels and LLM serving lab - Session 25</div>
  <h1>GPUMODE ROCm/HIP portability workbench.</h1>
  <p class="dek">This session turns CUDA-centered GPUMODE kernel lessons into an AMD portability
  exercise: translate runtime calls, preserve operation semantics, and identify which CUDA patterns
  need manual ROCm-specific replacements.</p>
</header>

<section>
  <div class="eye">Translation report</div>
  <h2>Mechanical ports versus real portability boundaries</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>CUDA source</th><th>translated HIP file</th><th>status</th><th>replacements</th><th>hard boundaries</th><th>remaining CUDA symbols</th></tr>
      {translation_rows()}
    </table>
  </div>
  <div class="why"><h3>Finding</h3><p>{esc(PORT["finding"])}</p></div>
</section>

<section>
  <div class="eye">CPU semantic proxy</div>
  <h2>Portability starts with same answers</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>operation</th><th>seconds</th><th>size</th><th>max error</th></tr>
      {semantic_rows()}
    </table>
  </div>
  <div class="why"><h3>Finding</h3><p>{esc(CPU["finding"])}</p></div>
</section>

<section>
  <div class="eye">HIP compile/run path</div>
  <h2>{esc(HIP["status"])}</h2>
  <div class="card" style="overflow-x:auto">
    <table>{hip_rows()}</table>
  </div>
</section>

<section>
  <div class="eye">GPUMODE links</div>
  <h2>Transcript-derived lesson anchors</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>#</th><th>lesson</th><th>topics</th><th>concepts</th><th>tools</th></tr>
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
(HERE / "out" / "index.html").write_text(page("GPU Serving Lab - 25 GPUMODE ROCm HIP Portability", body), encoding="utf-8")
print("wrote out/index.html")
