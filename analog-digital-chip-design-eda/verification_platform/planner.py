"""Conservative, template-based verification planning primitives."""

from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from pathlib import Path

from .ir import Requirement, VerificationIR


@dataclass(frozen=True)
class CheckPlan:
    id: str
    requirement_id: str
    kind: str
    assertion: str
    rationale: str


def plan_requirement(requirement: Requirement) -> CheckPlan:
    """Generate a bounded assertion template only for recognized requirement forms."""
    text = requirement.text.lower()
    if ("reset" in text or "rst" in text) and ("zero" in text or "0" in text) and "counter_q" not in text:
        signal = "reg0" if "reg0" in text else "control" if "control" in text else "count" if "count" in text else "ready" if "ready" in text else "counter_q"
        assertion = f"assert property (@(posedge clk) rst |-> {signal} == '0);"
        rationale = "reset requirement mapped to a clocked zero-state assertion"
    elif "hold" in text and "enable" in text:
        assertion = "assert property (@(posedge clk) disable iff (rst) !enable |=> $stable(counter_q));"
        rationale = "hold requirement mapped to a one-cycle stability assertion"
    elif "increment" in text and "enable" in text:
        assertion = "assert property (@(posedge clk) disable iff (rst) enable |=> counter_q == $past(counter_q) + 1'b1);"
        rationale = "enable requirement mapped to a one-cycle increment assertion"
    elif "never exceeds" in text and "count" in text:
        assertion = "assert property (@(posedge clk) count <= 2);"
        rationale = "FIFO bound requirement mapped to a depth-two count invariant"
    elif "write" in text and "not full" in text and "count" in text:
        assertion = "assert property (@(posedge clk) wr_en && count < 2 |=> count == $past(count) + 1'b1);"
        rationale = "FIFO write requirement mapped to a full-gated count increment"
    elif "nonzero address" in text and ("reg0" in text or "control" in text):
        signal = "reg0" if "reg0" in text else "control"
        assertion = f"assert property (@(posedge clk) wr_en && addr != 0 |=> $stable({signal}));"
        rationale = "register address requirement mapped to a nonzero-write stability assertion"
    elif "address zero" in text and "wdata" in text and ("reg0" in text or "control" in text):
        signal = "reg0" if "reg0" in text else "control"
        assertion = f"assert property (@(posedge clk) wr_en && addr == 0 |=> {signal} == $past(wdata));"
        rationale = "register write requirement mapped to an addressed data update assertion"
    else:
        raise ValueError(f"no safe assertion template for requirement {requirement.id}")
    return CheckPlan(f"CHECK-{requirement.id}", requirement.id, "sva", assertion, rationale)


def plan_ir(ir: VerificationIR) -> list[CheckPlan]:
    """Plan recognized requirements and leave unsupported ones for human review."""
    plans: list[CheckPlan] = []
    for requirement in ir.requirements:
        try:
            plans.append(plan_requirement(requirement))
        except ValueError:
            continue
    return plans


def planning_summary(ir: VerificationIR) -> dict[str, object]:
    """Return planned and human-review requirements without hiding failures."""
    planned, unplanned = [], []
    for requirement in ir.requirements:
        try:
            plan = plan_requirement(requirement)
            planned.append(plan.requirement_id)
        except ValueError as exc:
            unplanned.append({"requirement_id": requirement.id, "reason": str(exc)})
    return {"planned": planned, "unplanned": unplanned, "total": len(ir.requirements)}


def write_plan(plans: list[CheckPlan], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps([asdict(plan) for plan in plans], indent=2, sort_keys=True) + "\n", encoding="utf-8")
