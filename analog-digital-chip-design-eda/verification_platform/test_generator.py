from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.generator import generate_sva_module
from verification_platform.ir import Requirement
from verification_platform.planner import plan_requirement


def test_generated_sva_retains_requirement_traceability():
    source = generate_sva_module([plan_requirement(Requirement("REQ-1", "counter_q holds when enable is low"))])
    assert "requirement: REQ-1" in source
    assert "assert property" in source
    assert source.endswith("endmodule\n")
