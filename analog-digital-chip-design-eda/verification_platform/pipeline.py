"""Composition entry point for the first verification workflow."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .generator import write_sva_module
from .ingest import ingest_markdown
from .planner import plan_ir, write_plan
from .runner import run_command


def run_pipeline(
    specification: str | Path,
    command: list[str],
    *,
    tool: str,
    run_root: str | Path,
    source_revision: str = "unknown",
    timeout_seconds: float = 60.0,
) -> dict[str, Any]:
    """Run the deterministic plan/generate/execute stages and persist their outputs."""
    root = Path(run_root)
    root.mkdir(parents=True, exist_ok=True)
    spec_ir = ingest_markdown(specification, root=Path(specification).parent, source_revision=source_revision)
    plans = plan_ir(spec_ir)
    (root / "specification-ir.json").write_text(json.dumps(spec_ir.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_plan(plans, root / "verification-plan.json")
    write_sva_module(plans, root / "generated_checks.sv")
    run = run_command(
        command,
        tool=tool,
        run_root=root,
        source_revision=source_revision,
        timeout_seconds=timeout_seconds,
        expected_artifacts=["specification-ir.json", "verification-plan.json", "generated_checks.sv"],
    )
    return {"specification_ir": spec_ir, "plans": plans, "tool_run": run, "run_root": root}
