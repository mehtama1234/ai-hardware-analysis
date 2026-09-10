"""Deterministic UVM scaffold generation; execution requires a UVM-capable simulator."""

from __future__ import annotations

from pathlib import Path


def generate_uvm_agent(agent_name: str, signals: list[str]) -> str:
    if not agent_name.isidentifier() or not signals or any(not signal.isidentifier() for signal in signals):
        raise ValueError("agent name and at least one valid signal are required")
    prefix = agent_name.lower()
    signal_declarations = "\n".join(f"  logic {signal};" for signal in signals)
    transaction_fields = "\n".join(f"  rand logic {signal};" for signal in signals)
    return f"""// Generated UVM scaffold; review and compile against the target UVM library.
interface {prefix}_if(input logic clk);
{signal_declarations}
endinterface

class {prefix}_transaction extends uvm_sequence_item;
  `uvm_object_utils({prefix}_transaction)
{transaction_fields}
  function new(string name=\"{prefix}_transaction\"); super.new(name); endfunction
endclass

class {prefix}_agent extends uvm_agent;
  `uvm_component_utils({prefix}_agent)
  function new(string name, uvm_component parent); super.new(name, parent); endfunction
endclass

// Dependency order: interface -> transaction -> driver/monitor -> agent -> scoreboard -> env.
class {prefix}_driver extends uvm_driver #({prefix}_transaction);
  `uvm_component_utils({prefix}_driver)
  function new(string name, uvm_component parent); super.new(name, parent); endfunction
endclass

class {prefix}_monitor extends uvm_monitor;
  `uvm_component_utils({prefix}_monitor)
  function new(string name, uvm_component parent); super.new(name, parent); endfunction
endclass

class {prefix}_scoreboard extends uvm_scoreboard;
  `uvm_component_utils({prefix}_scoreboard)
  function new(string name, uvm_component parent); super.new(name, parent); endfunction
endclass

class {prefix}_env extends uvm_env;
  `uvm_component_utils({prefix}_env)
  {prefix}_agent agent;
  {prefix}_scoreboard scoreboard;
  function new(string name, uvm_component parent); super.new(name, parent); endfunction
endclass
"""


def write_uvm_agent(agent_name: str, signals: list[str], path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(generate_uvm_agent(agent_name, signals), encoding="utf-8")
    return output
