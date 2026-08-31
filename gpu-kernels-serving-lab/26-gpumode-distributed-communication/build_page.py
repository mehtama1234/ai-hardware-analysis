"""Build Session 26 GPUMODE distributed communication page."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common.report import esc, load_json, page


HERE = Path(__file__).resolve().parent
DATA = load_json(HERE / "out_gpumode_distributed_communication.json")
MODEL = DATA["collective_model"]
PROXY = DATA["local_allreduce_proxy"]
READY = DATA["runtime_readiness"]
IMPORTED = DATA.get("imported_benchmarks", {})


def model_rows() -> str:
    rows = MODEL["rows"]
    interesting = [
        row
        for row in rows
        if row["message_bytes"] in {1024, 262144, 67108864, 536870912}
        and row["world_size"] in {2, 8}
    ]
    return "\n".join(
        "<tr>"
        f"<td>{esc(row['topology'])}</td>"
        f"<td>{esc(row['world_size'])}</td>"
        f"<td>{esc(row['message_bytes'])}</td>"
        f"<td>{esc(row['ring_us'])}</td>"
        f"<td>{esc(row['tree_us'])}</td>"
        f"<td>{esc(row['nvshmem_put_reduce_proxy_us'])}</td>"
        f"<td>{esc(row['modeled_winner'])}</td>"
        f"<td>{esc(row['regime'])}</td>"
        "</tr>"
        for row in interesting
    )


def crossover_rows() -> str:
    return "\n".join(
        "<tr>"
        f"<td>{esc(row['topology'])}</td>"
        f"<td>{esc(row['world_size'])}</td>"
        f"<td>{esc(row['first_bandwidth_dominated_bytes'])}</td>"
        f"<td>{esc(row['winner_at_crossover'])}</td>"
        "</tr>"
        for row in MODEL["crossover"]
    )


def proxy_rows() -> str:
    rows = [
        ("world size", PROXY["world_size"]),
        ("elements per rank", PROXY["elements_per_rank"]),
        ("bytes reduced", PROXY["bytes_reduced"]),
        ("seconds", PROXY["seconds"]),
        ("effective GB/s", PROXY["effective_gbps"]),
        ("max abs error", PROXY["max_abs_error"]),
    ]
    return "\n".join(f"<tr><th>{esc(key)}</th><td>{esc(value)}</td></tr>" for key, value in rows)


def readiness_rows() -> str:
    tools = READY.get("tools", {})
    rows = [
        ("status", READY["status"]),
        ("torch.distributed", READY["torch_distributed_available"]),
        ("NCCL backend", READY["nccl_backend_available"]),
        ("Gloo backend", READY["gloo_backend_available"]),
        ("CUDA device count", READY["torch_cuda_device_count"]),
        ("nvidia-smi", tools.get("nvidia-smi")),
        ("all_reduce_perf", tools.get("nccl-tests-all_reduce_perf")),
        ("nvshmem-info", tools.get("nvshmem-info")),
        ("ibv_devinfo", tools.get("ibv_devinfo")),
        ("reason", READY["reason"]),
    ]
    return "\n".join(f"<tr><th>{esc(key)}</th><td>{esc(value)}</td></tr>" for key, value in rows)


def imported_rows() -> str:
    rows = IMPORTED.get("rows", [])
    if not rows:
        return '<tr><td colspan="7">No imported NCCL/NVSHMEM benchmark rows found.</td></tr>'
    return "\n".join(
        "<tr>"
        f"<td>{esc(row['source'])}</td>"
        f"<td>{esc(row['tool'])}</td>"
        f"<td>{esc(row['message_bytes'])}</td>"
        f"<td>{esc(row['time_us'])}</td>"
        f"<td>{esc(row['algbw_gbps'])}</td>"
        f"<td>{esc(row['busbw_gbps'])}</td>"
        f"<td>{esc(row['errors'])}</td>"
        "</tr>"
        for row in rows[:16]
    )


def imported_best_rows() -> str:
    rows = IMPORTED.get("best_by_tool", [])
    if not rows:
        return '<tr><td colspan="4">No imported benchmark winners found.</td></tr>'
    return "\n".join(
        "<tr>"
        f"<td>{esc(row['tool'])}</td>"
        f"<td>{esc(row['best_message_bytes'])}</td>"
        f"<td>{esc(row['best_busbw_gbps'])}</td>"
        f"<td>{esc(row['best_time_us'])}</td>"
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
        f"<td>{esc(', '.join(row.get('tools', [])[:4]))}</td>"
        "</tr>"
        for row in lessons
    )


body = f"""
<header>
  <div class="kick">GPU kernels and LLM serving lab - Session 26</div>
  <h1>GPUMODE distributed communication and collectives.</h1>
  <p class="dek">This session turns NCCL, NVSHMEM, distributed GEMM, and scaling lessons into
  a measured local all-reduce semantic check plus a topology/message-size model for collective
  bottleneck triage.</p>
</header>

<section>
  <div class="eye">Collective model</div>
  <h2>Latency regime versus bandwidth regime</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>topology</th><th>world</th><th>bytes</th><th>ring us</th><th>tree us</th><th>NVSHMEM proxy us</th><th>winner</th><th>regime</th></tr>
      {model_rows()}
    </table>
  </div>
  <div class="why"><h3>Finding</h3><p>{esc(MODEL["finding"])}</p></div>
</section>

<section>
  <div class="eye">Crossover guide</div>
  <h2>Where the model becomes bandwidth dominated</h2>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>topology</th><th>world</th><th>first bandwidth-dominated bytes</th><th>winner</th></tr>
      {crossover_rows()}
    </table>
  </div>
</section>

<section>
  <div class="eye">Local all-reduce proxy</div>
  <h2>Correctness before cluster claims</h2>
  <div class="card" style="overflow-x:auto">
    <table>{proxy_rows()}</table>
  </div>
  <div class="why"><h3>Finding</h3><p>{esc(PROXY["finding"])}</p></div>
</section>

<section>
  <div class="eye">Imported benchmarks</div>
  <h2>{esc(IMPORTED.get("status", "empty"))}</h2>
  <div class="why"><h3>Finding</h3><p>{esc(IMPORTED.get("finding", ""))}</p></div>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>source</th><th>tool</th><th>bytes</th><th>time us</th><th>alg GB/s</th><th>bus GB/s</th><th>errors</th></tr>
      {imported_rows()}
    </table>
  </div>
  <div class="card" style="overflow-x:auto">
    <table>
      <tr><th>tool</th><th>best bytes</th><th>best bus GB/s</th><th>best time us</th></tr>
      {imported_best_rows()}
    </table>
  </div>
</section>

<section>
  <div class="eye">Runtime readiness</div>
  <h2>{esc(READY["status"])}</h2>
  <div class="card" style="overflow-x:auto">
    <table>{readiness_rows()}</table>
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
(HERE / "out" / "index.html").write_text(page("GPU Serving Lab - 26 GPUMODE Distributed Communication", body), encoding="utf-8")
print("wrote out/index.html")
