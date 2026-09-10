"""Deterministic collateral-to-IR ingestion for customer projects."""
from __future__ import annotations
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from verification_platform.ingest import ingest_markdown
from verification_platform.ir import VerificationIR

MODULE_RE = re.compile(r"\bmodule\s+(?P<name>[A-Za-z_][A-Za-z0-9_$]*)")
PORT_RE = re.compile(r"\b(input|output|inout)\s+(?:logic|wire|reg)?\s*(?:\[[^]]+\])?\s*(?P<name>[A-Za-z_][A-Za-z0-9_$]*)")

def ingest_artifact(record: dict[str, Any], *, artifact_root: str | Path, output_root: str | Path) -> dict[str, Any]:
    source = Path(artifact_root) / str(record["path"])
    content = source.read_text(encoding="utf-8")
    ir: VerificationIR
    try:
        ir = ingest_markdown(source, root=artifact_root, source_revision=str(record["version"]))
    except ValueError:
        ir = VerificationIR(design_revision=str(record["version"]))
    modules = sorted(set(match.group("name") for match in MODULE_RE.finditer(content)))
    ports = sorted(set(match.group("name") for match in PORT_RE.finditer(content)))
    ir.checks = [{"type": "module", "name": name} for name in modules]
    ir.checks.extend({"type": "port", "name": name} for name in ports)
    ir.validate()
    destination = Path(output_root) / str(record["project_id"]) / "ir"
    destination.mkdir(parents=True, exist_ok=True)
    output = destination / f"{record['id']}.json"
    payload = ir.to_dict()
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    return {"artifact_id": record["id"], "project_id": record["project_id"], "requirements": len(ir.requirements), "modules": modules, "ports": ports, "ir_path": str(output), "ir_sha256": digest, "schema_version": ir.schema_version}
