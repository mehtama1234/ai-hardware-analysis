"""Build Session 23 GPUMODE shared-memory GEMM page."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.report import esc, load_json, page


HERE = Path(__file__).resolve().parent
DATA = load_json(HERE / "out_gpumode_shared_memory_gemm.json")
GEMM = DATA["shared_memory_gemm"]
CUDA = DATA["cuda"]
MODEL = GEMM["traffic_model"]


def measured_rows() -> str:
    return "\n".join(
        "<tr>"
        f"<td>{esc(row['path'])}</td>"
        f"<td>{esc(row['seconds'])}</td>"
        f"<td>{esc(row['gflops'])}</td>"
        f"<td>{esc(row['max_abs_error'])}</td>"
        f"<td>{esc(row['purpose'])}</td>"
        "</tr>"
        for row in GEMM["rows"]
    )


def model_rows() -> str:
    rows = [
        ("shape M,N,K", MODEL["shape"]),
        ("tile", MODEL["tile"]),
        ("naive global load elements", MODEL["naive_global_load_elements"]),
        ("tiled global load elements upper bound", MODEL["tiled_global_load_elements_upper_bound"]),
        ("naive bytes", MODEL["naive_bytes"]),
        ("tiled bytes upper bound", MODEL["tiled_bytes_upper_bound"]),
        ("modeled global-memory reduction pct", MODEL["modeled_global_memory_reduction_pct"]),
        ("naive arithmetic intensity FLOP/byte", MODEL["naive_arithmetic_intensity_flop_per_byte"]),
        ("tiled arithmetic intensity FLOP/byte", MODEL["tiled_arithmetic_intensity_flop_per_byte"]),
    ]
    return "\n".join(f"<tr><th>{esc(key)}</th><td>{esc(value)}</td></tr>" for key, value in rows)


def cuda_rows() -> str:
    if CUDA["status"] == "ran":
        kernel = CUDA.get("kernel", {})
        rows = [
            ("status", CUDA["status"]),
            ("shape", kernel.get("shape")),
            ("tile", kernel.get("tile")),
            ("naive ms", kernel.get("naive_ms")),
            ("tiled ms", kernel.get("tiled_ms")),
            ("speedup", kernel.get("speedup")),
            ("naive GFLOP/s", kernel.get("naive_gflops")),
            ("tiled GFLOP/s", kernel.get("tiled_gflops")),
            ("tiled max abs error", kernel.get("tiled_max_abs_error")),
        ]
    else:
        rows = [
            ("status", CUDA["status"]),
            ("reason", CUDA.get("reason") or CUDA.get("boundary", "")),
            ("source", CUDA.get("source", "shared_memory_gemm.cu")),
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
        f"<td>{esc('; '.join(row['exercise_candidates'][:2]))}</td>"
        "</tr>"
        for row in lessons
    )


body = f"""
<header>
  <div class="kick">GPU kernels and LLM serving lab - Session 23</div>
  <h1>GPUMODE shared-memory tiled GEMM microscope.</h1>
  <p class="dek">This session turns GPUMODE CUDA/CUTLASS tiling lessons into a measured bridge
  between naive matmul, shared-memory reuse, Triton tile models, and later Tensor Core kernels.</p>
</header>

<section>
  <div class="eye">Measured CPU proxy</div>
  <h2>Naive loops, tiled reuse, and library reference</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>path</th><th>seconds</th><th>GFLOP/s</th><th>max error</th><th>purpose</th></tr>
      {measured_rows()}
    </table>
  </div>
  <div class="why"><h3>Finding</h3><p>{esc(GEMM["finding"])}</p></div>
</section>

<section>
  <div class="eye">Traffic model</div>
  <h2>Shared memory is about global-memory reuse</h2>
  <div class="card" style="overflow-x:auto">
    <table>{model_rows()}</table>
  </div>
</section>

<section>
  <div class="eye">CUDA source path</div>
  <h2>{esc(CUDA["status"])}</h2>
  <div class="card" style="overflow-x:auto">
    <table>{cuda_rows()}</table>
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
(HERE / "out" / "index.html").write_text(page("GPU Serving Lab - 23 GPUMODE Shared Memory GEMM", body), encoding="utf-8")
print("wrote out/index.html")
