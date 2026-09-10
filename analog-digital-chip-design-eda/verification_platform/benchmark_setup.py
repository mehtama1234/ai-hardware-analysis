"""Shared collateral/planning setup for small benchmark adapters."""
from __future__ import annotations
from dataclasses import asdict
import json
from pathlib import Path
from .ingest import ingest_markdown
from .planner import plan_ir, planning_summary, write_plan
from .generator import write_sva_module

def write_planning_artifacts(spec_path: str | Path, run_root: str | Path, *, source_revision: str) -> dict:
    run = Path(run_root); run.mkdir(parents=True, exist_ok=True)
    spec = ingest_markdown(spec_path, root=Path(spec_path).parent, source_revision=source_revision)
    plans = plan_ir(spec)
    spec.checks = [asdict(plan) for plan in plans]
    (run / "specification-ir.json").write_text(json.dumps(spec.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_plan(plans, run / "verification-plan.json")
    write_sva_module(plans, run / "generated_checks.sv")
    (run / "planning-summary.json").write_text(json.dumps(planning_summary(spec), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"requirements": len(spec.requirements), "planned": len(plans), "unplanned": len(spec.requirements) - len(plans)}
