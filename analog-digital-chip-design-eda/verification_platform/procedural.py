"""Open-source-compatible procedural checker generation."""

from __future__ import annotations

from pathlib import Path

from .planner import CheckPlan


def generate_procedural_checker(plans: list[CheckPlan], *, module_name: str = "procedural_checks") -> str:
    if not module_name.isidentifier():
        raise ValueError("module name must be an identifier")
    lines = [f"// Generated procedural checker; {len(plans)} approved plans", f"module {module_name}(input logic clk, input logic rst, input logic enable, input logic [3:0] counter_q);", "  logic [3:0] previous_counter_q;", "  logic previous_valid;", "  initial begin previous_counter_q = '0; previous_valid = 1'b0; end", "  always @(posedge clk) begin"]
    for plan in plans:
        lines.append(f"    // requirement: {plan.requirement_id}")
        if "HOLD" in plan.requirement_id:
            lines.append("    if (previous_valid && !rst && !enable && counter_q !== previous_counter_q) $display(\"FAIL cycle=%0t signal=counter_q expected=%0d actual=%0d\", $time, previous_counter_q, counter_q);")
        elif "RESET" in plan.requirement_id:
            lines.append("    if (rst && counter_q !== 4'd0) $display(\"FAIL cycle=%0t signal=counter_q expected=0 actual=%0d\", $time, counter_q);")
        elif "ENABLE" in plan.requirement_id:
            lines.append("    if (previous_valid && !rst && enable && counter_q !== previous_counter_q + 1'b1) $display(\"FAIL cycle=%0t signal=counter_q increment\", $time);")
    lines.extend(["    previous_counter_q <= counter_q;", "    previous_valid <= 1'b1;", "  end", "endmodule", ""])
    return "\n".join(lines)


def write_procedural_checker(plans: list[CheckPlan], path: str | Path, *, module_name: str = "procedural_checks") -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(generate_procedural_checker(plans, module_name=module_name), encoding="utf-8")
    return output
