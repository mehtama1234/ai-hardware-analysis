from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.logic import dependency_cone


def test_dependency_cone_follows_assignments(tmp_path):
    rtl = tmp_path / "dut.sv"
    rtl.write_text("assign out = state + enable;\nassign state = input_data;\n", encoding="utf-8")
    assert dependency_cone(rtl, "out") == {"state", "enable", "input_data"}


def test_dependency_cone_includes_procedural_guard_and_ignores_literals(tmp_path):
    rtl = tmp_path / "counter.sv"
    rtl.write_text("always @(posedge clk) if (enable) counter_q <= counter_q + 4'd1;\n", encoding="utf-8")
    assert dependency_cone(rtl, "counter_q") == {"enable"}
