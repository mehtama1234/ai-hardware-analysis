from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from gpu_promotion.builder import capabilities


ROOT = Path(__file__).resolve().parents[2]
REPORT_JSON = ROOT / "gpu-handoff" / "gpu-host-preflight.json"
REPORT_MD = ROOT / "gpu-handoff" / "reports" / "gpu-host-preflight.md"


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _step_status(step: dict[str, Any], caps: dict[str, Any]) -> dict[str, Any]:
    missing = [name for name in step.get("required_capabilities", []) if not caps.get(name)]
    return {
        "step_id": step.get("id", ""),
        "title": step.get("title", ""),
        "required_capabilities": step.get("required_capabilities", []),
        "missing_capabilities": missing,
        "runnable_on_this_host": not missing,
        "command_count": len(step.get("commands", [])),
        "first_command": step.get("commands", [""])[0],
        "validation": step.get("validation", ""),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# GPUMODE GPU Host Preflight",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Status: `{report['status']}`",
        f"Accelerator ready: `{report['accelerator_ready']}`",
        f"Runnable steps: `{report['runnable_step_count']}/{report['step_count']}`",
        "",
        "## Capabilities",
        "",
    ]
    for key, value in report["capabilities"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Step Readiness", "", "| step | runnable | missing | first command |", "|---|---:|---|---|"])
    for step in report["steps"]:
        missing = ", ".join(step["missing_capabilities"]) or "none"
        lines.append(f"| `{step['step_id']}` | `{step['runnable_on_this_host']}` | {missing} | `{step['first_command']}` |")
    return "\n".join(lines).rstrip() + "\n"


def build_preflight() -> dict[str, Any]:
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    manifest = load_json(ROOT / "gpu-promotion" / "gpu-host-promotion-manifest.json", {})
    caps = capabilities()
    steps = [_step_status(step, caps) for step in manifest.get("steps", [])]
    accelerator_ready = bool(caps.get("nvidia_smi") or caps.get("hipcc") or caps.get("rocprof"))
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "preflight-complete" if len(steps) >= 9 else "incomplete",
        "accelerator_ready": accelerator_ready,
        "step_count": len(steps),
        "runnable_step_count": sum(1 for step in steps if step["runnable_on_this_host"]),
        "blocked_step_count": sum(1 for step in steps if not step["runnable_on_this_host"]),
        "capabilities": caps,
        "steps": steps,
    }
    write_json(REPORT_JSON, report)
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report
