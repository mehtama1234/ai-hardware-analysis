"""Evidence-gated requirement closure evaluation."""

from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from pathlib import Path

from .ir import VerificationIR


@dataclass(frozen=True)
class ClosureResult:
    requirement_id: str
    status: str
    reason: str
    evidence_count: int


def evaluate_closure(ir: VerificationIR) -> list[ClosureResult]:
    """Evaluate closure without allowing an agent to infer proof from prose."""
    ir.validate()
    passed_runs = {run["id"] for run in ir.tool_runs if run.get("status") == "passed"}
    failed_runs = {run["id"] for run in ir.tool_runs if run.get("status") in {"failed", "blocked"}}
    results: list[ClosureResult] = []
    for requirement in ir.requirements:
        if requirement.status == "failed":
            results.append(ClosureResult(requirement.id, "failed", "requirement is linked to a failed check", len(requirement.evidence)))
        elif not requirement.evidence:
            results.append(ClosureResult(requirement.id, "open", "no evidence artifacts are linked", 0))
        elif not passed_runs:
            results.append(ClosureResult(requirement.id, "open", "no passed tool run is recorded", len(requirement.evidence)))
        elif failed_runs:
            results.append(ClosureResult(requirement.id, "open", "a related tool run failed or was blocked", len(requirement.evidence)))
        else:
            results.append(ClosureResult(requirement.id, "proven", "evidence is present and a passed tool run is recorded", len(requirement.evidence)))
    return results


def write_closure(results: list[ClosureResult], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps([asdict(result) for result in results], indent=2, sort_keys=True) + "\n", encoding="utf-8")
