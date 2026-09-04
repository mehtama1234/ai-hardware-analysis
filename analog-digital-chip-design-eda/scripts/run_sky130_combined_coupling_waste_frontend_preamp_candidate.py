#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import run_sky130_lower_waste_frontend_preamp_candidate as base


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
CAP_BUDGET = EVIDENCE / "sky130-frontend-preamp-capacitance-budget.json"
CANDIDATE_NETLIST = LAB / "layout-workbench" / "extracted" / "sky130_combined_coupling_waste_frontend_candidate.spice"

base.CANDIDATE_NETLIST = CANDIDATE_NETLIST
base.Candidate_subckt = "sky130_combined_coupling_waste_frontend_candidate"
base.DECK_OUT = LAB / "spice" / "sky130_combined_coupling_waste_frontend_preamp_candidate.sp"
base.CSV_OUT = LAB / "measurements" / "sky130-combined-coupling-waste-frontend-preamp-candidate.csv"
base.OUT_JSON = EVIDENCE / "sky130-combined-coupling-waste-frontend-preamp-candidate.json"
base.OUT_MD = EVIDENCE / "sky130-combined-coupling-waste-frontend-preamp-candidate.md"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def cap_totals_and_useful(text: str) -> dict[str, float]:
    totals = {"sense_p": 0.0, "sense_n": 0.0}
    useful = 0.0
    for line in text.splitlines():
        match = re.match(r"C\d+\s+(\S+)\s+(\S+)\s+([-+0-9.]+)f\b", line.strip())
        if not match:
            continue
        node_a, node_b, value = match.groups()
        value_ff = float(value)
        if base.is_useful_sample_sense_cap(node_a, node_b):
            useful += value_ff / 2.0
        for node in (node_a, node_b):
            if node in totals:
                totals[node] += value_ff
    return {
        "sense_p": totals["sense_p"],
        "sense_n": totals["sense_n"],
        "average_sense": (totals["sense_p"] + totals["sense_n"]) / 2.0,
        "average_useful": useful,
    }


def write_candidate_netlist(_unused_scale: float) -> dict[str, Any]:
    budget = load(CAP_BUDGET)
    source_text = base.SOURCE_NETLIST.read_text(encoding="utf-8")
    source_caps = cap_totals_and_useful(source_text)
    target_total = float(budget["required_total_cap_if_useful_coupling_fixed_ff"])
    target_useful = float(budget["required_useful_coupling_if_total_cap_fixed_ff"])
    source_useful = float(budget["average_useful_sample_to_sense_cap_ff"])
    source_total = float(budget["average_sense_total_cap_ff"])
    useful_scale = target_useful / source_useful
    nonuseful_scale = (target_total - target_useful) / (source_total - source_useful)

    out_lines: list[str] = []
    scaled_useful_count = 0
    scaled_nonuseful_count = 0
    for line in source_text.splitlines():
        if line.startswith(".subckt sky130_ultra_sense_capacitive_frontend"):
            out_lines.append(line.replace("sky130_ultra_sense_capacitive_frontend", "sky130_combined_coupling_waste_frontend_candidate"))
            continue
        match = re.match(r"(C\d+\s+)(\S+)(\s+)(\S+)(\s+)([-+0-9.]+)(f\b.*)", line)
        if match:
            prefix, node_a, gap_a, node_b, gap_b, value, suffix = match.groups()
            touches_sense = node_a in {"sense_p", "sense_n"} or node_b in {"sense_p", "sense_n"}
            if base.is_useful_sample_sense_cap(node_a, node_b):
                out_lines.append(f"{prefix}{node_a}{gap_a}{node_b}{gap_b}{float(value) * useful_scale:.8g}{suffix}")
                scaled_useful_count += 1
                continue
            if touches_sense:
                out_lines.append(f"{prefix}{node_a}{gap_a}{node_b}{gap_b}{float(value) * nonuseful_scale:.8g}{suffix}")
                scaled_nonuseful_count += 1
                continue
        out_lines.append(line)
    candidate_text = "\n".join(out_lines).replace(".ends", ".ends sky130_combined_coupling_waste_frontend_candidate", 1) + "\n"
    CANDIDATE_NETLIST.write_text(candidate_text, encoding="utf-8")
    candidate_caps = cap_totals_and_useful(candidate_text)
    return {
        "source_totals_ff": {"sense_p": source_caps["sense_p"], "sense_n": source_caps["sense_n"]},
        "candidate_totals_ff": {"sense_p": candidate_caps["sense_p"], "sense_n": candidate_caps["sense_n"]},
        "source_average_useful_sample_to_sense_cap_ff": source_caps["average_useful"],
        "candidate_average_useful_sample_to_sense_cap_ff": candidate_caps["average_useful"],
        "scaled_nonuseful_sense_cap_count": scaled_nonuseful_count,
        "scaled_useful_sample_to_sense_cap_count": scaled_useful_count,
        "nonuseful_sense_cap_scale": nonuseful_scale,
        "useful_sample_to_sense_cap_scale": useful_scale,
    }


base.write_candidate_netlist = write_candidate_netlist


def main() -> int:
    report = base.build_report()
    report["result_type"] = "sky130_combined_coupling_waste_frontend_preamp_candidate"
    report["status"] = (
        "combined_coupling_waste_frontend_preamp_candidate_passed_scaled_rc_not_layout_proven"
        if report["output_margin_pass_count"] == report["case_count"]
        else "combined_coupling_waste_frontend_preamp_candidate_failed_scaled_rc_margin"
    )
    report["candidate_netlist"] = base.rel(CANDIDATE_NETLIST)
    report["generated_deck"] = base.rel(base.DECK_OUT)
    report["csv"] = base.rel(base.CSV_OUT)
    report["source_lower_waste_candidate"] = "evidence/aimc-simulator-adapters/sky130-lower-waste-frontend-preamp-candidate.json"
    report["next_gate"] = (
        "The combined scaled-RC candidate reaches the attached-preamp margin target. The next required work is to draw and extract this combined capacitance move as real layout and rerun the same test."
        if report["output_margin_pass_count"] == report["case_count"]
        else "The combined scaled-RC candidate still misses margin. The next required work is active low-input-capacitance isolation before the preamp."
    )
    report["claim_boundary"] = {
        "allowed": "tests whether the combined useful-coupling and lower-waste capacitance targets are electrically sufficient in a scaled extracted-RC experiment",
        "not_allowed": "does not prove a drawn layout, DRC/LVS, latch decision, SAR conversion, post-layout converter energy, or accepted converter evidence",
    }
    base.write_csv(report["rows"])
    base.OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    base.write_md(report)
    md = base.OUT_MD.read_text(encoding="utf-8")
    md = md.replace("# Sky130 Lower-Waste Frontend Preamp Candidate", "# Sky130 Combined Coupling/Waste Frontend Preamp Candidate")
    md = md.replace("This experiment asks one narrow question: if the useful sample-to-sense capacitors stay the same and only the wasted sense-node capacitance is reduced to the budget target, does the same preamp finally receive enough voltage?", "This experiment asks one narrow question: if useful sample-to-sense coupling rises to its target and wasted sense-node capacitance falls to its target in the same scaled extracted-RC candidate, does the same preamp finally receive enough voltage?")
    md = md.replace("Reducing capacitance that does not carry signal should raise the sense voltage without changing the intended coupling path.", "More useful coupling moves more sampled charge onto the sense node. Less wasted capacitance divides that charge over a smaller load. The useful voltage is the result of both terms together.")
    base.OUT_MD.write_text(md, encoding="utf-8")
    print("sky130_combined_coupling_waste_frontend_preamp_candidate")
    print(f"status,{report['status']}")
    print(f"candidate_average_sense_cap_ff,{report['candidate_average_sense_cap_ff']:.6f}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"sign_pass_count,{report['sign_pass_count']}")
    print(f"output_margin_pass_count,{report['output_margin_pass_count']}")
    print(f"minimum_abs_preamp_output_diff_v,{report['minimum_abs_preamp_output_diff_v']:.9e}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{base.OUT_JSON}")
    print(f"markdown,{base.OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
