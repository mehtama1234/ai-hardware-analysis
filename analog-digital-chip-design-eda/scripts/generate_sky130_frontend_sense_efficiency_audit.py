#!/usr/bin/env python3
import json
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-frontend-sense-efficiency-audit.json"
OUT_MD = EVIDENCE / "sky130-frontend-sense-efficiency-audit.md"


def load(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def min_transfer(rows: list[dict]) -> float:
    transfers = []
    for row in rows:
        if "sample_to_sense_transfer_ratio" in row:
            transfers.append(float(row["sample_to_sense_transfer_ratio"]))
        else:
            sample = abs(float(row.get("sample_diff_after_v", 0.0)))
            sense = abs(float(row.get("sense_diff_after_v", 0.0)))
            transfers.append(sense / sample if sample else 0.0)
    return min(transfers)


def direct_efficiency(direct_ff: float | None, sense_total_ff: float) -> float | None:
    if direct_ff is None or not sense_total_ff:
        return None
    return direct_ff / sense_total_ff


def candidate_row(name: str, extraction: dict, measured: dict, direct_ff: float | None) -> dict:
    sense_total = mean([
        float(extraction["capacitance_totals_ff"]["sense_p"]),
        float(extraction["capacitance_totals_ff"]["sense_n"]),
    ])
    transfer = min_transfer(measured["rows"])
    return {
        "candidate": name,
        "direct_sample_to_sense_capacitance_ff": direct_ff,
        "average_sense_node_capacitance_ff": sense_total,
        "direct_to_sense_capacitance_ratio": direct_efficiency(direct_ff, sense_total),
        "minimum_sample_to_sense_transfer_ratio": transfer,
        "remaining_transfer_improvement_x": 1.0 / transfer if transfer else None,
        "sign_preserved_case_count": int(measured.get("passing_sign_case_count", measured.get("passing_case_count", 0))),
        "case_count": int(measured["case_count"]),
    }


def fmt(value: float | None, digits: int = 6) -> str:
    if value is None:
        return "not extracted"
    return f"{value:.{digits}f}"


def write_md(report: dict) -> None:
    lines = [
        "# Sky130 Frontend Sense Efficiency Audit",
        "",
        f"- status: `{report['status']}`",
        f"- target transfer ratio: `{report['target_sample_to_sense_transfer_ratio']:.6f}`",
        f"- best measured transfer ratio: `{report['best_measured_transfer_ratio']:.6f}`",
        f"- remaining transfer improvement: `{report['remaining_transfer_improvement_x']:.2f}x`",
        f"- accepted post-layout evidence written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "The comparator does not see capacitance. It sees voltage.",
        "",
        "A frontend can add more direct sample-to-sense capacitance and still fail to give a large enough voltage if the sense node also becomes heavier. The useful question is therefore not only how much coupling was added. The useful question is how much of the sampled difference became voltage at the sense node.",
        "",
        "In plain terms: useful coupling is the pipe that moves charge, and total sense capacitance is the bucket that charge must fill. A bigger pipe helps. A bigger bucket pushes the voltage back down. The transfer improves only when the pipe grows faster than the bucket.",
        "",
        "## Measured Candidates",
        "",
        "| candidate | direct sample-to-sense fF | average sense capacitance fF | direct/sense ratio | minimum transfer | remaining gap | sign cases |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        gap = row["remaining_transfer_improvement_x"]
        lines.append(
            f"| {row['candidate']} | {fmt(row['direct_sample_to_sense_capacitance_ff'])} | "
            f"{row['average_sense_node_capacitance_ff']:.6f} | "
            f"{fmt(row['direct_to_sense_capacitance_ratio'])} | "
            f"{row['minimum_sample_to_sense_transfer_ratio']:.6f} | "
            f"{gap:.2f}x | {row['sign_preserved_case_count']}/{row['case_count']} |"
        )
    lines.extend([
        "",
        "## What The Table Says",
        "",
        "The balanced frontend solved the sign problem but left the signal small. Its measured transfer is about one tenth of the sampled voltage difference.",
        "",
        "The strong frontend made the direct coupling much larger and transfer rose to about 0.37. That proved the design direction was real: moving the sampled node closer to the sense node did produce more comparator input voltage.",
        "",
        "The ultra frontend pushed direct coupling further, to `0.8 fF`, and transfer improved again to `0.437908`. But the improvement slowed because the sense node also became larger. More of the layout is now being charged, so not every extra femtofarad of direct coupling becomes useful voltage.",
        "",
        "## What This Means For The Next Circuit",
        "",
        "The next circuit should not simply make the coupling plates larger again. That may keep increasing the sense-node bucket along with the pipe.",
        "",
        "The next physical move should do one of two things:",
        "",
        "1. reduce wasted sense capacitance while keeping direct sample-to-sense coupling high",
        "2. add a measured preamp or buffer so the small sense voltage is amplified before latch decision",
        "",
        "The first option is a passive layout repair. The second option spends active circuit power to buy decision margin. Both are legitimate, but they prove different things and should be measured separately.",
        "",
        "## Claim Boundary",
        "",
        report["claim_boundary"]["allowed"],
        "",
        report["claim_boundary"]["not_allowed"],
    ])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    balanced_extraction = load("sky130-balanced-frontend-starter-extraction.json")
    balanced_sign = load("sky130-balanced-frontend-sign-preservation.json")
    strong = load("sky130-strong-sense-frontend-candidate.json")
    ultra = load("sky130-ultra-sense-frontend-candidate.json")

    rows = [
        candidate_row("balanced", balanced_extraction, balanced_sign, None),
        candidate_row("strong", strong, strong, float(strong["direct_sample_to_sense_capacitance_ff"])),
        candidate_row("ultra", ultra, ultra, float(ultra["direct_sample_to_sense_capacitance_ff"])),
    ]
    best_transfer = max(row["minimum_sample_to_sense_transfer_ratio"] for row in rows)
    report = {
        "result_type": "sky130_frontend_sense_efficiency_audit",
        "status": "sense_efficiency_audit_shows_transfer_plateau_before_latch_target",
        "source_evidence": [
            "evidence/aimc-simulator-adapters/sky130-balanced-frontend-starter-extraction.json",
            "evidence/aimc-simulator-adapters/sky130-balanced-frontend-sign-preservation.json",
            "evidence/aimc-simulator-adapters/sky130-strong-sense-frontend-candidate.json",
            "evidence/aimc-simulator-adapters/sky130-ultra-sense-frontend-candidate.json",
        ],
        "target_sample_to_sense_transfer_ratio": 1.0,
        "best_measured_transfer_ratio": best_transfer,
        "remaining_transfer_improvement_x": 1.0 / best_transfer if best_transfer else None,
        "rows": rows,
        "claim_boundary": {
            "allowed": "This audit explains why extracted frontend transfer improves slower than direct coupling and identifies the next physical design choice.",
            "not_allowed": "This audit does not prove latch resolution, active reset devices, comparator offset, comparator noise, DRC/LVS, SAR conversion, or accepted post-layout converter evidence.",
        },
        "accepted_ready_now": False,
        "accepted_post_layout_written": False,
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print("sky130_frontend_sense_efficiency_audit")
    print(f"best_measured_transfer_ratio,{best_transfer:.6f}")
    print(f"remaining_transfer_improvement_x,{report['remaining_transfer_improvement_x']:.2f}")


if __name__ == "__main__":
    main()
