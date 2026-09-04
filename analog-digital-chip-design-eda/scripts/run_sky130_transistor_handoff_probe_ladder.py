#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
SPICE_DIR = LAB / "spice"
MEASUREMENTS = LAB / "measurements"
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
PDK_LIB = Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "ngspice" / "sky130.lib.spice"
FRONTEND_NETLIST = LAB / "layout-workbench" / "extracted" / "sky130_ultra_sense_capacitive_frontend_extracted.spice"
SOURCE_FRONTEND = EVIDENCE / "sky130-ultra-sense-frontend-candidate.json"
SOURCE_TRANSISTOR = EVIDENCE / "sky130-comparator-input-stage-ngspice.json"
SOURCE_HANDOFF = EVIDENCE / "sky130-frontend-transistor-input-stage-handoff-candidate.json"
DECK_OUT = SPICE_DIR / "sky130_transistor_handoff_probe_ladder.sp"
CSV_OUT = MEASUREMENTS / "sky130-transistor-handoff-probe-ladder.csv"
OUT_JSON = EVIDENCE / "sky130-transistor-handoff-probe-ladder.json"
OUT_MD = EVIDENCE / "sky130-transistor-handoff-probe-ladder.md"

TARGET_DIFF_MV = 0.15297058540778352
NGSPICE_TIMEOUT_S = 12


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def read_measure(stdout: str, name: str) -> float:
    values: list[float] = []
    for raw in stdout.splitlines():
        match = re.search(rf"{re.escape(name)}\s+=\s+([-+0-9.eE]+)", raw)
        if match:
            values.append(float(match.group(1)))
    if not values:
        raise ValueError(f"expected ngspice measurement {name!r}, found none")
    return values[-1]


def transistor_stage_body(input_p: str, input_n: str) -> str:
    return f"""
.param vdd=1.8
.param rd=100k
.param itail=20u
.param wn=8.0
.param lmin=0.15
.options method=trap reltol=1e-3 abstol=1e-14 vntol=1e-7

VDD vdd 0 {{vdd}}
RDP vdd outp {{rd}}
RDN vdd outn {{rd}}
XINP outp {input_p} tail 0 sky130_fd_pr__nfet_01v8 W={{wn}} L={{lmin}}
XINN outn {input_n} tail 0 sky130_fd_pr__nfet_01v8 W={{wn}} L={{lmin}}
ITAIL tail 0 {{itail}}
COUTP outp 0 2f
COUTN outn 0 2f
"""


def deck_standalone_transient() -> str:
    diff_v = TARGET_DIFF_MV / 1000.0
    vinp = 0.9 + diff_v / 2.0
    vinn = 0.9 - diff_v / 2.0
    return f"""* Probe A: standalone Sky130 transistor input stage in transient.
.global VSUBS
.lib "{PDK_LIB}" tt
VSUB VSUBS 0 0
VINP inp 0 PWL(0 0.9 0.1n {vinp:.12f} 3n {vinp:.12f})
VINN inn 0 PWL(0 0.9 0.1n {vinn:.12f} 3n {vinn:.12f})
{transistor_stage_body("inp", "inn")}
.tran 20p 3n
.measure tran outp_after_v FIND v(outp) AT=2.60n
.measure tran outn_after_v FIND v(outn) AT=2.60n
.measure tran tail_after_v FIND v(tail) AT=2.60n
.control
set noaskquit
run
.endc
.end
"""


def deck_frontend_equivalent_cap_load() -> str:
    diff_v = TARGET_DIFF_MV / 1000.0
    vinp = 0.9 + diff_v / 2.0
    vinn = 0.9 - diff_v / 2.0
    sense_diff = 0.000067
    sp = 0.9 + sense_diff / 2.0
    sn = 0.9 - sense_diff / 2.0
    return f"""* Probe B: transistor input stage driven by measured frontend sense voltage with equivalent frontend capacitance.
.global VSUBS
.lib "{PDK_LIB}" tt
VSUB VSUBS 0 0
VINP inp 0 PWL(0 0.9 0.1n {sp:.12f} 3n {sp:.12f})
VINN inn 0 PWL(0 0.9 0.1n {sn:.12f} 3n {sn:.12f})
CSENSEP inp 0 3.292970f
CSENSEN inn 0 3.292970f
CSAMPLEP inp 0 3.322430f
CSAMPLEN inn 0 3.322430f
{transistor_stage_body("inp", "inn")}
.tran 20p 3n
.measure tran outp_after_v FIND v(outp) AT=2.60n
.measure tran outn_after_v FIND v(outn) AT=2.60n
.measure tran input_diff_after_v PARAM v(inp)-v(inn)
.control
set noaskquit
run
.endc
.end
"""


def deck_frontend_plus_gate_cap_only() -> str:
    diff_v = TARGET_DIFF_MV / 1000.0
    vinp = 0.9 + diff_v / 2.0
    vinn = 0.9 - diff_v / 2.0
    return f"""* Probe C: extracted frontend plus transistor-like gate capacitance, no transistor equations.
.global VSUBS
.include "{FRONTEND_NETLIST}"
VDD vdd 0 1.8
VSS vss 0 0
VSUB VSUBS 0 0
VSP sp 0 PULSE(0 {vinp:.12f} 0.05n 20p 20p 20n 40n)
VSN sn 0 PULSE(0 {vinn:.12f} 0.05n 20p 20p 20n 40n)
VCS clk_sample 0 PULSE(0 1.8 1.00n 20p 20p 5n 10n)
VCL clk_latch 0 PULSE(0 1.8 2.00n 20p 20p 5n 10n)
VCM vcm_reset 0 0.9
XFRONT vss vdd sp sense_p clk_sample vcm_reset clk_latch sense_n sn sky130_ultra_sense_capacitive_frontend
RBIASP sense_p vcm_reset 100G
RBIASN sense_n vcm_reset 100G
CGP sense_p 0 3f
CGN sense_n 0 3f
.tran 20p 3n
.measure tran sense_p_after_v FIND v(sense_p) AT=2.60n
.measure tran sense_n_after_v FIND v(sense_n) AT=2.60n
.measure tran sample_p_after_v FIND v(sp) AT=2.60n
.measure tran sample_n_after_v FIND v(sn) AT=2.60n
.control
set noaskquit
run
.endc
.end
"""


def deck_frontend_plus_transistor_dc_gate() -> str:
    diff_v = TARGET_DIFF_MV / 1000.0
    vinp = 0.9 + diff_v / 2.0
    vinn = 0.9 - diff_v / 2.0
    return f"""* Probe D: extracted frontend drives transistor gates through large isolation.
.global VSUBS
.lib "{PDK_LIB}" tt
.include "{FRONTEND_NETLIST}"
VSUB VSUBS 0 0
VDD_SRC vdd 0 1.8
VSS vss 0 0
VSP sp 0 PULSE(0 {vinp:.12f} 0.05n 20p 20p 20n 40n)
VSN sn 0 PULSE(0 {vinn:.12f} 0.05n 20p 20p 20n 40n)
VCS clk_sample 0 PULSE(0 1.8 1.00n 20p 20p 5n 10n)
VCL clk_latch 0 PULSE(0 1.8 2.00n 20p 20p 5n 10n)
VCM vcm_reset 0 0.9
XFRONT vss vdd sp sense_p clk_sample vcm_reset clk_latch sense_n sn sky130_ultra_sense_capacitive_frontend
RBIASP sense_p vcm_reset 100G
RBIASN sense_n vcm_reset 100G
RGP sense_p gate_p 1Meg
RGN sense_n gate_n 1Meg
RGBP gate_p vcm_reset 100Meg
RGBN gate_n vcm_reset 100Meg
{transistor_stage_body("gate_p", "gate_n")}
.tran 20p 3n
.measure tran sense_p_after_v FIND v(sense_p) AT=2.60n
.measure tran sense_n_after_v FIND v(sense_n) AT=2.60n
.measure tran gate_p_after_v FIND v(gate_p) AT=2.60n
.measure tran gate_n_after_v FIND v(gate_n) AT=2.60n
.measure tran outp_after_v FIND v(outp) AT=2.60n
.measure tran outn_after_v FIND v(outn) AT=2.60n
.control
set noaskquit
run
.endc
.end
"""


PROBES = [
    ("standalone_transistor_transient", deck_standalone_transient),
    ("measured_sense_with_equivalent_cap_load", deck_frontend_equivalent_cap_load),
    ("extracted_frontend_with_gate_cap_only", deck_frontend_plus_gate_cap_only),
    ("extracted_frontend_with_isolated_real_transistor_gates", deck_frontend_plus_transistor_dc_gate),
]


def run_probe(name: str, deck_builder: Any) -> dict[str, Any]:
    DECK_OUT.write_text(deck_builder(), encoding="utf-8")
    try:
        result = subprocess.run(
            ["timeout", f"{NGSPICE_TIMEOUT_S}s", "ngspice", "-b", str(DECK_OUT)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=NGSPICE_TIMEOUT_S + 3,
        )
    except subprocess.TimeoutExpired:
        return {"probe": name, "ngspice_returncode": None, "ngspice_timed_out": True, "measured": False}
    row: dict[str, Any] = {
        "probe": name,
        "ngspice_returncode": result.returncode,
        "ngspice_timed_out": result.returncode == 124,
        "measured": result.returncode == 0,
    }
    if result.returncode != 0:
        row["error_excerpt"] = (result.stdout + result.stderr)[-1200:]
        return row
    for measurement in [
        "sense_p_after_v",
        "sense_n_after_v",
        "sample_p_after_v",
        "sample_n_after_v",
        "gate_p_after_v",
        "gate_n_after_v",
        "outp_after_v",
        "outn_after_v",
        "tail_after_v",
    ]:
        try:
            row[measurement] = read_measure(result.stdout, measurement)
        except ValueError:
            pass
    if "outp_after_v" in row and "outn_after_v" in row:
        row["output_diff_v"] = row["outn_after_v"] - row["outp_after_v"]
        row["output_sign_preserved"] = row["output_diff_v"] > 0.0
    if "sense_p_after_v" in row and "sense_n_after_v" in row:
        row["sense_diff_v"] = row["sense_p_after_v"] - row["sense_n_after_v"]
        row["sense_sign_preserved"] = row["sense_diff_v"] > 0.0
    if "gate_p_after_v" in row and "gate_n_after_v" in row:
        row["gate_diff_v"] = row["gate_p_after_v"] - row["gate_n_after_v"]
        row["gate_sign_preserved"] = row["gate_diff_v"] > 0.0
    return row


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    frontend = json.loads(SOURCE_FRONTEND.read_text(encoding="utf-8"))
    transistor = json.loads(SOURCE_TRANSISTOR.read_text(encoding="utf-8"))
    handoff = json.loads(SOURCE_HANDOFF.read_text(encoding="utf-8"))
    SPICE_DIR.mkdir(parents=True, exist_ok=True)
    rows = [run_probe(name, builder) for name, builder in PROBES]
    measured = [row for row in rows if row["measured"]]
    return {
        "result_type": "sky130_transistor_handoff_probe_ladder",
        "status": "probe_ladder_measured_partial_cause" if measured else "probe_ladder_all_timed_out_or_failed",
        "source_frontend": rel(SOURCE_FRONTEND),
        "source_standalone_transistor": rel(SOURCE_TRANSISTOR),
        "source_full_transistor_handoff": rel(SOURCE_HANDOFF),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "pdk_model_library": str(PDK_LIB),
        "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
        "probe_count": len(rows),
        "measured_probe_count": len(measured),
        "timed_out_probe_count": sum(1 for row in rows if row["ngspice_timed_out"]),
        "uses_sky130_transistor_input_stage": True,
        "uses_extracted_frontend_netlist_in_some_probes": True,
        "full_handoff_status": handoff["status"],
        "frontend_minimum_transfer_ratio": frontend["minimum_sample_to_sense_transfer_ratio"],
        "standalone_input_stage_gain_v_per_v": transistor["rows"][1]["gain_v_per_v"],
        "strict_payload_ready": False,
        "accepted_post_layout_written": False,
        "rows": rows,
        "claim_boundary": {
            "allowed": "runs smaller probes that separate transistor transient behavior, equivalent capacitive loading, extracted frontend loading, and isolated real-gate handoff",
            "not_allowed": "does not replace the full four-case transistor handoff, does not prove latch or SAR behavior, and does not create accepted post-layout converter evidence",
        },
    }


def write_csv(report: dict[str, Any]) -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    keys = sorted({key for row in report["rows"] for key in row})
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(report["rows"])


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Transistor Handoff Probe Ladder",
        "",
        f"- status: `{report['status']}`",
        f"- probe count: `{report['probe_count']}`",
        f"- measured probe count: `{report['measured_probe_count']}`",
        f"- timed-out probe count: `{report['timed_out_probe_count']}`",
        f"- full handoff status: `{report['full_handoff_status']}`",
        f"- strict payload ready: `{report['strict_payload_ready']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "The full handoff fails where too many things are joined at once. This probe ladder breaks the problem into smaller electrical questions: can the transistor stage run in transient, can it run with frontend-sized capacitance, can the extracted frontend survive gate-like capacitance, and can the extracted frontend touch isolated real transistor gates.",
        "",
        "## Probe Results",
        "",
        "| probe | measured | timed out | sense sign | gate sign | output sign | output diff mV |",
        "|---|---|---|---|---|---|---:|",
    ]
    for row in report["rows"]:
        output_mv = row.get("output_diff_v")
        lines.append(
            f"| `{row['probe']}` | `{row['measured']}` | `{row['ngspice_timed_out']}` | `{row.get('sense_sign_preserved', '')}` | `{row.get('gate_sign_preserved', '')}` | `{row.get('output_sign_preserved', '')}` | `{'' if output_mv is None else f'{output_mv * 1000.0:.6f}'}` |"
        )
    lines.extend(
        [
            "",
            "## Refused Claim",
            "",
            report["claim_boundary"]["not_allowed"],
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_csv(report)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("sky130_transistor_handoff_probe_ladder")
    print(f"status,{report['status']}")
    print(f"probe_count,{report['probe_count']}")
    print(f"measured_probe_count,{report['measured_probe_count']}")
    print(f"timed_out_probe_count,{report['timed_out_probe_count']}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    print(f"csv,{CSV_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
