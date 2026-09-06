#!/usr/bin/env python3
"""Bounded Sky130 transistor diagnostic from a hashed passing LVS snapshot."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import numpy as np

from audit_isolated_latch_connectivity import audit

ROOT = Path(__file__).resolve().parents[1]
CELL = "sky130_isolated_frontend_active_load_latch_v2"


def symmetrize_capacitances(source: str) -> str:
    """Diagnostic counterfactual: average each extracted C with its mirror.

    This is not a layout extraction and cannot qualify hardware. Missing
    mirrored edges count as zero; total capacitance is conserved.
    """
    pairs = [("out_p", "out_n"), ("sense_p", "sense_n"),
             ("latch_sense_p", "latch_sense_n"),
             ("m1_1000_12500#", "m1_3440_12500#")]
    mirror = {a: b for pair in pairs for a, b in (pair, pair[::-1])}
    caps, retained = {}, []
    for line in source.splitlines():
        if line.lstrip().lower().startswith("c"):
            fields = line.split()
            if len(fields) != 4 or not fields[3].endswith("f"):
                raise ValueError("Unexpected extracted capacitor syntax")
            key = tuple(sorted(fields[1:3]))
            caps[key] = caps.get(key, 0.0) + float(fields[3][:-1])
        else:
            retained.append(line)
    def reflected(key):
        return tuple(sorted(mirror.get(node, node) for node in key))
    keys = set(caps) | {reflected(key) for key in caps}
    averaged = {key: (caps.get(key, 0) + caps.get(reflected(key), 0)) / 2 for key in keys}
    if not math.isclose(sum(caps.values()), sum(averaged.values()), rel_tol=1e-12):
        raise ValueError("Counterfactual failed capacitance conservation")
    end = next(i for i, line in enumerate(retained) if line.lower().startswith(".ends"))
    retained[end:end] = [f"CSYM{i} {a} {b} {averaged[(a, b)]:.12g}f"
                         for i, (a, b) in enumerate(sorted(keys))]
    return "\n".join(retained) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lvs_run", type=Path)
    parser.add_argument("--load-ohm", type=float, default=100000)
    parser.add_argument("--input-diffs-mv", type=float, nargs="+", default=[-0.5, 0.5])
    parser.add_argument("--view", choices=("extracted", "schematic", "device-only-extracted", "symmetric-cap-diagnostic"), default="extracted")
    parser.add_argument("--eval-at-ns", type=float, default=8.2)
    parser.add_argument("--clock-rise-ps", type=float, default=20,
                        help="Ideal reset/evaluation source rise time; not a physical driver model")
    parser.add_argument("--precharge-v", type=float, default=1.8,
                        help="Ideal precharge rail; active load and sense resistors remain at 1.8 V")
    parser.add_argument("--schematic-equalizer", action="store_true",
                        help="Add an unlaid-out transmission-gate output equalizer; diagnostic only")
    args = parser.parse_args()
    if not math.isfinite(args.load_ohm) or args.load_ohm <= 0:
        parser.error("--load-ohm must be finite and positive")
    if any(not math.isfinite(value) or abs(value) > 1000 for value in args.input_diffs_mv):
        parser.error("input differences must be finite and within ±1000 mV")
    if not math.isfinite(args.eval_at_ns) or not 1 <= args.eval_at_ns <= 10:
        parser.error("evaluation time must be within 1..10 ns")
    if not math.isfinite(args.clock_rise_ps) or not 1 <= args.clock_rise_ps <= 2000:
        parser.error("clock rise time must be within 1..2000 ps")
    if not math.isfinite(args.precharge_v) or not 1.6 <= args.precharge_v <= 1.8:
        parser.error("precharge rail must be within 1.6..1.8 V")
    lvs = args.lvs_run.resolve()
    report = json.loads((lvs / "result.json").read_text())
    selected = "reference.spice" if args.view == "schematic" else "extracted.spice"
    netlist = lvs / selected
    digest = hashlib.sha256(netlist.read_bytes()).hexdigest()
    if report["status"] != "lvs_pass_subblock_only" or report["sha256"][selected] != digest:
        raise SystemExit("Require passing LVS and matching extracted-netlist hash")
    check = audit(netlist)
    if not check["topology_pass"] or not check["body_ties_pass"]:
        raise SystemExit("Connectivity preflight failed")
    output = ROOT / "evidence/aimc-simulator-adapters/isolated-latch-v2-transient" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output.mkdir(parents=True, exist_ok=False)
    shutil.copy2(netlist, output / "circuit.spice")
    if args.view == "symmetric-cap-diagnostic":
        (output / "circuit.spice").write_text(symmetrize_capacitances(netlist.read_text()))
    removed_caps = 0
    if args.view == "device-only-extracted":
        lines = netlist.read_text().splitlines()
        retained = [line for line in lines if not line.lstrip().lower().startswith("c")]
        removed_caps = len(lines) - len(retained)
        (output / "circuit.spice").write_text("\n".join(retained) + "\n")
    pdk = Path(os.environ.get("PDK_ROOT", str(Path.home() / "eda-tools/pdks")))
    library = pdk / "sky130A/libs.tech/ngspice/sky130.lib.spice"
    models = pdk / "sky130A/libs.ref/sky130_fd_pr/spice"
    model_files = [models / ("sky130_fd_pr__" + name + ".spice") for name in
                   ("nfet_01v8__tt.pm3", "nfet_01v8__mismatch.corner", "pfet_01v8__tt.corner", "pfet_01v8__mismatch.corner")]
    # Same TT model files selected by corners/tt.spice, with the scale from
    # all.spice. Only the two device classes present in this LVS cell are loaded.
    model_header = ".option scale=1u\n.param mc_mm_switch=0 mc_pr_switch=0\n" + "\n".join(f'.include "{path}"' for path in model_files)
    common_file = library.parent / "all.spice"
    common_source = common_file.read_text()
    marker = "* include all individual diode models"
    if marker not in common_source:
        raise SystemExit("PDK common setup changed; review model dependency selection")
    common_header = common_source.split(marker, 1)[0].replace('"parameters/lod.spice"', f'"{library.parent / "parameters/lod.spice"}"')
    model_header += "\n" + common_header
    config = {"lvs_run": str(lvs), "netlist_sha256": digest, "netlist_view": args.view, "model_library": str(library),
              "simulated_netlist_sha256": hashlib.sha256((output / "circuit.spice").read_bytes()).hexdigest(),
              "extracted_capacitors_removed_for_diagnostic": removed_caps,
              "library_sha256": hashlib.sha256(library.read_bytes()).hexdigest(),
              "model_corner": "tt", "temperature_c": 27, "input_common_mode_v": 0.9,
              "model_selection": "PDK TT nfet_01v8 and pfet_01v8 only; no model substitution",
              "model_file_sha256": {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in model_files + [models / "sky130_fd_pr__pfet_01v8__tt.pm3.spice", common_file, library.parent / "parameters/lod.spice"]},
              "input_diffs_mv": args.input_diffs_mv, "load_ohm": args.load_ohm, "isolation_bias_a": 4e-6,
              "eval_at_ns": args.eval_at_ns, "reset_release_ns": 8,
              "clock_rise_ps": args.clock_rise_ps,
              "precharge_rail_v": args.precharge_v, "active_and_sense_load_rail_v": 1.8,
              "precharge_rail_generation_verified": False,
              "schematic_equalizer_added": args.schematic_equalizer,
              "equalizer_circuit": "two_device_transmission_gate_release_10ns" if args.schematic_equalizer else None,
              "combined_circuit_lvs_verified": not args.schematic_equalizer and args.view == "extracted",
              "parasitics_modified_for_diagnostic": args.view in ("device-only-extracted", "symmetric-cap-diagnostic"),
              "diagnostic_output_threshold_v": 0.5, "timeout_per_case_s": 30,
              "boundary": "Selected schematic/extracted transistor latch with ideal external input, load resistors and bias source; not the complete sampled frontend or converter."}
    (output / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    rows = []
    for index, diff in enumerate(config["input_diffs_mv"]):
        case = output / f"case-{index}"
        case.mkdir()
        shutil.copy2(library.parent / "spinit", case / ".spiceinit")
        equalizer = '''VEQP eqp 0 PULSE(0 1.8 10n 20p 20p 30n 50n)
VEQN eqn 0 PULSE(1.8 0 10n 20p 20p 30n 50n)
XEQP out_p eqp out_n vdd sky130_fd_pr__pfet_01v8 w=4.8 l=0.6
XEQN out_p eqn out_n vss sky130_fd_pr__nfet_01v8 w=4.8 l=0.6''' if args.schematic_equalizer else ""
        deck = f'''* Signed small-signal extracted latch diagnostic, no structural MOS substitution.
{model_header}
.include "{output / 'circuit.spice'}"
.temp 27
.options method=gear reltol=1e-4 abstol=1e-14 vntol=1e-7
VDD vdd 0 {args.precharge_v:.12g}
VACTIVE vdd_active 0 1.8
VSS vss 0 0
VP sense_p 0 {0.9 + diff / 2000:.12g}
VN sense_n 0 {0.9 - diff / 2000:.12g}
IBIAS iso_tail 0 4u
RP vdd_active latch_sense_p {args.load_ohm:.12g}
RN vdd_active latch_sense_n {args.load_ohm:.12g}
VRESET reset 0 PULSE(0 1.8 8n {args.clock_rise_ps:.12g}p 20p 30n 50n)
VEVAL eval 0 PULSE(0 1.8 {args.eval_at_ns:.12g}n {args.clock_rise_ps:.12g}p 20p 30n 50n)
XU out_p out_n latch_sense_p latch_sense_n tail reset vdd vss eval sense_p sense_n iso_tail vdd_active {CELL}
{equalizer}
.tran 20p 20n
.measure tran op_final FIND v(out_p) AT=18n
.measure tran on_final FIND v(out_n) AT=18n
.measure tran lp_before FIND v(latch_sense_p) AT={min(8, args.eval_at_ns) - 0.2:.12g}n
.measure tran ln_before FIND v(latch_sense_n) AT={min(8, args.eval_at_ns) - 0.2:.12g}n
.control
run
write waveform.raw v(out_p) v(out_n) v(latch_sense_p) v(latch_sense_n) v(iso_tail) v(tail) v(reset) v(eval) i(VDD) i(VACTIVE)
.endc
.end
'''
        (case / "deck.spice").write_text(deck)
        row = {"input_diff_mv": diff, "measured": False, "pass": False}
        try:
            proc = subprocess.run(["ngspice", "-b", "-o", "simulator.log", "deck.spice"], cwd=case, capture_output=True,
                                  text=True, timeout=30)
            (case / "stdout.log").write_text(proc.stdout)
            (case / "stderr.log").write_text(proc.stderr)
            row["returncode"] = proc.returncode
            measured_text = (case / "simulator.log").read_text() if (case / "simulator.log").exists() else proc.stdout
            values = {}
            for name in ("op_final", "on_final", "lp_before", "ln_before"):
                match = re.search(rf"^\s*{name}\s*=\s*([-+\d.eE]+)", measured_text, re.M)
                if match:
                    values[name] = float(match[1])
            row["measured"] = proc.returncode == 0 and len(values) == 4 and all(math.isfinite(v) for v in values.values())
            row["measurements"] = values
            if row["measured"]:
                delta = values["op_final"] - values["on_final"]
                row["output_diff_v"] = delta
                row["polarity_pass"] = delta * diff > 0
                row["margin_pass"] = abs(delta) >= 0.5
                # ngspice writes real native doubles here. Require the expected
                # saved vectors instead of accepting a final-point-only gate.
                header, binary = (case / "waveform.raw").read_bytes().split(b"Binary:\n", 1)
                expected_vectors = ["time", "v(out_p)", "v(out_n)", "v(latch_sense_p)", "v(latch_sense_n)", "v(iso_tail)", "v(tail)", "v(reset)", "v(eval)", "i(vdd)", "i(vactive)"]
                actual_vectors = [line.split()[1] for line in header.decode().split("Variables:\n", 1)[1].splitlines() if line.strip()]
                if actual_vectors != expected_vectors:
                    raise ValueError("Unexpected waveform vector order")
                wave = np.frombuffer(binary, dtype=np.float64).reshape(-1, len(expected_vectors))
                finite = bool(np.isfinite(wave).all())
                row["node_voltage_extrema_v"] = {name: [float(wave[:, i].min()), float(wave[:, i].max())] for i, name in enumerate(expected_vectors[1:7], 1)}
                row["waveform_legal"] = finite and all(low >= 0 and high <= 1.8 for low, high in row["node_voltage_extrema_v"].values())
                row["pass"] = row["polarity_pass"] and row["margin_pass"] and row["waveform_legal"]
        except subprocess.TimeoutExpired as exc:
            row["timed_out"] = True
            for name, data in (("stdout.log", exc.stdout), ("stderr.log", exc.stderr)):
                (case / name).write_bytes(data if isinstance(data, bytes) else (data or "").encode())
        rows.append(row)
        (case / "result.json").write_text(json.dumps(row, indent=2) + "\n")
        print(json.dumps(row), flush=True)
    result = {"status": "diagnostic_pass" if all(row["pass"] for row in rows) else "diagnostic_fail",
              "rows": rows, "config": config, "accepted_converter": False}
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(output)
    return 0 if result["status"] == "diagnostic_pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
