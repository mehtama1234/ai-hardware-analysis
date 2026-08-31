"""Build Session 24 GPUMODE Tensor Core/CUTLASS page."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.report import esc, load_json, page


HERE = Path(__file__).resolve().parent
DATA = load_json(HERE / "out_gpumode_tensor_core_cutlass.json")
PRECISION = DATA["tensor_core_precision"]
TILES = DATA["tensor_core_tile_model"]
CUDA = DATA["cuda"]


def precision_rows() -> str:
    return "\n".join(
        "<tr>"
        f"<td>{esc(row['path'])}</td>"
        f"<td>{esc(row['input_dtype'])}</td>"
        f"<td>{esc(row['seconds'])}</td>"
        f"<td>{esc(row['gflops'])}</td>"
        f"<td>{esc(row['max_abs_error'])}</td>"
        f"<td>{esc(row['relative_l2_error_pct'])}</td>"
        "</tr>"
        for row in PRECISION["rows"]
    )


def tile_rows() -> str:
    return "\n".join(
        "<tr>"
        f"<td>{esc(row['name'])}</td>"
        f"<td>{esc(row['m'])}x{esc(row['n'])}x{esc(row['k'])}</td>"
        f"<td>{esc(row['input'])}</td>"
        f"<td>{esc(row['accumulator'])}</td>"
        f"<td>{esc(row['output_tiles'])}</td>"
        f"<td>{esc(row['k_tiles_per_output'])}</td>"
        f"<td>{esc(row['mma_ops'])}</td>"
        f"<td>{esc(row['eligible_shape'])}</td>"
        "</tr>"
        for row in TILES["rows"]
    )


def cuda_rows() -> str:
    readiness = CUDA.get("readiness", {})
    tools = readiness.get("tools", {})
    if CUDA["status"] == "ran":
        kernel = CUDA.get("kernel", {})
        rows = [
            ("status", CUDA["status"]),
            ("shape", kernel.get("shape")),
            ("wmma tile", kernel.get("wmma_tile")),
            ("milliseconds", kernel.get("milliseconds")),
            ("GFLOP/s", kernel.get("gflops")),
            ("max abs error", kernel.get("max_abs_error")),
        ]
    else:
        rows = [
            ("status", CUDA["status"]),
            ("reason", readiness.get("reason") or CUDA.get("boundary", "")),
            ("nvcc", tools.get("nvcc")),
            ("nvidia-smi", tools.get("nvidia-smi")),
            ("CUTLASS root", tools.get("cutlass_root")),
            ("torch CUDA available", readiness.get("torch_cuda_available")),
            ("CUTLASS headers available", readiness.get("cutlass_available")),
            ("source", CUDA.get("source", "wmma_tensor_core_gemm.cu")),
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
  <div class="kick">GPU kernels and LLM serving lab - Session 24</div>
  <h1>GPUMODE Tensor Core and CUTLASS matmul readiness.</h1>
  <p class="dek">This session follows shared-memory GEMM with the next production question:
  when a matmul becomes Tensor Core eligible, what precision drift should be expected, and
  what local CUDA/CUTLASS state is required before claiming GPU throughput.</p>
</header>

<section>
  <div class="eye">Precision proxy</div>
  <h2>Low-precision inputs need measured error</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>path</th><th>input dtype</th><th>seconds</th><th>GFLOP/s</th><th>max abs error</th><th>relative L2 error %</th></tr>
      {precision_rows()}
    </table>
  </div>
  <div class="why"><h3>Finding</h3><p>{esc(PRECISION["finding"])}</p></div>
</section>

<section>
  <div class="eye">MMA tile model</div>
  <h2>Tile eligibility before kernel tuning</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>model</th><th>MxNxK</th><th>input</th><th>accumulator</th><th>output tiles</th><th>K tiles/output</th><th>MMA ops</th><th>eligible</th></tr>
      {tile_rows()}
    </table>
  </div>
  <div class="why"><h3>Finding</h3><p>{esc(TILES["finding"])}</p></div>
</section>

<section>
  <div class="eye">CUDA and CUTLASS readiness</div>
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
(HERE / "out" / "index.html").write_text(page("GPU Serving Lab - 24 GPUMODE Tensor Core CUTLASS", body), encoding="utf-8")
print("wrote out/index.html")
