#!/usr/bin/env python3
"""Check extracted MOS connectivity against the intended isolation/latch graph.

This is a topology preflight, not a replacement for dimensional LVS or DRC.
MOS source/drain reversal is allowed; gate identity and net separation are not.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import math
import shlex
from pathlib import Path


def audit_substrate_capacitance(ext_path: Path, spice_path: Path, nodes=("out_p","out_n")) -> dict:
    """Check selected flat-cell node capacitances survive SPICE export."""
    expected = {}
    scale = None
    for line in ext_path.read_text().splitlines():
        fields = shlex.split(line)
        if fields and fields[0] == "scale":
            scale = float(fields[2])
        if fields and fields[0] == "node" and fields[1] in nodes:
            expected[fields[1]] = float(fields[3])
    actual = {node:0.0 for node in nodes}
    units = {"f": 1e-15, "p": 1e-12, "n": 1e-9}
    for line in spice_path.read_text().splitlines():
        fields = line.split()
        if not fields or not fields[0].startswith("C") or len(fields) < 4:
            continue
        for node in actual:
            if set(fields[1:3]) == {node, "vss"}:
                value = fields[3]
                actual[node] += float(value[:-1]) * units[value[-1]] if value[-1] in units else float(value)
    expected_f = {node: value * (scale or 0) * 1e-18 for node, value in expected.items()}
    passed = scale is not None and set(expected_f) == set(actual) and all(
        expected_f[node] > 0 and math.isclose(expected_f[node], actual[node], rel_tol=5e-5, abs_tol=1e-19)
        for node in actual)
    return {"pass": passed, "ext_capacitance_f": expected_f, "spice_capacitance_f": actual,
            "boundary": "Flat-cell selected-node-to-vss capacitance export consistency; not independent extraction signoff."}


def signature(kind, gate, a, b):
    return kind, gate, tuple(sorted((a, b)))


def audit(path: Path) -> dict:
    logical = []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if line.startswith("+") and logical:
            logical[-1] += " " + line[1:].strip()
        elif line and not line.startswith("*"):
            logical.append(line)
    ports = []
    devices = []
    for line in logical:
        fields = line.split()
        if fields[0].lower() == ".subckt":
            ports = fields[2:]
        elif fields[0].lower().startswith("x") and len(fields) >= 6:
            devices.append(fields[:6])
    expected = Counter([
        signature("nfet", "sense_p", "latch_sense_p", "iso_tail"),
        signature("nfet", "sense_n", "latch_sense_n", "iso_tail"),
        signature("nfet", "latch_sense_p", "out_p", "tail"),
        signature("nfet", "latch_sense_n", "out_n", "tail"),
        signature("nfet", "out_n", "out_p", "tail"),
        signature("nfet", "out_p", "out_n", "tail"),
        signature("nfet", "eval", "tail", "vss"),
        signature("pfet", "out_n", "out_p", "vdd_active"),
        signature("pfet", "out_p", "out_n", "vdd_active"),
        signature("pfet", "reset", "out_p", "vdd"),
        signature("pfet", "reset", "out_n", "vdd"),
    ])
    actual = Counter()
    body_issues = []
    for name, drain, gate, source, bulk, model in devices:
        kind = "nfet" if model == "sky130_fd_pr__nfet_01v8" else "pfet" if model == "sky130_fd_pr__pfet_01v8" else model
        actual[signature(kind, gate, drain, source)] += 1
        expected_bulk = "vss" if kind == "nfet" else "vdd_active" if source == "vdd_active" or drain == "vdd_active" else "vdd"
        if bulk != expected_bulk:
            body_issues.append({"device": name, "bulk": bulk, "expected": expected_bulk})
    required = {"out_p", "out_n", "sense_p", "sense_n", "tail", "iso_tail", "reset", "eval", "vdd", "vss", "vdd_active"}
    missing_ports = sorted(required - set(ports))
    topology_pass = not missing_ports and actual == expected
    return {"netlist": str(path), "topology_pass": topology_pass,
            "missing_ports": missing_ports,
            "missing_devices": list((expected - actual).elements()),
            "unexpected_devices": list((actual - expected).elements()),
            "body_tie_issues": body_issues,
            "body_ties_pass": not body_issues and len(devices) == 11,
            "claim_boundary": "Terminal-graph preflight only; not LVS, DRC, transient, or converter acceptance."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("netlist", type=Path)
    args = parser.parse_args()
    result = audit(args.netlist)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["topology_pass"] and result["body_ties_pass"] else 1)
