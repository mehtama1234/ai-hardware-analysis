#!/usr/bin/env python3
"""Check the intended preamp path in the final flat simulated SPICE view."""

import argparse
import hashlib
import json
from pathlib import Path


def audit(text):
    lines = []
    for raw in text.splitlines():
        line = raw.split(";", 1)[0].strip()
        if line.startswith("+") and lines:
            lines[-1] += " " + line[1:].strip()
        elif line and not line.startswith("*"):
            lines.append(line)
    devices = []
    for line in lines:
        fields = line.split()
        if fields[0].lower().startswith("x") and len(fields) >= 6 and fields[5] == "sky130_fd_pr__nfet_01v8":
            devices.append({"name": fields[0], "drain": fields[1], "gate": fields[2], "source": fields[3], "bulk": fields[4]})
    pair = [d for d in devices if "preamp_iso_tail_ext" in (d["drain"], d["source"])]
    checks = {}
    for side, gate, output in (("p", "row_drive", "latch_sense_p_ext"), ("n", "sar_comparator_input", "latch_sense_n_ext")):
        checks[side] = any(d["gate"] == gate and {d["drain"], d["source"]} == {"preamp_iso_tail_ext", output}
                           and d["bulk"] == "vss_escape" for d in pair)
    return {"schema_version": "extracted-preamp-boundary-audit-v1", "preamp_devices": pair,
            "input_to_latch_branches": checks, "physical_preamp_routing_complete": len(pair) == 2 and all(checks.values()),
            "scope": "Exact flat SKY130 macro boundary; other naming/topology is unverified, not automatically accepted.",
            "claim_boundary": "Connectivity only; does not establish gain, polarity, DRC/LVS, or converter acceptance."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--netlist", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.netlist.read_text())
    result["source"] = str(args.netlist.resolve())
    result["source_sha256"] = hashlib.sha256(args.netlist.read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
