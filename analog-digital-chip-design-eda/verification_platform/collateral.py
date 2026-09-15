"""Typed, hash-bound intake for heterogeneous hardware collateral."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any

from .ledger import evidence_for, sha256_file
from .registers import load_ipxact_spec, load_register_spec, load_systemrdl_spec
from .protocol import load_protocol_plan


SUPPORTED_KINDS = {
    "specification", "rtl", "testbench", "reference_model", "register_spec",
    "protocol_plan", "constraints",
}
REQUIREMENT_RE = re.compile(r"^\s*(?P<id>[A-Z][A-Z0-9_-]{2,}):\s*(?P<text>\S.*)$")


def _digest_body(payload: dict[str, Any], key: str) -> str:
    body = {name: value for name, value in payload.items() if name != key}
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _structured_entities(path: Path, kind: str) -> list[dict[str, Any]]:
    if kind == "specification":
        entities = []
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            match = REQUIREMENT_RE.match(line)
            if match:
                entities.append({"kind": "requirement", "id": match["id"], "text": match["text"], "location": {"line": line_number}})
        if not entities:
            raise ValueError("specification contains no explicit requirements")
        return entities
    if kind == "register_spec":
        spec = _load_register_source(path)
        return [{
            # Register names are local to a block.  Keep the normalized
            # entity ID globally stable when a SoC contains multiple blocks
            # that each legitimately define a register named, for example,
            # ``status``.
            "kind": "register", "id": f"{spec.name}.{register.name}",
            "name": register.name, "block": spec.name,
            "data_width": spec.data_width, "addr_width": spec.addr_width,
            "offset": register.offset, "width": register.width, "reset": register.reset,
            "fields": [{"name": field.name, "lsb": field.lsb, "width": field.width, "access": field.access, "reset": field.reset} for field in register.fields],
        } for register in spec.registers]
    if kind == "protocol_plan":
        plan = load_protocol_plan(path)
        return [{"kind": "protocol_step", "id": f"{plan.name}:{index}", **step} for index, step in enumerate(plan.to_dict()["steps"])]
    return []


def _load_register_source(path: Path):
    """Load any supported register source into the canonical register IR."""
    suffix = path.suffix.lower()
    if suffix in {".rdl", ".systemrdl"}:
        return load_systemrdl_spec(path)
    if suffix in {".xml", ".ipxact"}:
        return load_ipxact_spec(path)
    return load_register_spec(path)


def build_collateral_package(
    entries: list[dict[str, str]],
    *,
    root: str | Path,
    source_revision: str,
) -> dict[str, Any]:
    """Build a deterministic intake manifest without giving agents raw authority.

    Supported structured formats are parsed immediately.  Other supported
    kinds are inventoried and hash-bound, but are not treated as parsed
    behavioral truth.
    """
    if not entries or not source_revision:
        raise ValueError("entries and source_revision are required")
    root_path = Path(root).resolve()
    sources: list[dict[str, Any]] = []
    entities: list[dict[str, Any]] = []
    errors: list[str] = []
    seen_paths: set[str] = set()
    seen_entity_ids: dict[str, str] = {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str) or not isinstance(entry.get("kind"), str):
            errors.append(f"entry {index} must contain path and kind")
            continue
        kind, raw_path = entry["kind"], entry["path"]
        if kind not in SUPPORTED_KINDS:
            errors.append(f"unsupported collateral kind: {kind}")
            continue
        path = Path(raw_path)
        if path.is_absolute():
            errors.append(f"collateral path must be relative: {raw_path}")
            continue
        resolved = (root_path / path).resolve()
        try:
            relative = resolved.relative_to(root_path).as_posix()
        except ValueError:
            errors.append(f"collateral path escapes root: {raw_path}")
            continue
        if relative in seen_paths:
            errors.append(f"duplicate collateral path: {relative}")
            continue
        seen_paths.add(relative)
        if not resolved.is_file():
            errors.append(f"collateral file is missing: {relative}")
            continue
        source = evidence_for(resolved, root=root_path, kind=kind, source_revision=source_revision)
        record: dict[str, Any] = {
            "path": source.path, "kind": kind, "sha256": source.sha256,
            "source_revision": source.source_revision, "parser": "inventory-only",
            "status": "passed",
        }
        try:
            parsed = _structured_entities(resolved, kind)
            if kind in {"specification", "register_spec", "protocol_plan"}:
                record["parser"] = f"{kind}-parser-v1"
            if kind == "register_spec":
                normalized = _load_register_source(resolved)
                record["normalized_schema_version"] = normalized.schema_version
                record["normalized_spec_digest"] = normalized.digest()
            for entity in parsed:
                entity_record = {"source": source.path, "source_sha256": source.sha256, **entity}
                entity_id = f"{kind}:{entity.get('id', '')}"
                previous = seen_entity_ids.get(entity_id)
                if previous is not None:
                    errors.append(f"conflicting duplicate entity {entity_id}: {previous} and {source.path}")
                else:
                    seen_entity_ids[entity_id] = source.path
                entities.append(entity_record)
            record["entity_count"] = len(parsed)
        except (OSError, ValueError, KeyError, TypeError) as error:
            record["status"] = "blocked"
            record["error"] = str(error)
            errors.append(f"{relative}: {error}")
        sources.append(record)
    result: dict[str, Any] = {
        "schema_version": "collateral-package-v1",
        "source_revision": source_revision,
        # Keep the package portable; the verification root is supplied by the
        # caller during independent verification and is never part of the
        # evidence identity.
        "root": ".",
        "sources": sources,
        "entities": entities,
        "conflicts": errors,
        "status": "ready" if not errors and sources else "blocked",
        "claim_boundary": "typed, source-digest-bound collateral intake; parsed entities are not verification or signoff evidence",
    }
    result["package_sha256"] = _digest_body(result, "package_sha256")
    return result


def verify_collateral_package(package: dict[str, Any], *, root: str | Path) -> list[str]:
    """Verify package integrity and current source content without reparsing it."""
    errors: list[str] = []
    if package.get("schema_version") != "collateral-package-v1":
        errors.append("unsupported collateral package schema")
    if package.get("package_sha256") != _digest_body(package, "package_sha256"):
        errors.append("collateral package digest does not match")
    if package.get("status") not in {"ready", "blocked"}:
        errors.append("collateral package has invalid status")
    root_path = Path(root).resolve()
    seen_paths: set[str] = set()
    for source in package.get("sources", []):
        if not isinstance(source, dict):
            errors.append("collateral source record is malformed")
            continue
        raw_path = source.get("path", "")
        if raw_path in seen_paths:
            errors.append(f"duplicate collateral source record: {raw_path}")
        seen_paths.add(raw_path)
        if source.get("kind") not in SUPPORTED_KINDS:
            errors.append(f"collateral source has unsupported kind: {raw_path}")
        if source.get("source_revision") != package.get("source_revision"):
            errors.append(f"collateral source revision mismatch: {raw_path}")
        if source.get("status") not in {"passed", "blocked"}:
            errors.append(f"collateral source has invalid status: {raw_path}")
        if package.get("status") == "ready" and source.get("status") != "passed":
            errors.append(f"ready collateral package contains blocked source: {raw_path}")
        path = (root_path / raw_path).resolve()
        try:
            path.relative_to(root_path)
        except ValueError:
            errors.append(f"collateral source escapes root: {raw_path}")
            continue
        if not path.is_file():
            errors.append(f"collateral source is missing: {raw_path}")
        elif sha256_file(path) != source.get("sha256"):
            errors.append(f"collateral source digest mismatch: {raw_path}")
        elif source.get("kind") in {"specification", "register_spec", "protocol_plan"} and source.get("status") == "passed":
            try:
                expected_entities = [
                    {"source": source["path"], "source_sha256": source["sha256"], **entity}
                    for entity in _structured_entities(path, source["kind"])
                ]
                actual_entities = [
                    entity for entity in package.get("entities", [])
                    if isinstance(entity, dict) and entity.get("source") == source.get("path")
                ]
                canonical = lambda value: json.dumps(value, sort_keys=True, separators=(",", ":"))
                if sorted(map(canonical, actual_entities)) != sorted(map(canonical, expected_entities)):
                    errors.append(f"structured entity drift detected: {raw_path}")
                if source["kind"] == "register_spec" and source.get("normalized_spec_digest"):
                    if source["normalized_spec_digest"] != _load_register_source(path).digest():
                        errors.append(f"normalized register specification drift detected: {raw_path}")
            except (OSError, ValueError, KeyError, TypeError) as error:
                errors.append(f"cannot reparse structured collateral {raw_path}: {error}")
    if package.get("status") == "ready" and (package.get("conflicts") or not package.get("sources")):
        errors.append("ready collateral package contains conflicts")
    return errors


def write_collateral_package(package: dict[str, Any], path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(package, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output
