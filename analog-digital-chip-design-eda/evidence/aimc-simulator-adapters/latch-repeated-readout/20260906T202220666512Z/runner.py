#!/usr/bin/env python3
"""Repeat a preserved extracted-latch diagnostic without resetting SPICE state.

Optional transistor receivers are schematic-only additions, not LVS-qualified
combined geometry. Their 10%/90% output thresholds are engineering diagnostic
targets, not a characterized standard-cell input contract.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def replace_line(deck, prefix, replacement):
    pattern = rf"^{re.escape(prefix)}.*$"
    result, count = re.subn(pattern, replacement, deck, flags=re.M)
    if count != 1:
        raise ValueError(f"Expected exactly one {prefix!r} line")
    return result


def stimulus(differences, polarity):
    value = lambda diff: 0.9 + polarity * diff / 2000
    points = [(0, value(differences[0]))]
    for index, diff in enumerate(differences[1:], 1):
        points.extend([(50*index-5, value(differences[index-1])),
                       (50*index-4.98, value(diff))])
    return "PWL(" + " ".join(f"{t:.12g}n {v:.12g}" for t, v in points) + ")"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_run", type=Path)
    parser.add_argument("--receiver", action="store_true")
    parser.add_argument("--cycles", type=int, default=4)
    parser.add_argument("--reset-early-ns", type=float, default=0,
                        help="Begin output precharge earlier by shortening reset-high duration")
    parser.add_argument("--clock-fall-ps", type=float, default=20)
    args = parser.parse_args()
    if not 2 <= args.cycles <= 12:
        parser.error("cycles must be within 2..12")
    if not np.isfinite(args.reset_early_ns) or not 0 <= args.reset_early_ns <= 5:
        parser.error("reset advance must be within 0..5 ns")
    if not np.isfinite(args.clock_fall_ps) or not 1 <= args.clock_fall_ps <= 2000:
        parser.error("clock fall time must be within 1..2000 ps")
    source = args.source_run.resolve()
    baseline = json.loads((source/"result.json").read_text())
    config = baseline["config"]
    if config["netlist_view"] != "extracted" or config["schematic_equalizer_added"]:
        raise ValueError("Require unchanged extracted latch without schematic equalizer")
    if hashlib.sha256((source/"circuit.spice").read_bytes()).hexdigest() != config["simulated_netlist_sha256"]:
        raise ValueError("Extracted source hash mismatch")
    for name, digest in config["model_file_sha256"].items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"PDK model dependency changed: {name}")
    # Require the measured profile this experiment is designed to extend.
    if (config["load_ohm"], config["eval_at_ns"], config["precharge_rail_v"],
            config["clock_rise_ps"]) != (350000, 7.8, 1.75, 20):
        raise ValueError("Unexpected nominal profile; review repeated-cycle contract")
    out = ROOT/"evidence/aimc-simulator-adapters/latch-repeated-readout"/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out.mkdir(parents=True, exist_ok=False)
    for name, origin in {"circuit.spice": source/"circuit.spice", ".spiceinit": source/"case-0/.spiceinit",
                         "source_result.json": source/"result.json", "runner.py": Path(__file__)}.items():
        shutil.copy2(origin, out/name)
    differences = [-0.5 if i % 2 == 0 else 0.5 for i in range(args.cycles)]
    deck = (source/"case-0/deck.spice").read_text()
    deck = replace_line(deck, f'.include "{source / "circuit.spice"}"', f'.include "{out / "circuit.spice"}"')
    deck = replace_line(deck, "VP sense_p ", "VP sense_p 0 " + stimulus(differences, 1))
    deck = replace_line(deck, "VN sense_n ", "VN sense_n 0 " + stimulus(differences, -1))
    deck = replace_line(deck, ".tran ", f".tran 20p {50*args.cycles}n")
    deck = replace_line(deck, "VRESET reset ", f"VRESET reset 0 PULSE(0 1.8 8n 20p {args.clock_fall_ps:.12g}p {30-args.reset_early_ns:.12g}n 50n)")
    deck = replace_line(deck, "VEVAL eval ", f"VEVAL eval 0 PULSE(0 1.8 7.8n 20p {args.clock_fall_ps:.12g}p 30n 50n)")
    vectors = ["time", "v(out_p)", "v(out_n)", "v(latch_sense_p)", "v(latch_sense_n)",
               "v(iso_tail)", "v(tail)", "v(reset)", "v(eval)", "i(vdd)", "i(vactive)"]
    if args.receiver:
        receiver = "\n".join(
            f"XRXN{side} rx_{side} out_{side} vss vss sky130_fd_pr__nfet_01v8 w=1.2 l=0.6\n"
            f"XRXP{side} rx_{side} out_{side} vdd_active vdd_active sky130_fd_pr__pfet_01v8 w=2.4 l=0.6\n"
            f"CRX{side} rx_{side} vss 2f" for side in ("p", "n"))
        deck = deck.replace(".tran 20p", receiver + "\n.tran 20p")
        deck = replace_line(deck, "write waveform.raw ", "write waveform.raw " + " ".join(vectors[1:] + ["v(rx_p)", "v(rx_n)"]))
        vectors += ["v(rx_p)", "v(rx_n)"]
    (out/"deck.spice").write_text(deck)
    contract = {"source_run": str(source), "input_diffs_mv": differences, "period_ns": 50,
                "reset_advance_ns": args.reset_early_ns,
                "clock_fall_ps": args.clock_fall_ps,
                "sample_offset_ns": 18, "hold_window_ns": [16, 20], "differential_margin_v": 0.5,
                "reset_check_offset_ns": 7.6, "reset_max_diff_v": 0.001,
                "receiver_added": args.receiver, "combined_layout_lvs_verified": not args.receiver,
                "receiver_output_low_max_v": 0.18, "receiver_output_high_min_v": 1.62,
                "receiver_output_load_f": 2e-15 if args.receiver else None,
                "accepted_converter": False, "source_config": config,
                "sha256": {name: hashlib.sha256((out/name).read_bytes()).hexdigest()
                           for name in ("circuit.spice", "source_result.json", "runner.py", "deck.spice", ".spiceinit")}}
    (out/"contract.json").write_text(json.dumps(contract, indent=2)+"\n")
    try:
        proc = subprocess.run(["ngspice", "-b", "-o", "simulator.log", "deck.spice"], cwd=out,
                              capture_output=True, text=True, timeout=45)
        (out/"stdout.log").write_text(proc.stdout)
        (out/"stderr.log").write_text(proc.stderr)
        if proc.returncode:
            raise ValueError(f"ngspice returned {proc.returncode}")
        header, binary = (out/"waveform.raw").read_bytes().split(b"Binary:\n", 1)
        actual = [line.split()[1] for line in header.decode().split("Variables:\n", 1)[1].splitlines() if line.strip()]
        if actual != vectors:
            raise ValueError("Unexpected waveform vector order")
        wave = np.frombuffer(binary, dtype=np.float64).reshape(-1, len(vectors))
        if not np.isfinite(wave).all() or wave[-1, 0] < 50*args.cycles*1e-9-1e-15 or not np.all(np.diff(wave[:,0]) > 0):
            raise ValueError("Incomplete, nonfinite or nonmonotonic waveform")
        extrema = {name: [float(wave[:,i].min()), float(wave[:,i].max())]
                   for i, name in enumerate(vectors) if name.startswith("v(") and name not in ("v(reset)", "v(eval)")}
        legal = all(lo >= 0 and hi <= 1.8 for lo, hi in extrema.values())
        rows = []
        for index, diff in enumerate(differences):
            t = 50*index
            sample = np.array([np.interp((t+18)*1e-9, wave[:,0], wave[:,i]) for i in range(len(vectors))])
            reset = np.array([np.interp((t+7.6)*1e-9, wave[:,0], wave[:,i]) for i in (1,2)])
            hold = wave[(wave[:,0] >= (t+16)*1e-9) & (wave[:,0] <= (t+20)*1e-9)]
            signed = (hold[:,1]-hold[:,2])*np.sign(diff)
            row = {"cycle": index, "input_diff_mv": diff, "sample_outputs_v": sample[1:3].tolist(),
                   "sample_polarity_pass": bool((sample[1]-sample[2])*diff > 0),
                   "hold_min_signed_diff_v": float(signed.min()), "hold_margin_pass": bool((signed >= 0.5).all()),
                   "reset_outputs_v": reset.tolist(),
                   "reset_pass": bool(abs(reset[0]-reset[1]) <= 0.001 and np.all(abs(reset-1.75) <= 0.01))}
            if args.receiver:
                high = hold[:,-1] if diff > 0 else hold[:,-2]
                low = hold[:,-2] if diff > 0 else hold[:,-1]
                row["receiver_hold_high_min_v"] = float(high.min())
                row["receiver_hold_low_max_v"] = float(low.max())
                row["receiver_hold_pass"] = bool((high >= 1.62).all() and (low <= 0.18).all())
            row["pass"] = row["sample_polarity_pass"] and row["hold_margin_pass"] and row["reset_pass"] and legal and row.get("receiver_hold_pass", True)
            rows.append(row)
        result = {"status": "repeated_diagnostic_pass" if all(row["pass"] for row in rows) else "repeated_diagnostic_fail",
                  "waveform_legal": legal, "node_voltage_extrema_v": extrema, "rows": rows,
                  "accepted_converter": False, "boundary": "Nominal TT ideal-source repeated sub-block simulation; optional receivers are unlaid-out."}
    except (subprocess.TimeoutExpired, ValueError) as exc:
        result = {"status": "simulation_incomplete", "error": str(exc), "accepted_converter": False}
    (out/"result.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))
    print(out)
    return 0 if result["status"] == "repeated_diagnostic_pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
