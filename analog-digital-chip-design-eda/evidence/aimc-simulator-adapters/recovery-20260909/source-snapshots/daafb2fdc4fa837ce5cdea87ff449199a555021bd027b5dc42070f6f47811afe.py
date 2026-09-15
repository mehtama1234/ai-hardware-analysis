#!/usr/bin/env python3
"""Run a bounded transient on the extracted active macro decision boundary."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from audit_extracted_converter_boundary import audit as audit_preamp_boundary


ROOT = Path(__file__).resolve().parents[1]
PDK_ROOT = Path("/home/mehtama1/eda-tools/pdks")
LIBRARY = PDK_ROOT / "sky130A/libs.tech/ngspice/sky130.lib.spice"


def selected_model_header() -> str:
    models = PDK_ROOT / "sky130A/libs.ref/sky130_fd_pr/spice"
    model_files = [models / ("sky130_fd_pr__" + name + ".spice") for name in
                   ("nfet_01v8__tt.pm3", "nfet_01v8__mismatch.corner", "pfet_01v8__tt.corner", "pfet_01v8__mismatch.corner")]
    common_file = PDK_ROOT / "sky130A/libs.tech/ngspice/all.spice"
    common_source = common_file.read_text(encoding="utf-8")
    marker = "* include all individual diode models"
    if marker not in common_source:
        raise RuntimeError("Sky130 common model dependency marker changed")
    common_header = common_source.split(marker, 1)[0].replace('"parameters/lod.spice"', f'"{PDK_ROOT / "sky130A/libs.tech/ngspice/parameters/lod.spice"}"')
    return ".option scale=1u\n.param mc_mm_switch=0 mc_pr_switch=0\n" + "\n".join(f'.include "{path}"' for path in model_files) + "\n" + common_header


def measure(text: str, name: str) -> float | None:
    values = re.findall(rf"^\s*{re.escape(name)}\s*=\s*([-+0-9.eE]+)", text, re.MULTILINE)
    return float(values[-1]) if values else None


def top_subckt_name(netlist: Path) -> str:
    match = re.search(r"(?m)^\.subckt\s+(\S+)", netlist.read_text(encoding="utf-8"))
    if not match:
        raise RuntimeError(f"no top-level subcircuit found in {netlist}")
    return match.group(1)


def deck(netlist: Path, diff_mv: float, view: str) -> str:
    half = diff_mv / 2000.0
    row = 0.9 + half
    comparator = 0.9 - half
    macro_name = top_subckt_name(netlist)
    physical_macro = "preamp_iso_tail_ext" in netlist.read_text(encoding="utf-8")
    preamp_bias_a = float(__import__("os").environ.get("AIMC_PREAMP_BIAS_A", "4e-6"))
    sense_load_ohm = float(__import__("os").environ.get("AIMC_SENSE_LOAD_OHM", "100000"))
    sense_load_p_ohm = float(__import__("os").environ.get("AIMC_SENSE_LOAD_P_OHM", str(sense_load_ohm)))
    sense_load_n_ohm = float(__import__("os").environ.get("AIMC_SENSE_LOAD_N_OHM", str(sense_load_ohm)))
    preamp_bias_line = f"IPRE preamp_iso_tail_ext 0 {preamp_bias_a:.12g}" if physical_macro else ""
    macro_instance = ("XU vss vdd row_drive sar_comparator_input decision_p decision_n reset eval vss_escape "
                      "latch_sense_p_ext latch_sense_n_ext iso_tail_ext tail_ext vdd_ext "
                      + ("preamp_iso_tail_ext " if physical_macro else "") + f"{macro_name}")
    instance = ("XU decision_p decision_n latch_sense_p_ext latch_sense_n_ext tail_ext reset vdd_ext vss_escape eval sense_p sense_n iso_tail_ext vdd_ext escaped_input_latch"
                if view == "child-extracted" else
                macro_instance)
    sense_sources = (f"VP sense_p 0 {row:.12g}\nVN sense_n 0 {comparator:.12g}\n"
                     if view == "child-extracted" else "")
    return f'''* Extracted active converter macro decision-boundary transient.
{selected_model_header()}
.include "{netlist}"
.param vdd=1.8
VSS vss 0 0
VDD vdd 0 {{vdd}}
VROW row_drive 0 {row:.12g}
VCOMP sar_comparator_input 0 {comparator:.12g}
VRESET reset 0 PULSE(0 {{vdd}} 8.00n 20p 20p 30n 60n)
VEVAL eval 0 PULSE(0 {{vdd}} 8.20n 20p 20p 20n 30n)
VSSX vss_escape 0 0
VDD_EXT vdd_ext 0 {{vdd}}
RP vdd_ext latch_sense_p_ext {sense_load_p_ohm:.12g}
RN vdd_ext latch_sense_n_ext {sense_load_n_ohm:.12g}
IBIAS iso_tail_ext 0 4u
{preamp_bias_line}
RTAIL tail_ext 0 100G
{sense_sources}{instance}
.options method=gear reltol=2e-3 abstol=1e-14 vntol=1e-7 gmin=1e-12 itl1=1000 itl4=1000 maxord=2 cshunt=1e-15 rshunt=1e12
.tran 20p 20n uic
.measure tran decision_p_v FIND v(decision_p) AT=18n
.measure tran decision_n_v FIND v(decision_n) AT=18n
.measure tran decision_diff_v PARAM='decision_n_v-decision_p_v'
.measure tran supply_charge_c INTEG I(VDD) FROM=0 TO=20n
.measure tran active_supply_charge_c INTEG I(VDD_EXT) FROM=0 TO=20n
.control
run
.endc
.end
'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-dir", type=Path, required=True)
    parser.add_argument("--input-diffs-mv", type=float, nargs="+", default=[-0.1529705854, 0.1529705854])
    parser.add_argument("--view", choices=("extracted", "device-only-extracted", "child-extracted"), default="extracted",
                        help="Run the full extracted macro or retain extracted MOS devices while removing extracted capacitors as a convergence diagnostic.")
    args = parser.parse_args()
    candidate = args.candidate_dir.resolve()
    netlist = candidate / "aimc_converter_macro_active_candidate_extracted.spice"
    if not netlist.is_file():
        raise SystemExit(f"extracted macro netlist not found: {netlist}")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output = ROOT / "evidence/aimc-simulator-adapters/active-converter-macro-transient" / stamp
    output.mkdir(parents=True, exist_ok=False)
    simulated_netlist = netlist
    removed_capacitor_count = 0
    if args.view == "device-only-extracted":
        source_lines = netlist.read_text(encoding="utf-8").splitlines()
        retained_lines = [line for line in source_lines if not line.lstrip().startswith("C")]
        removed_capacitor_count = len(source_lines) - len(retained_lines)
        simulated_netlist = output / "macro_device_only_extracted.spice"
        simulated_netlist.write_text("\n".join(retained_lines) + "\n", encoding="utf-8")
    rows = []
    for index, diff in enumerate(args.input_diffs_mv):
        case = output / f"case-{index}"
        case.mkdir()
        case_deck = case / "deck.spice"
        case_deck.write_text(deck(simulated_netlist, diff, args.view), encoding="utf-8")
        try:
            proc = subprocess.run(["ngspice", "-b", str(case_deck)], cwd=case, text=True, capture_output=True, check=False, timeout=20)
            timed_out = False
        except subprocess.TimeoutExpired as exc:
            (case / "stdout.log").write_bytes(exc.stdout if isinstance(exc.stdout, bytes) else (exc.stdout or "").encode())
            (case / "stderr.log").write_bytes(exc.stderr if isinstance(exc.stderr, bytes) else (exc.stderr or "").encode())
            rows.append({"input_diff_mv": diff, "measured": False, "timed_out": True, "returncode": None, "error": str(exc)[-1000:]})
            continue
        (case / "stdout.log").write_text(proc.stdout, encoding="utf-8")
        (case / "stderr.log").write_text(proc.stderr, encoding="utf-8")
        row = {"input_diff_mv": diff, "measured": proc.returncode == 0, "timed_out": timed_out, "returncode": proc.returncode}
        if proc.returncode == 0:
            output_diff = measure(proc.stdout, "decision_diff_v")
            charge = measure(proc.stdout, "supply_charge_c")
            active_charge = measure(proc.stdout, "active_supply_charge_c")
            row.update({"decision_p_v": measure(proc.stdout, "decision_p_v"), "decision_n_v": measure(proc.stdout, "decision_n_v"), "decision_diff_v": output_diff,
                        "supply_charge_c": charge, "active_supply_charge_c": active_charge,
                        "supply_energy_j": -1.8 * (charge + active_charge) if charge is not None and active_charge is not None else None,
                        "energy_scope": "signed net energy delivered by VDD and VDD_EXT over 0–20 ns; excludes input/clock driver and bias-generation costs",
                        "polarity_pass": output_diff is not None and diff != 0 and output_diff != 0 and ((output_diff > 0) == (diff < 0)),
                        "polarity_applicable": diff != 0,
                        "logic_margin_pass": output_diff is not None and abs(output_diff) >= 0.9})
        else:
            row["error_excerpt"] = (proc.stdout + proc.stderr)[-1600:]
        rows.append(row)
    report = {
        "result_type": "sky130_active_converter_macro_extracted_transient",
        "status": "extracted_macro_decision_transient_characterized_not_converter_signoff" if all(row.get("measured") for row in rows) else "extracted_macro_decision_transient_incomplete",
        "candidate_dir": str(candidate),
        "netlist": str(netlist),
        "netlist_sha256": __import__("hashlib").sha256(netlist.read_bytes()).hexdigest(),
        "simulated_netlist": str(simulated_netlist),
        "simulated_netlist_sha256": __import__("hashlib").sha256(simulated_netlist.read_bytes()).hexdigest(),
        "view": args.view,
        "final_netlist_boundary_audit": audit_preamp_boundary(simulated_netlist.read_text()),
        "runner_sha256": __import__("hashlib").sha256(Path(__file__).read_bytes()).hexdigest(),
        "extracted_capacitors_removed_for_diagnostic": removed_capacitor_count,
        "model_library": str(LIBRARY),
        "input_common_mode_v": 0.9,
        "decision_time_ns": 18.0,
        "rows": rows,
        "measured_case_count": sum(bool(row.get("measured")) for row in rows),
        "polarity_pass_count": sum(bool(row.get("polarity_pass")) for row in rows),
        "logic_margin_pass_count": sum(bool(row.get("logic_margin_pass")) for row in rows),
        "accepted_converter": False,
        "claim_boundary": {
            "allowed": "bounded TT transient of the active macro decision boundary with explicit supply and polarity cases; device-only view retains extracted Sky130 MOS devices",
            "not_allowed": "does not prove SAR code correctness, noise/mismatch, PVT, full converter energy, or accepted post-layout evidence",
        },
    }
    path = output / "result.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "measured_case_count": report["measured_case_count"], "polarity_pass_count": report["polarity_pass_count"], "logic_margin_pass_count": report["logic_margin_pass_count"], "output": str(path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
