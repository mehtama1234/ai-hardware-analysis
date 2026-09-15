import json
from pathlib import Path

import pytest

from verification_platform.registers import (
    generate_c_header,
    generate_register_rtl,
    generate_scoreboard,
    generate_uvm_ral_model,
    load_register_spec,
    load_ipxact_spec,
    load_systemrdl_spec,
    RegisterShadow,
    verify_register_bundle,
    write_register_bundle,
)


def _spec(tmp_path: Path) -> Path:
    path = tmp_path / "register-spec.json"
    path.write_text(json.dumps({
        "schema_version": "register-spec-v1",
        "name": "control",
        "data_width": 32,
        "addr_width": 8,
        "registers": [
            {"name": "status", "offset": 0, "width": 32, "reset": 1, "fields": [
                {"name": "ready", "lsb": 0, "width": 1, "access": "RO", "reset": 1},
                {"name": "error", "lsb": 1, "width": 1, "access": "W1C", "reset": 0},
            ]},
            {"name": "config", "offset": 4, "width": 32, "reset": 0, "fields": [
                {"name": "enable", "lsb": 0, "width": 1, "access": "RW", "reset": 0},
            ]},
        ],
    }), encoding="utf-8")
    return path


def test_register_spec_generates_three_consistent_artifacts(tmp_path):
    spec = load_register_spec(_spec(tmp_path))
    rtl = generate_register_rtl(spec)
    header = generate_c_header(spec)
    ral = generate_uvm_ral_model(spec)
    assert "status[1]" in rtl and "status.ready" in rtl
    assert "CONTROL_STATUS_OFFSET 0x0u" in header
    assert "CONTROL_CONFIG_ENABLE_ACCESS_RW" in header
    assert "control_ral" in ral
    assert spec.digest() in rtl and spec.digest() in header and spec.digest() in ral
    scoreboard = generate_scoreboard(spec)
    assert "expected_status" in scoreboard
    assert "expected_status[1] <= expected_status[1] & ~wdata[1]" in scoreboard
    assert spec.digest() in scoreboard


def test_register_bundle_is_hash_bound_and_detects_tampering(tmp_path):
    spec = load_register_spec(_spec(tmp_path))
    output = tmp_path / "generated"
    manifest = write_register_bundle(spec, output)
    assert verify_register_bundle(spec, output, manifest) == []
    assert manifest["artifacts"]["scoreboard"]["path"] == "control_scoreboard.sv"
    (output / manifest["artifacts"]["c_header"]["path"]).write_text("tampered\n", encoding="utf-8")
    assert "generated artifact digest mismatch: control_regs.h" in verify_register_bundle(spec, output, manifest)


def test_register_bundle_detects_semantic_offset_drift_even_with_rehashed_manifest(tmp_path):
    spec = load_register_spec(_spec(tmp_path))
    output = tmp_path / "generated"
    manifest = write_register_bundle(spec, output)
    rtl_path = output / manifest["artifacts"]["rtl"]["path"]
    rtl_path.write_text(rtl_path.read_text(encoding="utf-8").replace("8'd4", "8'd8"), encoding="utf-8")
    manifest["artifacts"]["rtl"]["sha256"] = __import__("hashlib").sha256(rtl_path.read_bytes()).hexdigest()
    manifest["bundle_sha256"] = __import__("hashlib").sha256(json.dumps({key: value for key, value in manifest.items() if key != "bundle_sha256"}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    errors = verify_register_bundle(spec, output, manifest)
    assert "RTL artifact has wrong address for register: config" in errors


def test_register_bundle_rejects_artifact_path_escape(tmp_path):
    spec = load_register_spec(_spec(tmp_path))
    manifest = write_register_bundle(spec, tmp_path / "generated")
    manifest["artifacts"]["rtl"]["path"] = "../outside.sv"
    assert "generated artifact path escapes bundle: ../outside.sv" in verify_register_bundle(spec, tmp_path / "generated", manifest)


def test_register_spec_rejects_overlapping_fields(tmp_path):
    path = _spec(tmp_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["registers"][0]["fields"].append({"name": "bad", "lsb": 0, "width": 2, "access": "RW", "reset": 0})
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="overlapping fields"):
        load_register_spec(path)


def test_register_spec_rejects_reset_disagreement(tmp_path):
    path = _spec(tmp_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["registers"][0]["fields"][0]["reset"] = 0
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="field reset disagrees"):
        load_register_spec(path)


def test_ipxact_frontend_maps_register_fields_into_same_ir(tmp_path):
    path = tmp_path / "peripheral.xml"
    path.write_text("""<component xmlns:spirit=\"urn:spirit-org:1685-2014\"><spirit:name>peripheral</spirit:name><spirit:memoryMap><spirit:name>map</spirit:name><spirit:addressBlock><spirit:dataWidth>32</spirit:dataWidth><spirit:register><spirit:name>status</spirit:name><spirit:addressOffset>0x4</spirit:addressOffset><spirit:size>32</spirit:size><spirit:field><spirit:name>ready</spirit:name><spirit:bitOffset>0</spirit:bitOffset><spirit:bitWidth>1</spirit:bitWidth><spirit:access>read-only</spirit:access><spirit:reset><spirit:value>0x1</spirit:value></spirit:reset></spirit:field><spirit:field><spirit:name>error</spirit:name><spirit:bitOffset>1</spirit:bitOffset><spirit:bitWidth>1</spirit:bitWidth><spirit:access>write-one-to-clear</spirit:access></spirit:field></spirit:register></spirit:addressBlock></spirit:memoryMap></component>""", encoding="utf-8")
    spec = load_ipxact_spec(path, addr_width=8)
    assert spec.name == "peripheral"
    assert spec.registers[0].offset == 4
    assert [(field.name, field.access, field.reset) for field in spec.registers[0].fields] == [("ready", "RO", 1), ("error", "W1C", 0)]


def test_ipxact_frontend_rejects_unsupported_access(tmp_path):
    path = tmp_path / "bad.xml"
    path.write_text("""<component><name>x</name><register><name>r</name><addressOffset>0</addressOffset><field><name>f</name><bitOffset>0</bitOffset><bitWidth>1</bitWidth><access>write-once</access></field></register></component>""", encoding="utf-8")
    with pytest.raises(ValueError, match="unsupported IP-XACT access"):
        load_ipxact_spec(path)


def test_ipxact_frontend_defaults_omitted_access_to_read_write(tmp_path):
    path = tmp_path / "default-access.xml"
    path.write_text("<component><name>x</name><register><name>r</name><addressOffset>0</addressOffset><field><name>f</name><bitOffset>0</bitOffset><bitWidth>1</bitWidth></field></register></component>", encoding="utf-8")
    spec = load_ipxact_spec(path)
    assert spec.registers[0].fields[0].access == "RW"


def test_systemrdl_frontend_maps_supported_fields_into_same_ir(tmp_path: Path):
    path = tmp_path / "control.rdl"
    path.write_text(
        "addrmap control {\n"
        "  reg status @0x0 {\n"
        "    field { sw = r; reset = 1; } ready[0:0];\n"
        "    field { sw = rw; reset = 0; } enable[1:1];\n"
        "  };\n"
        "  reg events {\n"
        "    field { sw = rw; onwrite = wclr; } error[2:2];\n"
        "  };\n"
        "};\n",
        encoding="utf-8",
    )
    spec = load_systemrdl_spec(path, addr_width=8)
    assert spec.name == "control"
    assert [register.offset for register in spec.registers] == [0, 4]
    assert [(field.name, field.access, field.reset) for field in spec.registers[0].fields] == [
        ("ready", "RO", 1), ("enable", "RW", 0)
    ]
    assert spec.registers[1].fields[0].access == "W1C"
    assert spec.digest()


def test_systemrdl_frontend_rejects_register_without_supported_fields(tmp_path: Path):
    path = tmp_path / "bad.rdl"
    path.write_text("addrmap control { reg status { field status; }; };\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no supported ranged fields"):
        load_systemrdl_spec(path)


def test_register_shadow_enforces_rw_ro_and_w1c_semantics(tmp_path):
    spec = load_register_spec(_spec(tmp_path))
    shadow = RegisterShadow(spec)
    assert shadow.read(0) == 1
    assert shadow.write(4, 1) == 1
    assert shadow.read(4) == 1
    # RO ready remains unchanged; W1C error clears only when written as one.
    shadow.values[0] |= 1 << 1
    assert shadow.write(0, 1) == 3
    assert shadow.write(0, 2) == 1
    with pytest.raises(KeyError, match="unmapped register"):
        shadow.read(8)


def test_register_shadow_rejects_out_of_range_data(tmp_path):
    shadow = RegisterShadow(load_register_spec(_spec(tmp_path)))
    with pytest.raises(ValueError, match="out of range"):
        shadow.write(4, 1 << 32)
