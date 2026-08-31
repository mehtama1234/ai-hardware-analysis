from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = ROOT / "gpu-runs" / "fixtures"
IMPORT_DIR = ROOT / "gpu-runs" / "imports"
REPORT_JSON = ROOT / "gpu-runs" / "import-lint-report.json"
REPORT_MD = ROOT / "gpu-runs" / "reports" / "import-lint-report.md"
ALLOWED_KINDS = {"sample-fixture", "host-collected", "real-measured"}
ALLOWED_STEP_STATUSES = {"passed", "failed"}
REQUIRED_STEPS = {
    "cuda-kernel-compile",
    "triton-kernel-sweep",
    "persistent-kernels",
    "parallel-primitives",
    "torch-custom-extension",
    "model-integration-gpu",
    "vllm-serving-trace",
    "flash-attention-backward",
    "sparse-attention-kernels",
    "fused-training-kernels",
    "speculative-decoding-serving",
    "profiler-capture",
    "rocm-hip-port",
    "distributed-collectives",
    "distributed-training-optimizer",
    "full-gpu-regression",
}


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _paths() -> list[tuple[str, Path]]:
    return [("fixture", path) for path in sorted(FIXTURE_DIR.glob("*.json"))] + [
        ("import", path) for path in sorted(IMPORT_DIR.glob("*.json"))
    ]


def _lint_run(kind: str, path: Path, run: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    provenance = run.get("provenance", {})
    host = run.get("host", {})
    steps = run.get("promotion_steps", [])
    provenance_kind = provenance.get("kind")
    measured = provenance.get("measured")
    accelerator_ready = bool(host.get("cuda_available") or host.get("rocm_available"))

    if not run.get("run_id"):
        errors.append("missing run_id")
    if not run.get("generated_at"):
        errors.append("missing generated_at")
    if provenance_kind not in ALLOWED_KINDS:
        errors.append("invalid or missing provenance.kind")
    if not isinstance(measured, bool):
        errors.append("provenance.measured must be boolean")
    if not isinstance(host, dict) or not host.get("name"):
        errors.append("missing host.name")
    if not isinstance(steps, list) or not steps:
        errors.append("missing promotion_steps")

    if kind == "fixture" and provenance_kind != "sample-fixture":
        errors.append("fixture files must use sample-fixture provenance")
    if kind == "fixture" and measured is not False:
        errors.append("fixture files must not be marked measured")
    if kind == "import" and provenance_kind == "sample-fixture":
        errors.append("import files must not use sample-fixture provenance")
    if provenance_kind == "real-measured" and not accelerator_ready:
        errors.append("real-measured imports require cuda_available or rocm_available host evidence")
    if measured is True and provenance_kind != "real-measured":
        errors.append("measured=true requires real-measured provenance")
    if measured is False and provenance_kind == "real-measured":
        errors.append("real-measured provenance requires measured=true")
    if kind == "import" and provenance_kind == "host-collected" and accelerator_ready:
        warnings.append("accelerator host import is host-collected but could be real-measured")

    step_ids = set()
    for index, step in enumerate(steps, start=1):
        step_id = step.get("id")
        step_ids.add(step_id)
        status = step.get("status")
        metrics = step.get("metrics", {})
        evidence = step.get("evidence", [])
        if step_id not in REQUIRED_STEPS:
            errors.append(f"step {index} has unknown id {step_id!r}")
        if status not in ALLOWED_STEP_STATUSES and not str(status).startswith("skipped:"):
            errors.append(f"step {step_id} has invalid status {status!r}")
        if not isinstance(metrics, dict) or not metrics:
            errors.append(f"step {step_id} missing metrics")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"step {step_id} missing evidence")
        if provenance_kind == "real-measured" and status == "passed" and not metrics:
            errors.append(f"real-measured passed step {step_id} has no metrics")

    if kind == "import" and not REQUIRED_STEPS.issubset(step_ids):
        warnings.append(f"import covers {len(step_ids & REQUIRED_STEPS)}/{len(REQUIRED_STEPS)} promotion steps")

    return {
        "path": str(path.relative_to(ROOT)),
        "kind": kind,
        "run_id": run.get("run_id", ""),
        "provenance_kind": provenance_kind,
        "measured": measured,
        "vendor": host.get("vendor", "unknown"),
        "accelerator": host.get("accelerator", "unknown"),
        "step_count": len(steps),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# GPUMODE GPU Run Import Lint",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Status: `{report['status']}`",
        f"Files: `{report['file_count']}`",
        f"Errors: `{report['error_count']}`",
        f"Warnings: `{report['warning_count']}`",
        "",
        "| file | kind | run | provenance | measured | steps | errors | warnings |",
        "|---|---|---|---|---:|---:|---:|---:|",
    ]
    for row in report["files"]:
        lines.append(
            f"| `{row['path']}` | {row['kind']} | `{row['run_id']}` | "
            f"`{row['provenance_kind']}` | `{row['measured']}` | {row['step_count']} | "
            f"{row['error_count']} | {row['warning_count']} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def lint_imports() -> dict[str, Any]:
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    files = [_lint_run(kind, path, load_json(path, {})) for kind, path in _paths()]
    error_count = sum(row["error_count"] for row in files)
    warning_count = sum(row["warning_count"] for row in files)
    import_files = [row for row in files if row["kind"] == "import"]
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "lint-clean" if files and import_files and error_count == 0 else "failed",
        "file_count": len(files),
        "fixture_count": sum(1 for row in files if row["kind"] == "fixture"),
        "import_count": len(import_files),
        "error_count": error_count,
        "warning_count": warning_count,
        "files": files,
    }
    write_json(REPORT_JSON, report)
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report
