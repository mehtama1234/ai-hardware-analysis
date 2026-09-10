from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.rtl import ingest_rtl_ports, write_rtl_inventory


def test_rtl_inventory_extracts_typed_ports(tmp_path):
    rtl = tmp_path / "counter.sv"
    rtl.write_text("module counter(input logic clk, input logic [3:0] data, output logic q); endmodule\n", encoding="utf-8")
    inventory = ingest_rtl_ports(rtl, root=tmp_path, source_revision="rtl-v1")
    assert inventory["modules"][0]["ports"][1] == {"name": "data", "direction": "input", "kind": "logic", "range": "[3:0]"}
    assert len(inventory["inventory_sha256"]) == 64
    assert write_rtl_inventory(tmp_path / "rtl.json", inventory).is_file()
