#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
LATCH_MARGIN = EVIDENCE / "sky130-balanced-frontend-latch-decision.json"
STARTER = EVIDENCE / "sky130-balanced-frontend-starter-extraction.json"
OUT_JSON = EVIDENCE / "sky130-balanced-frontend-sense-gain-target.json"
OUT_MD = EVIDENCE / "sky130-balanced-frontend-sense-gain-target.md"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Balanced Frontend Sense-Gain Target",
        "",
        f"- status: `{report['status']}`",
        f"- minimum sense-to-latch-input ratio: `{report['minimum_sense_to_latch_input_ratio']:.6f}`",
        f"- required sense gain improvement: `{report['required_sense_gain_improvement_x']:.2f}x`",
        f"- target sample-to-sense transfer ratio: `{report['target_sample_to_sense_transfer_ratio']:.6f}`",
        f"- current minimum sample-to-sense transfer ratio: `{report['current_minimum_sample_to_sense_transfer_ratio']:.6f}`",
        f"- accepted ready now: `{report['accepted_ready_now']}`",
        "",
        "## First Principle",
        "",
        "The balanced frontend fixed the direction problem. It did not yet fix the size problem. A latch cannot make a reliable digital decision from a sign that is present but too small.",
        "",
        "The sample voltage difference is the thing we want to preserve. The sense-node voltage difference is what the latch actually receives. The useful design number is therefore simple: how much of the sample difference reaches the sense nodes before the latch is asked to decide.",
        "",
        "The current extracted starter sends only about one tenth of the needed latch input. The next physical frontend must increase sample-to-sense transfer while keeping the two sides matched. That means larger intentional coupling, smaller wasted sense-node capacitance, or a preamp/buffer. Each choice has a cost: more kickback, more offset, more power, or more area.",
        "",
        "## Design Target",
        "",
        "| quantity | value | meaning |",
        "|---|---:|---|",
        f"| current minimum sense signal | `{report['minimum_abs_sense_diff_v']:.9e} V` | smallest extracted sense difference across the four passing sign cases |",
        f"| latch proxy input target | `{report['ideal_latch_input_target_v']:.9e} V` | input size used by the earlier passing latch proxy |",
        f"| required gain improvement | `{report['required_sense_gain_improvement_x']:.2f}x` | multiplier needed before rerunning latch from extracted sense nodes |",
        f"| sense capacitance delta | `{report['sense_capacitance_delta_ff']:.6f} fF` | balance is good; the problem is transfer size, not first-order mismatch |",
        "",
        "## Allowed Next Designs",
        "",
    ]
    for item in report["allowed_next_designs"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Acceptance Checks", ""])
    for item in report["acceptance_checks"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    latch = load(LATCH_MARGIN)
    starter = load(STARTER)
    min_ratio = float(latch["minimum_sense_to_latch_input_ratio"])
    target_ratio = 1.0
    required_improvement = target_ratio / min_ratio if min_ratio else float("inf")
    rows = latch["rows"]
    transfer_ratios = [
        abs(float(row["sense_diff_after_v"])) / abs(float(row["input_diff_mv"]) / 1000.0)
        for row in rows
        if row.get("input_diff_mv")
    ]
    report = {
        "result_type": "sky130_balanced_frontend_sense_gain_target",
        "status": "sense_gain_target_ready_before_latch_rerun",
        "source_latch_margin": "evidence/aimc-simulator-adapters/sky130-balanced-frontend-latch-decision.json",
        "source_starter_extraction": "evidence/aimc-simulator-adapters/sky130-balanced-frontend-starter-extraction.json",
        "minimum_sense_to_latch_input_ratio": min_ratio,
        "required_sense_gain_improvement_x": required_improvement,
        "target_sample_to_sense_transfer_ratio": target_ratio,
        "current_minimum_sample_to_sense_transfer_ratio": min(transfer_ratios),
        "current_maximum_sample_to_sense_transfer_ratio": max(transfer_ratios),
        "minimum_abs_sense_diff_v": latch["minimum_abs_sense_diff_v"],
        "ideal_latch_input_target_v": latch["ideal_latch_input_target_v"],
        "sense_capacitance_delta_ff": starter["sense_capacitance_delta_ff"],
        "allowed_next_designs": [
            "increase mirrored sample_p-to-sense_p and sample_n-to-sense_n coupling while keeping extracted sense_p and sense_n totals matched",
            "reduce non-signal capacitance on sense_p and sense_n so less sampled charge is wasted on clock, supply, ground, and substrate paths",
            "add a small differential preamp or source-follower buffer only if its offset, noise, and input capacitance are measured separately",
            "rerun extracted sign preservation after every physical edit before trying the latch again",
        ],
        "acceptance_checks": [
            "minimum sample-to-sense transfer ratio reaches the latch proxy target or a new bounded latch proof resolves from the smaller input",
            "both input signs preserve sign after extraction",
            "sense_p and sense_n total capacitance remain matched within the starter extraction balance rule",
            "sample-node kickback remains below the hard half-LSB comparator boundary",
            "accepted evidence remains false until latch resolution, offset/noise, DRC, and LVS are all available for the same physical candidate",
        ],
        "accepted_ready_now": False,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "turns the measured extracted sense-node shortfall into a numeric next frontend target",
            "not_allowed": "does not modify layout, does not prove latch resolution, does not prove offset or noise, does not run DRC/LVS, and does not write accepted post-layout evidence",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print("sky130_balanced_frontend_sense_gain_target")
    print(f"status,{report['status']}")
    print(f"required_sense_gain_improvement_x,{required_improvement:.2f}")
    print(f"current_minimum_sample_to_sense_transfer_ratio,{report['current_minimum_sample_to_sense_transfer_ratio']:.6f}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
