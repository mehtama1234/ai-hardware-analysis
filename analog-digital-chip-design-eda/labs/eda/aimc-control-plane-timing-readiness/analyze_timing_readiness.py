#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = ROOT / "labs" / "digital" / "aimc-control-plane-synthesis" / "reports"
REQUEST_NETLIST = REPORT_DIR / "aimc_control_plane_synth.v"
REQUEST_LOG = REPORT_DIR / "aimc_control_plane_synth.log"
OPERATION_NETLIST = REPORT_DIR / "aimc_operation_partition_synth.v"
OPERATION_LOG = REPORT_DIR / "aimc_operation_partition_synth.log"


def stat_value(cell_name: str, text: str) -> int:
    match = re.search(rf"^\s+{re.escape(cell_name)}\s+(\d+)\s*$", text, re.MULTILINE)
    if not match:
        return 0
    return int(match.group(1))


def main() -> int:
    if not REQUEST_NETLIST.exists():
        print(f"FAIL missing synthesized netlist: {REQUEST_NETLIST}")
        print("Run: cd labs/digital/aimc-control-plane-synthesis && yosys synth_aimc_control_plane.ys")
        return 1
    if not REQUEST_LOG.exists():
        print(f"FAIL missing Yosys log: {REQUEST_LOG}")
        return 1
    if not OPERATION_NETLIST.exists():
        print(f"FAIL missing synthesized netlist: {OPERATION_NETLIST}")
        print("Run: cd labs/digital/aimc-control-plane-synthesis && yosys synth_aimc_operation_partition.ys")
        return 1
    if not OPERATION_LOG.exists():
        print(f"FAIL missing Yosys log: {OPERATION_LOG}")
        return 1

    request_netlist = REQUEST_NETLIST.read_text(encoding="utf-8")
    request_log = REQUEST_LOG.read_text(encoding="utf-8")
    operation_netlist = OPERATION_NETLIST.read_text(encoding="utf-8")
    operation_log = OPERATION_LOG.read_text(encoding="utf-8")
    request_dff_bits = stat_value("$_DFF_PN0_", request_log) + stat_value("$_DFF_PN1_", request_log)
    operation_dff_bits = stat_value("$_DFF_PN0_", operation_log) + stat_value("$_DFF_PN1_", operation_log)
    request_memory_line = "Number of memories:               0" in request_log
    request_process_line = "Number of processes:              0" in request_log
    operation_memory_line = "Number of memories:               0" in operation_log
    operation_process_line = "Number of processes:              0" in operation_log
    registered_path = "output reg [1:0] path" not in request_netlist and "output [1:0] path" in request_netlist
    registered_reason = "output reg [2:0] reason" not in request_netlist and "output [2:0] reason" in request_netlist
    combinational_placement = "output reg [1:0] placement" not in operation_netlist and "output [1:0] placement" in operation_netlist
    combinational_reason = "output reg [3:0] reason" not in operation_netlist and "output [3:0] reason" in operation_netlist

    print("aimc_control_plane_timing_readiness")
    print("status,ready_for_sta_not_timing_closed")
    print(f"request_dff_bits,{request_dff_bits}")
    print(f"request_and_cells,{stat_value('$_AND_', request_log)}")
    print(f"request_or_cells,{stat_value('$_OR_', request_log)}")
    print(f"request_xor_cells,{stat_value('$_XOR_', request_log)}")
    print(f"request_mux_cells,{stat_value('$_MUX_', request_log)}")
    print(f"request_not_cells,{stat_value('$_NOT_', request_log)}")
    print(f"request_no_memories,{str(request_memory_line).lower()}")
    print(f"request_no_processes,{str(request_process_line).lower()}")
    print(f"request_path_output_lowered,{str(registered_path).lower()}")
    print(f"request_reason_output_lowered,{str(registered_reason).lower()}")
    print(f"operation_dff_bits,{operation_dff_bits}")
    print(f"operation_and_cells,{stat_value('$_AND_', operation_log)}")
    print(f"operation_or_cells,{stat_value('$_OR_', operation_log)}")
    print(f"operation_xor_cells,{stat_value('$_XOR_', operation_log)}")
    print(f"operation_mux_cells,{stat_value('$_MUX_', operation_log)}")
    print(f"operation_not_cells,{stat_value('$_NOT_', operation_log)}")
    print(f"operation_no_memories,{str(operation_memory_line).lower()}")
    print(f"operation_no_processes,{str(operation_process_line).lower()}")
    print(f"operation_placement_output_lowered,{str(combinational_placement).lower()}")
    print(f"operation_reason_output_lowered,{str(combinational_reason).lower()}")
    print("missing_for_timing,liberty_cell_delays")
    print("missing_for_timing,wire_delays")
    print("missing_for_timing,clock_period")
    print("missing_for_timing,input_arrival_and_output_required_times")
    print("claim,request_and_operation_partition_structure_available_but_timing_not_proven")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
