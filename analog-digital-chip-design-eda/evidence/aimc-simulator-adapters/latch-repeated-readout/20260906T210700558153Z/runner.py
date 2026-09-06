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


def stimulus(differences, polarity, setup_ns=5, period_ns=50):
    value = lambda diff: 0.9 + polarity * diff / 2000
    points = [(0, value(differences[0]))]
    for index, diff in enumerate(differences[1:], 1):
        points.extend([(period_ns*index-setup_ns, value(differences[index-1])),
                       (period_ns*index-setup_ns+0.02, value(diff))])
    return "PWL(" + " ".join(f"{t:.12g}n {v:.12g}" for t, v in points) + ")"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_run", type=Path)
    parser.add_argument("--receiver", action="store_true")
    parser.add_argument("--receiver-profile", choices=("original", "compact", "skewed"), default="original")
    parser.add_argument("--receiver-layout", type=Path, help="Use a DRC/LVS-passing receiver extraction instead of schematic devices")
    parser.add_argument("--combined-layout", type=Path, help="Use a single DRC/LVS-passing routed latch/receiver extraction")
    parser.add_argument("--cycles", type=int, default=4)
    parser.add_argument("--reset-early-ns", type=float, default=0,
                        help="Begin output precharge earlier by shortening reset-high duration")
    parser.add_argument("--clock-fall-ps", type=float, default=20)
    parser.add_argument("--reset-high-v", type=float, default=1.8,
                        help="Ideal reset-driver high level; keep distinct from the evaluation rail")
    parser.add_argument("--corner", choices=("tt","ff","ss","fs","sf"), default="tt")
    parser.add_argument("--temperature-c", type=float, default=27)
    parser.add_argument("--mismatch-seed", type=int, help="Enable PDK MC_MM_SWITCH with an explicit pre-parse ngspice seed")
    parser.add_argument("--input-diffs-mv", type=float, nargs="+", help="Explicit diagnostic sequence; overrides cycle count")
    parser.add_argument("--timeout-s", type=float, default=45, help="Bounded simulator wall-time limit")
    parser.add_argument("--calibration-offset-mv", type=float, default=0,
                        help="Ideal differential input correction; no physical trim implementation")
    parser.add_argument("--input-setup-ns", type=float, default=5,
                        help="Change inputs this long before the next cycle start, during reset")
    parser.add_argument("--period-ns", type=float, default=50,
                        help="Cycle period; lengthens reset interval without extending evaluation")
    args = parser.parse_args()
    if not np.isfinite(args.period_ns) or not 50 <= args.period_ns <= 200:
        parser.error("period must be within 50..200 ns")
    if not np.isfinite(args.input_setup_ns) or not 5 <= args.input_setup_ns <= 10:
        parser.error("input setup must be within 5..10 ns before cycle start")
    if not np.isfinite(args.calibration_offset_mv) or abs(args.calibration_offset_mv)>50:
        parser.error("calibration correction must be finite and within ±50 mV")
    if not np.isfinite(args.timeout_s) or not 1 <= args.timeout_s <= 180:
        parser.error("timeout must be within 1..180 seconds")
    if args.input_diffs_mv is not None:
        if not 2 <= len(args.input_diffs_mv) <= 12 or any(not np.isfinite(x) or x == 0 or abs(x)>100 for x in args.input_diffs_mv):
            parser.error("input sequence requires 2..12 finite, nonzero differences within ±100 mV")
        args.cycles = len(args.input_diffs_mv)
    if args.combined_layout:
        if args.receiver_layout:
            parser.error("Select combined layout or separate receiver layout, not both")
        args.receiver = True
        args.receiver_profile = "compact"
    if args.receiver_layout and not args.receiver:
        parser.error("--receiver-layout requires --receiver")
    if args.receiver_layout:
        args.receiver_profile = "compact"
    if not 2 <= args.cycles <= 12:
        parser.error("cycles must be within 2..12")
    if not np.isfinite(args.reset_early_ns) or not 0 <= args.reset_early_ns <= 5:
        parser.error("reset advance must be within 0..5 ns")
    if not np.isfinite(args.clock_fall_ps) or not 1 <= args.clock_fall_ps <= 2000:
        parser.error("clock fall time must be within 1..2000 ps")
    if not np.isfinite(args.reset_high_v) or not 1.6 <= args.reset_high_v <= 1.8:
        parser.error("reset high level must be within 1.6..1.8 V")
    if not np.isfinite(args.temperature_c) or not -40 <= args.temperature_c <= 125:
        parser.error("diagnostic temperature must be within -40..125 C")
    if args.mismatch_seed is not None and not 1 <= args.mismatch_seed <= 2147483647:
        parser.error("mismatch seed must be a positive signed 32-bit integer")
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
    if args.combined_layout:
        combined = args.combined_layout.resolve()
        physical = json.loads((combined/"result.json").read_text())
        if physical["status"] != "combined_drc_lvs_pass_not_transient" or physical["source_latch"] != config["lvs_run"]:
            raise ValueError("Combined verification or source-latch identity mismatch")
        for name in ("combined_latch_receiver.mag", "extracted.spice", "reference.spice"):
            if hashlib.sha256((combined/name).read_bytes()).hexdigest() != physical["sha256"][name]:
                raise ValueError(f"Combined physical evidence hash mismatch: {name}")
        shutil.copy2(combined/"extracted.spice", out/"circuit.spice")
        shutil.copy2(combined/"result.json", out/"combined_physical.json")
    differences = args.input_diffs_mv if args.input_diffs_mv is not None else [-0.5 if i % 2 == 0 else 0.5 for i in range(args.cycles)]
    applied_differences = [value+args.calibration_offset_mv for value in differences]
    if any(abs(value)>100 for value in applied_differences):
        raise ValueError("Corrected physical input exceeds ±100 mV diagnostic range")
    deck = (source/"case-0/deck.spice").read_text()
    if args.mismatch_seed is not None:
        deck = replace_line(deck, ".param mc_mm_switch=", ".param mc_mm_switch=1 mc_pr_switch=0")
        # Local initialization is read before the deck's AGAUSS parameters.
        init = out/".spiceinit"
        init.write_text(init.read_text()+f"\nset seed = {args.mismatch_seed}\nsetseed {args.mismatch_seed}\n")
        if deck.count(".control\nrun\n") != 1:
            raise ValueError("Unexpected control block for seeded parameter reset")
        deck = deck.replace(".control\nrun\n", f".control\nsetseed {args.mismatch_seed}\nreset\nrun\n")
    effective_models = {}
    for name,digest in config["model_file_sha256"].items():
        replacement = name.replace("__tt.", f"__{args.corner}.")
        model_path = Path(replacement)
        effective_models[replacement] = hashlib.sha256(model_path.read_bytes()).hexdigest()
        deck = deck.replace(name,replacement)
    corner_file = Path(config["model_library"]).parent/"corners"/f"{args.corner}.spice"
    corner_text = corner_file.read_text()
    for device,suffix in (("nfet","pm3"),("pfet","corner")):
        if f"sky130_fd_pr__{device}_01v8__{args.corner}.{suffix}.spice" not in corner_text:
            raise ValueError("PDK corner selection changed; review scoped model loading")
    deck = replace_line(deck, ".temp ", f".temp {args.temperature_c:.12g}")
    deck = replace_line(deck, f'.include "{source / "circuit.spice"}"', f'.include "{out / "circuit.spice"}"')
    if args.combined_layout:
        deck = replace_line(deck, "XU ", "XU out_p out_n latch_sense_p latch_sense_n tail reset vdd vss eval sense_p sense_n iso_tail vdd_active rx_p rx_n combined_latch_receiver")
    deck = replace_line(deck, "VP sense_p ", "VP sense_p 0 " + stimulus(applied_differences, 1, args.input_setup_ns,args.period_ns))
    deck = replace_line(deck, "VN sense_n ", "VN sense_n 0 " + stimulus(applied_differences, -1, args.input_setup_ns,args.period_ns))
    deck = replace_line(deck, ".tran ", f".tran 20p {args.period_ns*args.cycles:.12g}n")
    deck = replace_line(deck, "VRESET reset ", f"VRESET reset 0 PULSE(0 {args.reset_high_v:.12g} 8n 20p {args.clock_fall_ps:.12g}p {30-args.reset_early_ns:.12g}n {args.period_ns:.12g}n)")
    deck = replace_line(deck, "VEVAL eval ", f"VEVAL eval 0 PULSE(0 1.8 7.8n 20p {args.clock_fall_ps:.12g}p 30n {args.period_ns:.12g}n)")
    vectors = ["time", "v(out_p)", "v(out_n)", "v(latch_sense_p)", "v(latch_sense_n)",
               "v(iso_tail)", "v(tail)", "v(reset)", "v(eval)", "i(vdd)", "i(vactive)"]
    if args.receiver:
        nw, nl, pw, pl = {"original": (1.2, 0.6, 2.4, 0.6),
                          "compact": (0.42, 0.15, 0.42, 0.15),
                          "skewed": (0.84, 0.15, 0.42, 0.6)}[args.receiver_profile]
        receiver = "\n".join(
            f"XRXN{side} rx_{side} out_{side} vss vss sky130_fd_pr__nfet_01v8 w={nw} l={nl}\n"
            f"XRXP{side} rx_{side} out_{side} vdd_active vdd_active sky130_fd_pr__pfet_01v8 w={pw} l={pl}\n"
            f"CRX{side} rx_{side} vss 2f" for side in ("p", "n"))
        if args.receiver_layout:
            receiver_dir = args.receiver_layout.resolve()
            receiver_report = json.loads((receiver_dir/"result.json").read_text())
            if receiver_report["status"] != "receiver_drc_lvs_pass_subblock_only":
                raise ValueError("Receiver physical verification failed")
            for name in ("extracted.spice", "compact_receiver.mag", "reference.spice"):
                if hashlib.sha256((receiver_dir/name).read_bytes()).hexdigest() != receiver_report["sha256"][name]:
                    raise ValueError(f"Receiver evidence hash mismatch: {name}")
            shutil.copy2(receiver_dir/"extracted.spice", out/"receiver.spice")
            shutil.copy2(receiver_dir/"result.json", out/"receiver_physical.json")
            receiver = f'.include "{out/"receiver.spice"}"\n' + "\n".join(
                f"XRX{side} out_{side} rx_{side} vdd_active vss compact_receiver\nCRX{side} rx_{side} vss 2f"
                for side in ("p", "n"))
        if args.combined_layout:
            receiver = "CRXp rx_p vss 2f\nCRXn rx_n vss 2f"
        deck = deck.replace(".tran 20p", receiver + "\n.tran 20p")
        deck = replace_line(deck, "write waveform.raw ", "write waveform.raw " + " ".join(vectors[1:] + ["v(rx_p)", "v(rx_n)"]))
        vectors += ["v(rx_p)", "v(rx_n)"]
    (out/"deck.spice").write_text(deck)
    contract = {"source_run": str(source), "input_diffs_mv": differences, "period_ns": args.period_ns,
                "input_setup_ns": args.input_setup_ns,
                "applied_input_diffs_mv": applied_differences, "calibration_offset_mv": args.calibration_offset_mv,
                "calibration_implementation": "Ideal stimulus differential addition; no physical trim circuit",
                "timeout_s": args.timeout_s,
                "reset_advance_ns": args.reset_early_ns,
                "clock_fall_ps": args.clock_fall_ps,
                "reset_high_v": args.reset_high_v,
                "effective_model_corner": args.corner, "effective_temperature_c": args.temperature_c,
                "mismatch_enabled": args.mismatch_seed is not None, "mismatch_seed": args.mismatch_seed,
                "mismatch_seed_method": "startup_seed_plus_control_setseed_reset" if args.mismatch_seed is not None else None,
                "process_mc_enabled": False,
                "effective_model_file_sha256": effective_models,
                "corner_selector_sha256": hashlib.sha256(corner_file.read_bytes()).hexdigest(),
                "sample_offset_ns": 18, "hold_window_ns": [16, 20], "differential_margin_v": 0.5,
                "reset_check_offset_ns": 7.6, "reset_max_diff_v": 0.001,
                "receiver_added": args.receiver, "combined_layout_lvs_verified": bool(args.combined_layout) or not args.receiver,
                "combined_layout": str(args.combined_layout.resolve()) if args.combined_layout else None,
                "receiver_profile": args.receiver_profile if args.receiver else None,
                "receiver_layout": str(args.receiver_layout.resolve()) if args.receiver_layout else None,
                "receiver_extracted_sha256": hashlib.sha256((out/"receiver.spice").read_bytes()).hexdigest() if args.receiver_layout else None,
                "physical_boundary": "Single routed latch/receiver extraction; ideal external clocks, bias and supplies; 2 fF receiver output loads" if args.combined_layout else "Individually extracted subblocks; ideal connecting wires, no combined-layout extraction" if args.receiver_layout else None,
                "receiver_dimensions_um": {"nfet_w": nw, "nfet_l": nl, "pfet_w": pw, "pfet_l": pl} if args.receiver else None,
                "receiver_output_low_max_v": 0.18, "receiver_output_high_min_v": 1.62,
                "receiver_output_load_f": 2e-15 if args.receiver else None,
                "accepted_converter": False, "source_config": config,
                "sha256": {name: hashlib.sha256((out/name).read_bytes()).hexdigest()
                           for name in ("circuit.spice", "source_result.json", "runner.py", "deck.spice", ".spiceinit")}}
    (out/"contract.json").write_text(json.dumps(contract, indent=2)+"\n")
    try:
        proc = subprocess.run(["ngspice", "-b", "-o", "simulator.log", "deck.spice"], cwd=out,
                              capture_output=True, text=True, timeout=args.timeout_s)
        (out/"stdout.log").write_text(proc.stdout)
        (out/"stderr.log").write_text(proc.stderr)
        if proc.returncode:
            raise ValueError(f"ngspice returned {proc.returncode}")
        header, binary = (out/"waveform.raw").read_bytes().split(b"Binary:\n", 1)
        actual = [line.split()[1] for line in header.decode().split("Variables:\n", 1)[1].splitlines() if line.strip()]
        if actual != vectors:
            raise ValueError("Unexpected waveform vector order")
        wave = np.frombuffer(binary, dtype=np.float64).reshape(-1, len(vectors))
        if not np.isfinite(wave).all() or wave[-1, 0] < args.period_ns*args.cycles*1e-9-1e-15 or not np.all(np.diff(wave[:,0]) > 0):
            raise ValueError("Incomplete, nonfinite or nonmonotonic waveform")
        extrema = {name: [float(wave[:,i].min()), float(wave[:,i].max())]
                   for i, name in enumerate(vectors) if name.startswith("v(") and name not in ("v(reset)", "v(eval)")}
        legal = all(lo >= 0 and hi <= 1.8 for lo, hi in extrema.values())
        rows = []
        for index, diff in enumerate(differences):
            t = args.period_ns*index
            sample = np.array([np.interp((t+18)*1e-9, wave[:,0], wave[:,i]) for i in range(len(vectors))])
            reset = np.array([np.interp((t+7.6)*1e-9, wave[:,0], wave[:,i]) for i in (1,2)])
            hold = wave[(wave[:,0] >= (t+16)*1e-9) & (wave[:,0] <= (t+20)*1e-9)]
            signed = (hold[:,1]-hold[:,2])*np.sign(diff)
            row = {"cycle": index, "input_diff_mv": diff, "sample_outputs_v": sample[1:3].tolist(),
                   "applied_input_diff_mv": applied_differences[index],
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
                  "accepted_converter": False, "boundary": "Nominal TT ideal-source sub-block simulation; see contract for receiver view and physical integration limits."}
    except (subprocess.TimeoutExpired, ValueError) as exc:
        result = {"status": "simulation_incomplete", "error": str(exc), "accepted_converter": False}
    (out/"result.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))
    print(out)
    return 0 if result["status"] == "repeated_diagnostic_pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
