"""Build conservative verification plans from persisted verification IR."""
from __future__ import annotations
from dataclasses import asdict
import json
from pathlib import Path
from typing import Any

from verification_platform.ir import EvidenceRef, Requirement, VerificationIR
from verification_platform.planner import plan_ir, planning_summary

def plan_persisted_ir(ir_path: str | Path, *, output_root: str | Path, project_id: str, artifact_id: str) -> dict[str, Any]:
    payload = json.loads(Path(ir_path).read_text(encoding="utf-8"))
    requirements = []
    for item in payload.get("requirements", []):
        source = item.get("source")
        requirements.append(Requirement(id=item["id"], text=item["text"], status=item.get("status", "planned"), source=EvidenceRef(**source) if source else None, evidence=[EvidenceRef(**ref) for ref in item.get("evidence", [])]))
    ir = VerificationIR(schema_version=payload.get("schema_version", "verification-ir-v1"), design_revision=payload.get("design_revision", "unknown"), requirements=requirements, checks=payload.get("checks", []), tool_runs=payload.get("tool_runs", []), closure_decisions=payload.get("closure_decisions", []))
    ir.validate()
    plans = plan_ir(ir)
    summary = planning_summary(ir)
    destination = Path(output_root) / project_id / "plans"
    destination.mkdir(parents=True, exist_ok=True)
    output = destination / f"{artifact_id}.json"
    output.write_text(json.dumps([asdict(plan) for plan in plans], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"project_id": project_id, "artifact_id": artifact_id, "plan_path": str(output), "plans": [asdict(plan) for plan in plans], "summary": summary}
