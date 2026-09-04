#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "first-real-converter-combined-active-handoff-work-order.json"
OUT_MD = EVIDENCE / "first-real-converter-combined-active-handoff-work-order.md"

FRONTEND = EVIDENCE / "sky130-ultra-sense-frontend-candidate.json"
DIRECT_PROXY = EVIDENCE / "first-real-converter-frontend-to-input-stage-proxy.json"
ESTIMATE = EVIDENCE / "first-real-converter-frontend-active-handoff-estimate.json"

CANDIDATE_ID = "aimc_readout_candidate_001"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def build_report() -> dict[str, Any]:
    frontend = load(FRONTEND)
    direct = load(DIRECT_PROXY)
    estimate = load(ESTIMATE)
    return {
        "result_type": "first_real_converter_combined_active_handoff_work_order",
        "status": "combined_active_handoff_work_order_ready",
        "candidate_id": CANDIDATE_ID,
        "source_evidence": [
            rel(FRONTEND),
            rel(DIRECT_PROXY),
            rel(ESTIMATE),
        ],
        "why_this_is_next": {
            "frontend_transfer_ratio": frontend["minimum_sample_to_sense_transfer_ratio"],
            "frontend_minimum_sense_diff_v": estimate["minimum_frontend_sense_diff_v"],
            "separate_input_stage_gain_v_per_v": estimate["minimum_measured_input_stage_gain_v_per_v"],
            "estimated_active_output_diff_v": estimate["minimum_estimated_output_diff_v"],
            "direct_proxy_status": direct["status"],
            "reason": "The passive frontend keeps sign but leaves a small voltage. Separate active gain says that small voltage may become usable. The direct handoff timed out, so the next work is a robust same-deck combined handoff, not another estimate.",
        },
        "new_physical_object": {
            "name": "sky130_frontend_input_stage_handoff_candidate",
            "role": "one deck that connects the extracted ultra frontend output boundary to a Sky130 active input stage and measures whether the active output keeps sign and becomes large enough for a latch",
            "minimum_contents": [
                "the extracted ultra frontend capacitance or an equivalent explicit RC network with named sense_p and sense_n nodes",
                "a Sky130 transistor differential input stage with bounded bias current and load",
                "explicit common-mode reset or bias path for sense_p and sense_n",
                "bounded operating-point and transient commands that finish under the local runtime gate",
                "positive and negative input cases at the comparator-budget edge",
            ],
        },
        "acceptance_tests": [
            {
                "name": "A1. bounded simulator run",
                "must_show": "ngspice returns for every positive and negative case within the timeout bound",
                "why": "a proof path cannot depend on an unbounded interactive simulator stall",
            },
            {
                "name": "A2. sign handoff",
                "must_show": "the active output sign matches the original sampled input sign for quiet reset and reset-pulse cases",
                "why": "gain is useless if the circuit flips the decision",
            },
            {
                "name": "A3. active output margin",
                "must_show": "minimum active output difference is at least 0.5 mV before the latch",
                "why": "the latch needs a larger state than the passive frontend's tens of microvolts",
            },
            {
                "name": "A4. loading check",
                "must_show": "the added input stage does not reduce frontend sense transfer below the current 0.437908 ratio by more than 10 percent",
                "why": "an amplifier that steals the stored charge can erase the signal it is supposed to enlarge",
            },
            {
                "name": "A5. claim boundary",
                "must_show": "the result explicitly keeps accepted_post_layout_written false and same_run_strict_payload_ready false",
                "why": "this is still a handoff block, not the full converter payload",
            },
        ],
        "expected_outputs": [
            "labs/analog/analog-in-memory-foundation-model-hardware/spice/sky130_frontend_input_stage_handoff_candidate.sp",
            "labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-frontend-input-stage-handoff-candidate.csv",
            "evidence/aimc-simulator-adapters/sky130-frontend-input-stage-handoff-candidate.json",
            "evidence/aimc-simulator-adapters/sky130-frontend-input-stage-handoff-candidate.md",
            "docs/research/sky130-frontend-input-stage-handoff-candidate.md",
        ],
        "done_after_this_only_if": [
            "bounded ngspice run finishes for all cases",
            "both polarities preserve sign",
            "active output difference is large enough for the latch target",
            "the result names remaining latch, SAR, energy, noise, area, DRC/LVS, and same-run payload blockers",
        ],
        "not_done_after_this": [
            "clocked latch resolution",
            "comparator offset and noise",
            "kickback back into the sample nodes",
            "SAR bit cycling",
            "full supply-current energy",
            "DRC/LVS-clean extracted area",
            "strict accepted post-layout converter evidence",
        ],
        "accepted_post_layout_written": False,
        "same_run_strict_payload_ready": False,
        "claim_boundary": {
            "allowed": "turns the current active-handoff timeout and estimate into an exact executable next work order",
            "not_allowed": "does not prove the combined active handoff, full comparator, full converter, accepted post-layout evidence, or replacement economics",
        },
    }


def write_markdown(report: dict[str, Any]) -> None:
    why = report["why_this_is_next"]
    obj = report["new_physical_object"]
    lines = [
        "# First Real Converter Combined Active Handoff Work Order",
        "",
        f"- status: `{report['status']}`",
        f"- candidate id: `{report['candidate_id']}`",
        f"- frontend transfer ratio: `{why['frontend_transfer_ratio']:.6f}`",
        f"- frontend minimum sense diff V: `{why['frontend_minimum_sense_diff_v']:.9e}`",
        f"- separate input-stage gain V/V: `{why['separate_input_stage_gain_v_per_v']:.6f}`",
        f"- estimated active output diff V: `{why['estimated_active_output_diff_v']:.9e}`",
        f"- direct proxy status: `{why['direct_proxy_status']}`",
        f"- same-run strict payload ready: `{report['same_run_strict_payload_ready']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "The signal chain has two jobs. The passive frontend must not lose the sign of the sampled voltage. The active input stage must spend current to make that signed difference larger. The present evidence says the first job works weakly, and the second job works separately. The missing proof is whether the two jobs work when they are connected in one bounded circuit run.",
        "",
        "A small-signal estimate is not enough because the active stage is not an invisible calculator. Its input capacitance, bias path, common-mode point, and operating-point solve can change the very voltage it is supposed to amplify. The next object must therefore connect the frontend and input stage directly and measure the handoff.",
        "",
        "## New Physical Object",
        "",
        f"`{obj['name']}`",
        "",
        obj["role"],
        "",
        "Minimum contents:",
    ]
    lines.extend(f"- {item}" for item in obj["minimum_contents"])
    lines.extend(["", "## Acceptance Tests", ""])
    for item in report["acceptance_tests"]:
        lines.extend(
            [
                f"### {item['name']}",
                "",
                f"Must show: {item['must_show']}.",
                "",
                f"Why: {item['why']}.",
                "",
            ]
        )
    lines.extend(["## Expected Outputs", ""])
    lines.extend(f"- `{item}`" for item in report["expected_outputs"])
    lines.extend(["", "## Done After This Only If", ""])
    lines.extend(f"- {item}" for item in report["done_after_this_only_if"])
    lines.extend(["", "## Still Not Done After This", ""])
    lines.extend(f"- {item}" for item in report["not_done_after_this"])
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("first_real_converter_combined_active_handoff_work_order")
    print(f"status,{report['status']}")
    print(f"candidate_id,{report['candidate_id']}")
    print(f"acceptance_tests,{len(report['acceptance_tests'])}")
    print(f"expected_outputs,{len(report['expected_outputs'])}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
