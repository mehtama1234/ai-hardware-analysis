from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.ir import Requirement
from verification_platform.planner import plan_requirement
from verification_platform.procedural import generate_procedural_checker


def test_procedural_backend_generates_iverilog_friendly_checker():
    source = generate_procedural_checker([plan_requirement(Requirement("REQ-COUNTER-HOLD", "counter_q holds when enable is low"))])
    assert "always @(posedge clk)" in source
    assert "$display(\"FAIL" in source
    assert "requirement: REQ-COUNTER-HOLD" in source
