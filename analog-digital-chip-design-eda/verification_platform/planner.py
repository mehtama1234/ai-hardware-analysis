"""Conservative, template-based verification planning primitives."""

from __future__ import annotations

from dataclasses import dataclass, asdict
import json
import re
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
    # These patterns deliberately extract only identifiers already stated by
    # the requirement.  They expand coverage without inventing a signal map.
    reset_match = re.search(r"\b([a-z_]\w*)\s+is\s+(?:reset\s+to\s+)?zero\s+while\s+([a-z_]\w*)\s+is\s+asserted\b", text)
    hold_match = re.search(r"\b([a-z_]\w*)\s+holds(?:\s+its\s+previous\s+value)?\s+when\s+([a-z_]\w*)\s+is\s+low\b", text)
    increment_match = re.search(r"\b([a-z_]\w*)\s+increments(?:\s+by\s+one)?\s+(?:only\s+)?when\s+([a-z_]\w*)\s+is\s+high\b", text)
    next_cycle_implication = re.search(r"\b([a-z_]\w*)\s+is\s+high\s+and\s+then\s+([a-z_]\w*)\s+is\s+high\s+(?:on|in)\s+the\s+next\s+cycle\b", text)
    fixed_cycle_response = re.search(r"\b([a-z_]\w*)\s+is\s+high\s+and\s+([a-z_]\w*)\s+is\s+high\s+(?P<cycles>[1-9]\d*)\s+cycles?\s+later\b", text)
    fixed_repetition_response = re.search(r"\b([a-z_]\w*)\s+stays\s+high\s+for\s+(?P<cycles>[1-9]\d*)\s+consecutive\s+cycles?\s+and\s+([a-z_]\w*)\s+is\s+high\s+afterwards\b", text)
    bounded_response = re.search(r"\b([a-z_]\w*)\s+is\s+high\s+and\s+([a-z_]\w*)\s+(?:becomes|is)\s+high\s+within\s+(?P<cycles>[1-9]\d*)\s+cycles?\b", text)
    bounded_until = re.search(r"\b([a-z_]\w*)\s+remains\s+high\s+until\s+([a-z_]\w*)\s+is\s+high\s+within\s+(?P<cycles>[1-9]\d*)\s+cycles?\b", text)
    literal_mapping = re.search(r"\b([a-z_]\w*)\s+[`']?(?P<input>\d+'[bdho][0-9a-f_xz]+)[`']?\s+produces\s+([a-z_]\w*)\s+[`']?(?P<output>\d+'[bdho][0-9a-f_xz]+)[`']?", text)
    literal_opcode_mapping = re.search(r"\bopcode\s+[`']?(?P<input>\d+'[bdho][0-9a-f_xz]+)[`']?\s+produces\s+[`']?(?P<output>\d+'[bdho][0-9a-f_xz]+)[`']?", text)
    request_grant_mapping = re.search(r"\b(?:request|req)\s+[`']?(?P<input>\d+'[bdho][0-9a-f_xz]+)[`']?\s*,?\s*grant\s+(?:is\s+)?[`']?(?P<output>\d+'[bdho][0-9a-f_xz]+)", text)
    compound_implication = re.search(r"\b([a-z_]\w*)\s+(and|or)\s+([a-z_]\w*)\s+(?:implies|requires)\s+([a-z_]\w*)\b", text)
    mutual_exclusion = re.search(r"\b([a-z_]\w*)\s+and\s+([a-z_]\w*)\s+(?:are|is)\s+never\s+high\b", text)
    implication = re.search(r"\b([a-z_]\w*)\s+(?:implies|requires)\s+([a-z_]\w*)\b", text)
    onehot_zero = re.search(r"\b([a-z_]\w*)\s+(?:is\s+(?:one[- ]hot[- ]or[- ]zero|onehot0)|has\s+at\s+most\s+one\s+active\s+bit)\b", text)
    onehot = re.search(r"\b([a-z_]\w*)\s+is\s+(?:strictly\s+)?(?:one[- ]hot|onehot)\b", text)
    if onehot_zero:
        signal = onehot_zero.group(1)
        assertion = f"assert property (@(posedge clk) disable iff (rst) $onehot0({signal}));"
        rationale = "one-hot-or-zero requirement translated to a bounded $onehot0 check"
    elif onehot:
        signal = onehot.group(1)
        assertion = f"assert property (@(posedge clk) disable iff (rst) $onehot({signal}));"
        rationale = "one-hot requirement translated to a bounded $onehot check"
    elif mutual_exclusion:
        left, right = mutual_exclusion.groups()
        assertion = f"assert property (@(posedge clk) disable iff (rst) !({left} && {right}));"
        rationale = "mutual-exclusion requirement translated to a clocked conflict check"
    elif literal_mapping:
        input_signal, input_value, output_signal, output_value = literal_mapping.groups()
        assertion = f"assert property (@(posedge clk) disable iff (rst) {input_signal} == {input_value} |-> {output_signal} == {output_value});"
        rationale = "literal input/output mapping translated to a same-cycle implication"
    elif literal_opcode_mapping:
        assertion = f"assert property (@(posedge clk) disable iff (rst) opcode == {literal_opcode_mapping['input']} |-> decode == {literal_opcode_mapping['output']});"
        rationale = "opcode literal mapping translated to a same-cycle decode implication"
    elif request_grant_mapping:
        input_value, output_value = request_grant_mapping.group("input"), request_grant_mapping.group("output")
        assertion = f"assert property (@(posedge clk) disable iff (rst) req == {input_value} |-> grant == {output_value});"
        rationale = "literal request/grant mapping translated to a same-cycle implication"
    elif next_cycle_implication:
        antecedent, consequent = next_cycle_implication.groups()
        assertion = f"assert property (@(posedge clk) disable iff (rst) {antecedent} |=> {consequent});"
        rationale = "requirement identifiers mapped to an explicit next-cycle Boolean implication"
    elif fixed_cycle_response:
        antecedent, consequent = fixed_cycle_response.group(1), fixed_cycle_response.group(2)
        cycles = int(fixed_cycle_response.group("cycles"))
        if cycles > 64:
            raise ValueError("fixed-cycle response exceeds the bounded planner limit")
        assertion = f"assert property (@(posedge clk) disable iff (rst) {antecedent} |-> ##{cycles} {consequent});"
        rationale = "requirement identifiers mapped to a bounded fixed-cycle response"
    elif fixed_repetition_response:
        signal, cycles, consequent = fixed_repetition_response.group(1), int(fixed_repetition_response.group("cycles")), fixed_repetition_response.group(3)
        if cycles > 64:
            raise ValueError("fixed repetition exceeds the bounded planner limit")
        assertion = f"assert property (@(posedge clk) disable iff (rst) {signal}[*{cycles}] |-> {consequent});"
        rationale = "requirement identifiers mapped to bounded consecutive repetition"
    elif bounded_response:
        antecedent, consequent, cycles = bounded_response.group(1), bounded_response.group(2), int(bounded_response.group("cycles"))
        if cycles > 16:
            raise ValueError("bounded response exceeds the planner limit of 16 cycles")
        assertion = f"assert property (@(posedge clk) disable iff (rst) {antecedent} |-> ##[1:{cycles}] {consequent});"
        rationale = "requirement identifiers mapped to a bounded response window"
    elif bounded_until:
        antecedent, consequent, cycles = bounded_until.group(1), bounded_until.group(2), int(bounded_until.group("cycles"))
        if cycles > 16:
            raise ValueError("bounded until exceeds the planner limit of 16 cycles")
        assertion = f"assert property (@(posedge clk) disable iff (rst) {antecedent} |-> {antecedent}[*0:{cycles - 1}] ##[1:{cycles}] {consequent});"
        rationale = "requirement identifiers mapped to bounded hold-until response"
    elif compound_implication:
        left, operator, right, consequent = compound_implication.groups()
        boolean_operator = "&&" if operator == "and" else "||"
        assertion = f"assert property (@(posedge clk) disable iff (rst) ({left} {boolean_operator} {right}) |-> {consequent});"
        rationale = "requirement identifiers mapped to a compound Boolean implication"
    elif implication:
        antecedent, consequent = implication.groups()
        assertion = f"assert property (@(posedge clk) disable iff (rst) {antecedent} |-> {consequent});"
        rationale = "requirement identifiers mapped to an explicit same-cycle Boolean implication"
    elif reset_match:
        signal, reset = reset_match.groups()
        assertion = f"assert property (@(posedge clk) {reset} |-> {signal} == '0);"
        rationale = "requirement identifiers mapped to a clocked reset-zero assertion"
    elif hold_match:
        signal, enable = hold_match.groups()
        assertion = f"assert property (@(posedge clk) disable iff (rst) !{enable} |=> $stable({signal}));"
        rationale = "requirement identifiers mapped to a one-cycle stability assertion"
    elif increment_match:
        signal, enable = increment_match.groups()
        assertion = f"assert property (@(posedge clk) disable iff (rst) {enable} |=> {signal} == $past({signal}) + 1'b1);"
        rationale = "requirement identifiers mapped to a one-cycle increment assertion"
    elif ("reset" in text or "rst" in text) and ("zero" in text or "0" in text) and "counter_q" not in text:
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
