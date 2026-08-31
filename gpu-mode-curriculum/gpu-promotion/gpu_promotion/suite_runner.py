from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "gpu-promotion" / "gpu-host-promotion-manifest.json"
REPORT_JSON = ROOT / "gpu-promotion" / "suite-run-report.json"
REPORT_MD = ROOT / "gpu-promotion" / "reports" / "suite-run-report.md"


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _has_placeholder(command: str) -> bool:
    return "<" in command or ">" in command


def _status_for_command(command: str, dry_run: bool, allow_placeholders: bool) -> str:
    if _has_placeholder(command) and not allow_placeholders:
        return "skipped-placeholder"
    return "planned" if dry_run else "pending"


def _run_command(command: str, timeout_seconds: int) -> dict[str, Any]:
    started = datetime.now(timezone.utc).isoformat()
    try:
        result = subprocess.run(
            shlex.split(command),
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
        return {
            "started_at": started,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "returncode": result.returncode,
            "stdout_tail": result.stdout[-2000:],
            "stderr_tail": result.stderr[-2000:],
            "status": "passed" if result.returncode == 0 else "failed",
        }
    except Exception as exc:
        return {
            "started_at": started,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "returncode": None,
            "stdout_tail": "",
            "stderr_tail": str(exc),
            "status": "failed",
        }


def build_plan(manifest: dict[str, Any], dry_run: bool, allow_placeholders: bool) -> list[dict[str, Any]]:
    rows = []
    order = 0
    for step in manifest.get("steps", []):
        for command in step.get("commands", []):
            order += 1
            rows.append(
                {
                    "order": order,
                    "step_id": step.get("id"),
                    "step_status": step.get("status"),
                    "command": command,
                    "status": _status_for_command(command, dry_run, allow_placeholders),
                    "expected_evidence": step.get("expected_evidence", []),
                    "validation": step.get("validation", ""),
                }
            )
    return rows


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# GPU Promotion Suite Run",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Run ID: `{report['run_id']}`",
        f"Mode: `{report['mode']}`",
        f"Status: `{report['status']}`",
        "",
        "| order | step | status | command |",
        "|---:|---|---|---|",
    ]
    for row in report["commands"]:
        lines.append(f"| {row['order']} | `{row['step_id']}` | {row['status']} | `{row['command']}` |")
    return "\n".join(lines).rstrip() + "\n"


def run_suite(
    run_id: str,
    dry_run: bool = True,
    step_filter: set[str] | None = None,
    allow_placeholders: bool = False,
    timeout_seconds: int = 600,
) -> dict[str, Any]:
    manifest = load_json(MANIFEST, {})
    commands = build_plan(manifest, dry_run=dry_run, allow_placeholders=allow_placeholders)
    if step_filter:
        commands = [row for row in commands if row["step_id"] in step_filter]
    for row in commands:
        if row["status"] == "pending":
            result = _run_command(row["command"], timeout_seconds)
            row.update(result)
    failed = sum(1 for row in commands if row["status"] == "failed")
    passed = sum(1 for row in commands if row["status"] == "passed")
    skipped = sum(1 for row in commands if row["status"].startswith("skipped"))
    planned = sum(1 for row in commands if row["status"] == "planned")
    status = "failed" if failed else "dry-run-ready" if dry_run else "executed"
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "mode": "dry-run" if dry_run else "execute",
        "status": status,
        "manifest": "gpu-promotion/gpu-host-promotion-manifest.json",
        "command_count": len(commands),
        "planned": planned,
        "passed": passed,
        "skipped": skipped,
        "failed": failed,
        "step_count": len({row["step_id"] for row in commands}),
        "commands": commands,
    }
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    write_json(REPORT_JSON, report)
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run or plan the GPU promotion suite from the manifest.")
    parser.add_argument("--run-id", default="local-suite-dry-run", help="Stable suite run id.")
    parser.add_argument("--execute", action="store_true", help="Execute commands instead of writing a dry-run plan.")
    parser.add_argument("--step", action="append", default=[], help="Limit to one promotion step id. May be repeated.")
    parser.add_argument("--allow-placeholders", action="store_true", help="Allow commands containing placeholder tokens.")
    parser.add_argument("--timeout-seconds", type=int, default=600, help="Timeout for each executed command.")
    args = parser.parse_args(argv)
    report = run_suite(
        run_id=args.run_id,
        dry_run=not args.execute,
        step_filter=set(args.step) if args.step else None,
        allow_placeholders=args.allow_placeholders,
        timeout_seconds=args.timeout_seconds,
    )
    print(
        f"wrote {REPORT_JSON.relative_to(ROOT)} and {REPORT_MD.relative_to(ROOT)} "
        f"({report['command_count']} commands, status={report['status']})"
    )
    return 1 if report["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
