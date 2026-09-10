"""Conservative typed inventory for simple SystemVerilog module ports."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any

from .ledger import evidence_for


MODULE_RE = re.compile(r"module\s+(?P<name>[A-Za-z_]\w*)\s*\((?P<ports>.*?)\)\s*;", re.S)
PORT_RE = re.compile(r"\b(?P<direction>input|output|inout)\s+(?:(?P<kind>logic|wire|reg)\s+)?(?:(?P<range>\[[^\]]+\])\s+)?(?P<name>[A-Za-z_]\w*)")


def ingest_rtl_ports(path: str | Path, *, root: str | Path, source_revision: str) -> dict[str, Any]:
    """Extract module/port direction and declared range with source hash."""
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    if not source_revision:
        raise ValueError("source_revision is required")
    modules = []
    for module in MODULE_RE.finditer(text):
        ports = []
        for port in PORT_RE.finditer(module["ports"]):
            ports.append({"name": port["name"], "direction": port["direction"], "kind": port["kind"] or "implicit", "range": port["range"] or "scalar"})
        modules.append({"name": module["name"], "ports": ports})
    if not modules:
        raise ValueError("no simple SystemVerilog module declaration found")
    source = evidence_for(file_path, root=root, kind="rtl-source", source_revision=source_revision)
    report: dict[str, Any] = {"schema_version": "rtl-collateral-v1", "source": source, "modules": modules}
    report["inventory_sha256"] = hashlib.sha256(json.dumps(report, sort_keys=True, default=lambda value: value.__dict__, separators=(",", ":")).encode()).hexdigest()
    return report


def write_rtl_inventory(path: str | Path, inventory: dict[str, Any]) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(inventory, indent=2, sort_keys=True, default=lambda value: value.__dict__) + "\n", encoding="utf-8")
    return output
