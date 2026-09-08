"""Build the GPUMODE curriculum site from generated indexes."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"
CURRICULUM = ROOT / "analysis" / "gpumode-curriculum.json"
CURRICULUM_GRAPH = ROOT / "analysis" / "curriculum-graph.json"
WORKBENCH = ROOT / "analysis" / "gpu-systems-workbench.json"
PROJECT_INDEX = ROOT / "programming-projects" / "index.json"
PROJECT_RUN_REPORT = ROOT / "programming-projects" / "project-run-report.json"
PROJECT_CAPSTONE = ROOT / "programming-projects" / "capstone-portfolio.json"
PROJECT_NOTEBOOK_INDEX = ROOT / "programming-projects" / "notebook-index.json"
LESSON_LAB_INDEX = ROOT / "lesson-labs" / "index.json"
LESSON_LAB_RUN_REPORT = ROOT / "lesson-labs" / "run-report.json"
KERNEL_BENCHMARK_PLAN = ROOT / "kernel-benchmarks" / "plan.json"
KERNEL_BENCHMARK_REPORT = ROOT / "kernel-benchmarks" / "reports" / "kernel-benchmark-report.json"
COMPILER_RUNTIME_REPORT = ROOT / "compiler-runtime-inspection" / "compiler-runtime-report.json"
TENSOR_CORE_GEMM_REPORT = ROOT / "tensor-core-gemm" / "tensor-core-gemm-report.json"
PERSISTENT_KERNELS_REPORT = ROOT / "persistent-kernels" / "persistent-kernels-report.json"
PARALLEL_PRIMITIVES_REPORT = ROOT / "parallel-primitives" / "parallel-primitives-report.json"
RUNTIME_MATRIX = ROOT / "runtime-matrix" / "matrix.json"
PROFILER_EVIDENCE_REPORT = ROOT / "profiler-evidence" / "reports" / "profiler-evidence-report.json"
SERVING_TRACE_REPORT = ROOT / "serving-traces" / "reports" / "serving-trace-report.json"
KV_CACHE_REPORT = ROOT / "kv-cache-paged-attention" / "kv-cache-report.json"
ATTENTION_SERVING_REPORT = ROOT / "attention-serving-stack" / "attention-serving-report.json"
FLASH_ATTENTION_BACKWARD = ROOT / "flash-attention-backward" / "flash-attention-backward-report.json"
SPARSE_ATTENTION_REPORT = ROOT / "sparse-attention-kernels" / "sparse-attention-report.json"
FUSED_TRAINING_REPORT = ROOT / "fused-training-kernels" / "fused-training-report.json"
SERVING_ENGINE_COMPARISON = ROOT / "serving-engine-comparison" / "serving-engine-comparison.json"
SPECULATIVE_DECODING_REPORT = ROOT / "speculative-decoding-serving" / "speculative-decoding-report.json"
DIST_TOPOLOGY = ROOT / "distributed-topology" / "distributed-topology-plan.json"
DISTRIBUTED_COLLECTIVES = ROOT / "distributed-collectives" / "distributed-collectives-report.json"
DISTRIBUTED_COLLECTIVES_BENCHMARK = ROOT / "distributed-collectives" / "reports" / "collective-benchmark-run.json"
DISTRIBUTED_TRAINING_OPTIMIZER = ROOT / "distributed-training-optimizer" / "distributed-training-optimizer-report.json"
MOE_ROUTING_REPORT = ROOT / "moe-routing-all-to-all" / "moe-routing-report.json"
HARDWARE_CAPACITY_PLAN = ROOT / "hardware-capacity-planning" / "hardware-capacity-plan.json"
QUANTIZATION_REPORT = ROOT / "quantization-memory-formats" / "quantization-report.json"
NUMERICAL_REPRODUCIBILITY = ROOT / "numerical-reproducibility" / "numerical-reproducibility-report.json"
CUDA_GRAPHS_LATENCY = ROOT / "cuda-graphs-latency" / "cuda-graphs-latency-report.json"
MULTI_TENANT_SCHEDULING = ROOT / "multi-tenant-gpu-scheduling" / "multi-tenant-scheduling-report.json"
CUSTOM_OP_REPORT = ROOT / "custom-ops" / "reports" / "custom-op-report.json"
AUTOTUNE_DB = ROOT / "autotune-db" / "autotune-db.json"
MODEL_INTEGRATION_REPORT = ROOT / "model-integration" / "reports" / "tiny-transformer-report.json"
REGRESSION_LEDGER = ROOT / "regression-ledger" / "regression-ledger.json"
GPU_PROMOTION = ROOT / "gpu-promotion" / "gpu-host-promotion-manifest.json"
GPU_PROMOTION_SUITE = ROOT / "gpu-promotion" / "suite-run-report.json"
GPU_IMPORT_LINT = ROOT / "gpu-runs" / "import-lint-report.json"
GPU_RUNS = ROOT / "gpu-runs" / "gpu-run-report.json"
GPU_PROVENANCE = ROOT / "gpu-provenance" / "gpu-provenance-report.json"
GPU_MEASUREMENT_QUEUE = ROOT / "gpu-measurement-queue" / "gpu-measurement-queue.json"
GPU_ACCEPTANCE_LOGIC = ROOT / "gpu-measurement-queue" / "acceptance-logic-report.json"
GPU_HOST_PREFLIGHT = ROOT / "gpu-handoff" / "gpu-host-preflight.json"
GPU_HANDOFF = ROOT / "gpu-handoff" / "gpu-host-handoff.json"
ASSESSMENT = ROOT / "assessment" / "question-bank.json"
ASSESSMENT_GRADING = ROOT / "assessment" / "grading-report.json"
CAPSTONE_ACCEPTANCE = ROOT / "capstone-acceptance" / "capstone-acceptance.json"


def esc(value: Any) -> str:
    return html.escape(str(value))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


STYLE = """
:root{--bg:#0E1420;--bg2:#141D2C;--ink:#EAEEF4;--soft:#B4BFD0;--dim:#8493A8;--line:rgba(150,170,205,.14);--accent:#4FA8B8;--amber:#E3A63A;--green:#74B87A;--serif:"Iowan Old Style",Palatino,Georgia,serif;--sans:-apple-system,system-ui,"Segoe UI",Roboto,Arial,sans-serif;--mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);line-height:1.65}.wrap{max-width:1000px;margin:0 auto;padding:56px 24px 80px}
.kick{font-family:var(--mono);font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:var(--accent)}h1{font-family:var(--serif);font-size:clamp(34px,6vw,56px);line-height:1.05;margin:14px 0 0;color:#fff}
.dek{font-size:19px;color:var(--soft);max-width:72ch;margin-top:18px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin:30px 0}
.card{background:var(--bg2);border:1px solid var(--line);border-radius:12px;padding:16px 18px}.card h2{font-family:var(--serif);font-size:22px;margin:0 0 8px;color:#fff}.card p{margin:0;color:var(--soft)}
section{padding:34px 0;border-top:1px solid var(--line)}h2{font-family:var(--serif);font-size:28px;margin:0 0 12px;color:#fff}table{width:100%;border-collapse:collapse;font-size:13.5px}
th,td{padding:9px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{font-family:var(--mono);font-size:10.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--dim)}
td{color:var(--soft)}a{color:var(--accent);text-decoration:none}.pill{display:inline-block;font-family:var(--mono);font-size:11px;color:var(--green);border:1px solid var(--line);border-radius:999px;padding:2px 7px;margin:2px}
.meta{font-family:var(--mono);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--accent)}.small{font-size:12.5px;color:var(--dim)}.bridge-list{display:grid;gap:10px;margin:14px 0}.bridge-item{background:var(--bg2);border:1px solid var(--line);border-radius:8px;padding:14px 16px}.bridge-item h3{font-size:16px;color:#fff;margin:0 0 5px}.bridge-item p{margin:0;color:var(--soft)}
"""


def render_topics(curriculum: dict[str, Any]) -> str:
    cards = []
    for topic, count in sorted(curriculum["topic_counts"].items(), key=lambda item: (-item[1], item[0])):
        cards.append(f'<div class="card"><h2>{esc(topic)}</h2><p>{esc(count)} lesson matches</p></div>')
    return "\n".join(cards)


def render_readiness(curriculum: dict[str, Any]) -> str:
    cards = []
    for status, count in sorted(curriculum["lab_readiness_counts"].items(), key=lambda item: (-item[1], item[0])):
        cards.append(f'<div class="card"><h2>{esc(status)}</h2><p>{esc(count)} lesson matches</p></div>')
    return "\n".join(cards)


def render_labs(curriculum: dict[str, Any]) -> str:
    rows = []
    for lab in curriculum["proposed_labs"]:
        topics = " ".join(f'<span class="pill">{esc(topic)}</span>' for topic in lab["topics"])
        implementation = lab.get("implemented_as", "")
        rows.append(
            "<tr>"
            f"<td>{esc(lab['id'])}</td>"
            f"<td>{esc(lab['title'])}</td>"
            f"<td>{esc(lab.get('status', 'planned'))}</td>"
            f"<td>{topics}</td>"
            f"<td>{esc(lab['deliverable'])}</td>"
            f"<td>{esc(lab['extends'])}</td>"
            f"<td>{esc(implementation)}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def render_graph_order(graph: dict[str, Any]) -> str:
    rows = []
    for item in graph.get("practical_topic_order", [])[:12]:
        rows.append(
            "<tr>"
            f"<td>{esc(item['topic'])}</td>"
            f"<td>{esc(item['lesson_count'])}</td>"
            f"<td>{esc(item['prerequisite_signal_count'])}</td>"
            f"<td>{esc(', '.join(item.get('implemented_labs', [])[:4]))}</td>"
            f"<td>{esc(item['order_score'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="5">No graph order generated.</td></tr>'


def bridge_slug(profile_id: str) -> str:
    return f"bridge-{profile_id}.html"


def lesson_slug(lesson: dict[str, Any]) -> str:
    return f"lesson-{int(lesson['index']):03d}.html"


def render_workbench_profiles(workbench: dict[str, Any]) -> str:
    rows = []
    for profile in workbench["profiles"]:
        rows.append(
            "<tr>"
            f'<td><a href="{esc(bridge_slug(profile["id"]))}">{esc(profile["id"])}</a></td>'
            f"<td>{esc(profile['label'])}</td>"
            f"<td>{esc(profile['recommended_labs'][0]['id'] if profile['recommended_labs'] else '')}</td>"
            f"<td>{esc(profile['latest_measurements'][0]['path'] if profile['latest_measurements'] else '')}</td>"
            f"<td>{esc(profile['related_papers'][0]['title'] if profile['related_papers'] else '')}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def project_slug(project_id: str) -> str:
    return f"project-{project_id}.html"


def render_project_rows(project_index: dict[str, Any], run_report: dict[str, Any] | None = None) -> str:
    run_by_id = {row["id"]: row for row in (run_report or {}).get("projects", [])}
    rows = []
    for project in project_index.get("projects", []):
        run = run_by_id.get(project["id"], {})
        rows.append(
            "<tr>"
            f'<td><a href="{esc(project_slug(project["id"]))}">{esc(project["id"])}</a></td>'
            f"<td>{esc(project['track'])}</td>"
            f"<td>{esc(project['profile'])}</td>"
            f"<td>{esc(run.get('run', {}).get('status', 'not-run'))}</td>"
            f"<td>{esc(run.get('contract', {}).get('status', 'not-validated'))}</td>"
            f"<td>{esc(project['starter'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="6">No programming projects generated.</td></tr>'


def lesson_lab_slug(lab_id: str) -> str:
    return f"lesson-lab-{lab_id}.html"


def render_lesson_lab_rows(lesson_lab_index: dict[str, Any], run_report: dict[str, Any] | None = None) -> str:
    run_by_id = {row["id"]: row for row in (run_report or {}).get("labs", [])}
    rows = []
    for lab in lesson_lab_index.get("labs", []):
        run = run_by_id.get(lab["id"], {})
        rows.append(
            "<tr>"
            f"<td>{esc(lab['lesson_index'])}</td>"
            f'<td><a href="{esc(lesson_lab_slug(lab["id"]))}">{esc(lab["id"])}</a></td>'
            f"<td>{esc(lab['lesson_title'])}</td>"
            f"<td>{esc(run.get('contract', {}).get('status', 'not-run'))}</td>"
            f"<td>{esc(', '.join(lab.get('direct_programming_projects', [])[:3]))}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="5">No lesson labs generated.</td></tr>'


def build_lesson_lab_pages(lesson_lab_index: dict[str, Any], run_report: dict[str, Any] | None = None) -> None:
    run_by_id = {row["id"]: row for row in (run_report or {}).get("labs", [])}
    for lab in lesson_lab_index.get("labs", []):
        lab_dir = ROOT / lab["path"]
        metadata = load_json(lab_dir / "lab.json")
        contract = load_json(lab_dir / "measurement-contract.json")
        tasks = load_json(lab_dir / "tasks.json")
        run = run_by_id.get(lab["id"], {})
        lesson = metadata.get("lesson", {})
        task_rows = "".join(
            "<tr>"
            f"<td>{esc(task.get('id', ''))}</td>"
            f"<td>{esc(task.get('kind', ''))}</td>"
            f"<td>{esc(task.get('description', ''))}</td>"
            f"<td>{esc(task.get('evidence', ''))}</td>"
            "</tr>"
            for task in tasks.get("tasks", [])
        )
        contract_fields = "".join(f"<li>{esc(field)}</li>" for field in contract.get("required_fields", []))
        body = f"""<meta charset="utf-8">
<title>{esc(lab["id"])} - GPUMODE Lesson Lab</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated lesson lab</div>
  <h1>{esc(lesson.get("title", lab["id"]))}</h1>
  <p class="dek">Lesson #{esc(lab["lesson_index"])} has a runnable local lab scaffold, measurement contract,
  and promotion path into GPU runtime code.</p>
  <div class="grid">
    <div class="card"><h2>{esc(metadata.get("status", ""))}</h2><p>implementation status</p></div>
    <div class="card"><h2>{esc(run.get("contract", {}).get("status", "not-run"))}</h2><p>contract status</p></div>
    <div class="card"><h2><a href="../{esc(lab["path"])}/README.md">README</a></h2><p>lab instructions</p></div>
    <div class="card"><h2><a href="lesson-{int(lab["lesson_index"]):03d}.html">Lesson</a></h2><p>curriculum page</p></div>
  </div>

  <section>
    <h2>Files</h2>
    <table><tr><th>kind</th><th>path</th></tr>
      <tr><td>source</td><td>{esc(lab["path"])}/lab.py</td></tr>
      <tr><td>starter</td><td>{esc(lab["path"])}/starter.py</td></tr>
      <tr><td>measure</td><td>{esc(lab["path"])}/measure.py</td></tr>
      <tr><td>measurement</td><td>{esc(lab["path"])}/measurements.json</td></tr>
      <tr><td>contract</td><td>{esc(lab["path"])}/measurement-contract.json</td></tr>
    </table>
  </section>

  <section>
    <h2>Coverage Before This Lab</h2>
    <p class="small">deep lab candidates: {esc(', '.join(metadata.get("coverage_before", {}).get("candidate_deep_labs", [])) or "none")}</p>
    <p class="small">direct programming projects: {esc(', '.join(metadata.get("coverage_before", {}).get("direct_programming_projects", [])) or "none")}</p>
  </section>

  <section>
    <h2>Contract Fields</h2>
    <ul>{contract_fields}</ul>
  </section>

  <section>
    <h2>Tasks</h2>
    <table><tr><th>task</th><th>kind</th><th>description</th><th>evidence</th></tr>{task_rows}</table>
  </section>

  <section>
    <p class="small"><a href="lesson-labs.html">Back to lesson labs</a> / <a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
        (SITE / lesson_lab_slug(lab["id"])).write_text(body, encoding="utf-8")


def build_lesson_labs_page(lesson_lab_index: dict[str, Any], run_report: dict[str, Any] | None = None) -> None:
    build_lesson_lab_pages(lesson_lab_index, run_report)
    body = f"""<meta charset="utf-8">
<title>GPUMODE Lesson Lab Coverage</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated one-lab-per-lesson layer</div>
  <h1>GPUMODE lesson lab coverage.</h1>
  <p class="dek">Gap analysis and generated lab scaffolds for every GPUMODE lesson.</p>
  <div class="grid">
    <div class="card"><h2>{esc(lesson_lab_index.get("lesson_count", 0))}</h2><p>lessons analyzed</p></div>
    <div class="card"><h2>{esc(lesson_lab_index.get("generated_lab_count", 0))}</h2><p>lesson labs generated</p></div>
    <div class="card"><h2>{esc((run_report or {}).get("passed_contracts", 0))}</h2><p>contracts passed</p></div>
    <div class="card"><h2><a href="../lesson-labs/run-report.md">Run Report</a></h2><p>latest measurements</p></div>
  </div>

  <section>
    <h2>Lesson Lab Index</h2>
    <table><tr><th>#</th><th>lab</th><th>lesson</th><th>contract</th><th>project anchors before generation</th></tr>{render_lesson_lab_rows(lesson_lab_index, run_report)}</table>
  </section>
</div>
"""
    (SITE / "lesson-labs.html").write_text(body, encoding="utf-8")


def render_kernel_benchmark_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for bench in (report or {}).get("benchmarks", []):
        median_seconds = f"{bench.get('seconds', {}).get('median', 0):.8f}"
        rows.append(
            "<tr>"
            f"<td>{esc(bench['id'])}</td>"
            f"<td>{esc(bench['family'])}</td>"
            f"<td>{esc(bench.get('shape_class', ''))}</td>"
            f"<td>{esc(bench['status'])}</td>"
            f"<td>{esc(median_seconds)}</td>"
            f"<td>{esc(bench.get('result', {}).get('device', ''))}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="6">No kernel benchmark report generated.</td></tr>'


def render_kernel_family_rows(plan: dict[str, Any] | None = None) -> str:
    rows = []
    for family in (plan or {}).get("families", []):
        rows.append(
            "<tr>"
            f"<td>{esc(family['id'])}</td>"
            f"<td>{esc(family['title'])}</td>"
            f"<td>{esc(family['lesson_count'])}</td>"
            f"<td>{esc(family['cuda_source'])}</td>"
            f"<td>{esc(family['triton_source'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="5">No kernel benchmark plan generated.</td></tr>'


def build_kernel_benchmarks_page(plan: dict[str, Any] | None = None, report: dict[str, Any] | None = None) -> None:
    readiness = (report or {}).get("accelerator_readiness", {})
    body = f"""<meta charset="utf-8">
<title>GPUMODE Kernel Benchmarks</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated kernel benchmark layer</div>
  <h1>GPUMODE kernel benchmarks.</h1>
  <p class="dek">Curriculum-aware benchmark sweeps for memory, reduction, normalization,
  matmul, and fusion kernel families, with CUDA/Triton source promotion paths.</p>
  <div class="grid">
    <div class="card"><h2>{esc((plan or {}).get("covered_lessons", 0))} / {esc((plan or {}).get("lesson_count", 0))}</h2><p>lessons mapped</p></div>
    <div class="card"><h2>{esc((report or {}).get("benchmark_count", 0))}</h2><p>benchmark cases</p></div>
    <div class="card"><h2>{esc((report or {}).get("passed", 0))}</h2><p>cases passed</p></div>
    <div class="card"><h2>{esc(readiness.get("torch_device", "unknown"))}</h2><p>local torch device</p></div>
    <div class="card"><h2><a href="../kernel-benchmarks/PLAN.md">Plan</a></h2><p>lesson map</p></div>
    <div class="card"><h2><a href="../kernel-benchmarks/reports/kernel-benchmark-report.md">Report</a></h2><p>latest run</p></div>
  </div>

  <section>
    <h2>Benchmark Families</h2>
    <table><tr><th>family</th><th>purpose</th><th>lessons</th><th>CUDA source</th><th>Triton source</th></tr>{render_kernel_family_rows(plan)}</table>
  </section>

  <section>
    <h2>Benchmark Sweeps</h2>
    <table><tr><th>benchmark</th><th>family</th><th>shape</th><th>status</th><th>median seconds</th><th>device</th></tr>{render_kernel_benchmark_rows(report)}</table>
  </section>

  <section>
    <h2>Runtime Readiness</h2>
    <table><tr><th>tool</th><th>available</th></tr>
      <tr><td>torch device</td><td>{esc(readiness.get("torch_device", "unknown"))}</td></tr>
      <tr><td>nvcc</td><td>{esc(readiness.get("nvcc", False))}</td></tr>
      <tr><td>hipcc</td><td>{esc(readiness.get("hipcc", False))}</td></tr>
      <tr><td>nvidia-smi</td><td>{esc(readiness.get("nvidia_smi", False))}</td></tr>
      <tr><td>triton import</td><td>{esc(readiness.get("triton_available", False))}</td></tr>
    </table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "kernel-benchmarks.html").write_text(body, encoding="utf-8")


def render_compiler_runtime_feature_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for feature, count in (report or {}).get("feature_counts", {}).items():
        rows.append(f"<tr><td>{esc(feature)}</td><td>{esc(count)}</td></tr>")
    return "\n".join(rows) if rows else '<tr><td colspan="2">No compiler/runtime features generated.</td></tr>'


def render_compiler_runtime_source_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for row in (report or {}).get("source_rows", []):
        risks = ", ".join(row.get("risk_ids", [])) or "none"
        features = ", ".join(name for name, enabled in row.get("features", {}).items() if enabled)
        rows.append(
            "<tr>"
            f"<td>{esc(row['group'])}</td>"
            f"<td>{esc(row['path'])}</td>"
            f"<td>{esc(row['lines'])}</td>"
            f"<td>{esc(features)}</td>"
            f"<td>{esc(risks)}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="5">No compiler/runtime source rows generated.</td></tr>'


def build_compiler_runtime_page(report: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE Compiler Runtime Inspection</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated source inspection lab</div>
  <h1>GPUMODE compiler runtime inspection.</h1>
  <p class="dek">Static inspection of CUDA, Triton, ROCm/HIP, and custom-op source
  for launch indexing, masks, shared memory, barriers, tensor-core hints, and GPU-host promotion commands.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("source_count", 0))}</h2><p>source files</p></div>
    <div class="card"><h2>{esc((report or {}).get("group_count", 0))}</h2><p>source groups</p></div>
    <div class="card"><h2>{esc((report or {}).get("status", "missing"))}</h2><p>inspection status</p></div>
    <div class="card"><h2><a href="../compiler-runtime-inspection/reports/compiler-runtime-report.md">Report</a></h2><p>Markdown inspection</p></div>
  </div>

  <section>
    <h2>Feature Counts</h2>
    <table><tr><th>feature</th><th>sources</th></tr>{render_compiler_runtime_feature_rows(report)}</table>
  </section>

  <section>
    <h2>Source Rows</h2>
    <table><tr><th>group</th><th>path</th><th>lines</th><th>features</th><th>risks</th></tr>{render_compiler_runtime_source_rows(report)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "compiler-runtime-inspection.html").write_text(body, encoding="utf-8")


def render_tensor_core_gemm_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for row in (report or {}).get("scenarios", []):
        cta = row.get("cta_tile", {})
        mma = row.get("mma_shape", {})
        rows.append(
            "<tr>"
            f"<td>{esc(row['scenario_id'])}</td>"
            f"<td>{esc(row['status'])}</td>"
            f"<td>{esc(row.get('shape', {}).get('dtype', ''))}</td>"
            f"<td>{esc(cta.get('m'))}x{esc(cta.get('n'))}x{esc(cta.get('k'))}</td>"
            f"<td>{esc(mma.get('m'))}x{esc(mma.get('n'))}x{esc(mma.get('k'))}</td>"
            f"<td>{esc(row.get('shared_memory_bytes', 0))}</td>"
            f"<td>{esc(row.get('register_pressure_proxy', 0))}</td>"
            f"<td>{esc(row.get('arithmetic_intensity', 0))}</td>"
            f"<td>{esc(row.get('epilogue', ''))}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="9">No tensor-core GEMM scenarios generated.</td></tr>'


def build_tensor_core_gemm_page(report: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE CUTLASS CuTe Tensor Core GEMM</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated tensor-core GEMM lab</div>
  <h1>GPUMODE CUTLASS CuTe tensor-core GEMM.</h1>
  <p class="dek">CTA, warp, and MMA tiling planner for BF16, FP16, INT8,
  FP8-style, and LoRA GEMM shapes with shared memory, register pressure,
  epilogue fusion, arithmetic intensity, and GPU-host profiler promotion.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("scenario_count", 0))}</h2><p>scenarios</p></div>
    <div class="card"><h2>{esc((report or {}).get("tensor_core_eligible_scenarios", 0))}</h2><p>tensor-core eligible</p></div>
    <div class="card"><h2>{esc((report or {}).get("fused_epilogue_scenarios", 0))}</h2><p>fused epilogues</p></div>
    <div class="card"><h2><a href="../tensor-core-gemm/reports/tensor-core-gemm-report.md">Report</a></h2><p>Markdown GEMM report</p></div>
  </div>

  <section>
    <h2>Tensor Core GEMM Scenarios</h2>
    <table><tr><th>scenario</th><th>status</th><th>dtype</th><th>CTA</th><th>MMA</th><th>shared memory</th><th>registers</th><th>intensity</th><th>epilogue</th></tr>{render_tensor_core_gemm_rows(report)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "tensor-core-gemm.html").write_text(body, encoding="utf-8")


def render_persistent_kernel_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for row in (report or {}).get("scenarios", []):
        rows.append(
            "<tr>"
            f"<td>{esc(row['scenario_id'])}</td>"
            f"<td>{esc(row['kernel_family'])}</td>"
            f"<td>{esc(row['strategy'])}</td>"
            f"<td>{esc(row.get('occupancy_proxy', 0))}</td>"
            f"<td>{esc(row.get('speedup_vs_baseline', 0))}</td>"
            f"<td>{esc(row.get('hbm_reduction', 0))}</td>"
            f"<td>{esc(row.get('resident_ctas_per_sm', 0))}</td>"
            f"<td>{esc(row.get('producer_consumer', False))}</td>"
            f"<td>{esc(row['status'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="9">No persistent-kernel scenarios generated.</td></tr>'


def build_persistent_kernels_page(report: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE persistent kernels</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated persistent-kernel lab</div>
  <h1>GPUMODE persistent kernels.</h1>
  <p><strong>Analytical scenarios, not GPU measurements.</strong> Timings are supplied
  constants. Speedup, residency and traffic reductions are model outputs;
  passing design checks does not establish numerical correctness or device execution.</p>
  <p class="dek">Persistent softmax, matmul, grouped GEMM, normalization, and attention
  scenarios with occupancy, register pressure, shared memory residency, launch
  amortization, producer/consumer structure, and GPU-host profiler promotion.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("scenario_count", 0))}</h2><p>scenarios</p></div>
    <div class="card"><h2>{esc((report or {}).get("passed_scenarios", 0))}</h2><p>passed design checks</p></div>
    <div class="card"><h2>{esc((report or {}).get("family_count", 0))}</h2><p>kernel families</p></div>
    <div class="card"><h2><a href="../persistent-kernels/reports/persistent-kernels-report.md">Report</a></h2><p>Markdown persistent-kernel report</p></div>
  </div>

  <section>
    <h2>Persistent Kernel Scenarios</h2>
    <table><tr><th>scenario</th><th>family</th><th>strategy</th><th>occupancy proxy</th><th>modeled speedup</th><th>modeled HBM reduction</th><th>modeled resident CTA/SM</th><th>producer</th><th>design status</th></tr>{render_persistent_kernel_rows(report)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "persistent-kernels.html").write_text(body, encoding="utf-8")


def render_parallel_primitives_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for row in (report or {}).get("scenarios", []):
        rows.append(
            "<tr>"
            f"<td>{esc(row['scenario_id'])}</td>"
            f"<td>{esc(row['primitive'])}</td>"
            f"<td>{esc(row['algorithm'])}</td>"
            f"<td>{esc(row.get('work_efficiency', 0))}</td>"
            f"<td>{esc(row.get('bandwidth_proxy_gbps', 0))}</td>"
            f"<td>{esc(row.get('occupancy_proxy', 0))}</td>"
            f"<td>{esc(row.get('stable_order_required', False))}</td>"
            f"<td>{esc(row['status'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="8">No parallel primitive scenarios generated.</td></tr>'


def build_parallel_primitives_page(report: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE parallel primitives</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated parallel-primitives lab</div>
  <h1>GPUMODE parallel primitives.</h1>
  <p><strong>Analytical scenarios, not GPU measurements.</strong> Timings are supplied
  constants. Efficiency and bandwidth are derived proxies; numerical correctness
  and stable ordering have not been executed by this scenario report.</p>
  <p class="dek">Reduction, scan, stream compaction, radix sort, histogram, and
  segmented reduction scenarios with memory traffic, occupancy, atomics,
  stability, shared-memory pressure, and GPU-host profiler promotion.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("scenario_count", 0))}</h2><p>scenarios</p></div>
    <div class="card"><h2>{esc((report or {}).get("passed_scenarios", 0))}</h2><p>passed design checks</p></div>
    <div class="card"><h2>{esc((report or {}).get("primitive_count", 0))}</h2><p>primitive families</p></div>
    <div class="card"><h2><a href="../parallel-primitives/reports/parallel-primitives-report.md">Report</a></h2><p>Markdown primitive report</p></div>
  </div>

  <section>
    <h2>Primitive Scenarios</h2>
    <table><tr><th>scenario</th><th>primitive</th><th>algorithm</th><th>modeled efficiency</th><th>bandwidth proxy</th><th>occupancy proxy</th><th>stable order required</th><th>design status</th></tr>{render_parallel_primitives_rows(report)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "parallel-primitives.html").write_text(body, encoding="utf-8")


def render_runtime_profile_rows(matrix: dict[str, Any] | None = None) -> str:
    rows = []
    for profile in (matrix or {}).get("profiles", []):
        commands = "<br>".join(esc(command) for command in profile.get("commands", [])[:3])
        rows.append(
            "<tr>"
            f"<td>{esc(profile['id'])}</td>"
            f"<td>{esc(profile['status'])}</td>"
            f"<td>{esc(', '.join(profile.get('required_capabilities', [])))}</td>"
            f"<td>{esc(profile['purpose'])}</td>"
            f"<td>{commands}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="5">No runtime matrix generated.</td></tr>'


def build_runtime_matrix_page(matrix: dict[str, Any] | None = None) -> None:
    capabilities = (matrix or {}).get("local_capabilities", {})
    capability_rows = "".join(
        "<tr>"
        f"<td>{esc(key)}</td>"
        f"<td>{esc(value)}</td>"
        "</tr>"
        for key, value in capabilities.items()
    ) or '<tr><td colspan="2">No local capabilities recorded.</td></tr>'
    body = f"""<meta charset="utf-8">
<title>GPUMODE Runtime Matrix</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated runtime gates</div>
  <h1>GPUMODE runtime matrix.</h1>
  <p class="dek">Machine-profile gates for CPU, CUDA, Triton, ROCm/HIP, profiler,
  and distributed execution paths.</p>
  <div class="grid">
    <div class="card"><h2>{esc((matrix or {}).get("profile_count", 0))}</h2><p>profiles</p></div>
    <div class="card"><h2>{esc((matrix or {}).get("ready_profiles", 0))}</h2><p>ready locally</p></div>
    <div class="card"><h2>{esc((matrix or {}).get("fallback_profiles", 0))}</h2><p>source-ready fallback</p></div>
    <div class="card"><h2><a href="../runtime-matrix/MATRIX.md">Matrix</a></h2><p>Markdown gate plan</p></div>
  </div>

  <section>
    <h2>Profiles</h2>
    <table><tr><th>profile</th><th>status</th><th>required</th><th>purpose</th><th>commands</th></tr>{render_runtime_profile_rows(matrix)}</table>
  </section>

  <section>
    <h2>Local Capabilities</h2>
    <table><tr><th>capability</th><th>value</th></tr>{capability_rows}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "runtime-matrix.html").write_text(body, encoding="utf-8")


def render_profiler_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for row in (report or {}).get("rows", []):
        rows.append(
            "<tr>"
            f"<td>{esc(row['source'])}</td>"
            f"<td>{esc(row['name'])}</td>"
            f"<td>{esc(row['classification'])}</td>"
            f"<td>{esc(row['duration_us'])}</td>"
            f"<td>{esc('; '.join(row.get('remediation', [])[:3]))}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="5">No profiler evidence report generated.</td></tr>'


def render_profiler_counts(report: dict[str, Any] | None = None) -> str:
    rows = []
    for name, count in sorted((report or {}).get("classification_counts", {}).items()):
        rows.append(f"<tr><td>{esc(name)}</td><td>{esc(count)}</td></tr>")
    return "\n".join(rows) if rows else '<tr><td colspan="2">No classifications generated.</td></tr>'


def render_native_profiler_captures(report: dict[str, Any] | None = None) -> str:
    rows = []
    for capture in (report or {}).get("native_captures", []):
        rows.append(
            "<tr>"
            f"<td>{esc(capture.get('project'))}</td>"
            f"<td>{esc(capture.get('evidence_kind'))}</td>"
            f"<td>{esc(capture.get('sass', {}).get('instruction_line_count'))}</td>"
            f"<td>{esc(capture.get('nsight_compute', {}).get('metric'))}</td>"
            f"<td>{esc(capture.get('artifact'))}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="5">No native profiler captures recorded.</td></tr>'


def build_profiler_evidence_page(report: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE Profiler Evidence</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated profiler parser</div>
  <h1>GPUMODE profiler evidence.</h1>
  <p class="dek">Normalized rows are teaching fixtures; separately listed native captures
  retain measured device evidence. Fixture classifications are heuristics, not verified
  hardware diagnoses.</p>
  <p class="dek">Normalized Nsight Compute, Nsight Systems, and rocprof-shaped rows into
  bottleneck classifications and remediation actions.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("row_count", 0))}</h2><p>normalized rows</p></div>
    <div class="card"><h2>{esc((report or {}).get("source_count", 0))}</h2><p>profiler sources</p></div>
    <div class="card"><h2>{esc((report or {}).get("native_capture_count", 0))}</h2><p>native captures</p></div>
    <div class="card"><h2><a href="../profiler-evidence/reports/profiler-evidence-report.md">Report</a></h2><p>Markdown evidence</p></div>
    <div class="card"><h2><a href="../profiler-evidence/README.md">README</a></h2><p>fixture contract</p></div>
  </div>

  <section>
    <h2>Native profiler captures</h2>
    <table><tr><th>project</th><th>evidence kind</th><th>HMMA/SASS lines</th><th>Nsight metric</th><th>artifact</th></tr>{render_native_profiler_captures(report)}</table>
  </section>

  <section>
    <h2>Classification Counts</h2>
    <table><tr><th>classification</th><th>rows</th></tr>{render_profiler_counts(report)}</table>
  </section>

  <section>
    <h2>Profiler-shaped Fixture Rows</h2>
    <table><tr><th>source</th><th>name</th><th>heuristic classification</th><th>fixture duration us</th><th>remediation</th></tr>{render_profiler_rows(report)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "profiler-evidence.html").write_text(body, encoding="utf-8")


def render_serving_trace_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for trace in (report or {}).get("traces", []):
        for policy in trace.get("policies", []):
            summary = policy["summary"]
            rows.append(
                "<tr>"
                f"<td>{esc(trace['trace_id'])}</td>"
                f"<td>{esc(summary['policy'])}</td>"
                f"<td>{esc(summary['completed_count'])}/{esc(summary['request_count'])}</td>"
                f"<td>{esc(summary['output_tokens_per_second'])}</td>"
                f"<td>{esc(summary['p50_ttft_ms'])}</td>"
                f"<td>{esc(summary['p95_ttft_ms'])}</td>"
                f"<td>{esc(summary['mean_tpot_ms'])}</td>"
                f"<td>{esc(summary['peak_live_kv_blocks'])}</td>"
                f"<td>{esc(summary['prefix_cache_blocks_saved'])}</td>"
                "</tr>"
            )
    return "\n".join(rows) if rows else '<tr><td colspan="9">No serving trace report generated.</td></tr>'


def render_serving_comparison_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for row in (report or {}).get("comparisons", []):
        rows.append(
            "<tr>"
            f"<td>{esc(row['trace_id'])}</td>"
            f"<td>{esc(row['throughput_speedup'])}</td>"
            f"<td>{esc(row['p50_ttft_delta_ms'])}</td>"
            f"<td>{esc(row['prefix_cache_blocks_saved'])}</td>"
            f"<td>{esc(row['peak_live_kv_blocks'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="5">No serving comparisons generated.</td></tr>'


def build_serving_traces_page(report: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE Serving Trace Replay</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated serving systems lab</div>
  <h1>GPUMODE serving trace replay.</h1>
  <p class="dek">Request trace replay for vLLM-style TTFT, TPOT, throughput,
  prefix-cache reuse, and peak KV-cache pressure analysis.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("trace_count", 0))}</h2><p>request traces</p></div>
    <div class="card"><h2>{esc((report or {}).get("passed_traces", 0))}</h2><p>traces passed</p></div>
    <div class="card"><h2>{esc(len((report or {}).get("policy_ids", [])))}</h2><p>policies compared</p></div>
    <div class="card"><h2><a href="../serving-traces/reports/serving-trace-report.md">Report</a></h2><p>Markdown replay report</p></div>
  </div>

  <section>
    <h2>Policy Comparisons</h2>
    <table><tr><th>trace</th><th>throughput speedup</th><th>p50 TTFT delta ms</th><th>prefix blocks saved</th><th>peak KV blocks</th></tr>{render_serving_comparison_rows(report)}</table>
  </section>

  <section>
    <h2>Trace Metrics</h2>
    <table><tr><th>trace</th><th>policy</th><th>completed</th><th>tok/s</th><th>p50 TTFT</th><th>p95 TTFT</th><th>mean TPOT</th><th>peak KV</th><th>prefix saved</th></tr>{render_serving_trace_rows(report)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "serving-traces.html").write_text(body, encoding="utf-8")


def render_kv_cache_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for row in (report or {}).get("scenarios", []):
        rows.append(
            "<tr>"
            f"<td>{esc(row['scenario_id'])}</td>"
            f"<td>{esc(row['status'])}</td>"
            f"<td>{esc(row['peak_block_savings'])}</td>"
            f"<td>{esc(row['waste_ratio_reduction'])}</td>"
            f"<td>{esc(row['admission_delta'])}</td>"
            f"<td>{esc(row['paged']['prefix_blocks_reused'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="6">No KV-cache scenarios generated.</td></tr>'


def build_kv_cache_page(report: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE KV Cache PagedAttention</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated serving allocator lab</div>
  <h1>GPUMODE KV cache and PagedAttention.</h1>
  <p class="dek">Block-table allocator model for KV-cache fragmentation,
  prefix reuse, eviction, admission pressure, and GPU serving promotion.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("scenario_count", 0))}</h2><p>scenarios</p></div>
    <div class="card"><h2>{esc((report or {}).get("passed_scenarios", 0))}</h2><p>passed scenarios</p></div>
    <div class="card"><h2>{esc((report or {}).get("total_prefix_blocks_reused", 0))}</h2><p>prefix blocks reused</p></div>
    <div class="card"><h2><a href="../kv-cache-paged-attention/reports/kv-cache-report.md">Report</a></h2><p>Markdown KV-cache report</p></div>
  </div>

  <section>
    <h2>Allocator Comparison</h2>
    <table><tr><th>scenario</th><th>status</th><th>peak block savings</th><th>waste reduction</th><th>admission delta</th><th>prefix blocks reused</th></tr>{render_kv_cache_rows(report)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "kv-cache-paged-attention.html").write_text(body, encoding="utf-8")


def render_attention_serving_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for row in (report or {}).get("scenarios", []):
        rows.append(
            "<tr>"
            f"<td>{esc(row['scenario_id'])}</td>"
            f"<td>{esc(row['status'])}</td>"
            f"<td>{esc(row['hbm_reduction'])}</td>"
            f"<td>{esc(row['tiles']['shared_memory_bytes'])}</td>"
            f"<td>{esc(row['arithmetic_intensity'])}</td>"
            f"<td>{esc(row['scheduler']['policy'])}</td>"
            f"<td>{esc(row['scheduler']['prefix_blocks_reused'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="7">No attention serving scenarios generated.</td></tr>'


def build_attention_serving_page(report: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE FlashAttention vLLM Serving Stack</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated attention serving systems lab</div>
  <h1>GPUMODE FlashAttention to vLLM serving stack.</h1>
  <p class="dek">End-to-end attention lab connecting tiled online softmax,
  KV-cache block reuse, prefill/decode scheduling, CUDA Graph bucket fit,
  numerical tolerance, and GPU-host profiling promotion.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("scenario_count", 0))}</h2><p>scenarios</p></div>
    <div class="card"><h2>{esc((report or {}).get("passed_scenarios", 0))}</h2><p>passed scenarios</p></div>
    <div class="card"><h2>{esc((report or {}).get("total_prefix_blocks_reused", 0))}</h2><p>prefix blocks reused</p></div>
    <div class="card"><h2><a href="../attention-serving-stack/reports/attention-serving-report.md">Report</a></h2><p>Markdown stack report</p></div>
  </div>

  <section>
    <h2>FlashAttention Serving Scenarios</h2>
    <table><tr><th>scenario</th><th>status</th><th>HBM reduction</th><th>shared memory</th><th>intensity</th><th>scheduler</th><th>prefix reuse</th></tr>{render_attention_serving_rows(report)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "attention-serving-stack.html").write_text(body, encoding="utf-8")


def render_flash_attention_backward_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for row in (report or {}).get("scenarios", []):
        shape = row.get("shape", {})
        rows.append(
            "<tr>"
            f"<td>{esc(row['scenario_id'])}</td>"
            f"<td>{esc(shape.get('dtype', ''))}</td>"
            f"<td>{esc(shape.get('seq_q', 0))}x{esc(shape.get('seq_kv', 0))}</td>"
            f"<td>{esc(row.get('speedup_vs_baseline', 0))}</td>"
            f"<td>{esc(row.get('hbm_reduction', 0))}</td>"
            f"<td>{esc(row.get('recompute_overhead_ratio', 0))}</td>"
            f"<td>{esc(row.get('occupancy_proxy', 0))}</td>"
            f"<td>{esc(', '.join(row.get('gradient_paths', [])))}</td>"
            f"<td>{esc(row['status'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="9">No FlashAttention backward scenarios generated.</td></tr>'


def build_flash_attention_backward_page(report: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE FlashAttention backward</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated FlashAttention backward lab</div>
  <h1>GPUMODE FlashAttention backward.</h1>
  <p class="dek">Training-side attention backward scenarios covering dQ, dK, dV,
  dSoftmax, online-softmax recompute, dropout, grouped-query attention,
  activation-memory savings, HBM traffic, numerical error, and GPU profiler promotion.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("scenario_count", 0))}</h2><p>scenarios</p></div>
    <div class="card"><h2>{esc((report or {}).get("passed_scenarios", 0))}</h2><p>passed design checks</p></div>
    <div class="card"><h2>{esc((report or {}).get("dropout_scenarios", 0))}</h2><p>dropout cases</p></div>
    <div class="card"><h2><a href="../flash-attention-backward/reports/flash-attention-backward-report.md">Report</a></h2><p>Markdown backward report</p></div>
  </div>

  <section>
    <h2>Backward Scenarios</h2>
    <table><tr><th>scenario</th><th>dtype</th><th>seq q/kv</th><th>speedup</th><th>HBM reduction</th><th>recompute</th><th>occupancy</th><th>gradients</th><th>status</th></tr>{render_flash_attention_backward_rows(report)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "flash-attention-backward.html").write_text(body, encoding="utf-8")


def render_sparse_attention_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for row in (report or {}).get("scenarios", []):
        shape = row.get("shape", {})
        rows.append(
            "<tr>"
            f"<td>{esc(row['scenario_id'])}</td>"
            f"<td>{esc(row.get('pattern', 'unknown'))}</td>"
            f"<td>{esc(shape.get('seq_q', 0))}x{esc(shape.get('seq_kv', 0))}</td>"
            f"<td>{esc(row.get('density', 0))}</td>"
            f"<td>{esc(row.get('speedup_vs_dense', 0))}</td>"
            f"<td>{esc(row.get('hbm_reduction', 0))}</td>"
            f"<td>{esc(row.get('load_balance_proxy', 0))}</td>"
            f"<td>{esc(', '.join(row.get('kernel_paths', [])))}</td>"
            f"<td>{esc(row['status'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="9">No sparse attention scenarios generated.</td></tr>'


def build_sparse_attention_page(report: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE sparse attention kernels</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated sparse attention lab</div>
  <h1>GPUMODE sparse attention kernels.</h1>
  <p class="dek">Sparse, ragged, neighborhood, and top-k attention scenarios covering
  metadata build, sparse QK, online softmax, sparse PV, decode, backward, load
  balance, numerical error, and GPU profiler promotion.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("scenario_count", 0))}</h2><p>scenarios</p></div>
    <div class="card"><h2>{esc((report or {}).get("pattern_count", 0))}</h2><p>patterns</p></div>
    <div class="card"><h2>{esc((report or {}).get("ragged_scenarios", 0))}</h2><p>ragged cases</p></div>
    <div class="card"><h2><a href="../sparse-attention-kernels/reports/sparse-attention-report.md">Report</a></h2><p>Markdown sparse attention report</p></div>
  </div>

  <section>
    <h2>Sparse Scenarios</h2>
    <table><tr><th>scenario</th><th>pattern</th><th>seq q/kv</th><th>density</th><th>speedup</th><th>HBM reduction</th><th>load balance</th><th>kernel paths</th><th>status</th></tr>{render_sparse_attention_rows(report)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "sparse-attention-kernels.html").write_text(body, encoding="utf-8")


def render_fused_training_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for row in (report or {}).get("scenarios", []):
        rows.append(
            "<tr>"
            f"<td>{esc(row['scenario_id'])}</td>"
            f"<td>{esc(row.get('kernel_family', 'unknown'))}</td>"
            f"<td>{esc(row.get('dtype', ''))}</td>"
            f"<td>{esc(row.get('speedup_vs_unfused', 0))}</td>"
            f"<td>{esc(row.get('hbm_reduction', 0))}</td>"
            f"<td>{esc(row.get('launch_reduction', 0))}</td>"
            f"<td>{esc(row.get('max_abs_error', 0))}</td>"
            f"<td>{esc(', '.join(row.get('kernel_paths', [])))}</td>"
            f"<td>{esc(row['status'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="9">No fused training scenarios generated.</td></tr>'


def build_fused_training_page(report: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE fused training kernels</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated fused training kernel lab</div>
  <h1>GPUMODE fused training kernels.</h1>
  <p class="dek">LLM training kernel scenarios covering RMSNorm, SwiGLU, fused
  cross-entropy, AdamW, grad clipping, dropout/residual/norm fusion, backward
  checks, optimizer state, launch count, HBM traffic, and profiler promotion.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("scenario_count", 0))}</h2><p>scenarios</p></div>
    <div class="card"><h2>{esc((report or {}).get("family_count", 0))}</h2><p>kernel families</p></div>
    <div class="card"><h2>{esc((report or {}).get("optimizer_state_scenarios", 0))}</h2><p>optimizer cases</p></div>
    <div class="card"><h2><a href="../fused-training-kernels/reports/fused-training-report.md">Report</a></h2><p>Markdown fused training report</p></div>
  </div>

  <section>
    <h2>Training Kernel Scenarios</h2>
    <table><tr><th>scenario</th><th>family</th><th>dtype</th><th>speedup</th><th>HBM reduction</th><th>launch reduction</th><th>max error</th><th>kernel paths</th><th>status</th></tr>{render_fused_training_rows(report)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "fused-training-kernels.html").write_text(body, encoding="utf-8")


def render_serving_engine_recommendation_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for row in (report or {}).get("scenario_recommendations", []):
        rows.append(
            "<tr>"
            f"<td>{esc(row['scenario_id'])}</td>"
            f"<td>{esc(row['recommended_engine'])}</td>"
            f"<td>{esc(row['runner_up'])}</td>"
            f"<td>{esc(row['why'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="4">No serving engine recommendations generated.</td></tr>'


def render_serving_engine_score_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for scenario in (report or {}).get("scenarios", []):
        for engine in scenario.get("engines", [])[:5]:
            rows.append(
                "<tr>"
                f"<td>{esc(scenario['scenario_id'])}</td>"
                f"<td>{esc(engine['engine'])}</td>"
                f"<td>{esc(engine['score'])}</td>"
                f"<td>{esc(engine['estimated_output_tokens_per_second'])}</td>"
                f"<td>{esc(engine['estimated_p50_ttft_ms'])}</td>"
                f"<td>{esc(engine['estimated_peak_kv_blocks'])}</td>"
                f"<td>{esc(', '.join(engine.get('features', [])[:4]))}</td>"
                "</tr>"
            )
    return "\n".join(rows) if rows else '<tr><td colspan="7">No serving engine scores generated.</td></tr>'


def build_serving_engine_comparison_page(report: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE Serving Engine Comparison</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated production inference lab</div>
  <h1>GPUMODE serving engine comparison.</h1>
  <p class="dek">Scenario-weighted comparison of vLLM, Hugging Face TGI, SGLang,
  TensorRT-LLM, and HF Transformers baseline using the local serving trace replay metrics.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("engine_count", 0))}</h2><p>engines compared</p></div>
    <div class="card"><h2>{esc((report or {}).get("scenario_count", 0))}</h2><p>production scenarios</p></div>
    <div class="card"><h2>{esc((report or {}).get("status", "missing"))}</h2><p>comparison status</p></div>
    <div class="card"><h2><a href="../serving-engine-comparison/reports/serving-engine-comparison.md">Report</a></h2><p>Markdown comparison</p></div>
  </div>

  <section>
    <h2>Scenario Recommendations</h2>
    <table><tr><th>scenario</th><th>recommended</th><th>runner up</th><th>why</th></tr>{render_serving_engine_recommendation_rows(report)}</table>
  </section>

  <section>
    <h2>Engine Scores</h2>
    <table><tr><th>scenario</th><th>engine</th><th>score</th><th>tok/s</th><th>p50 TTFT</th><th>peak KV</th><th>features</th></tr>{render_serving_engine_score_rows(report)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "serving-engine-comparison.html").write_text(body, encoding="utf-8")


def render_speculative_decoding_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for row in (report or {}).get("scenarios", []):
        rows.append(
            "<tr>"
            f"<td>{esc(row['scenario_id'])}</td>"
            f"<td>{esc(row.get('workload', 'unknown'))}</td>"
            f"<td>{esc(row.get('engine_hint', 'unknown'))}</td>"
            f"<td>{esc(row.get('draft_width', 0))}</td>"
            f"<td>{esc(row.get('acceptance_rate', 0))}</td>"
            f"<td>{esc(row.get('speedup_vs_baseline', 0))}</td>"
            f"<td>{esc(row.get('wasted_draft_ratio', 0))}</td>"
            f"<td>{esc(row.get('scheduler_policy', 'unknown'))}</td>"
            f"<td>{esc(row['status'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="9">No speculative decoding scenarios generated.</td></tr>'


def build_speculative_decoding_page(report: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE speculative decoding serving</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated speculative decoding serving lab</div>
  <h1>GPUMODE speculative decoding serving.</h1>
  <p class="dek">Draft/target verification, acceptance rate, rollback pressure,
  wasted draft work, KV commit accounting, TTFT/TPOT, engine fit, scheduler
  policy, and GPU-host or Colab promotion evidence.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("scenario_count", 0))}</h2><p>scenarios</p></div>
    <div class="card"><h2>{esc((report or {}).get("passed_scenarios", 0))}</h2><p>passed scenarios</p></div>
    <div class="card"><h2>{esc((report or {}).get("review_scenarios", 0))}</h2><p>review cases</p></div>
    <div class="card"><h2><a href="../speculative-decoding-serving/reports/speculative-decoding-report.md">Report</a></h2><p>Markdown speculative decoding report</p></div>
  </div>

  <section>
    <h2>Speculative Serving Scenarios</h2>
    <table><tr><th>scenario</th><th>workload</th><th>engine</th><th>draft</th><th>acceptance</th><th>speedup</th><th>wasted</th><th>scheduler</th><th>status</th></tr>{render_speculative_decoding_rows(report)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "speculative-decoding-serving.html").write_text(body, encoding="utf-8")


def render_distributed_topology_recommendations(report: dict[str, Any] | None = None) -> str:
    rows = []
    for row in (report or {}).get("recommendations", []):
        strategy = row.get("strategy", {})
        rows.append(
            "<tr>"
            f"<td>{esc(row['workload_id'])}</td>"
            f"<td>{esc(row['recommended_topology'])}</td>"
            f"<td>{esc(strategy.get('tensor_parallel', 0))}</td>"
            f"<td>{esc(strategy.get('pipeline_parallel', 0))}</td>"
            f"<td>{esc(strategy.get('data_parallel', 0))}</td>"
            f"<td>{esc(row['bottleneck'])}</td>"
            f"<td>{esc(row['estimated_collective_ms'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="7">No distributed topology recommendations generated.</td></tr>'


def render_distributed_topology_candidates(report: dict[str, Any] | None = None) -> str:
    rows = []
    for plan in (report or {}).get("plans", []):
        for candidate in plan.get("candidates", [])[:5]:
            rows.append(
                "<tr>"
                f"<td>{esc(plan['workload']['id'])}</td>"
                f"<td>{esc(candidate['topology_id'])}</td>"
                f"<td>{esc(candidate['status'])}</td>"
                f"<td>{esc(candidate['memory_gb_per_gpu'])}</td>"
                f"<td>{esc(candidate['estimated_collective_ms'])}</td>"
                f"<td>{esc(candidate['bottleneck'])}</td>"
                "</tr>"
            )
    return "\n".join(rows) if rows else '<tr><td colspan="6">No distributed topology candidates generated.</td></tr>'


def build_distributed_topology_page(report: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE Distributed Topology</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated multi-GPU planning lab</div>
  <h1>GPUMODE distributed topology.</h1>
  <p class="dek">Topology and parallelism plan for tensor parallel, pipeline parallel,
  data parallel, memory capacity, and collective latency tradeoffs.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("topology_count", 0))}</h2><p>topologies</p></div>
    <div class="card"><h2>{esc((report or {}).get("workload_count", 0))}</h2><p>workloads</p></div>
    <div class="card"><h2>{esc((report or {}).get("candidate_count", 0))}</h2><p>viable candidates</p></div>
    <div class="card"><h2><a href="../distributed-topology/reports/distributed-topology-plan.md">Report</a></h2><p>Markdown topology plan</p></div>
  </div>

  <section>
    <h2>Recommendations</h2>
    <table><tr><th>workload</th><th>topology</th><th>tensor</th><th>pipeline</th><th>data</th><th>bottleneck</th><th>collective ms</th></tr>{render_distributed_topology_recommendations(report)}</table>
  </section>

  <section>
    <h2>Candidate Plans</h2>
    <table><tr><th>workload</th><th>topology</th><th>status</th><th>memory GB/GPU</th><th>collective ms</th><th>bottleneck</th></tr>{render_distributed_topology_candidates(report)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "distributed-topology.html").write_text(body, encoding="utf-8")


def render_distributed_collectives_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for row in (report or {}).get("scenarios", []):
        rows.append(
            "<tr>"
            f"<td>{esc(row['scenario_id'])}</td>"
            f"<td>{esc(row['collective'])}</td>"
            f"<td>{esc(row['algorithm'])}</td>"
            f"<td>{esc(row['ranks'])}</td>"
            f"<td>{esc(row['backend'])}</td>"
            f"<td>{esc(row['exposed_comm_ms'])}</td>"
            f"<td>{esc(row['bandwidth_efficiency'])}</td>"
            f"<td>{esc(row['overlap_gain'])}</td>"
            f"<td>{esc(row['status'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="9">No distributed collective scenarios generated.</td></tr>'


def render_distributed_collectives_benchmark_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for row in (report or {}).get("benchmarks", []):
        rows.append(
            "<tr>"
            f"<td>{esc(row.get('collective', ''))}</td>"
            f"<td>{esc(row.get('status', ''))}</td>"
            f"<td>{esc(row.get('bytes_per_rank', ''))}</td>"
            f"<td>{esc(row.get('mean_ms', ''))}</td>"
            f"<td>{esc(row.get('estimated_bus_gbps', ''))}</td>"
            f"<td>{esc(row.get('reason', ''))}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="6">No measured benchmark rows on this host.</td></tr>'


def build_distributed_collectives_page(report: dict[str, Any] | None = None) -> None:
    benchmark = load_json(DISTRIBUTED_COLLECTIVES_BENCHMARK) if DISTRIBUTED_COLLECTIVES_BENCHMARK.exists() else None
    body = f"""<meta charset="utf-8">
<title>GPUMODE Distributed Collectives</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated collective communication lab</div>
  <h1>GPUMODE distributed collectives.</h1>
  <p class="dek">Algorithm-level all-reduce, reduce-scatter, all-gather, all-to-all,
  and broadcast planning across NCCL, RCCL, NVSHMEM, topology bandwidth, latency,
  communication overlap, and GPU-host promotion requirements.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("scenario_count", 0))}</h2><p>scenarios</p></div>
    <div class="card"><h2>{esc((report or {}).get("passed_scenarios", 0))}</h2><p>passing scenarios</p></div>
    <div class="card"><h2>{esc((report or {}).get("collective_count", 0))}</h2><p>collective families</p></div>
    <div class="card"><h2>{esc((benchmark or {}).get("status", "not-run"))}</h2><p>local benchmark artifact</p></div>
    <div class="card"><h2><a href="../distributed-collectives/reports/distributed-collectives-report.md">Report</a></h2><p>Markdown collectives report</p></div>
  </div>

  <section>
    <h2>Collective Scenarios</h2>
    <table><tr><th>scenario</th><th>collective</th><th>algorithm</th><th>ranks</th><th>backend</th><th>exposed ms</th><th>efficiency</th><th>overlap gain</th><th>status</th></tr>{render_distributed_collectives_rows(report)}</table>
  </section>

  <section>
    <h2>Benchmark Artifact</h2>
    <p class="small">Run on a GPU host with: <code>torchrun --nproc_per_node=2 scripts/run_distributed_collectives_benchmark.py</code></p>
    <table><tr><th>collective</th><th>status</th><th>bytes/rank</th><th>mean ms</th><th>bus GB/s</th><th>reason</th></tr>{render_distributed_collectives_benchmark_rows(benchmark)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "distributed-collectives.html").write_text(body, encoding="utf-8")


def render_distributed_training_optimizer_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for row in (report or {}).get("scenarios", []):
        rows.append(
            "<tr>"
            f"<td>{esc(row['scenario_id'])}</td>"
            f"<td>{esc(row['strategy'])}</td>"
            f"<td>{esc(row['ranks'])}</td>"
            f"<td>{esc(row['memory_gb_per_gpu'])}</td>"
            f"<td>{esc(row['exposed_comm_ms'])}</td>"
            f"<td>{esc(row['pipeline_bubble_ms'])}</td>"
            f"<td>{esc(row['optimizer_state_savings'])}</td>"
            f"<td>{esc(row['tokens_per_second'])}</td>"
            f"<td>{esc(row['status'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="9">No distributed training optimizer scenarios generated.</td></tr>'


def build_distributed_training_optimizer_page(report: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE Distributed Training Optimizer</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated distributed training lab</div>
  <h1>GPUMODE distributed training optimizer.</h1>
  <p class="dek">DDP, ZeRO, FSDP, tensor/pipeline parallelism, activation checkpointing,
  optimizer-state sharding, reduce-scatter/all-gather exposure, pipeline bubbles,
  precision choices, and GPU-host promotion evidence.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("scenario_count", 0))}</h2><p>scenarios</p></div>
    <div class="card"><h2>{esc((report or {}).get("passed_scenarios", 0))}</h2><p>passing scenarios</p></div>
    <div class="card"><h2>{esc((report or {}).get("strategy_count", 0))}</h2><p>optimizer strategies</p></div>
    <div class="card"><h2><a href="../distributed-training-optimizer/reports/distributed-training-optimizer-report.md">Report</a></h2><p>Markdown optimizer report</p></div>
  </div>

  <section>
    <h2>Training Plans</h2>
    <table><tr><th>scenario</th><th>strategy</th><th>ranks</th><th>memory GB/GPU</th><th>exposed comm ms</th><th>bubble ms</th><th>optimizer savings</th><th>tokens/s</th><th>status</th></tr>{render_distributed_training_optimizer_rows(report)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "distributed-training-optimizer.html").write_text(body, encoding="utf-8")


def render_moe_routing_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for row in (report or {}).get("scenarios", []):
        rows.append(
            "<tr>"
            f"<td>{esc(row['scenario_id'])}</td>"
            f"<td>{esc(row['status'])}</td>"
            f"<td>{esc(row['drop_rate'])}</td>"
            f"<td>{esc(row['fairness_index'])}</td>"
            f"<td>{esc(row['load_imbalance'])}</td>"
            f"<td>{esc(row['all_to_all_payload_gb'])}</td>"
            f"<td>{esc(row['estimated_all_to_all_ms'])}</td>"
            f"<td>{esc(row['bottleneck'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="8">No MoE routing scenarios generated.</td></tr>'


def build_moe_routing_page(report: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE MoE Routing All-to-All</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated MoE distributed lab</div>
  <h1>GPUMODE MoE routing and all-to-all.</h1>
  <p class="dek">Top-k expert routing model for load balance, capacity drops,
  all-to-all payload, fabric latency, bottleneck classification, and GPU-host promotion.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("scenario_count", 0))}</h2><p>scenarios</p></div>
    <div class="card"><h2>{esc((report or {}).get("passed_scenarios", 0))}</h2><p>healthy scenarios</p></div>
    <div class="card"><h2>{esc((report or {}).get("tuning_required_scenarios", 0))}</h2><p>tuning-required scenarios</p></div>
    <div class="card"><h2><a href="../moe-routing-all-to-all/reports/moe-routing-report.md">Report</a></h2><p>Markdown MoE report</p></div>
  </div>

  <section>
    <h2>Routing Scenarios</h2>
    <table><tr><th>scenario</th><th>status</th><th>drop rate</th><th>fairness</th><th>imbalance</th><th>payload GB</th><th>all-to-all ms</th><th>bottleneck</th></tr>{render_moe_routing_rows(report)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "moe-routing-all-to-all.html").write_text(body, encoding="utf-8")


def render_hardware_capacity_recommendations(report: dict[str, Any] | None = None) -> str:
    rows = []
    for row in (report or {}).get("recommendations", []):
        rows.append(
            "<tr>"
            f"<td>{esc(row['workload_id'])}</td>"
            f"<td>{esc(row['recommended_profile'])}</td>"
            f"<td>{esc(row['bottleneck'])}</td>"
            f"<td>{esc(row['memory_required_gb'])}</td>"
            f"<td>{esc(row['memory_headroom_gb'])}</td>"
            f"<td>{esc(row['estimated_power_w'])}</td>"
            f"<td>{esc(row['estimated_cost_per_hour'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="7">No hardware capacity recommendations generated.</td></tr>'


def render_hardware_capacity_evaluations(report: dict[str, Any] | None = None) -> str:
    rows = []
    for row in (report or {}).get("evaluations", [])[:25]:
        rows.append(
            "<tr>"
            f"<td>{esc(row['workload_id'])}</td>"
            f"<td>{esc(row['profile_id'])}</td>"
            f"<td>{esc(row['status'])}</td>"
            f"<td>{esc(row['memory_required_gb'])}</td>"
            f"<td>{esc(row['memory_headroom_gb'])}</td>"
            f"<td>{esc(row['bottleneck'])}</td>"
            f"<td>{esc(row['throughput_score'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="7">No hardware capacity evaluations generated.</td></tr>'


def build_hardware_capacity_page(report: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE Hardware Capacity</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated hardware planning lab</div>
  <h1>GPUMODE hardware capacity.</h1>
  <p class="dek">Workload-to-GPU sizing for model memory, KV-cache pressure,
  memory headroom, bottleneck class, power, cost, and measured GPU-host validation commands.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("profile_count", 0))}</h2><p>hardware profiles</p></div>
    <div class="card"><h2>{esc((report or {}).get("workload_count", 0))}</h2><p>workloads sized</p></div>
    <div class="card"><h2>{esc((report or {}).get("recommendation_count", 0))}</h2><p>recommendations</p></div>
    <div class="card"><h2><a href="../hardware-capacity-planning/reports/hardware-capacity-plan.md">Report</a></h2><p>Markdown capacity plan</p></div>
  </div>

  <section>
    <h2>Recommendations</h2>
    <table><tr><th>workload</th><th>profile</th><th>bottleneck</th><th>memory GB</th><th>memory headroom</th><th>power W</th><th>cost/hr</th></tr>{render_hardware_capacity_recommendations(report)}</table>
  </section>

  <section>
    <h2>Evaluation Matrix</h2>
    <table><tr><th>workload</th><th>profile</th><th>status</th><th>memory GB</th><th>headroom</th><th>bottleneck</th><th>score</th></tr>{render_hardware_capacity_evaluations(report)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "hardware-capacity.html").write_text(body, encoding="utf-8")


def render_quantization_format_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for row in (report or {}).get("formats", []):
        rows.append(
            "<tr>"
            f"<td>{esc(row['format_id'])}</td>"
            f"<td>{esc(row['bits'])}</td>"
            f"<td>{esc(row['compression_vs_fp32'])}</td>"
            f"<td>{esc(row['max_abs_error'])}</td>"
            f"<td>{esc(row['cosine_similarity'])}</td>"
            f"<td>{esc(row['dequant_tax_ratio'])}</td>"
            f"<td>{esc(row['fused_speedup_proxy'])}</td>"
            f"<td>{esc(row['serving_fit'])}</td>"
            f"<td>{esc(row['status'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="9">No quantization format sweep generated.</td></tr>'


def render_quantization_recommendation_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for row in (report or {}).get("recommendations", []):
        facts = row.get("facts", {})
        rows.append(
            "<tr>"
            f"<td>{esc(row['scenario'])}</td>"
            f"<td>{esc(row['recommended_format'])}</td>"
            f"<td>{esc(facts.get('compression_vs_fp32', ''))}</td>"
            f"<td>{esc(facts.get('cosine_similarity', ''))}</td>"
            f"<td>{esc(row['why'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="5">No quantization recommendations generated.</td></tr>'


def build_quantization_page(report: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE Quantization Memory Formats</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated quantization lab</div>
  <h1>GPUMODE quantization memory formats.</h1>
  <p class="dek">Format sweep for BF16, FP8-style, INT8, INT4, and NF4 weight-only
  paths with compression, accuracy drift, dequant tax, serving fit, and GPU promotion commands.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("format_count", 0))}</h2><p>formats swept</p></div>
    <div class="card"><h2>{esc((report or {}).get("passed_format_count", 0))}</h2><p>accuracy-passing formats</p></div>
    <div class="card"><h2>{esc((report or {}).get("calibration_needed_count", 0))}</h2><p>need calibration</p></div>
    <div class="card"><h2><a href="../quantization-memory-formats/reports/quantization-report.md">Report</a></h2><p>Markdown quantization report</p></div>
  </div>

  <section>
    <h2>Format Sweep</h2>
    <table><tr><th>format</th><th>bits</th><th>compression</th><th>max error</th><th>cosine</th><th>dequant tax</th><th>speedup proxy</th><th>serving fit</th><th>status</th></tr>{render_quantization_format_rows(report)}</table>
  </section>

  <section>
    <h2>Recommendations</h2>
    <table><tr><th>scenario</th><th>format</th><th>compression</th><th>cosine</th><th>why</th></tr>{render_quantization_recommendation_rows(report)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "quantization-memory-formats.html").write_text(body, encoding="utf-8")


def render_numerical_reproducibility_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for row in (report or {}).get("scenarios", []):
        rows.append(
            "<tr>"
            f"<td>{esc(row['mode'])}</td>"
            f"<td>{esc(row['category'])}</td>"
            f"<td>{esc(row['status'])}</td>"
            f"<td>{esc(row['tolerance'])}</td>"
            f"<td>{esc(row['repeat_max_abs_drift'])}</td>"
            f"<td>{esc(row['reference_max_abs_error'])}</td>"
            f"<td>{esc(row['cosine_similarity'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="7">No numerical reproducibility scenarios generated.</td></tr>'


def build_numerical_reproducibility_page(report: dict[str, Any] | None = None) -> None:
    reduction = (report or {}).get("reduction_order", {})
    body = f"""<meta charset="utf-8">
<title>GPUMODE Numerical Reproducibility</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated numerics lab</div>
  <h1>GPUMODE numerical reproducibility.</h1>
  <p class="dek">Precision-mode tolerance and reduction order checks for deterministic
  seeds, fast math drift, low-precision modes, and GPU-host promotion.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("scenario_count", 0))}</h2><p>precision scenarios</p></div>
    <div class="card"><h2>{esc((report or {}).get("passed_scenarios", 0))}</h2><p>passed scenarios</p></div>
    <div class="card"><h2>{esc((report or {}).get("tolerance_review_scenarios", 0))}</h2><p>tolerance reviews</p></div>
    <div class="card"><h2><a href="../numerical-reproducibility/reports/numerical-reproducibility-report.md">Report</a></h2><p>Markdown numerics report</p></div>
  </div>

  <section>
    <h2>Precision Modes</h2>
    <table><tr><th>mode</th><th>category</th><th>status</th><th>tolerance</th><th>repeat drift</th><th>reference error</th><th>cosine</th></tr>{render_numerical_reproducibility_rows(report)}</table>
  </section>

  <section>
    <h2>Reduction Order</h2>
    <table><tr><th>case</th><th>status</th><th>max order delta</th><th>tolerance</th></tr><tr><td>{esc(reduction.get("case", ""))}</td><td>{esc(reduction.get("status", ""))}</td><td>{esc(reduction.get("max_order_delta", ""))}</td><td>{esc(reduction.get("tolerance", ""))}</td></tr></table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "numerical-reproducibility.html").write_text(body, encoding="utf-8")


def render_cuda_graphs_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for row in (report or {}).get("scenarios", []):
        rows.append(
            "<tr>"
            f"<td>{esc(row['scenario_id'])}</td>"
            f"<td>{esc(row['status'])}</td>"
            f"<td>{esc(row['eager_p95_ms'])}</td>"
            f"<td>{esc(row['graph_p95_ms'])}</td>"
            f"<td>{esc(row['p95_latency_reduction'])}</td>"
            f"<td>{esc(row['latency_jitter_reduction'])}</td>"
            f"<td>{esc(row['fallback_strategy'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="7">No CUDA Graphs latency scenarios generated.</td></tr>'


def build_cuda_graphs_latency_page(report: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE CUDA Graphs Latency</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated launch-overhead lab</div>
  <h1>GPUMODE CUDA Graphs latency.</h1>
  <p class="dek">Latency-stabilization model for CUDA Graph capture eligibility,
  warmup, static-shape constraints, p95 decode latency reduction, and fallback
  strategies for dynamic serving paths.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("scenario_count", 0))}</h2><p>scenarios</p></div>
    <div class="card"><h2>{esc((report or {}).get("capture_ready_count", 0))}</h2><p>capture-ready</p></div>
    <div class="card"><h2>{esc((report or {}).get("fallback_required_count", 0))}</h2><p>fallback-required</p></div>
    <div class="card"><h2><a href="../cuda-graphs-latency/reports/cuda-graphs-latency-report.md">Report</a></h2><p>Markdown CUDA Graphs report</p></div>
  </div>

  <section>
    <h2>Latency Scenarios</h2>
    <table><tr><th>scenario</th><th>status</th><th>eager p95 ms</th><th>graph p95 ms</th><th>p95 reduction</th><th>jitter reduction</th><th>fallback</th></tr>{render_cuda_graphs_rows(report)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "cuda-graphs-latency.html").write_text(body, encoding="utf-8")


def render_multi_tenant_plan_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for plan in (report or {}).get("plans", []):
        rows.append(
            "<tr>"
            f"<td>{esc(plan['policy_id'])}</td>"
            f"<td>{esc(plan['accepted_count'])}</td>"
            f"<td>{esc(plan['rejected_count'])}</td>"
            f"<td>{esc(plan['fairness_index'])}</td>"
            f"<td>{esc(plan['estimated_utilization'])}</td>"
            f"<td>{esc(plan['policy_score'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="6">No multi-tenant scheduling plans generated.</td></tr>'


def render_multi_tenant_placement_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    recommended = (report or {}).get("recommended_policy")
    best = next((plan for plan in (report or {}).get("plans", []) if plan.get("policy_id") == recommended), {})
    for row in best.get("placements", []):
        rows.append(
            "<tr>"
            f"<td>{esc(row['tenant_id'])}</td>"
            f"<td>{esc(row['partition_id'])}</td>"
            f"<td>{esc(row['status'])}</td>"
            f"<td>{esc(row['isolation'])}</td>"
            f"<td>{esc(row['slo_status'])}</td>"
            f"<td>{esc(row['memory_headroom_gb'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="6">No recommended placements generated.</td></tr>'


def build_multi_tenant_scheduling_page(report: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE Multi-Tenant Scheduling</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated GPU cluster scheduling lab</div>
  <h1>GPUMODE multi-tenant scheduling.</h1>
  <p class="dek">MIG/MPS/Kubernetes-style placement model for AI serving, batch,
  CI, and training tenants with memory headroom, isolation, fairness, and SLO evidence.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("policy_count", 0))}</h2><p>policies compared</p></div>
    <div class="card"><h2>{esc((report or {}).get("tenant_count", 0))}</h2><p>tenants modeled</p></div>
    <div class="card"><h2>{esc((report or {}).get("accepted_count", 0))}</h2><p>accepted in recommended plan</p></div>
    <div class="card"><h2><a href="../multi-tenant-gpu-scheduling/reports/multi-tenant-scheduling-report.md">Report</a></h2><p>Markdown scheduling report</p></div>
  </div>

  <section>
    <h2>Policy Comparison</h2>
    <table><tr><th>policy</th><th>accepted</th><th>queued</th><th>fairness</th><th>utilization</th><th>score</th></tr>{render_multi_tenant_plan_rows(report)}</table>
  </section>

  <section>
    <h2>Recommended Placements</h2>
    <table><tr><th>tenant</th><th>partition</th><th>status</th><th>isolation</th><th>SLO</th><th>memory headroom GB</th></tr>{render_multi_tenant_placement_rows(report)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "multi-tenant-scheduling.html").write_text(body, encoding="utf-8")


def render_custom_op_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for case in (report or {}).get("cases", []):
        shape = case.get("shape", {})
        rows.append(
            "<tr>"
            f"<td>{esc(case['id'])}</td>"
            f"<td>{esc(case['dtype'])}</td>"
            f"<td>{esc(shape.get('batch', 0))}x{esc(shape.get('hidden', 0))}</td>"
            f"<td>{esc(case['status'])}</td>"
            f"<td>{esc(case['max_abs_error'])}</td>"
            f"<td>{esc(case['grad_x_max_abs_error'])}</td>"
            f"<td>{esc(case['seconds']['fused']['median'])}</td>"
            f"<td>{esc(case['elements_per_second'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="8">No custom-op report generated.</td></tr>'


def build_custom_ops_page(report: dict[str, Any] | None = None) -> None:
    readiness = (report or {}).get("accelerator_readiness", {})
    body = f"""<meta charset="utf-8">
<title>GPUMODE PyTorch Custom Op</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated custom operator lab</div>
  <h1>GPUMODE PyTorch custom op.</h1>
  <p class="dek">Forward/backward correctness, fuzz shape coverage, CPU timing,
  and source-ready CUDA extension code for `fused_bias_gelu_residual`.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("operator", ""))}</h2><p>operator</p></div>
    <div class="card"><h2>{esc((report or {}).get("passed", 0))} / {esc((report or {}).get("case_count", 0))}</h2><p>cases passed</p></div>
    <div class="card"><h2>{esc(readiness.get("compiled_extension_status", "unknown"))}</h2><p>compiled extension status</p></div>
    <div class="card"><h2><a href="../custom-ops/reports/custom-op-report.md">Report</a></h2><p>Markdown report</p></div>
  </div>

  <section>
    <h2>Correctness And Timing Cases</h2>
    <table><tr><th>case</th><th>dtype</th><th>shape</th><th>status</th><th>max abs error</th><th>grad x error</th><th>fused median s</th><th>elements/s</th></tr>{render_custom_op_rows(report)}</table>
  </section>

  <section>
    <h2>Source Files</h2>
    <table><tr><th>kind</th><th>path</th></tr>
      <tr><td>Python op</td><td>custom-ops/custom_ops/fused_bias_gelu_residual.py</td></tr>
      <tr><td>benchmark</td><td>custom-ops/custom_ops/bench.py</td></tr>
      <tr><td>C++ binding</td><td>custom-ops/csrc/fused_bias_gelu_residual.cpp</td></tr>
      <tr><td>CUDA kernel</td><td>custom-ops/csrc/fused_bias_gelu_residual_kernel.cu</td></tr>
    </table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "custom-ops.html").write_text(body, encoding="utf-8")


def render_autotune_rows(database: dict[str, Any] | None = None) -> str:
    rows = []
    for record in (database or {}).get("records", []):
        selected = record.get("selected", {})
        config = selected.get("config", {})
        rows.append(
            "<tr>"
            f"<td>{esc(record['id'])}</td>"
            f"<td>{esc(record['family'])}</td>"
            f"<td>{esc(record['shape_class'])}</td>"
            f"<td>{esc(config.get('id', ''))}</td>"
            f"<td>{esc(record.get('selection_status', 'unknown'))}</td>"
            f"<td>{esc(record.get('measured_seconds', 0))}</td>"
            f"<td>{esc(selected.get('estimated_seconds', 0))}</td>"
            f"<td>{esc(selected.get('estimated_speedup_vs_measured', 0))}</td>"
            f"<td>{esc(', '.join(record.get('promotion_targets', [])))}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="9">No autotune records generated.</td></tr>'


def build_autotune_db_page(database: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE Autotuning Database</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated autotuning layer</div>
  <h1>GPUMODE autotuning database.</h1>
  <p class="dek">Benchmark-derived tuning records for selecting starting configs
  by operator family and shape class before CUDA, Triton, or extension promotion.</p>
  <div class="grid">
    <div class="card"><h2>{esc((database or {}).get("record_count", 0))}</h2><p>tuning records</p></div>
    <div class="card"><h2>{esc(len((database or {}).get("families", [])))}</h2><p>operator families</p></div>
    <div class="card"><h2><a href="../autotune-db/reports/autotune-report.md">Report</a></h2><p>Markdown selector report</p></div>
    <div class="card"><h2><a href="../autotune-db/autotune-db.json">JSON</a></h2><p>machine-readable database</p></div>
  </div>

  <section>
    <h2>Selected Configs</h2>
    <table><tr><th>record</th><th>family</th><th>shape</th><th>selected config</th><th>status</th><th>measured s</th><th>estimated s</th><th>modeled speedup</th><th>targets</th></tr>{render_autotune_rows(database)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "autotune-db.html").write_text(body, encoding="utf-8")


def render_model_integration_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for case in (report or {}).get("cases", []):
        shape = case.get("shape", {})
        rows.append(
            "<tr>"
            f"<td>{esc(case['id'])}</td>"
            f"<td>{esc(shape.get('batch', 0))}x{esc(shape.get('seq', 0))}x{esc(shape.get('hidden', 0))}</td>"
            f"<td>{esc(case['status'])}</td>"
            f"<td>{esc(case['max_abs_error'])}</td>"
            f"<td>{esc(case['grad_max_abs_error'])}</td>"
            f"<td>{esc(case['seconds']['fused']['median'])}</td>"
            f"<td>{esc(case['tokens_per_second'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="7">No model integration report generated.</td></tr>'


def build_model_integration_page(report: dict[str, Any] | None = None) -> None:
    selected = (report or {}).get("selected_tuning_summary", {})
    selected_rows = "".join(
        "<tr>"
        f"<td>{esc(family)}</td>"
        f"<td>{esc(row.get('record_id', 'missing'))}</td>"
        f"<td>{esc(row.get('config_id', ''))}</td>"
        f"<td>{esc(row.get('estimated_speedup_vs_measured', ''))}</td>"
        "</tr>"
        for family, row in selected.items()
    ) or '<tr><td colspan="4">No selected tuning records generated.</td></tr>'
    body = f"""<meta charset="utf-8">
<title>GPUMODE Model Integration</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated model integration lab</div>
  <h1>GPUMODE model integration.</h1>
  <p class="dek">A tiny-causal-transformer-block benchmark that connects layernorm,
  QKV matmul, causal attention, custom-op fusion, and autotune record selection.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("model", ""))}</h2><p>model path</p></div>
    <div class="card"><h2>{esc((report or {}).get("passed", 0))} / {esc((report or {}).get("case_count", 0))}</h2><p>cases passed</p></div>
    <div class="card"><h2>{esc((report or {}).get("uses_custom_op", ""))}</h2><p>custom op</p></div>
    <div class="card"><h2><a href="../model-integration/reports/tiny-transformer-report.md">Report</a></h2><p>Markdown report</p></div>
  </div>

  <section>
    <h2>Model Cases</h2>
    <table><tr><th>case</th><th>shape</th><th>status</th><th>max abs error</th><th>grad error</th><th>fused median s</th><th>tokens/s</th></tr>{render_model_integration_rows(report)}</table>
  </section>

  <section>
    <h2>Selected Autotune Records</h2>
    <table><tr><th>family</th><th>record</th><th>config</th><th>speedup</th></tr>{selected_rows}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "model-integration.html").write_text(body, encoding="utf-8")


def render_regression_rows(ledger: dict[str, Any] | None = None) -> str:
    rows = []
    for row in (ledger or {}).get("metrics", []):
        rows.append(
            "<tr>"
            f"<td>{esc(row['layer'])}</td>"
            f"<td>{esc(row['id'])}</td>"
            f"<td>{esc(row['metric'])}</td>"
            f"<td>{esc(row['value'])}</td>"
            f"<td>{esc(row['status'])}</td>"
            f"<td>{esc(row['source'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="6">No regression metrics generated.</td></tr>'


def build_regression_ledger_page(ledger: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE Regression Ledger</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated regression layer</div>
  <h1>GPUMODE regression ledger.</h1>
  <p class="dek">Stable metrics collected from kernel benchmarks, custom ops,
  autotune records, model integration, and serving traces.</p>
  <div class="grid">
    <div class="card"><h2>{esc((ledger or {}).get("metric_count", 0))}</h2><p>metrics</p></div>
    <div class="card"><h2>{esc((ledger or {}).get("passed", 0))}</h2><p>passed</p></div>
    <div class="card"><h2>{esc((ledger or {}).get("failed", 0))}</h2><p>failed</p></div>
    <div class="card"><h2><a href="../regression-ledger/reports/regression-ledger.md">Report</a></h2><p>Markdown ledger</p></div>
  </div>

  <section>
    <h2>Metrics</h2>
    <table><tr><th>layer</th><th>id</th><th>metric</th><th>value</th><th>status</th><th>source</th></tr>{render_regression_rows(ledger)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "regression-ledger.html").write_text(body, encoding="utf-8")


def render_gpu_promotion_rows(manifest: dict[str, Any] | None = None) -> str:
    rows = []
    for step in (manifest or {}).get("steps", []):
        rows.append(
            "<tr>"
            f"<td>{esc(step['id'])}</td>"
            f"<td>{esc(step['status'])}</td>"
            f"<td>{esc(', '.join(step.get('required_capabilities', [])))}</td>"
            f"<td>{esc(', '.join(step.get('missing_capabilities', [])) or 'none')}</td>"
            f"<td>{esc(step['commands'][0] if step.get('commands') else '')}</td>"
            f"<td>{esc(step['validation'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="6">No GPU promotion steps generated.</td></tr>'


def build_gpu_promotion_page(manifest: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE GPU Promotion</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated GPU-host runbook</div>
  <h1>GPUMODE GPU promotion.</h1>
  <p class="dek">Ordered promotion manifest for moving local CPU/source-ready
  evidence onto CUDA, Triton, ROCm/HIP, profiler, serving, and multi-GPU hosts.</p>
  <div class="grid">
    <div class="card"><h2>{esc((manifest or {}).get("step_count", 0))}</h2><p>promotion steps</p></div>
    <div class="card"><h2>{esc((manifest or {}).get("ready_on_this_host", 0))}</h2><p>ready here</p></div>
    <div class="card"><h2>{esc((manifest or {}).get("ready_on_gpu_host", 0))}</h2><p>GPU-host steps</p></div>
    <div class="card"><h2><a href="../gpu-promotion/reports/gpu-host-promotion-runbook.md">Runbook</a></h2><p>Markdown runbook</p></div>
  </div>

  <section>
    <h2>Promotion Steps</h2>
    <table><tr><th>step</th><th>status</th><th>required</th><th>missing locally</th><th>first command</th><th>validation</th></tr>{render_gpu_promotion_rows(manifest)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "gpu-promotion.html").write_text(body, encoding="utf-8")


def render_gpu_promotion_suite_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for row in (report or {}).get("commands", []):
        rows.append(
            "<tr>"
            f"<td>{esc(row['order'])}</td>"
            f"<td>{esc(row['step_id'])}</td>"
            f"<td>{esc(row['status'])}</td>"
            f"<td>{esc(row['command'])}</td>"
            f"<td>{esc(', '.join(row.get('expected_evidence', [])))}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="5">No GPU promotion suite commands generated.</td></tr>'


def build_gpu_promotion_suite_page(report: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE GPU Promotion Suite</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Ordered GPU-host command plan</div>
  <h1>GPUMODE GPU promotion suite.</h1>
  <p class="dek">Dry-run and execute-mode command plan generated from the GPU
  promotion manifest, with expected evidence and validation text for each command.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("command_count", 0))}</h2><p>commands</p></div>
    <div class="card"><h2>{esc((report or {}).get("step_count", 0))}</h2><p>promotion steps</p></div>
    <div class="card"><h2>{esc((report or {}).get("status", "missing"))}</h2><p>suite status</p></div>
    <div class="card"><h2><a href="../gpu-promotion/reports/suite-run-report.md">Report</a></h2><p>Markdown suite plan</p></div>
  </div>

  <section>
    <h2>Command Plan</h2>
    <table><tr><th>#</th><th>step</th><th>status</th><th>command</th><th>evidence</th></tr>{render_gpu_promotion_suite_rows(report)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "gpu-promotion-suite.html").write_text(body, encoding="utf-8")


def render_gpu_run_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for row in (report or {}).get("rows", []):
        metric_keys = ", ".join(sorted(row.get("metrics", {})))
        rows.append(
            "<tr>"
            f"<td>{esc(row['run_id'])}</td>"
            f"<td>{esc(row['host'])}</td>"
            f"<td>{esc(row['accelerator'])}</td>"
            f"<td>{esc(row['step_id'])}</td>"
            f"<td>{esc(row['status'])}</td>"
            f"<td>{esc(metric_keys)}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="6">No GPU run imports generated.</td></tr>'


def build_gpu_runs_page(report: dict[str, Any] | None = None) -> None:
    coverage = (report or {}).get("coverage", {})
    body = f"""<meta charset="utf-8">
<title>GPUMODE GPU Run Imports</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Accelerator host evidence import</div>
  <h1>GPUMODE GPU run imports.</h1>
  <p class="dek">Imported GPU-host validation rows linked back to the promotion
  manifest, including CUDA, Triton, ROCm/HIP, profiler, serving, distributed, and regression evidence.</p>
  <div class="grid">
    <div class="card"><h2>{esc(coverage.get("run_count", 0))}</h2><p>imported runs</p></div>
    <div class="card"><h2>{esc(coverage.get("vendor_count", 0))}</h2><p>GPU vendors</p></div>
    <div class="card"><h2>{esc(coverage.get("promotion_step_count", 0))}</h2><p>promotion steps</p></div>
    <div class="card"><h2><a href="../gpu-runs/reports/gpu-run-report.md">Report</a></h2><p>Markdown imports</p></div>
  </div>

  <section>
    <h2>Imported Steps</h2>
    <table><tr><th>run</th><th>host</th><th>accelerator</th><th>step</th><th>status</th><th>metrics</th></tr>{render_gpu_run_rows(report)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "gpu-runs.html").write_text(body, encoding="utf-8")


def render_gpu_import_lint_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for row in (report or {}).get("files", []):
        rows.append(
            "<tr>"
            f"<td>{esc(row['path'])}</td>"
            f"<td>{esc(row['kind'])}</td>"
            f"<td>{esc(row['provenance_kind'])}</td>"
            f"<td>{esc(row['measured'])}</td>"
            f"<td>{esc(row['step_count'])}</td>"
            f"<td>{esc(row['error_count'])}</td>"
            f"<td>{esc(row['warning_count'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="7">No GPU import lint report generated.</td></tr>'


def build_gpu_import_lint_page(report: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE GPU Import Lint</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Run import schema gate</div>
  <h1>GPUMODE GPU import lint.</h1>
  <p class="dek">Schema and provenance linting for sample fixtures and collected GPU-run import files.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("status", "missing"))}</h2><p>lint status</p></div>
    <div class="card"><h2>{esc((report or {}).get("file_count", 0))}</h2><p>files checked</p></div>
    <div class="card"><h2>{esc((report or {}).get("error_count", 0))}</h2><p>errors</p></div>
    <div class="card"><h2><a href="../gpu-runs/reports/import-lint-report.md">Report</a></h2><p>Markdown lint</p></div>
  </div>

  <section>
    <h2>Files</h2>
    <table><tr><th>file</th><th>kind</th><th>provenance</th><th>measured</th><th>steps</th><th>errors</th><th>warnings</th></tr>{render_gpu_import_lint_rows(report)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "gpu-import-lint.html").write_text(body, encoding="utf-8")


def render_gpu_provenance_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for run in (report or {}).get("runs", []):
        rows.append(
            "<tr>"
            f"<td>{esc(run['run_id'])}</td>"
            f"<td>{esc(run['provenance_kind'])}</td>"
            f"<td>{esc(run['measured'])}</td>"
            f"<td>{esc(run['vendor'])}</td>"
            f"<td>{esc(run['accelerator'])}</td>"
            f"<td>{esc(run['row_count'])}</td>"
            f"<td>{esc(run['passed_steps'])}</td>"
            f"<td>{esc(run['skipped_steps'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="8">No GPU provenance report generated.</td></tr>'


def build_gpu_provenance_page(report: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE GPU Evidence Provenance</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Evidence provenance guardrail</div>
  <h1>GPUMODE GPU evidence provenance.</h1>
  <p class="dek">Separates sample fixtures, local host-collected smoke runs, and true measured accelerator-host evidence.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("real_gpu_evidence_status", "missing"))}</h2><p>real GPU evidence</p></div>
    <div class="card"><h2>{esc((report or {}).get("measured_run_count", 0))}</h2><p>measured GPU runs</p></div>
    <div class="card"><h2>{esc((report or {}).get("sample_run_count", 0))}</h2><p>sample fixture runs</p></div>
    <div class="card"><h2><a href="../gpu-provenance/reports/gpu-provenance-report.md">Report</a></h2><p>Markdown provenance</p></div>
  </div>

  <section>
    <h2>Runs</h2>
    <table><tr><th>run</th><th>provenance</th><th>measured</th><th>vendor</th><th>accelerator</th><th>rows</th><th>passed</th><th>skipped</th></tr>{render_gpu_provenance_rows(report)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "gpu-provenance.html").write_text(body, encoding="utf-8")


def render_gpu_measurement_queue_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for task in (report or {}).get("tasks", []):
        rows.append(
            "<tr>"
            f"<td>{esc(task['step_id'])}</td>"
            f"<td>{esc(task['host_class'])}</td>"
            f"<td>{esc(task['measurement_status'])}</td>"
            f"<td>{esc(task.get('accepted_measured_rows', 0))}/{esc(task.get('real_measured_rows', 0))}</td>"
            f"<td>{esc(task['command_count'])}</td>"
            f"<td>{esc(', '.join(task.get('required_metrics', [])))}</td>"
            f"<td>{esc('; '.join(task.get('acceptance_thresholds', [])))}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="7">No GPU measurement queue generated.</td></tr>'


def build_gpu_measurement_queue_page(report: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE GPU Measurement Queue</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">GPU-host measurement contracts</div>
  <h1>GPUMODE GPU measurement queue.</h1>
  <p class="dek">Per-step host classes, commands, evidence paths, required metrics, and acceptance thresholds for real accelerator validation.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("status", "missing"))}</h2><p>queue status</p></div>
    <div class="card"><h2>{esc((report or {}).get("task_count", 0))}</h2><p>measurement tasks</p></div>
    <div class="card"><h2>{esc((report or {}).get("accepted_task_count", 0))}/{esc((report or {}).get("measured_task_count", 0))}</h2><p>accepted measured tasks</p></div>
    <div class="card"><h2><a href="../gpu-measurement-queue/reports/gpu-measurement-queue.md">Report</a></h2><p>Markdown queue</p></div>
  </div>

  <section>
    <h2>Measurement Tasks</h2>
    <table><tr><th>step</th><th>host class</th><th>status</th><th>accepted</th><th>commands</th><th>metrics</th><th>thresholds</th></tr>{render_gpu_measurement_queue_rows(report)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "gpu-measurement-queue.html").write_text(body, encoding="utf-8")


def render_gpu_acceptance_logic_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for case in (report or {}).get("cases", []):
        rows.append(
            "<tr>"
            f"<td>{esc(case['step_id'])}</td>"
            f"<td>{esc(case.get('good', {}).get('accepted'))}</td>"
            f"<td>{esc(not case.get('bad', {}).get('accepted', True))}</td>"
            f"<td>{esc(', '.join(case.get('good', {}).get('checks', {}).keys()))}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="4">No GPU acceptance logic report generated.</td></tr>'


def build_gpu_acceptance_logic_page(report: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE GPU Acceptance Logic</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Threshold regression gate</div>
  <h1>GPUMODE GPU acceptance logic.</h1>
  <p class="dek">Regression checks proving each GPU measurement threshold accepts canonical good metrics and rejects canonical bad metrics.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("status", "missing"))}</h2><p>logic status</p></div>
    <div class="card"><h2>{esc((report or {}).get("case_count", 0))}</h2><p>step cases</p></div>
    <div class="card"><h2>{esc((report or {}).get("accepted_good_cases", 0))}/{esc((report or {}).get("rejected_bad_cases", 0))}</h2><p>accepted good / rejected bad</p></div>
    <div class="card"><h2><a href="../gpu-measurement-queue/reports/acceptance-logic-report.md">Report</a></h2><p>Markdown logic</p></div>
  </div>

  <section>
    <h2>Cases</h2>
    <table><tr><th>step</th><th>good accepted</th><th>bad rejected</th><th>checks</th></tr>{render_gpu_acceptance_logic_rows(report)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "gpu-acceptance-logic.html").write_text(body, encoding="utf-8")


def render_gpu_host_preflight_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for step in (report or {}).get("steps", []):
        rows.append(
            "<tr>"
            f"<td>{esc(step['step_id'])}</td>"
            f"<td>{esc(step['runnable_on_this_host'])}</td>"
            f"<td>{esc(', '.join(step.get('missing_capabilities', [])) or 'none')}</td>"
            f"<td>{esc(step['command_count'])}</td>"
            f"<td>{esc(step['first_command'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="5">No GPU host preflight generated.</td></tr>'


def build_gpu_host_preflight_page(report: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE GPU Host Preflight</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Accelerator host readiness</div>
  <h1>GPUMODE GPU host preflight.</h1>
  <p class="dek">Capability snapshot and per-step runnable/blocked status before executing the GPU promotion suite.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("status", "missing"))}</h2><p>preflight status</p></div>
    <div class="card"><h2>{esc((report or {}).get("accelerator_ready", False))}</h2><p>accelerator ready</p></div>
    <div class="card"><h2>{esc((report or {}).get("runnable_step_count", 0))}/{esc((report or {}).get("step_count", 0))}</h2><p>runnable steps</p></div>
    <div class="card"><h2><a href="../gpu-handoff/reports/gpu-host-preflight.md">Report</a></h2><p>Markdown preflight</p></div>
  </div>

  <section>
    <h2>Step Readiness</h2>
    <table><tr><th>step</th><th>runnable</th><th>missing</th><th>commands</th><th>first command</th></tr>{render_gpu_host_preflight_rows(report)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "gpu-host-preflight.html").write_text(body, encoding="utf-8")


def render_gpu_handoff_files(handoff: dict[str, Any] | None = None) -> str:
    rows = []
    for path in (handoff or {}).get("bundle_files", []):
        rows.append(f"<tr><td>{esc(path)}</td></tr>")
    return "\n".join(rows) if rows else '<tr><td>No GPU handoff files generated.</td></tr>'


def build_gpu_handoff_page(handoff: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE GPU Host Handoff</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Portable accelerator run bundle</div>
  <h1>GPUMODE GPU host handoff.</h1>
  <p class="dek">A generated handoff bundle for running the promotion suite,
  collecting GPU-run imports, rebuilding reports, and verifying capstone acceptance on an accelerator host.</p>
  <div class="grid">
    <div class="card"><h2>{esc((handoff or {}).get("status", "missing"))}</h2><p>handoff status</p></div>
    <div class="card"><h2>{esc((handoff or {}).get("suite_summary", {}).get("command_count", 0))}</h2><p>suite commands</p></div>
    <div class="card"><h2>{esc((handoff or {}).get("entrypoint", ""))}</h2><p>entrypoint</p></div>
    <div class="card"><h2><a href="../gpu-handoff/reports/gpu-host-handoff.md">Report</a></h2><p>Markdown handoff</p></div>
  </div>

  <section>
    <h2>Bundle Files</h2>
    <table><tr><th>path</th></tr>{render_gpu_handoff_files(handoff)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "gpu-handoff.html").write_text(body, encoding="utf-8")


def render_capstone_acceptance_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for criterion in (report or {}).get("criteria", []):
        rows.append(
            "<tr>"
            f"<td>{esc(criterion['id'])}</td>"
            f"<td>{esc(criterion['status'])}</td>"
            f"<td>{esc(criterion['earned'])}/{esc(criterion['points'])}</td>"
            f"<td>{esc(', '.join(criterion.get('evidence', [])))}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="4">No capstone acceptance criteria generated.</td></tr>'


def build_capstone_acceptance_page(report: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE Capstone Acceptance</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated portfolio evaluator</div>
  <h1>GPUMODE capstone acceptance.</h1>
  <p class="dek">Portfolio-grade acceptance score across curriculum coverage,
  projects, labs, kernels, custom ops, autotune, model integration, serving,
  regression, GPU promotion, runtime gates, site, and audit evidence.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("score", 0))} / {esc((report or {}).get("max_score", 0))}</h2><p>score</p></div>
    <div class="card"><h2>{esc((report or {}).get("status", "missing"))}</h2><p>status</p></div>
    <div class="card"><h2>{esc((report or {}).get("passed_criteria", 0))} / {esc((report or {}).get("criteria_count", 0))}</h2><p>criteria passed</p></div>
    <div class="card"><h2><a href="../capstone-acceptance/reports/capstone-acceptance.md">Report</a></h2><p>Markdown acceptance</p></div>
  </div>

  <section>
    <h2>Rubric</h2>
    <table><tr><th>criterion</th><th>status</th><th>points</th><th>evidence</th></tr>{render_capstone_acceptance_rows(report)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "capstone-acceptance.html").write_text(body, encoding="utf-8")


def render_assessment_question_rows(assessment: dict[str, Any] | None = None) -> str:
    rows = []
    for question in (assessment or {}).get("questions", []):
        sources = ", ".join(source.get("provider", "") for source in question.get("related_tutorial_sources", []))
        rows.append(
            "<tr>"
            f"<td>{esc(question['id'])}</td>"
            f"<td>{esc(question['topic'])}</td>"
            f"<td>{esc(question['difficulty'])}</td>"
            f"<td>{esc(question['points'])}</td>"
            f"<td>{esc(question.get('lesson_count', 0))}</td>"
            f"<td>{esc(sources)}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="6">No assessment questions generated.</td></tr>'


def render_assessment_task_rows(assessment: dict[str, Any] | None = None) -> str:
    rows = []
    for task in (assessment or {}).get("practical_tasks", []):
        rows.append(
            "<tr>"
            f"<td>{esc(task['id'])}</td>"
            f"<td>{esc(task['layer'])}</td>"
            f"<td>{esc(task['command'])}</td>"
            f"<td>{esc(task['points'])}</td>"
            f"<td>{esc(', '.join(task.get('grading_checks', [])))}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="5">No practical tasks generated.</td></tr>'


def build_assessment_page(assessment: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE Assessment Bank</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated exam and practical tasks</div>
  <h1>GPUMODE assessment bank.</h1>
  <p class="dek">Concept checks and practical tasks tied to GPUMODE lessons,
  official CUDA/Triton/ROCm/JAX/Hugging Face sources, and local evidence artifacts.</p>
  <div class="grid">
    <div class="card"><h2>{esc((assessment or {}).get("concept_question_count", 0))}</h2><p>concept questions</p></div>
    <div class="card"><h2>{esc((assessment or {}).get("practical_task_count", 0))}</h2><p>practical tasks</p></div>
    <div class="card"><h2>{esc((assessment or {}).get("total_points", 0))}</h2><p>total points</p></div>
    <div class="card"><h2><a href="../assessment/reports/assessment-report.md">Report</a></h2><p>Markdown assessment</p></div>
  </div>

  <section>
    <h2>Concept Checks</h2>
    <table><tr><th>question</th><th>topic</th><th>difficulty</th><th>points</th><th>lessons</th><th>sources</th></tr>{render_assessment_question_rows(assessment)}</table>
  </section>

  <section>
    <h2>Practical Tasks</h2>
    <table><tr><th>task</th><th>layer</th><th>command</th><th>points</th><th>grading checks</th></tr>{render_assessment_task_rows(assessment)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "assessment.html").write_text(body, encoding="utf-8")


def render_assessment_grading_rows(report: dict[str, Any] | None = None) -> str:
    rows = []
    for row in (report or {}).get("results", []):
        label = row.get("layer") or row.get("topic")
        rows.append(
            "<tr>"
            f"<td>{esc(row['id'])}</td>"
            f"<td>{esc(row['type'])}</td>"
            f"<td>{esc(label)}</td>"
            f"<td>{esc(row['status'])}</td>"
            f"<td>{esc(row['earned'])}/{esc(row['points'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="5">No assessment grading results generated.</td></tr>'


def build_assessment_grading_page(report: dict[str, Any] | None = None) -> None:
    body = f"""<meta charset="utf-8">
<title>GPUMODE Assessment Grading</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Artifact-backed assessment score</div>
  <h1>GPUMODE assessment grading.</h1>
  <p class="dek">Machine-readable grading for concept-check readiness and
  practical task evidence across the implemented GPU curriculum stack.</p>
  <div class="grid">
    <div class="card"><h2>{esc((report or {}).get("score", 0))} / {esc((report or {}).get("max_score", 0))}</h2><p>score</p></div>
    <div class="card"><h2>{esc((report or {}).get("status", "missing"))}</h2><p>status</p></div>
    <div class="card"><h2>{esc((report or {}).get("practical_count", 0))}</h2><p>practical tasks</p></div>
    <div class="card"><h2><a href="../assessment/reports/grading-report.md">Report</a></h2><p>Markdown grading</p></div>
  </div>

  <section>
    <h2>Graded Items</h2>
    <table><tr><th>item</th><th>type</th><th>layer/topic</th><th>status</th><th>points</th></tr>{render_assessment_grading_rows(report)}</table>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "assessment-grading.html").write_text(body, encoding="utf-8")


def build_project_pages(
    project_index: dict[str, Any],
    run_report: dict[str, Any] | None = None,
    notebook_index: dict[str, Any] | None = None,
) -> None:
    run_by_id = {row["id"]: row for row in (run_report or {}).get("projects", [])}
    notebook_by_id = {row["project_id"]: row for row in (notebook_index or {}).get("notebooks", [])}
    for project in project_index.get("projects", []):
        root_project_path = ROOT / project["path"]
        metadata = load_json(root_project_path / "project.json")
        contract = load_json(root_project_path / "measurement-contract.json")
        run = run_by_id.get(project["id"], {})
        notebook = notebook_by_id.get(project["id"], {})
        lessons = lesson_rows(metadata.get("lessons", []))
        tutorials = tutorial_rows(metadata.get("tutorial_sources", []))
        papers = paper_link_rows(metadata.get("papers", []))
        contract_fields = "".join(f"<li>{esc(field)}</li>" for field in contract.get("required_fields", []))
        checks = run.get("contract", {}).get("checks", {})
        check_rows = "".join(
            "<tr>"
            f"<td>{esc(name)}</td>"
            f"<td>{esc('passed' if value else 'failed')}</td>"
            "</tr>"
            for name, value in checks.items()
        ) or '<tr><td colspan="2">No run report generated yet.</td></tr>'
        body = f"""<meta charset="utf-8">
<title>{esc(project["track"])} - GPU Programming Project</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated GPU programming project</div>
  <h1>{esc(project["track"])}</h1>
  <p class="dek">{esc(metadata.get("diagnosis", ""))}</p>
  <div class="grid">
    <div class="card"><h2>{esc(project["profile"])}</h2><p>workbench profile</p></div>
    <div class="card"><h2>{esc(run.get("run", {}).get("status", "not-run"))}</h2><p>starter run status</p></div>
    <div class="card"><h2>{esc(run.get("contract", {}).get("status", "not-validated"))}</h2><p>measurement contract</p></div>
    <div class="card"><h2><a href="../{esc(project["path"])}/README.md">README</a></h2><p>project instructions</p></div>
  </div>

  <section>
    <h2>Project Files</h2>
    <table><tr><th>kind</th><th>path</th></tr>
      <tr><td>starter</td><td>{esc(project["starter"])}</td></tr>
      <tr><td>measure</td><td>{esc(project.get("measure", ""))}</td></tr>
      <tr><td>source</td><td>{esc(project["source"])}</td></tr>
      <tr><td>tasks</td><td>{esc(project.get("tasks", ""))}</td></tr>
      <tr><td>local measurement</td><td>{esc(project.get("local_measurement", ""))}</td></tr>
      <tr><td>measurement contract</td><td>{esc(project["measurement_contract"])}</td></tr>
      <tr><td>notebook</td><td>{esc(notebook.get("path", ""))}</td></tr>
    </table>
  </section>

  <section>
    <h2>Contract Fields</h2>
    <ul>{contract_fields}</ul>
    <table><tr><th>check</th><th>status</th></tr>{check_rows}</table>
  </section>

  <section>
    <h2>Existing Lab And Measurement</h2>
    <p class="small">lab: {esc(metadata.get("lab", {}).get("path", ""))}</p>
    <p class="small">command: {esc(metadata.get("lab", {}).get("command", ""))}</p>
    <p class="small">measurement: {esc(metadata.get("measurement", {}).get("path", ""))}</p>
  </section>

  <section>
    <h2>GPUMODE Lesson Anchors</h2>
    <table><tr><th>#</th><th>lesson</th><th>topics</th><th>concepts</th><th>exercise candidates</th></tr>{lessons}</table>
  </section>

  <section>
    <h2>External Tutorial Sources</h2>
    <table><tr><th>provider</th><th>source</th><th>focus</th><th>why it belongs here</th></tr>{tutorials}</table>
  </section>

  <section>
    <h2>Paper Cross-Checks</h2>
    <table><tr><th>venue</th><th>paper</th><th>theme</th><th>confidence</th><th>GPUMODE links</th></tr>{papers}</table>
  </section>

  <section>
    <p class="small"><a href="projects.html">Back to programming projects</a> / <a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
        (SITE / project_slug(project["id"])).write_text(body, encoding="utf-8")


def build_projects_page(
    project_index: dict[str, Any],
    run_report: dict[str, Any] | None = None,
    notebook_index: dict[str, Any] | None = None,
) -> None:
    build_project_pages(project_index, run_report, notebook_index)
    body = f"""<meta charset="utf-8">
<title>GPU Programming Projects</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated programming layer</div>
  <h1>GPU programming projects.</h1>
  <p class="dek">Concrete CUDA, Triton, ROCm/HIP, vLLM-style, JAX, Hugging Face, profiler,
  and distributed-communication projects generated from the GPUMODE workbench.</p>
  <div class="grid">
    <div class="card"><h2>{esc(project_index.get("project_count", 0))}</h2><p>generated projects</p></div>
    <div class="card"><h2>{esc((run_report or {}).get("passed_contracts", 0))}</h2><p>contracts passed</p></div>
    <div class="card"><h2>{esc((run_report or {}).get("failed_contracts", 0))}</h2><p>contracts failed</p></div>
    <div class="card"><h2>{esc((notebook_index or {}).get("notebook_count", 0))}</h2><p>generated notebooks</p></div>
    <div class="card"><h2><a href="../programming-projects/project-run-report.md">Run Report</a></h2><p>latest starter evidence</p></div>
    <div class="card"><h2><a href="capstone.html">Capstone</a></h2><p>portfolio graph and milestones</p></div>
  </div>

  <section>
    <h2>Project Index</h2>
    <table>
      <tr><th>project</th><th>track</th><th>profile</th><th>starter</th><th>contract</th><th>starter path</th></tr>
      {render_project_rows(project_index, run_report)}
    </table>
  </section>
</div>
"""
    (SITE / "projects.html").write_text(body, encoding="utf-8")


def build_capstone_page(capstone: dict[str, Any]) -> None:
    order_rows = "".join(
        "<tr>"
        f"<td>{esc(idx)}</td>"
        f"<td>{esc(project_id)}</td>"
        f"<td>{esc(capstone.get('projects_by_id', {}).get(project_id, {}).get('track', ''))}</td>"
        f"<td>{esc(capstone.get('projects_by_id', {}).get(project_id, {}).get('profile', ''))}</td>"
        "</tr>"
        for idx, project_id in enumerate(capstone.get("execution_order", []), start=1)
    )
    milestone_rows = []
    for milestone in capstone.get("milestones", []):
        for project in milestone.get("projects", []):
            milestone_rows.append(
                "<tr>"
                f"<td>{esc(milestone['title'])}</td>"
                f"<td>{esc(project['project_id'])}</td>"
                f"<td>{esc(project['status'])}</td>"
                f"<td>{esc(project['contract'])}</td>"
                f"<td>{esc(project['measurement_path'])}</td>"
                "</tr>"
            )
    caveats = capstone.get("runtime_caveats", [])
    caveat_rows = "".join(
        "<tr>"
        f"<td>{esc(row['project_id'])}</td>"
        f"<td>{esc(row['note'])}</td>"
        "</tr>"
        for row in caveats
    ) or '<tr><td colspan="2">No runtime caveats recorded.</td></tr>'
    body = f"""<meta charset="utf-8">
<title>GPU Programming Capstone Portfolio</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated capstone portfolio</div>
  <h1>GPU programming capstone.</h1>
  <p class="dek">Portfolio-level dependency graph, milestone plan, contract status, and
  runtime caveats across the generated GPU programming projects.</p>
  <div class="grid">
    <div class="card"><h2>{esc(capstone.get("project_count", 0))}</h2><p>projects</p></div>
    <div class="card"><h2>{esc(capstone.get("graph", {}).get("edge_count", 0))}</h2><p>dependency edges</p></div>
    <div class="card"><h2>{esc(capstone.get("passed_contracts", 0))}</h2><p>contracts passed</p></div>
    <div class="card"><h2><a href="../programming-projects/capstone-portfolio.md">Portfolio</a></h2><p>Markdown report</p></div>
  </div>

  <section>
    <h2>Execution Order</h2>
    <table><tr><th>#</th><th>project</th><th>track</th><th>profile</th></tr>{order_rows}</table>
  </section>

  <section>
    <h2>Milestones</h2>
    <table><tr><th>milestone</th><th>project</th><th>starter</th><th>contract</th><th>measurement</th></tr>{''.join(milestone_rows)}</table>
  </section>

  <section>
    <h2>Runtime Caveats</h2>
    <table><tr><th>project</th><th>caveat</th></tr>{caveat_rows}</table>
  </section>

  <section>
    <p class="small"><a href="projects.html">Back to programming projects</a> / <a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
    (SITE / "capstone.html").write_text(body, encoding="utf-8")


def render_lessons(curriculum: dict[str, Any]) -> str:
    rows = []
    for lesson in curriculum["lessons"][:140]:
        topics = " ".join(f'<span class="pill">{esc(topic)}</span>' for topic in lesson["topics"])
        concepts = ", ".join(lesson["concepts"][:4])
        tools = ", ".join(lesson["tools"][:4])
        exercises = "; ".join(lesson["exercise_candidates"][:2])
        rows.append(
            "<tr>"
            f"<td>{esc(lesson['index'])}</td>"
            f'<td><a href="{esc(lesson_slug(lesson))}">{esc(lesson["title"])}</a><div class="small"><a href="{esc(lesson["url"])}">video</a></div></td>'
            f"<td>{topics}</td>"
            f"<td>{esc(concepts)}</td>"
            f"<td>{esc(tools)}</td>"
            f"<td>{esc(lesson['lab_readiness'])}</td>"
            f"<td>{esc(exercises)}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def matching_profiles_for_lesson(lesson: dict[str, Any], workbench: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not workbench:
        return []
    matches = []
    lesson_topics = set(lesson.get("topics", []))
    lesson_concepts = set(lesson.get("concepts", []))
    lesson_labs = set(lesson.get("candidate_lab_links", []))
    for profile in workbench["profiles"]:
        profile_lessons = {row["index"] for row in profile.get("recommended_lessons", [])}
        profile_labs = {row["id"] for row in profile.get("recommended_labs", [])}
        topic_hits = lesson_topics.intersection(
            topic for row in profile.get("recommended_lessons", []) for topic in row.get("topics", [])
        )
        concept_hits = lesson_concepts.intersection(
            concept for row in profile.get("recommended_lessons", []) for concept in row.get("concepts", [])
        )
        score = 10 if lesson["index"] in profile_lessons else 0
        score += 5 * len(lesson_labs.intersection(profile_labs))
        score += 2 * len(topic_hits) + 3 * len(concept_hits)
        if score <= 0:
            continue
        matches.append(
            {
                "id": profile["id"],
                "label": profile["label"],
                "url": bridge_slug(profile["id"]),
                "top_lab": profile["recommended_labs"][0]["id"] if profile.get("recommended_labs") else "",
                "top_measurement": profile["latest_measurements"][0]["path"] if profile.get("latest_measurements") else "",
                "matched_topics": sorted(topic_hits),
                "matched_concepts": sorted(concept_hits),
                "score": score,
            }
        )
    return sorted(matches, key=lambda row: (-row["score"], row["id"]))[:6]


def lesson_lab_rows(lesson: dict[str, Any], labs_by_id: dict[str, dict[str, Any]]) -> str:
    rows = []
    for lab_id in lesson.get("candidate_lab_links", []):
        lab = labs_by_id.get(lab_id)
        if not lab:
            continue
        rows.append(
            "<tr>"
            f"<td>{esc(lab['id'])}</td>"
            f"<td>{esc(lab['title'])}</td>"
            f"<td>{esc(lab.get('status', 'planned'))}</td>"
            f"<td>{esc(lab.get('implemented_as', ''))}</td>"
            f"<td>{esc(lab['deliverable'])}</td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else '<tr><td colspan="5">No candidate labs generated.</td></tr>'


def lesson_profile_rows(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return '<tr><td colspan="5">No profile bridges generated.</td></tr>'
    return "\n".join(
        "<tr>"
        f'<td><a href="{esc(row["url"])}">{esc(row["id"])}</a></td>'
        f"<td>{esc(row['label'])}</td>"
        f"<td>{esc(row['top_lab'])}</td>"
        f"<td>{esc(row['top_measurement'])}</td>"
        f"<td>{esc(', '.join(row['matched_concepts'] or row['matched_topics']))}</td>"
        "</tr>"
        for row in rows
    )


def build_lesson_pages(
    curriculum: dict[str, Any],
    workbench: dict[str, Any] | None,
    lesson_lab_index: dict[str, Any] | None = None,
) -> None:
    labs_by_id = {lab["id"]: lab for lab in curriculum["proposed_labs"]}
    lesson_labs_by_index = {
        row["lesson_index"]: row for row in (lesson_lab_index or {}).get("labs", [])
    }
    for lesson in curriculum["lessons"]:
        topics = " ".join(f'<span class="pill">{esc(topic)}</span>' for topic in lesson.get("topics", []))
        concepts = ", ".join(lesson.get("concepts", [])) or "None generated"
        tools = ", ".join(lesson.get("tools", [])) or "None generated"
        prereqs = ", ".join(lesson.get("prerequisites", [])) or "None generated"
        exercises = "; ".join(lesson.get("exercise_candidates", [])) or "None generated"
        mentions = ", ".join(lesson.get("paper_or_repo_mentions", [])) or "None generated"
        profiles = matching_profiles_for_lesson(lesson, workbench)
        lesson_lab = lesson_labs_by_index.get(lesson["index"], {})
        lesson_lab_card = ""
        lesson_lab_section = ""
        if lesson_lab:
            lesson_lab_card = (
                f'<div class="card"><h2><a href="{esc(lesson_lab_slug(lesson_lab["id"]))}">Lesson Lab</a></h2>'
                f'<p>{esc(lesson_lab.get("status", ""))}</p></div>'
            )
            lesson_lab_section = f"""
  <section>
    <h2>Implemented Per-Lesson Lab</h2>
    <table><tr><th>lab</th><th>path</th><th>status</th></tr>
      <tr><td><a href="{esc(lesson_lab_slug(lesson_lab["id"]))}">{esc(lesson_lab["id"])}</a></td><td>{esc(lesson_lab["path"])}</td><td>{esc(lesson_lab["status"])}</td></tr>
    </table>
  </section>
"""
        body = f"""<meta charset="utf-8">
<title>{esc(lesson["title"])} - GPUMODE Lesson</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated GPUMODE lesson page</div>
  <h1>{esc(lesson["title"])}</h1>
  <p class="dek">Lesson #{esc(lesson["index"])} is linked to generated topics, prerequisites,
  exercises, runnable labs, and bottleneck bridge pages.</p>
  <div class="grid">
    <div class="card"><h2>{esc(lesson.get("transcript_status", ""))}</h2><p>transcript status</p></div>
    <div class="card"><h2>{esc(lesson.get("word_count", 0))}</h2><p>transcript words</p></div>
    <div class="card"><h2><a href="{esc(lesson["url"])}">Video</a></h2><p>source lesson</p></div>
    {lesson_lab_card}
  </div>

  <section>
    <h2>Topic And Concept Signals</h2>
    <p>{topics}</p>
    <div class="bridge-list">
      <div class="bridge-item"><h3>Concepts</h3><p>{esc(concepts)}</p></div>
      <div class="bridge-item"><h3>Tools</h3><p>{esc(tools)}</p></div>
      <div class="bridge-item"><h3>Prerequisites</h3><p>{esc(prereqs)}</p></div>
      <div class="bridge-item"><h3>Exercise Candidates</h3><p>{esc(exercises)}</p></div>
    </div>
  </section>

  <section>
    <h2>Candidate Runnable Labs</h2>
    <table><tr><th>id</th><th>lab</th><th>status</th><th>implemented as</th><th>deliverable</th></tr>{lesson_lab_rows(lesson, labs_by_id)}</table>
  </section>

  {lesson_lab_section}

  <section>
    <h2>Workbench Bridge Matches</h2>
    <table><tr><th>profile</th><th>bottleneck</th><th>top lab</th><th>top measurement</th><th>evidence</th></tr>{lesson_profile_rows(profiles)}</table>
  </section>

  <section>
    <h2>Paper Or Repo Mentions</h2>
    <p>{esc(mentions)}</p>
  </section>

  <section>
    <p class="small"><a href="index.html">Back to curriculum index</a> / <a href="workbench.html">Back to workbench</a></p>
  </section>
</div>
"""
        (SITE / lesson_slug(lesson)).write_text(body, encoding="utf-8")


def lesson_rows(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return '<tr><td colspan="5">No lessons generated.</td></tr>'
    return "\n".join(
        "<tr>"
        f"<td>{esc(row['index'])}</td>"
        f'<td><a href="{esc(row["url"])}">{esc(row["title"])}</a></td>'
        f"<td>{esc(', '.join(row.get('topics', [])[:5]))}</td>"
        f"<td>{esc(', '.join(row.get('concepts', [])[:5]))}</td>"
        f"<td>{esc('; '.join(row.get('exercise_candidates', [])[:2]))}</td>"
        "</tr>"
        for row in rows
    )


def lab_rows(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return '<tr><td colspan="4">No labs generated.</td></tr>'
    return "\n".join(
        "<tr>"
        f"<td>{esc(row['id'])}</td>"
        f"<td>{esc(row['status'])}</td>"
        f"<td>{esc(row.get('implemented_as') or '')}</td>"
        f"<td>{esc(row['deliverable'])}</td>"
        "</tr>"
        for row in rows
    )


def measurement_rows(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return '<tr><td colspan="4">No measurements generated.</td></tr>'
    return "\n".join(
        "<tr>"
        f"<td>{esc(row['path'])}</td>"
        f"<td>{esc(row['status'])}</td>"
        f"<td>{esc(row.get('cuda_status') or '')}</td>"
        f"<td>{esc(row['summary'])}</td>"
        "</tr>"
        for row in rows
    )


def tutorial_rows(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return '<tr><td colspan="4">No tutorial sources generated.</td></tr>'
    return "\n".join(
        "<tr>"
        f"<td>{esc(row['provider'])}</td>"
        f'<td><a href="{esc(row["url"])}">{esc(row["title"])}</a></td>'
        f"<td>{esc(', '.join(row.get('focus_terms', [])[:6]))}</td>"
        f"<td>{esc(row['why'])}</td>"
        "</tr>"
        for row in rows
    )


def exercise_path_html(path: dict[str, Any]) -> str:
    if not path:
        return '<div class="bridge-item">No exercise path generated.</div>'
    steps = "".join(f"<li>{esc(step)}</li>" for step in path.get("steps", []))
    checks = "".join(f"<li>{esc(check)}</li>" for check in path.get("success_checks", []))
    lab = path.get("lab", {})
    measurement = path.get("measurement", {})
    source = path.get("source_reading", {})
    return f"""
    <div class="bridge-item">
      <h3>{esc(path.get("title", ""))}</h3>
      <p>{esc(path.get("objective", ""))}</p>
      <p class="small">source: <a href="{esc(source.get("url", ""))}">{esc(source.get("provider", ""))}: {esc(source.get("title", ""))}</a></p>
      <p class="small">run: {esc(lab.get("command", ""))}</p>
      <p class="small">artifact: {esc(measurement.get("path", ""))}</p>
      <h3>Steps</h3>
      <ol>{steps}</ol>
      <h3>Success Checks</h3>
      <ul>{checks}</ul>
    </div>
"""


def paper_link_rows(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return '<tr><td colspan="5">No papers generated.</td></tr>'
    rendered = []
    for paper in rows:
        lessons = "<br>".join(
            f'<a href="{esc(link["url"])}">#{esc(link["index"])} {esc(link["title"])}</a>'
            f'<div class="small">{esc(", ".join(link.get("matched_concepts") or link.get("matched_topics") or link.get("matched_terms", [])))}</div>'
            for link in paper.get("linked_lessons", [])
        )
        rendered.append(
            "<tr>"
            f"<td>{esc(paper['venue'])}</td>"
            f"<td>{esc(paper['title'])}</td>"
            f"<td>{esc(paper['theme'])}</td>"
            f"<td>{esc(paper['confidence'])}</td>"
            f"<td>{lessons}</td>"
            "</tr>"
        )
    return "\n".join(rendered)


def build_bridge_pages(workbench: dict[str, Any]) -> None:
    for profile in workbench["profiles"]:
        body = f"""<meta charset="utf-8">
<title>{esc(profile["label"])} - GPUMODE Bridge</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Generated GPUMODE bridge</div>
  <h1>{esc(profile["label"])}</h1>
  <p class="dek">{esc(profile["diagnosis"])}</p>
  <div class="bridge-list">
    <div class="bridge-item"><h3>Next measured move</h3><p>{esc(profile["next_action"])}</p></div>
    <div class="bridge-item"><h3>Profile ID</h3><p class="small">{esc(profile["id"])}</p></div>
  </div>

  <section>
    <h2>Runnable Labs</h2>
    <table><tr><th>lab</th><th>status</th><th>implemented as</th><th>deliverable</th></tr>{lab_rows(profile["recommended_labs"])}</table>
  </section>

  <section>
    <h2>Latest Measurements</h2>
    <table><tr><th>artifact</th><th>status</th><th>CUDA</th><th>summary</th></tr>{measurement_rows(profile["latest_measurements"])}</table>
  </section>

  <section>
    <h2>GPUMODE Lesson Anchors</h2>
    <table><tr><th>#</th><th>lesson</th><th>topics</th><th>concepts</th><th>exercise candidates</th></tr>{lesson_rows(profile["recommended_lessons"])}</table>
  </section>

  <section>
    <h2>External Tutorial Sources</h2>
    <table><tr><th>provider</th><th>source</th><th>focus</th><th>why it belongs here</th></tr>{tutorial_rows(profile.get("tutorial_sources", []))}</table>
  </section>

  <section>
    <h2>End-To-End Exercise Path</h2>
    {exercise_path_html(profile.get("exercise_path", {}))}
  </section>

  <section>
    <h2>Corpus Papers To Lessons</h2>
    <table><tr><th>venue</th><th>paper</th><th>theme</th><th>confidence</th><th>GPUMODE links</th></tr>{paper_link_rows(profile["related_papers"])}</table>
  </section>

  <section>
    <p class="small"><a href="workbench.html">Back to workbench</a> / <a href="index.html">Back to curriculum index</a></p>
  </section>
</div>
"""
        (SITE / bridge_slug(profile["id"])).write_text(body, encoding="utf-8")


def build() -> None:
    SITE.mkdir(parents=True, exist_ok=True)
    from scripts.build_executable_evidence_page import build_page
    build_page()
    curriculum = load_json(CURRICULUM)
    graph = load_json(CURRICULUM_GRAPH) if CURRICULUM_GRAPH.exists() else {}
    workbench = load_json(WORKBENCH) if WORKBENCH.exists() else None
    project_index = load_json(PROJECT_INDEX) if PROJECT_INDEX.exists() else None
    project_run_report = load_json(PROJECT_RUN_REPORT) if PROJECT_RUN_REPORT.exists() else None
    project_capstone = load_json(PROJECT_CAPSTONE) if PROJECT_CAPSTONE.exists() else None
    project_notebook_index = load_json(PROJECT_NOTEBOOK_INDEX) if PROJECT_NOTEBOOK_INDEX.exists() else None
    lesson_lab_index = load_json(LESSON_LAB_INDEX) if LESSON_LAB_INDEX.exists() else None
    lesson_lab_run_report = load_json(LESSON_LAB_RUN_REPORT) if LESSON_LAB_RUN_REPORT.exists() else None
    kernel_benchmark_plan = load_json(KERNEL_BENCHMARK_PLAN) if KERNEL_BENCHMARK_PLAN.exists() else None
    kernel_benchmark_report = load_json(KERNEL_BENCHMARK_REPORT) if KERNEL_BENCHMARK_REPORT.exists() else None
    compiler_runtime_report = load_json(COMPILER_RUNTIME_REPORT) if COMPILER_RUNTIME_REPORT.exists() else None
    tensor_core_gemm_report = load_json(TENSOR_CORE_GEMM_REPORT) if TENSOR_CORE_GEMM_REPORT.exists() else None
    persistent_kernels_report = load_json(PERSISTENT_KERNELS_REPORT) if PERSISTENT_KERNELS_REPORT.exists() else None
    parallel_primitives_report = load_json(PARALLEL_PRIMITIVES_REPORT) if PARALLEL_PRIMITIVES_REPORT.exists() else None
    runtime_matrix = load_json(RUNTIME_MATRIX) if RUNTIME_MATRIX.exists() else None
    profiler_evidence_report = load_json(PROFILER_EVIDENCE_REPORT) if PROFILER_EVIDENCE_REPORT.exists() else None
    serving_trace_report = load_json(SERVING_TRACE_REPORT) if SERVING_TRACE_REPORT.exists() else None
    kv_cache_report = load_json(KV_CACHE_REPORT) if KV_CACHE_REPORT.exists() else None
    attention_serving_report = load_json(ATTENTION_SERVING_REPORT) if ATTENTION_SERVING_REPORT.exists() else None
    flash_attention_backward = load_json(FLASH_ATTENTION_BACKWARD) if FLASH_ATTENTION_BACKWARD.exists() else None
    sparse_attention = load_json(SPARSE_ATTENTION_REPORT) if SPARSE_ATTENTION_REPORT.exists() else None
    fused_training = load_json(FUSED_TRAINING_REPORT) if FUSED_TRAINING_REPORT.exists() else None
    serving_engine_comparison = load_json(SERVING_ENGINE_COMPARISON) if SERVING_ENGINE_COMPARISON.exists() else None
    speculative_decoding = load_json(SPECULATIVE_DECODING_REPORT) if SPECULATIVE_DECODING_REPORT.exists() else None
    distributed_topology = load_json(DIST_TOPOLOGY) if DIST_TOPOLOGY.exists() else None
    distributed_collectives = load_json(DISTRIBUTED_COLLECTIVES) if DISTRIBUTED_COLLECTIVES.exists() else None
    distributed_training_optimizer = load_json(DISTRIBUTED_TRAINING_OPTIMIZER) if DISTRIBUTED_TRAINING_OPTIMIZER.exists() else None
    moe_routing_report = load_json(MOE_ROUTING_REPORT) if MOE_ROUTING_REPORT.exists() else None
    hardware_capacity = load_json(HARDWARE_CAPACITY_PLAN) if HARDWARE_CAPACITY_PLAN.exists() else None
    quantization_report = load_json(QUANTIZATION_REPORT) if QUANTIZATION_REPORT.exists() else None
    numerical_reproducibility = load_json(NUMERICAL_REPRODUCIBILITY) if NUMERICAL_REPRODUCIBILITY.exists() else None
    cuda_graphs_latency = load_json(CUDA_GRAPHS_LATENCY) if CUDA_GRAPHS_LATENCY.exists() else None
    multi_tenant_scheduling = load_json(MULTI_TENANT_SCHEDULING) if MULTI_TENANT_SCHEDULING.exists() else None
    custom_op_report = load_json(CUSTOM_OP_REPORT) if CUSTOM_OP_REPORT.exists() else None
    autotune_db = load_json(AUTOTUNE_DB) if AUTOTUNE_DB.exists() else None
    model_integration_report = load_json(MODEL_INTEGRATION_REPORT) if MODEL_INTEGRATION_REPORT.exists() else None
    regression_ledger = load_json(REGRESSION_LEDGER) if REGRESSION_LEDGER.exists() else None
    gpu_promotion = load_json(GPU_PROMOTION) if GPU_PROMOTION.exists() else None
    gpu_promotion_suite = load_json(GPU_PROMOTION_SUITE) if GPU_PROMOTION_SUITE.exists() else None
    gpu_import_lint = load_json(GPU_IMPORT_LINT) if GPU_IMPORT_LINT.exists() else None
    gpu_runs = load_json(GPU_RUNS) if GPU_RUNS.exists() else None
    gpu_provenance = load_json(GPU_PROVENANCE) if GPU_PROVENANCE.exists() else None
    gpu_measurement_queue = load_json(GPU_MEASUREMENT_QUEUE) if GPU_MEASUREMENT_QUEUE.exists() else None
    gpu_acceptance_logic = load_json(GPU_ACCEPTANCE_LOGIC) if GPU_ACCEPTANCE_LOGIC.exists() else None
    gpu_host_preflight = load_json(GPU_HOST_PREFLIGHT) if GPU_HOST_PREFLIGHT.exists() else None
    gpu_handoff = load_json(GPU_HANDOFF) if GPU_HANDOFF.exists() else None
    assessment = load_json(ASSESSMENT) if ASSESSMENT.exists() else None
    assessment_grading = load_json(ASSESSMENT_GRADING) if ASSESSMENT_GRADING.exists() else None
    capstone_acceptance = load_json(CAPSTONE_ACCEPTANCE) if CAPSTONE_ACCEPTANCE.exists() else None
    build_lesson_pages(curriculum, workbench, lesson_lab_index)
    workbench_card = ""
    workbench_profile_table = ""
    if workbench:
        coverage = workbench["coverage"]
        build_bridge_pages(workbench)
        workbench_card = (
            '<div class="card"><h2><a href="workbench.html">Workbench</a></h2>'
            f'<p>{esc(coverage["profile_count"])} bottleneck profiles, '
            f'{esc(coverage["measurement_artifacts"])} measurement artifacts, '
            f'{esc(coverage["paper_json"])} corpus papers scored, '
            f'{esc(coverage.get("lesson_corpus_bridge_links", 0))} lesson-paper links.</p></div>'
        )
        workbench_profile_table = f"""
  <section>
    <h2>Workbench Bridge Pages</h2>
    <table>
      <tr><th>profile</th><th>bottleneck</th><th>top lab</th><th>top measurement</th><th>top paper</th></tr>
      {render_workbench_profiles(workbench)}
    </table>
  </section>
"""
    project_card = ""
    project_table = ""
    if project_index:
        build_projects_page(project_index, project_run_report, project_notebook_index)
        if project_capstone:
            build_capstone_page(project_capstone)
        project_card = (
            '<div class="card"><h2><a href="projects.html">Projects</a></h2>'
            f'<p>{esc(project_index.get("project_count", 0))} generated programming projects, '
            f'{esc((project_run_report or {}).get("passed_contracts", 0))} contract checks passed, '
            f'{esc((project_notebook_index or {}).get("notebook_count", 0))} notebooks'
            f'{", capstone ready" if project_capstone else ""}.</p></div>'
        )
        project_table = f"""
  <section>
    <h2>Programming Project Layer</h2>
    <table>
      <tr><th>project</th><th>track</th><th>profile</th><th>starter</th><th>contract</th><th>starter path</th></tr>
      {render_project_rows(project_index, project_run_report)}
    </table>
  </section>
"""
    lesson_lab_card = ""
    lesson_lab_table = ""
    if lesson_lab_index:
        build_lesson_labs_page(lesson_lab_index, lesson_lab_run_report)
        lesson_lab_card = (
            '<div class="card"><h2><a href="lesson-labs.html">Lesson Labs</a></h2>'
            f'<p>{esc(lesson_lab_index.get("generated_lab_count", 0))} generated lesson labs, '
            f'{esc((lesson_lab_run_report or {}).get("passed_contracts", 0))} contract checks passed.</p></div>'
        )
        lesson_lab_table = f"""
  <section>
    <h2>One Lab Per Lesson Coverage</h2>
    <table>
      <tr><th>#</th><th>lab</th><th>lesson</th><th>contract</th><th>project anchors before generation</th></tr>
      {render_lesson_lab_rows(lesson_lab_index, lesson_lab_run_report)}
    </table>
  </section>
"""
    kernel_benchmark_card = ""
    kernel_benchmark_table = ""
    if kernel_benchmark_plan or kernel_benchmark_report:
        build_kernel_benchmarks_page(kernel_benchmark_plan, kernel_benchmark_report)
        kernel_benchmark_card = (
            '<div class="card"><h2><a href="kernel-benchmarks.html">Kernel Benchmarks</a></h2>'
            f'<p>{esc((kernel_benchmark_report or {}).get("benchmark_count", 0))} benchmark cases, '
            f'{esc((kernel_benchmark_report or {}).get("passed", 0))} passed, '
            f'{esc((kernel_benchmark_plan or {}).get("covered_lessons", 0))} lessons mapped.</p></div>'
        )
        kernel_benchmark_table = f"""
  <section>
    <h2>Kernel Benchmark Layer</h2>
    <table>
      <tr><th>family</th><th>purpose</th><th>lessons</th><th>CUDA source</th><th>Triton source</th></tr>
      {render_kernel_family_rows(kernel_benchmark_plan)}
    </table>
  </section>
"""
    compiler_runtime_card = ""
    compiler_runtime_table = ""
    if compiler_runtime_report:
        build_compiler_runtime_page(compiler_runtime_report)
        compiler_runtime_card = (
            '<div class="card"><h2><a href="compiler-runtime-inspection.html">Compiler Runtime</a></h2>'
            f'<p>{esc(compiler_runtime_report.get("source_count", 0))} sources, '
            f'{esc(compiler_runtime_report.get("group_count", 0))} groups, '
            f'{esc(compiler_runtime_report.get("status", "missing"))}.</p></div>'
        )
        compiler_runtime_table = f"""
  <section>
    <h2>Compiler Runtime Inspection Layer</h2>
    <table>
      <tr><th>feature</th><th>sources</th></tr>
      {render_compiler_runtime_feature_rows(compiler_runtime_report)}
    </table>
  </section>
"""
    tensor_core_gemm_card = ""
    tensor_core_gemm_table = ""
    if tensor_core_gemm_report:
        build_tensor_core_gemm_page(tensor_core_gemm_report)
        tensor_core_gemm_card = (
            '<div class="card"><h2><a href="tensor-core-gemm.html">Tensor Core GEMM</a></h2>'
            f'<p>{esc(tensor_core_gemm_report.get("scenario_count", 0))} scenarios, '
            f'{esc(tensor_core_gemm_report.get("tensor_core_eligible_scenarios", 0))} tensor-core eligible, '
            f'{esc(tensor_core_gemm_report.get("fused_epilogue_scenarios", 0))} fused epilogues.</p></div>'
        )
        tensor_core_gemm_table = f"""
  <section>
    <h2>CUTLASS CuTe Tensor Core GEMM Layer</h2>
    <table>
      <tr><th>scenario</th><th>status</th><th>dtype</th><th>CTA</th><th>MMA</th><th>shared memory</th><th>registers</th><th>intensity</th><th>epilogue</th></tr>
      {render_tensor_core_gemm_rows(tensor_core_gemm_report)}
    </table>
  </section>
"""
    runtime_matrix_card = ""
    runtime_matrix_table = ""
    persistent_kernels_card = ""
    persistent_kernels_table = ""
    if persistent_kernels_report:
        build_persistent_kernels_page(persistent_kernels_report)
        persistent_kernels_card = (
            '<div class="card"><h2><a href="persistent-kernels.html">Persistent Kernels</a></h2>'
            f'<p>{esc(persistent_kernels_report.get("scenario_count", 0))} scenarios, '
            f'{esc(persistent_kernels_report.get("passed_scenarios", 0))} passed, '
            f'{esc(persistent_kernels_report.get("family_count", 0))} families.</p></div>'
        )
        persistent_kernels_table = f"""
  <section>
    <h2>Persistent Kernel Layer</h2>
    <table>
      <tr><th>scenario</th><th>family</th><th>strategy</th><th>occupancy</th><th>speedup</th><th>HBM reduction</th><th>resident CTA/SM</th><th>producer</th><th>status</th></tr>
      {render_persistent_kernel_rows(persistent_kernels_report)}
    </table>
  </section>
"""
    parallel_primitives_card = ""
    parallel_primitives_table = ""
    if parallel_primitives_report:
        build_parallel_primitives_page(parallel_primitives_report)
        parallel_primitives_card = (
            '<div class="card"><h2><a href="parallel-primitives.html">Parallel Primitives</a></h2>'
            f'<p>{esc(parallel_primitives_report.get("scenario_count", 0))} scenarios, '
            f'{esc(parallel_primitives_report.get("passed_scenarios", 0))} passed, '
            f'{esc(parallel_primitives_report.get("primitive_count", 0))} primitives.</p></div>'
        )
        parallel_primitives_table = f"""
  <section>
    <h2>Parallel Primitive Layer</h2>
    <table>
      <tr><th>scenario</th><th>primitive</th><th>algorithm</th><th>efficiency</th><th>bandwidth proxy</th><th>occupancy</th><th>stable</th><th>status</th></tr>
      {render_parallel_primitives_rows(parallel_primitives_report)}
    </table>
  </section>
"""
    if runtime_matrix:
        build_runtime_matrix_page(runtime_matrix)
        runtime_matrix_card = (
            '<div class="card"><h2><a href="runtime-matrix.html">Runtime Matrix</a></h2>'
            f'<p>{esc(runtime_matrix.get("profile_count", 0))} profiles, '
            f'{esc(runtime_matrix.get("ready_profiles", 0))} ready locally, '
            f'{esc(runtime_matrix.get("fallback_profiles", 0))} source-ready fallback.</p></div>'
        )
        runtime_matrix_table = f"""
  <section>
    <h2>Runtime Matrix</h2>
    <table>
      <tr><th>profile</th><th>status</th><th>required</th><th>purpose</th><th>commands</th></tr>
      {render_runtime_profile_rows(runtime_matrix)}
    </table>
  </section>
"""
    profiler_evidence_card = ""
    profiler_evidence_table = ""
    if profiler_evidence_report:
        build_profiler_evidence_page(profiler_evidence_report)
        profiler_evidence_card = (
            '<div class="card"><h2><a href="profiler-evidence.html">Profiler Evidence</a></h2>'
            f'<p>{esc(profiler_evidence_report.get("row_count", 0))} rows, '
            f'{esc(profiler_evidence_report.get("source_count", 0))} sources, '
            f'{esc(len(profiler_evidence_report.get("classification_counts", {})))} classifications.</p></div>'
        )
        profiler_evidence_table = f"""
  <section>
    <h2>Profiler Evidence Layer</h2>
    <table>
      <tr><th>classification</th><th>rows</th></tr>
      {render_profiler_counts(profiler_evidence_report)}
    </table>
  </section>
"""
    serving_trace_card = ""
    serving_trace_table = ""
    if serving_trace_report:
        build_serving_traces_page(serving_trace_report)
        serving_trace_card = (
            '<div class="card"><h2><a href="serving-traces.html">Serving Traces</a></h2>'
            f'<p>{esc(serving_trace_report.get("trace_count", 0))} traces, '
            f'{esc(serving_trace_report.get("passed_traces", 0))} passed, '
            f'{esc(len(serving_trace_report.get("policy_ids", [])))} policies.</p></div>'
        )
        serving_trace_table = f"""
  <section>
    <h2>Serving Trace Layer</h2>
    <table>
      <tr><th>trace</th><th>throughput speedup</th><th>p50 TTFT delta ms</th><th>prefix blocks saved</th><th>peak KV blocks</th></tr>
      {render_serving_comparison_rows(serving_trace_report)}
    </table>
  </section>
"""
    kv_cache_card = ""
    kv_cache_table = ""
    if kv_cache_report:
        build_kv_cache_page(kv_cache_report)
        kv_cache_card = (
            '<div class="card"><h2><a href="kv-cache-paged-attention.html">KV Cache</a></h2>'
            f'<p>{esc(kv_cache_report.get("scenario_count", 0))} scenarios, '
            f'{esc(kv_cache_report.get("passed_scenarios", 0))} passed, '
            f'{esc(kv_cache_report.get("total_prefix_blocks_reused", 0))} prefix blocks reused.</p></div>'
        )
        kv_cache_table = f"""
  <section>
    <h2>KV Cache PagedAttention Layer</h2>
    <table>
      <tr><th>scenario</th><th>status</th><th>peak block savings</th><th>waste reduction</th><th>admission delta</th><th>prefix blocks reused</th></tr>
      {render_kv_cache_rows(kv_cache_report)}
    </table>
  </section>
"""
    attention_serving_card = ""
    attention_serving_table = ""
    if attention_serving_report:
        build_attention_serving_page(attention_serving_report)
        attention_serving_card = (
            '<div class="card"><h2><a href="attention-serving-stack.html">Attention Serving</a></h2>'
            f'<p>{esc(attention_serving_report.get("scenario_count", 0))} scenarios, '
            f'{esc(attention_serving_report.get("passed_scenarios", 0))} passed, '
            f'{esc(attention_serving_report.get("total_prefix_blocks_reused", 0))} prefix blocks reused.</p></div>'
        )
        attention_serving_table = f"""
  <section>
    <h2>FlashAttention To vLLM Serving Layer</h2>
    <table>
      <tr><th>scenario</th><th>status</th><th>HBM reduction</th><th>shared memory</th><th>intensity</th><th>scheduler</th><th>prefix reuse</th></tr>
      {render_attention_serving_rows(attention_serving_report)}
    </table>
  </section>
"""
    flash_attention_backward_card = ""
    flash_attention_backward_table = ""
    if flash_attention_backward:
        build_flash_attention_backward_page(flash_attention_backward)
        flash_attention_backward_card = (
            '<div class="card"><h2><a href="flash-attention-backward.html">FlashAttention Backward</a></h2>'
            f'<p>{esc(flash_attention_backward.get("scenario_count", 0))} scenarios, '
            f'{esc(flash_attention_backward.get("passed_scenarios", 0))} passed, '
            f'{esc(flash_attention_backward.get("dropout_scenarios", 0))} dropout case.</p></div>'
        )
        flash_attention_backward_table = f"""
  <section>
    <h2>FlashAttention Backward Layer</h2>
    <table>
      <tr><th>scenario</th><th>dtype</th><th>seq q/kv</th><th>speedup</th><th>HBM reduction</th><th>recompute</th><th>occupancy</th><th>gradients</th><th>status</th></tr>
      {render_flash_attention_backward_rows(flash_attention_backward)}
    </table>
  </section>
"""
    sparse_attention_card = ""
    sparse_attention_table = ""
    if sparse_attention:
        build_sparse_attention_page(sparse_attention)
        sparse_attention_card = (
            '<div class="card"><h2><a href="sparse-attention-kernels.html">Sparse Attention Kernels</a></h2>'
            f'<p>{esc(sparse_attention.get("scenario_count", 0))} scenarios, '
            f'{esc(sparse_attention.get("pattern_count", 0))} patterns, '
            f'{esc(sparse_attention.get("ragged_scenarios", 0))} ragged cases.</p></div>'
        )
        sparse_attention_table = f"""
  <section>
    <h2>Sparse Attention Kernel Layer</h2>
    <table>
      <tr><th>scenario</th><th>pattern</th><th>seq q/kv</th><th>density</th><th>speedup</th><th>HBM reduction</th><th>load balance</th><th>kernel paths</th><th>status</th></tr>
      {render_sparse_attention_rows(sparse_attention)}
    </table>
  </section>
"""
    fused_training_card = ""
    fused_training_table = ""
    if fused_training:
        build_fused_training_page(fused_training)
        fused_training_card = (
            '<div class="card"><h2><a href="fused-training-kernels.html">Fused Training Kernels</a></h2>'
            f'<p>{esc(fused_training.get("scenario_count", 0))} scenarios, '
            f'{esc(fused_training.get("family_count", 0))} families, '
            f'{esc(fused_training.get("optimizer_state_scenarios", 0))} optimizer cases.</p></div>'
        )
        fused_training_table = f"""
  <section>
    <h2>Fused Training Kernel Layer</h2>
    <table>
      <tr><th>scenario</th><th>family</th><th>dtype</th><th>speedup</th><th>HBM reduction</th><th>launch reduction</th><th>max error</th><th>kernel paths</th><th>status</th></tr>
      {render_fused_training_rows(fused_training)}
    </table>
  </section>
"""
    serving_engine_card = ""
    serving_engine_table = ""
    if serving_engine_comparison:
        build_serving_engine_comparison_page(serving_engine_comparison)
        serving_engine_card = (
            '<div class="card"><h2><a href="serving-engine-comparison.html">Serving Engines</a></h2>'
            f'<p>{esc(serving_engine_comparison.get("engine_count", 0))} engines, '
            f'{esc(serving_engine_comparison.get("scenario_count", 0))} scenarios, '
            f'{esc(serving_engine_comparison.get("status", "missing"))}.</p></div>'
        )
        serving_engine_table = f"""
  <section>
    <h2>Serving Engine Comparison Layer</h2>
    <table>
      <tr><th>scenario</th><th>recommended</th><th>runner up</th><th>why</th></tr>
      {render_serving_engine_recommendation_rows(serving_engine_comparison)}
    </table>
  </section>
"""
    speculative_decoding_card = ""
    speculative_decoding_table = ""
    if speculative_decoding:
        build_speculative_decoding_page(speculative_decoding)
        speculative_decoding_card = (
            '<div class="card"><h2><a href="speculative-decoding-serving.html">Speculative Decoding</a></h2>'
            f'<p>{esc(speculative_decoding.get("scenario_count", 0))} scenarios, '
            f'{esc(speculative_decoding.get("passed_scenarios", 0))} passed, '
            f'{esc(speculative_decoding.get("review_scenarios", 0))} review cases.</p></div>'
        )
        speculative_decoding_table = f"""
  <section>
    <h2>Speculative Decoding Serving Layer</h2>
    <table>
      <tr><th>scenario</th><th>workload</th><th>engine</th><th>draft</th><th>acceptance</th><th>speedup</th><th>wasted</th><th>scheduler</th><th>status</th></tr>
      {render_speculative_decoding_rows(speculative_decoding)}
    </table>
  </section>
"""
    distributed_topology_card = ""
    distributed_topology_table = ""
    if distributed_topology:
        build_distributed_topology_page(distributed_topology)
        distributed_topology_card = (
            '<div class="card"><h2><a href="distributed-topology.html">Distributed Topology</a></h2>'
            f'<p>{esc(distributed_topology.get("topology_count", 0))} topologies, '
            f'{esc(distributed_topology.get("workload_count", 0))} workloads, '
            f'{esc(distributed_topology.get("candidate_count", 0))} candidates.</p></div>'
        )
    distributed_topology_table = f"""
  <section>
    <h2>Distributed Topology Layer</h2>
    <table>
      <tr><th>workload</th><th>topology</th><th>tensor</th><th>pipeline</th><th>data</th><th>bottleneck</th><th>collective ms</th></tr>
      {render_distributed_topology_recommendations(distributed_topology)}
    </table>
  </section>
"""
    distributed_collectives_card = ""
    distributed_collectives_table = ""
    if distributed_collectives:
        build_distributed_collectives_page(distributed_collectives)
        distributed_collectives_card = (
            '<div class="card"><h2><a href="distributed-collectives.html">Distributed Collectives</a></h2>'
            f'<p>{esc(distributed_collectives.get("scenario_count", 0))} scenarios, '
            f'{esc(distributed_collectives.get("passed_scenarios", 0))} passed, '
            f'{esc(distributed_collectives.get("collective_count", 0))} collective families.</p></div>'
        )
        distributed_collectives_table = f"""
  <section>
    <h2>Distributed Collectives Layer</h2>
    <table>
      <tr><th>scenario</th><th>collective</th><th>algorithm</th><th>ranks</th><th>backend</th><th>exposed ms</th><th>efficiency</th><th>overlap gain</th><th>status</th></tr>
      {render_distributed_collectives_rows(distributed_collectives)}
    </table>
  </section>
"""
    distributed_training_optimizer_card = ""
    distributed_training_optimizer_table = ""
    if distributed_training_optimizer:
        build_distributed_training_optimizer_page(distributed_training_optimizer)
        distributed_training_optimizer_card = (
            '<div class="card"><h2><a href="distributed-training-optimizer.html">Training Optimizer</a></h2>'
            f'<p>{esc(distributed_training_optimizer.get("scenario_count", 0))} scenarios, '
            f'{esc(distributed_training_optimizer.get("passed_scenarios", 0))} passed, '
            f'{esc(distributed_training_optimizer.get("strategy_count", 0))} strategies.</p></div>'
        )
        distributed_training_optimizer_table = f"""
  <section>
    <h2>Distributed Training Optimizer Layer</h2>
    <table>
      <tr><th>scenario</th><th>strategy</th><th>ranks</th><th>memory GB/GPU</th><th>exposed comm ms</th><th>bubble ms</th><th>optimizer savings</th><th>tokens/s</th><th>status</th></tr>
      {render_distributed_training_optimizer_rows(distributed_training_optimizer)}
    </table>
  </section>
"""
    moe_routing_card = ""
    moe_routing_table = ""
    if moe_routing_report:
        build_moe_routing_page(moe_routing_report)
        moe_routing_card = (
            '<div class="card"><h2><a href="moe-routing-all-to-all.html">MoE Routing</a></h2>'
            f'<p>{esc(moe_routing_report.get("scenario_count", 0))} scenarios, '
            f'{esc(moe_routing_report.get("passed_scenarios", 0))} healthy, '
            f'{esc(moe_routing_report.get("tuning_required_scenarios", 0))} tuning-required.</p></div>'
        )
        moe_routing_table = f"""
  <section>
    <h2>MoE Routing All-to-All Layer</h2>
    <table>
      <tr><th>scenario</th><th>status</th><th>drop rate</th><th>fairness</th><th>imbalance</th><th>payload GB</th><th>all-to-all ms</th><th>bottleneck</th></tr>
      {render_moe_routing_rows(moe_routing_report)}
    </table>
  </section>
"""
    hardware_capacity_card = ""
    hardware_capacity_table = ""
    if hardware_capacity:
        build_hardware_capacity_page(hardware_capacity)
        hardware_capacity_card = (
            '<div class="card"><h2><a href="hardware-capacity.html">Hardware Capacity</a></h2>'
            f'<p>{esc(hardware_capacity.get("profile_count", 0))} profiles, '
            f'{esc(hardware_capacity.get("workload_count", 0))} workloads, '
            f'{esc(hardware_capacity.get("recommendation_count", 0))} recommendations.</p></div>'
        )
        hardware_capacity_table = f"""
  <section>
    <h2>Hardware Capacity Layer</h2>
    <table>
      <tr><th>workload</th><th>profile</th><th>bottleneck</th><th>memory GB</th><th>memory headroom</th><th>power W</th><th>cost/hr</th></tr>
      {render_hardware_capacity_recommendations(hardware_capacity)}
    </table>
  </section>
"""
    quantization_card = ""
    quantization_table = ""
    if quantization_report:
        build_quantization_page(quantization_report)
        quantization_card = (
            '<div class="card"><h2><a href="quantization-memory-formats.html">Quantization</a></h2>'
            f'<p>{esc(quantization_report.get("format_count", 0))} formats, '
            f'{esc(quantization_report.get("passed_format_count", 0))} passed, '
            f'{esc(quantization_report.get("calibration_needed_count", 0))} calibration-needed.</p></div>'
        )
        quantization_table = f"""
  <section>
    <h2>Quantization Memory Format Layer</h2>
    <table>
      <tr><th>format</th><th>bits</th><th>compression</th><th>max error</th><th>cosine</th><th>dequant tax</th><th>speedup proxy</th><th>serving fit</th><th>status</th></tr>
      {render_quantization_format_rows(quantization_report)}
    </table>
  </section>
"""
    numerical_card = ""
    numerical_table = ""
    if numerical_reproducibility:
        build_numerical_reproducibility_page(numerical_reproducibility)
        numerical_card = (
            '<div class="card"><h2><a href="numerical-reproducibility.html">Numerics</a></h2>'
            f'<p>{esc(numerical_reproducibility.get("scenario_count", 0))} scenarios, '
            f'{esc(numerical_reproducibility.get("passed_scenarios", 0))} passed, '
            f'{esc(numerical_reproducibility.get("tolerance_review_scenarios", 0))} tolerance-review.</p></div>'
        )
        numerical_table = f"""
  <section>
    <h2>Numerical Reproducibility Layer</h2>
    <table>
      <tr><th>mode</th><th>category</th><th>status</th><th>tolerance</th><th>repeat drift</th><th>reference error</th><th>cosine</th></tr>
      {render_numerical_reproducibility_rows(numerical_reproducibility)}
    </table>
  </section>
"""
    cuda_graphs_card = ""
    cuda_graphs_table = ""
    if cuda_graphs_latency:
        build_cuda_graphs_latency_page(cuda_graphs_latency)
        cuda_graphs_card = (
            '<div class="card"><h2><a href="cuda-graphs-latency.html">CUDA Graphs</a></h2>'
            f'<p>{esc(cuda_graphs_latency.get("scenario_count", 0))} scenarios, '
            f'{esc(cuda_graphs_latency.get("capture_ready_count", 0))} capture-ready, '
            f'{esc(cuda_graphs_latency.get("fallback_required_count", 0))} fallback-required.</p></div>'
        )
        cuda_graphs_table = f"""
  <section>
    <h2>CUDA Graphs Latency Layer</h2>
    <table>
      <tr><th>scenario</th><th>status</th><th>eager p95 ms</th><th>graph p95 ms</th><th>p95 reduction</th><th>jitter reduction</th><th>fallback</th></tr>
      {render_cuda_graphs_rows(cuda_graphs_latency)}
    </table>
  </section>
"""
    multi_tenant_card = ""
    multi_tenant_table = ""
    if multi_tenant_scheduling:
        build_multi_tenant_scheduling_page(multi_tenant_scheduling)
        multi_tenant_card = (
            '<div class="card"><h2><a href="multi-tenant-scheduling.html">Multi-Tenant Scheduling</a></h2>'
            f'<p>{esc(multi_tenant_scheduling.get("policy_count", 0))} policies, '
            f'{esc(multi_tenant_scheduling.get("tenant_count", 0))} tenants, '
            f'{esc(multi_tenant_scheduling.get("accepted_count", 0))} accepted in recommended plan.</p></div>'
        )
        multi_tenant_table = f"""
  <section>
    <h2>Multi-Tenant GPU Scheduling Layer</h2>
    <table>
      <tr><th>policy</th><th>accepted</th><th>queued</th><th>fairness</th><th>utilization</th><th>score</th></tr>
      {render_multi_tenant_plan_rows(multi_tenant_scheduling)}
    </table>
  </section>
"""
    custom_op_card = ""
    custom_op_table = ""
    if custom_op_report:
        build_custom_ops_page(custom_op_report)
        custom_op_card = (
            '<div class="card"><h2><a href="custom-ops.html">Custom Op</a></h2>'
            f'<p>{esc(custom_op_report.get("operator", ""))}, '
            f'{esc(custom_op_report.get("passed", 0))}/{esc(custom_op_report.get("case_count", 0))} cases passed, '
            f'{esc(custom_op_report.get("accelerator_readiness", {}).get("compiled_extension_status", "unknown"))}.</p></div>'
        )
        custom_op_table = f"""
  <section>
    <h2>PyTorch Custom Op Layer</h2>
    <table>
      <tr><th>case</th><th>dtype</th><th>shape</th><th>status</th><th>max abs error</th><th>grad x error</th><th>fused median s</th><th>elements/s</th></tr>
      {render_custom_op_rows(custom_op_report)}
    </table>
  </section>
"""
    autotune_card = ""
    autotune_table = ""
    if autotune_db:
        build_autotune_db_page(autotune_db)
        autotune_card = (
            '<div class="card"><h2><a href="autotune-db.html">Autotune DB</a></h2>'
            f'<p>{esc(autotune_db.get("record_count", 0))} records across '
            f'{esc(len(autotune_db.get("families", [])))} families.</p></div>'
        )
        autotune_table = f"""
  <section>
    <h2>Autotuning Database Layer</h2>
    <table>
      <tr><th>record</th><th>family</th><th>shape</th><th>selected config</th><th>measured s</th><th>estimated s</th><th>speedup</th><th>targets</th></tr>
      {render_autotune_rows(autotune_db)}
    </table>
  </section>
"""
    model_integration_card = ""
    model_integration_table = ""
    if model_integration_report:
        build_model_integration_page(model_integration_report)
        model_integration_card = (
            '<div class="card"><h2><a href="model-integration.html">Model Integration</a></h2>'
            f'<p>{esc(model_integration_report.get("model", ""))}, '
            f'{esc(model_integration_report.get("passed", 0))}/{esc(model_integration_report.get("case_count", 0))} cases passed.</p></div>'
        )
        model_integration_table = f"""
  <section>
    <h2>Model Integration Layer</h2>
    <table>
      <tr><th>case</th><th>shape</th><th>status</th><th>max abs error</th><th>grad error</th><th>fused median s</th><th>tokens/s</th></tr>
      {render_model_integration_rows(model_integration_report)}
    </table>
  </section>
"""
    regression_card = ""
    regression_table = ""
    if regression_ledger:
        build_regression_ledger_page(regression_ledger)
        regression_card = (
            '<div class="card"><h2><a href="regression-ledger.html">Regression Ledger</a></h2>'
            f'<p>{esc(regression_ledger.get("metric_count", 0))} metrics, '
            f'{esc(regression_ledger.get("failed", 0))} failed.</p></div>'
        )
        regression_table = f"""
  <section>
    <h2>Regression Ledger Layer</h2>
    <table>
      <tr><th>layer</th><th>id</th><th>metric</th><th>value</th><th>status</th><th>source</th></tr>
      {render_regression_rows(regression_ledger)}
    </table>
  </section>
"""
    gpu_promotion_card = ""
    gpu_promotion_table = ""
    if gpu_promotion:
        build_gpu_promotion_page(gpu_promotion)
        gpu_promotion_card = (
            '<div class="card"><h2><a href="gpu-promotion.html">GPU Promotion</a></h2>'
            f'<p>{esc(gpu_promotion.get("step_count", 0))} steps, '
            f'{esc(gpu_promotion.get("ready_on_gpu_host", 0))} GPU-host gated.</p></div>'
        )
        gpu_promotion_table = f"""
  <section>
    <h2>GPU Host Promotion Layer</h2>
    <table>
      <tr><th>step</th><th>status</th><th>required</th><th>missing locally</th><th>first command</th><th>validation</th></tr>
      {render_gpu_promotion_rows(gpu_promotion)}
    </table>
  </section>
"""
    gpu_promotion_suite_card = ""
    gpu_promotion_suite_table = ""
    if gpu_promotion_suite:
        build_gpu_promotion_suite_page(gpu_promotion_suite)
        gpu_promotion_suite_card = (
            '<div class="card"><h2><a href="gpu-promotion-suite.html">Promotion Suite</a></h2>'
            f'<p>{esc(gpu_promotion_suite.get("command_count", 0))} commands, '
            f'{esc(gpu_promotion_suite.get("step_count", 0))} steps, '
            f'{esc(gpu_promotion_suite.get("status", "missing"))}.</p></div>'
        )
        gpu_promotion_suite_table = f"""
  <section>
    <h2>GPU Promotion Suite Layer</h2>
    <table>
      <tr><th>#</th><th>step</th><th>status</th><th>command</th><th>evidence</th></tr>
      {render_gpu_promotion_suite_rows(gpu_promotion_suite)}
    </table>
  </section>
"""
    gpu_runs_card = ""
    gpu_runs_table = ""
    gpu_import_lint_card = ""
    gpu_import_lint_table = ""
    if gpu_import_lint:
        build_gpu_import_lint_page(gpu_import_lint)
        gpu_import_lint_card = (
            '<div class="card"><h2><a href="gpu-import-lint.html">Import Lint</a></h2>'
            f'<p>{esc(gpu_import_lint.get("status", "missing"))}, '
            f'{esc(gpu_import_lint.get("error_count", 0))} errors.</p></div>'
        )
        gpu_import_lint_table = f"""
  <section>
    <h2>GPU Import Lint Layer</h2>
    <table>
      <tr><th>file</th><th>kind</th><th>provenance</th><th>measured</th><th>steps</th><th>errors</th><th>warnings</th></tr>
      {render_gpu_import_lint_rows(gpu_import_lint)}
    </table>
  </section>
"""
    if gpu_runs:
        build_gpu_runs_page(gpu_runs)
        coverage = gpu_runs.get("coverage", {})
        gpu_runs_card = (
            '<div class="card"><h2><a href="gpu-runs.html">GPU Runs</a></h2>'
            f'<p>{esc(coverage.get("run_count", 0))} imported runs, '
            f'{esc(coverage.get("vendor_count", 0))} vendors, '
            f'{esc(coverage.get("promotion_step_count", 0))} promotion steps.</p></div>'
        )
        gpu_runs_table = f"""
  <section>
    <h2>GPU Run Import Layer</h2>
    <table>
      <tr><th>run</th><th>host</th><th>accelerator</th><th>step</th><th>status</th><th>metrics</th></tr>
      {render_gpu_run_rows(gpu_runs)}
    </table>
  </section>
"""
    gpu_handoff_card = ""
    gpu_handoff_table = ""
    gpu_provenance_card = ""
    gpu_provenance_table = ""
    if gpu_provenance:
        build_gpu_provenance_page(gpu_provenance)
        gpu_provenance_card = (
            '<div class="card"><h2><a href="gpu-provenance.html">GPU Provenance</a></h2>'
            f'<p>{esc(gpu_provenance.get("real_gpu_evidence_status", "missing"))}, '
            f'{esc(gpu_provenance.get("measured_run_count", 0))} measured GPU runs.</p></div>'
        )
        gpu_provenance_table = f"""
  <section>
    <h2>GPU Evidence Provenance Layer</h2>
    <table>
      <tr><th>run</th><th>provenance</th><th>measured</th><th>vendor</th><th>accelerator</th><th>rows</th><th>passed</th><th>skipped</th></tr>
      {render_gpu_provenance_rows(gpu_provenance)}
    </table>
  </section>
"""
    gpu_measurement_queue_card = ""
    gpu_measurement_queue_table = ""
    if gpu_measurement_queue:
        build_gpu_measurement_queue_page(gpu_measurement_queue)
        gpu_measurement_queue_card = (
            '<div class="card"><h2><a href="gpu-measurement-queue.html">Measurement Queue</a></h2>'
            f'<p>{esc(gpu_measurement_queue.get("task_count", 0))} tasks, '
            f'{esc(gpu_measurement_queue.get("accepted_task_count", 0))}/{esc(gpu_measurement_queue.get("measured_task_count", 0))} accepted measured.</p></div>'
        )
        gpu_measurement_queue_table = f"""
  <section>
    <h2>GPU Measurement Queue Layer</h2>
    <table>
      <tr><th>step</th><th>host class</th><th>status</th><th>accepted</th><th>commands</th><th>metrics</th><th>thresholds</th></tr>
      {render_gpu_measurement_queue_rows(gpu_measurement_queue)}
    </table>
  </section>
"""
    gpu_acceptance_logic_card = ""
    gpu_acceptance_logic_table = ""
    if gpu_acceptance_logic:
        build_gpu_acceptance_logic_page(gpu_acceptance_logic)
        gpu_acceptance_logic_card = (
            '<div class="card"><h2><a href="gpu-acceptance-logic.html">Acceptance Logic</a></h2>'
            f'<p>{esc(gpu_acceptance_logic.get("accepted_good_cases", 0))} good accepted, '
            f'{esc(gpu_acceptance_logic.get("rejected_bad_cases", 0))} bad rejected.</p></div>'
        )
        gpu_acceptance_logic_table = f"""
  <section>
    <h2>GPU Acceptance Logic Layer</h2>
    <table>
      <tr><th>step</th><th>good accepted</th><th>bad rejected</th><th>checks</th></tr>
      {render_gpu_acceptance_logic_rows(gpu_acceptance_logic)}
    </table>
  </section>
"""
    gpu_host_preflight_card = ""
    gpu_host_preflight_table = ""
    if gpu_host_preflight:
        build_gpu_host_preflight_page(gpu_host_preflight)
        gpu_host_preflight_card = (
            '<div class="card"><h2><a href="gpu-host-preflight.html">GPU Preflight</a></h2>'
            f'<p>{esc(gpu_host_preflight.get("runnable_step_count", 0))}/{esc(gpu_host_preflight.get("step_count", 0))} runnable, '
            f'accelerator ready {esc(gpu_host_preflight.get("accelerator_ready", False))}.</p></div>'
        )
        gpu_host_preflight_table = f"""
  <section>
    <h2>GPU Host Preflight Layer</h2>
    <table>
      <tr><th>step</th><th>runnable</th><th>missing</th><th>commands</th><th>first command</th></tr>
      {render_gpu_host_preflight_rows(gpu_host_preflight)}
    </table>
  </section>
"""
    if gpu_handoff:
        build_gpu_handoff_page(gpu_handoff)
        gpu_handoff_card = (
            '<div class="card"><h2><a href="gpu-handoff.html">GPU Handoff</a></h2>'
            f'<p>{esc(gpu_handoff.get("status", "missing"))}, '
            f'{esc(gpu_handoff.get("suite_summary", {}).get("command_count", 0))} commands.</p></div>'
        )
        gpu_handoff_table = f"""
  <section>
    <h2>GPU Host Handoff Layer</h2>
    <table>
      <tr><th>path</th></tr>
      {render_gpu_handoff_files(gpu_handoff)}
    </table>
  </section>
"""
    assessment_card = ""
    assessment_table = ""
    if assessment:
        build_assessment_page(assessment)
        assessment_card = (
            '<div class="card"><h2><a href="assessment.html">Assessment</a></h2>'
            f'<p>{esc(assessment.get("concept_question_count", 0))} concept questions, '
            f'{esc(assessment.get("practical_task_count", 0))} practical tasks, '
            f'{esc(assessment.get("total_points", 0))} points.</p></div>'
        )
        assessment_table = f"""
  <section>
    <h2>Assessment Layer</h2>
    <table>
      <tr><th>task</th><th>layer</th><th>command</th><th>points</th><th>grading checks</th></tr>
      {render_assessment_task_rows(assessment)}
    </table>
  </section>
"""
    assessment_grading_card = ""
    assessment_grading_table = ""
    if assessment_grading:
        build_assessment_grading_page(assessment_grading)
        assessment_grading_card = (
            '<div class="card"><h2><a href="assessment-grading.html">Assessment Grade</a></h2>'
            f'<p>{esc(assessment_grading.get("score", 0))}/{esc(assessment_grading.get("max_score", 0))} points, '
            f'{esc(assessment_grading.get("status", "missing"))}.</p></div>'
        )
        assessment_grading_table = f"""
  <section>
    <h2>Assessment Grading Layer</h2>
    <table>
      <tr><th>item</th><th>type</th><th>layer/topic</th><th>status</th><th>points</th></tr>
      {render_assessment_grading_rows(assessment_grading)}
    </table>
  </section>
"""
    capstone_acceptance_card = ""
    capstone_acceptance_table = ""
    if capstone_acceptance:
        build_capstone_acceptance_page(capstone_acceptance)
        capstone_acceptance_card = (
            '<div class="card"><h2><a href="capstone-acceptance.html">Capstone Acceptance</a></h2>'
            f'<p>{esc(capstone_acceptance.get("score", 0))}/{esc(capstone_acceptance.get("max_score", 0))} points, '
            f'{esc(capstone_acceptance.get("status", "missing"))}.</p></div>'
        )
        capstone_acceptance_table = f"""
  <section>
    <h2>Capstone Acceptance Layer</h2>
    <table>
      <tr><th>criterion</th><th>status</th><th>points</th><th>evidence</th></tr>
      {render_capstone_acceptance_rows(capstone_acceptance)}
    </table>
  </section>
"""
    body = f"""<meta charset="utf-8">
<title>GPUMODE Curriculum Expansion</title>
<style>{STYLE}</style>
<div class="wrap">
  <div class="kick">Transcript-backed GPU systems curriculum</div>
  <h1>GPUMODE lessons into runnable labs.</h1>
  <p><a href="advanced-executable-evidence.html">Advanced executable evidence: GEMM, attention, training, caching and packed quantization</a></p>
  <p class="dek">This generated page turns the GPUMODE video index into topic clusters and
  concrete lab candidates that extend the CUDA, Triton, ROCm/HIP, JAX, Hugging Face, and vLLM
  serving work in the GPU kernels lab.</p>

  <div class="grid">
    <div class="card"><h2>{esc(curriculum["lesson_count"])}</h2><p>videos indexed</p></div>
    <div class="card"><h2>{esc(curriculum["transcript_count"])}</h2><p>transcripts available locally</p></div>
    <div class="card"><h2>{esc(len(curriculum["proposed_labs"]))}</h2><p>deep labs proposed</p></div>
    <div class="card"><h2>{esc(graph.get("node_count", 0))} / {esc(graph.get("edge_count", 0))}</h2><p>graph nodes / edges</p></div>
    {workbench_card}
    {project_card}
    <div class="card"><h2><a href="teaching.html">Teaching Notes</a></h2><p>First-principles explanations beside the code: question, files, measurement, and limits.</p></div>
    <div class="card"><h2><a href="worked-walkthroughs.html">Worked Walkthroughs</a></h2><p>Eight core labs with predict, run, change, and explain steps.</p></div>
    {lesson_lab_card}
    {kernel_benchmark_card}
    {compiler_runtime_card}
    {tensor_core_gemm_card}
    {persistent_kernels_card}
    {parallel_primitives_card}
    {runtime_matrix_card}
    {profiler_evidence_card}
    {serving_trace_card}
    {kv_cache_card}
    {attention_serving_card}
    {flash_attention_backward_card}
    {sparse_attention_card}
    {fused_training_card}
    {serving_engine_card}
    {speculative_decoding_card}
    {distributed_topology_card}
    {distributed_collectives_card}
    {distributed_training_optimizer_card}
    {moe_routing_card}
    {hardware_capacity_card}
    {quantization_card}
    {numerical_card}
    {cuda_graphs_card}
    {multi_tenant_card}
    {custom_op_card}
    {autotune_card}
    {model_integration_card}
    {regression_card}
    {gpu_promotion_card}
    {gpu_promotion_suite_card}
    {gpu_import_lint_card}
    {gpu_runs_card}
    {gpu_provenance_card}
    {gpu_measurement_queue_card}
    {gpu_acceptance_logic_card}
    {gpu_host_preflight_card}
    {gpu_handoff_card}
    {assessment_card}
    {assessment_grading_card}
    {capstone_acceptance_card}
  </div>

  <section>
    <h2>Topic Map</h2>
    <div class="grid">{render_topics(curriculum)}</div>
  </section>

  <section>
    <h2>Lab Readiness</h2>
    <div class="grid">{render_readiness(curriculum)}</div>
  </section>

  <section>
    <h2>Curriculum Graph</h2>
    <table>
      <tr><th>topic</th><th>lessons</th><th>prerequisite signals</th><th>implemented labs</th><th>order score</th></tr>
      {render_graph_order(graph)}
    </table>
  </section>

  <section>
    <h2>Deep Lab Backlog</h2>
    <table>
      <tr><th>id</th><th>lab</th><th>status</th><th>topics</th><th>deliverable</th><th>extends</th><th>implemented as</th></tr>
      {render_labs(curriculum)}
    </table>
  </section>

  {workbench_profile_table}

  {project_table}

  {lesson_lab_table}

  {kernel_benchmark_table}

  {compiler_runtime_table}

  {tensor_core_gemm_table}

  {persistent_kernels_table}

  {parallel_primitives_table}

  {runtime_matrix_table}

  {profiler_evidence_table}

  {serving_trace_table}

  {kv_cache_table}

  {attention_serving_table}

  {flash_attention_backward_table}

  {sparse_attention_table}

  {fused_training_table}

  {serving_engine_table}

  {speculative_decoding_table}

  {distributed_topology_table}

  {distributed_collectives_table}

  {distributed_training_optimizer_table}

  {moe_routing_table}

  {hardware_capacity_table}

  {quantization_table}

  {numerical_table}

  {cuda_graphs_table}

  {multi_tenant_table}

  {custom_op_table}

  {autotune_table}

  {model_integration_table}

  {regression_table}

  {gpu_promotion_table}

  {gpu_promotion_suite_table}

  {gpu_import_lint_table}

  {gpu_runs_table}

  {gpu_provenance_table}

  {gpu_measurement_queue_table}

  {gpu_acceptance_logic_table}

  {gpu_host_preflight_table}

  {gpu_handoff_table}

  {assessment_table}

  {assessment_grading_table}

  {capstone_acceptance_table}

  <section>
    <h2>Lesson Index</h2>
    <table>
      <tr><th>#</th><th>lesson</th><th>topics</th><th>concepts</th><th>tools</th><th>readiness</th><th>exercise candidates</th></tr>
      {render_lessons(curriculum)}
    </table>
  </section>
</div>
"""
    (SITE / "index.html").write_text(body, encoding="utf-8")
    print("wrote", SITE / "index.html")


if __name__ == "__main__":
    build()
