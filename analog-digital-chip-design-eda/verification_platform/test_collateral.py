import hashlib
import json
from pathlib import Path

from verification_platform.collateral import build_collateral_package, verify_collateral_package, write_collateral_package


def _sources(tmp_path: Path):
    spec = tmp_path / "spec.md"
    spec.write_text("REQ-ONE: reset output\n", encoding="utf-8")
    registers = tmp_path / "registers.json"
    registers.write_text(json.dumps({
        "schema_version": "register-spec-v1", "name": "ctrl", "data_width": 32, "addr_width": 8,
        "registers": [{"name": "status", "offset": 0, "width": 32, "reset": 1, "fields": [{"name": "ready", "lsb": 0, "width": 1, "access": "RO", "reset": 1}]}],
    }), encoding="utf-8")
    protocol = tmp_path / "protocol.json"
    protocol.write_text(json.dumps({"schema_version": "protocol-plan-v1", "name": "p", "addr_width": 8, "data_width": 32, "steps": [{"operation": "read", "address": 0, "expected": 1}]}), encoding="utf-8")
    return spec, registers, protocol


def test_collateral_package_parses_supported_entities_and_verifies_sources(tmp_path: Path):
    spec, registers, protocol = _sources(tmp_path)
    package = build_collateral_package(
        [{"path": spec.name, "kind": "specification"}, {"path": registers.name, "kind": "register_spec"}, {"path": protocol.name, "kind": "protocol_plan"}],
        root=tmp_path, source_revision="collateral-v1",
    )
    assert package["status"] == "ready"
    assert {item["kind"] for item in package["entities"]} == {"requirement", "register", "protocol_step"}
    register_source = next(item for item in package["sources"] if item["kind"] == "register_spec")
    assert register_source["normalized_schema_version"] == "register-spec-v1"
    assert len(register_source["normalized_spec_digest"]) == 64
    assert verify_collateral_package(package, root=tmp_path) == []
    output = write_collateral_package(package, tmp_path / "run" / "collateral.json")
    assert output.is_file()


def test_collateral_package_blocks_parse_errors_and_duplicate_entities(tmp_path: Path):
    spec, registers, _ = _sources(tmp_path)
    duplicate = tmp_path / "spec-copy.md"
    duplicate.write_text(spec.read_text(encoding="utf-8"), encoding="utf-8")
    package = build_collateral_package(
        [{"path": spec.name, "kind": "specification"}, {"path": duplicate.name, "kind": "specification"}, {"path": registers.name, "kind": "wrong"}],
        root=tmp_path, source_revision="collateral-v2",
    )
    assert package["status"] == "blocked"
    assert any("duplicate entity specification:REQ-ONE" in item for item in package["conflicts"])
    assert any("unsupported collateral kind" in item for item in package["conflicts"])


def test_collateral_package_namespaces_register_entities_by_block(tmp_path: Path):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    template = {
        "schema_version": "register-spec-v1", "data_width": 32, "addr_width": 8,
        "registers": [{"name": "status", "offset": 0, "width": 32, "reset": 0,
                        "fields": [{"name": "ready", "lsb": 0, "width": 1, "access": "RO", "reset": 0}]}],
    }
    first.write_text(json.dumps({**template, "name": "block_a"}), encoding="utf-8")
    second.write_text(json.dumps({**template, "name": "block_b"}), encoding="utf-8")
    package = build_collateral_package(
        [{"path": first.name, "kind": "register_spec"}, {"path": second.name, "kind": "register_spec"}],
        root=tmp_path, source_revision="collateral-register-blocks-v1",
    )
    assert package["status"] == "ready"
    assert {entity["id"] for entity in package["entities"]} == {"block_a.status", "block_b.status"}
    assert verify_collateral_package(package, root=tmp_path) == []


def test_collateral_package_accepts_ipxact_suffix(tmp_path: Path):
    source = tmp_path / "control.ipxact"
    source.write_text(
        "<component><name>control</name><memoryMap><addressBlock><dataWidth>32</dataWidth>"
        "<register><name>status</name><addressOffset>0x0</addressOffset><size>32</size>"
        "<field><name>ready</name><bitOffset>0</bitOffset><bitWidth>1</bitWidth>"
        "<access>read-only</access></field></register></addressBlock></memoryMap></component>",
        encoding="utf-8",
    )
    package = build_collateral_package(
        [{"path": source.name, "kind": "register_spec"}],
        root=tmp_path, source_revision="collateral-ipxact-v1",
    )
    assert package["status"] == "ready"
    assert package["entities"][0]["id"] == "control.status"
    assert verify_collateral_package(package, root=tmp_path) == []


def test_collateral_package_detects_source_drift(tmp_path: Path):
    spec, _, _ = _sources(tmp_path)
    package = build_collateral_package([{"path": spec.name, "kind": "specification"}], root=tmp_path, source_revision="collateral-v3")
    spec.write_text("REQ-ONE: changed\n", encoding="utf-8")
    assert verify_collateral_package(package, root=tmp_path) == [f"collateral source digest mismatch: {spec.name}"]


def test_collateral_package_detects_rehashed_entity_drift(tmp_path: Path):
    spec, _, _ = _sources(tmp_path)
    package = build_collateral_package([{"path": spec.name, "kind": "specification"}], root=tmp_path, source_revision="collateral-v4")
    package["entities"][0]["text"] = "fabricated meaning"
    package["package_sha256"] = hashlib.sha256(json.dumps({key: value for key, value in package.items() if key != "package_sha256"}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    errors = verify_collateral_package(package, root=tmp_path)
    assert "structured entity drift detected: spec.md" in errors


def test_collateral_package_rejects_inconsistent_rehashed_source_record(tmp_path: Path):
    spec, _, _ = _sources(tmp_path)
    package = build_collateral_package([{"path": spec.name, "kind": "specification"}], root=tmp_path, source_revision="collateral-v5")
    package["sources"][0]["status"] = "blocked"
    package["package_sha256"] = hashlib.sha256(json.dumps({key: value for key, value in package.items() if key != "package_sha256"}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    errors = verify_collateral_package(package, root=tmp_path)
    assert "ready collateral package contains blocked source: spec.md" in errors


def test_collateral_package_detects_rehashed_normalized_register_drift(tmp_path: Path):
    _, registers, _ = _sources(tmp_path)
    package = build_collateral_package([{"path": registers.name, "kind": "register_spec"}], root=tmp_path, source_revision="collateral-register-digest-v1")
    source = package["sources"][0]
    source["normalized_spec_digest"] = "0" * 64
    package["package_sha256"] = hashlib.sha256(json.dumps({key: value for key, value in package.items() if key != "package_sha256"}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert f"normalized register specification drift detected: {registers.name}" in verify_collateral_package(package, root=tmp_path)
