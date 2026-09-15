#!/usr/bin/env python3
"""Extract a parent macro without flattening and audit named preamp instances."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


MAGIC = Path("/home/mehtama1/eda-tools/magic-8.3.682/bin/magic")
RCFILE = Path("/home/mehtama1/git-repo/ai-hardware-analysis/analog-digital-chip-design-eda/labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/.magicrc")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    candidate = args.candidate.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    tcl = output / "extract-hierarchical.tcl"
    netlist = output / "hierarchical.spice"
    tcl.write_text(
        "drc on\n"
        f"path search +{candidate}\n"
        "load aimc_converter_macro_active_candidate -force\n"
        "select top cell\n"
        "drc check\ndrc count\nextract all\n"
        "ext2spice hierarchy on\next2spice subcircuit on\n"
        "ext2spice subcircuit top on\next2spice cthresh 0\n"
        "ext2spice rthresh 0\n"
        "ext2spice -o hierarchical.spice\nquit -noprompt\n",
        encoding="utf-8",
    )
    proc = subprocess.run(
        [str(MAGIC), "-dnull", "-noconsole", "-rcfile", str(RCFILE), str(tcl)],
        cwd=output, capture_output=True, text=True, timeout=120,
        env={**__import__("os").environ, "PDK_ROOT": "/home/mehtama1/eda-tools/pdks"},
    )
    log = output / "magic.log"
    log.write_text(proc.stdout + proc.stderr, encoding="utf-8")
    text = netlist.read_text(encoding="utf-8") if netlist.exists() else ""
    subckts = {}
    for match in re.finditer(r"(?ms)^\.subckt\s+(\S+)\s+(.+?)\n(.*?)^\.ends", text):
        subckts[match.group(1)] = match.group(0)
    instances = {}
    top = subckts.get("aimc_converter_macro_active_candidate") or subckts.get("aimc_converter_macro_active_candidate_flat", "")
    for name in ("physical_preamp_p", "physical_preamp_n"):
        rows = []
        lines = top.splitlines()
        for index, line in enumerate(lines):
            if re.match(rf"^X{name}\b", line.strip()):
                instance = line.strip()
                cursor = index + 1
                while cursor < len(lines) and lines[cursor].lstrip().startswith("+"):
                    instance += " " + lines[cursor].strip()[1:].strip()
                    cursor += 1
                rows.append(instance)
        instances[name] = rows
    expected_interfaces = {
        "physical_preamp_p": {
            "ports": [
                "physical_preamp_p/preamp_iso_tail_ext",
                "physical_preamp_p/latch_sense_p_ext",
                "physical_preamp_p/row_drive",
                "vss_escape_uq1",
            ],
            "cell": "preamp_p_parent_bound",
        },
        "physical_preamp_n": {
            "ports": [
                "physical_preamp_n/preamp_iso_tail_ext",
                "physical_preamp_n/latch_sense_n_ext",
                "physical_preamp_n/sar_comparator_input",
                "vss_escape_uq1",
            ],
            "cell": "preamp_n_parent_bound",
        },
    }
    interface_checks = {}
    for name, expected in expected_interfaces.items():
        actual = instances[name][0].split() if len(instances[name]) == 1 else []
        interface_checks[name] = {
            "expected_ports": expected["ports"],
            "actual_instance": instances[name][0] if len(instances[name]) == 1 else None,
            "expected_cell": expected["cell"],
            "ports_exact": actual[1:-1] == expected["ports"],
            "cell_exact": bool(actual) and actual[-1] == expected["cell"],
        }
        interface_checks[name]["passed"] = (
            interface_checks[name]["ports_exact"] and interface_checks[name]["cell_exact"]
        )
    drc_zero = "Total DRC errors found: 0" in log.read_text(encoding="utf-8")
    parent_interface_passed = all(item["passed"] for item in interface_checks.values())
    result = {
        "status": "hierarchical_parent_interface_passed" if proc.returncode == 0 and netlist.exists() and drc_zero and parent_interface_passed else "hierarchical_parent_interface_failed",
        "magic_returncode": proc.returncode,
        "drc_zero": drc_zero,
        "netlist": str(netlist),
        "netlist_sha256": hashlib.sha256(netlist.read_bytes()).hexdigest() if netlist.exists() else None,
        "subcircuits": sorted(subckts),
        "named_preamp_instances": instances,
        "parent_interface_checks": interface_checks,
        "parent_interface_passed": parent_interface_passed,
        "claim_boundary": "Hierarchy-preserving extraction only; instance binding is not analog electrical qualification or commercial signoff.",
    }
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["status"] != "hierarchical_extraction_passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
