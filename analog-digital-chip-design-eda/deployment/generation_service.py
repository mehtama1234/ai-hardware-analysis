"""Persist traceable checker and UVM artifacts from a stored verification plan."""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
from pathlib import Path
from typing import Any

from verification_platform.generator import write_sva_module
from verification_platform.planner import CheckPlan
from verification_platform.procedural import write_procedural_checker
from verification_platform.uvm import write_uvm_agent


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generate_persisted_plan(
    plan_path: str | Path,
    *,
    output_root: str | Path,
    project_id: str,
    artifact_id: str,
    signals: list[str] | None = None,
) -> dict[str, Any]:
    """Generate reviewable artifacts without modifying customer collateral.

    The procedural checker is the open-source execution candidate. Concurrent
    SVA and UVM remain explicitly review-only until the target tool/library
    capability is measured by an execution adapter.
    """
    source = Path(plan_path)
    payload = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("verification plan must be a list")
    plans = [CheckPlan(**item) for item in payload]
    destination = Path(output_root) / project_id / "generated" / artifact_id
    destination.mkdir(parents=True, exist_ok=True)

    sva_path = destination / "generated_checks.sv"
    procedural_path = destination / "procedural_checks.sv"
    uvm_path = destination / "uvm_agent.sv"
    write_sva_module(plans, sva_path)
    write_procedural_checker(plans, procedural_path)
    selected_signals = sorted(set(signals or ["clk", "rst", "enable", "counter_q"]))
    write_uvm_agent("verification", selected_signals, uvm_path)

    files = {
        "sva": {"path": str(sva_path), "sha256": _digest(sva_path), "status": "review_only"},
        "procedural": {"path": str(procedural_path), "sha256": _digest(procedural_path), "status": "execution_candidate"},
        "uvm": {"path": str(uvm_path), "sha256": _digest(uvm_path), "status": "review_only"},
    }
    manifest = {
        "schema_version": "verification-generated-artifacts-v1",
        "project_id": project_id,
        "artifact_id": artifact_id,
        "plan_path": str(source),
        "plan_sha256": _digest(source),
        "plans": [asdict(plan) for plan in plans],
        "files": files,
        "execution_candidate": "procedural",
    }
    manifest_path = destination / "generation-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest["manifest_path"] = str(manifest_path)
    manifest["manifest_sha256"] = _digest(manifest_path)
    return manifest
