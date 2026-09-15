"""Schema-bound protocol plans and deterministic sequence generation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import hashlib
import json
from pathlib import Path
import re
from typing import Any


IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
OPERATIONS = {"write", "read", "poll"}


@dataclass(frozen=True)
class ProtocolStep:
    operation: str
    address: int
    data: int = 0
    expected: int = 0
    timeout_cycles: int = 16


def augment_protocol_plan(plan: "ProtocolPlan", gaps: list[dict[str, Any]]) -> "ProtocolPlan":
    """Add validated coverage-gap transactions in deterministic order.

    A gap is an agent proposal, not evidence of coverage.  The returned plan
    must still be executed and measured by the verification flow.
    """
    plan.validate()
    existing = {(step.operation, step.address, step.data, step.expected, step.timeout_cycles) for step in plan.steps}
    additions: list[ProtocolStep] = []
    for index, raw in enumerate(gaps):
        if not isinstance(raw, dict):
            raise ValueError(f"coverage gap at index {index} must be an object")
        step = ProtocolStep(
            operation=str(raw.get("operation", "")), address=int(raw.get("address", -1)),
            data=int(raw.get("data", 0)), expected=int(raw.get("expected", 0)),
            timeout_cycles=int(raw.get("timeout_cycles", 16)),
        )
        candidate = (step.operation, step.address, step.data, step.expected, step.timeout_cycles)
        if candidate not in existing:
            additions.append(step)
            existing.add(candidate)
    additions.sort(key=lambda step: (step.address, step.operation, step.data, step.expected, step.timeout_cycles))
    augmented = replace(plan, steps=plan.steps + tuple(additions))
    augmented.validate()
    return augmented


@dataclass(frozen=True)
class ProtocolPlan:
    name: str
    clock: str
    reset: str
    addr_width: int
    data_width: int
    valid: str
    ready: str
    address: str
    write: str
    write_data: str
    read_data: str
    steps: tuple[ProtocolStep, ...]
    schema_version: str = "protocol-plan-v1"

    def validate(self) -> None:
        if self.schema_version != "protocol-plan-v1":
            raise ValueError("unsupported protocol plan schema")
        names = (self.name, self.clock, self.reset, self.valid, self.ready, self.address, self.write, self.write_data, self.read_data)
        if any(not IDENTIFIER.fullmatch(name) for name in names):
            raise ValueError("protocol plan contains an invalid identifier")
        if self.addr_width <= 0 or self.data_width <= 0 or self.data_width % 8:
            raise ValueError("protocol widths must be positive and data_width must be byte aligned")
        max_address = (1 << self.addr_width) - 1
        max_data = (1 << self.data_width) - 1
        if not self.steps:
            raise ValueError("protocol plan must contain at least one step")
        for index, step in enumerate(self.steps):
            if step.operation not in OPERATIONS:
                raise ValueError(f"unsupported protocol operation at step {index}: {step.operation}")
            if step.address < 0 or step.address > max_address:
                raise ValueError(f"protocol address is out of range at step {index}")
            if step.data < 0 or step.data > max_data or step.expected < 0 or step.expected > max_data:
                raise ValueError(f"protocol data is out of range at step {index}")
            if step.timeout_cycles <= 0:
                raise ValueError(f"protocol timeout must be positive at step {index}")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)

    def digest(self) -> str:
        return hashlib.sha256(json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_protocol_plan(path: str | Path) -> ProtocolPlan:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("protocol plan must be an object")
    steps = tuple(ProtocolStep(
        operation=str(raw["operation"]),
        address=int(raw["address"]),
        data=int(raw.get("data", 0)),
        expected=int(raw.get("expected", 0)),
        timeout_cycles=int(raw.get("timeout_cycles", 16)),
    ) for raw in payload.get("steps", []))
    plan = ProtocolPlan(
        name=str(payload.get("name", "")), clock=str(payload.get("clock", "clk")), reset=str(payload.get("reset", "rst")),
        addr_width=int(payload.get("addr_width", 0)), data_width=int(payload.get("data_width", 0)),
        valid=str(payload.get("valid", "req_valid")), ready=str(payload.get("ready", "req_ready")),
        address=str(payload.get("address", "req_addr")), write=str(payload.get("write", "req_write")),
        write_data=str(payload.get("write_data", "req_wdata")), read_data=str(payload.get("read_data", "rsp_rdata")), steps=steps,
        schema_version=str(payload.get("schema_version", "")),
    )
    plan.validate()
    return plan


def generate_protocol_sequence(plan: ProtocolPlan) -> str:
    """Generate a compile-ready, handshake-safe procedural sequence module."""
    plan.validate()
    module = f"{plan.name}_sequence"
    ports = [f"input logic {plan.clock}", f"input logic {plan.reset}", f"output logic {plan.valid}", f"output logic {plan.write}", f"output logic [{plan.addr_width - 1}:0] {plan.address}", f"output logic [{plan.data_width - 1}:0] {plan.write_data}", f"input logic {plan.ready}", f"input logic [{plan.data_width - 1}:0] {plan.read_data}", "output logic error"]
    lines = [f"// Generated protocol-plan-v1 digest {plan.digest()}", f"module {module}({', '.join(ports)});", "  integer timeout;", "  integer completed_steps;", "  initial begin", f"    {plan.valid} = 1'b0; {plan.write} = 1'b0; {plan.address} = '0; {plan.write_data} = '0; error = 1'b0; completed_steps = 0;", f"    wait (!{plan.reset});"]
    for index, step in enumerate(plan.steps):
        lines.append(f"    // step {index}: {step.operation} address=0x{step.address:X}")
        lines.append(f"    {plan.address} = {plan.addr_width}'h{step.address:x};")
        lines.append(f"    {plan.write} = 1'b{1 if step.operation == 'write' else 0};")
        lines.append(f"    {plan.write_data} = {plan.data_width}'h{step.data:x};")
        lines.append(f"    {plan.valid} = 1'b1; timeout = 0;")
        lines.append(f"    while (!{plan.ready} && timeout < {step.timeout_cycles}) begin @(posedge {plan.clock}); timeout = timeout + 1; end")
        lines.append(f"    if (!{plan.ready}) error = 1'b1; else completed_steps = completed_steps + 1;")
        lines.append(f"    @(posedge {plan.clock}); #1 {plan.valid} = 1'b0;")
        if step.operation in {"read", "poll"}:
            lines.append(f"    if ({plan.read_data} !== {plan.data_width}'h{step.expected:x}) error = 1'b1;")
    lines.extend([f'    $display("PROTOCOL_SEQUENCE_COVERAGE covered=%0d total={len(plan.steps)}", completed_steps);', '    if (error) $display("PROTOCOL_SEQUENCE_RESULT status=failed");', '    else $display("PROTOCOL_SEQUENCE_RESULT status=passed");', "    $finish;", "  end", "endmodule", ""])
    return "\n".join(lines)


def write_protocol_sequence(plan: ProtocolPlan, path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(generate_protocol_sequence(plan), encoding="utf-8")
    return output
