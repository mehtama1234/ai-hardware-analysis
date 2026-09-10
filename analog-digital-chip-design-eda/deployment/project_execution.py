"""Open-source project-collateral execution adapters for the pilot service."""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
import re
from typing import Any

from verification_platform.runner import run_command

MODULE_RE = re.compile(r"\bmodule\s+([A-Za-z_][A-Za-z0-9_$]*)")


def compile_project_rtl(
    record: dict[str, Any],
    *,
    collateral_root: str | Path,
    run_root: str | Path,
    source_revision: str | None = None,
    timeout_seconds: float = 120.0,
) -> dict[str, Any]:
    """Compile uploaded RTL with Icarus and persist the normal provenance ledger."""
    source = Path(collateral_root) / str(record["path"])
    if not source.is_file():
        raise FileNotFoundError(source)
    content = source.read_text(encoding="utf-8")
    modules = sorted(set(MODULE_RE.findall(content)))
    if not modules:
        raise ValueError("collateral contains no SystemVerilog module")
    top = modules[0]
    output = Path(run_root) / "compiled.out"
    tool_run = run_command(
        ["iverilog", "-g2012", "-s", top, "-o", str(output), str(source)],
        tool="iverilog-project-compile",
        run_root=run_root,
        source_revision=source_revision or str(record["version"]),
        timeout_seconds=timeout_seconds,
        expected_artifacts=["compiled.out"],
    )
    result = {
        "project_id": record["project_id"],
        "artifact_id": record["id"],
        "top_module": top,
        "modules": modules,
        "status": tool_run.status,
        "exit_code": tool_run.exit_code,
        "tool_run": asdict(tool_run),
    }
    result_path = Path(run_root) / "project-compile-result.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result["result_path"] = str(result_path)
    return result
