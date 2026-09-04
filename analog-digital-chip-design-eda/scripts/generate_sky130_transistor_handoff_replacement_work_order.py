#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-transistor-handoff-replacement-work-order.json"
OUT_MD = EVIDENCE / "sky130-transistor-handoff-replacement-work-order.md"

ACTIVE_MACRO = EVIDENCE / "sky130-frontend-input-stage-handoff-candidate.json"
TIMED_OUT_PROXY = EVIDENCE / "first-real-converter-frontend-to-input-stage-proxy.json"
INPUT_STAGE = EVIDENCE / "sky130-comparator-input-stage-ngspice.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def build_report() -> dict[str, Any]:
    macro = load(ACTIVE_MACRO)
    proxy = load(TIMED_OUT_PROXY)
    input_stage = load(INPUT_STAGE)
    return {
        "result_type": "sky130_transistor_handoff_replacement_work_order",
        "status": "transistor_handoff_replacement_work_order_ready",
        "candidate_id": "aimc_readout_candidate_001",
        "source_evidence": [rel(ACTIVE_MACRO), rel(TIMED_OUT_PROXY), rel(INPUT_STAGE)],
        "current_passed_boundary": {
            "object": macro["handoff_candidate"],
            "status": macro["status"],
            "minimum_output_diff_v": macro["minimum_output_diff_v"],
            "sign_pass_count": macro["sign_pass_count"],
            "case_count": macro["case_count"],
            "uses_active_gain_macro": macro["uses_active_gain_macro"],
            "uses_sky130_transistor_input_stage": macro["uses_sky130_transistor_input_stage"],
        },
        "current_failed_boundary": {
            "object": "frontend_to_sky130_transistor_input_stage_proxy",
            "status": proxy["status"],
            "timed_out_case_count": proxy["timed_out_case_count"],
            "case_count": proxy["case_count"],
        },
        "replacement_object": {
            "name": "sky130_frontend_transistor_input_stage_handoff_candidate",
            "purpose": "replace the active gain macro with a Sky130 transistor differential input stage while preserving the same frontend input cases and acceptance tests",
            "must_keep_from_macro_run": [
                "same extracted ultra frontend netlist",
                "same positive and negative comparator-budget input cases",
                "same quiet-reset and reset-pulse cases",
                "same sign-handoff check",
                "same 0.5 mV minimum active-output margin",
                "same explicit false accepted_post_layout_written flag",
            ],
            "must_replace": [
                "bounded gain macro",
                "ideal output without input capacitance",
                "macro gain imported from separate evidence",
            ],
            "must_add": [
                "Sky130 nfet or complementary input devices connected directly to sense_p and sense_n",
                "finite input capacitance that loads the extracted frontend",
                "explicit bias current or reset path that lets ngspice solve without unbounded model startup",
                "measured output polarity and gain from the same deck",
                "runtime-bound failure reporting for each case",
            ],
        },
        "acceptance_tests": [
            "T1. every case returns from ngspice inside the runtime bound",
            "T2. measured sign matches the original sampled input sign in all four cases",
            "T3. minimum active output difference is at least 0.5 mV",
            "T4. sample-to-sense transfer after transistor loading stays within 10 percent of the macro handoff run",
            "T5. report states uses_sky130_transistor_input_stage=true, uses_active_gain_macro=false, same_run_strict_payload_ready=false, accepted_post_layout_written=false",
        ],
        "expected_outputs": [
            "labs/analog/analog-in-memory-foundation-model-hardware/spice/sky130_frontend_transistor_input_stage_handoff_candidate.sp",
            "labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-frontend-transistor-input-stage-handoff-candidate.csv",
            "evidence/aimc-simulator-adapters/sky130-frontend-transistor-input-stage-handoff-candidate.json",
            "evidence/aimc-simulator-adapters/sky130-frontend-transistor-input-stage-handoff-candidate.md",
            "docs/research/sky130-frontend-transistor-input-stage-handoff-candidate.md",
        ],
        "first_principle": "The macro proof says the signal chain is mathematically possible. The transistor replacement must show the same thing physically: the real input devices must sense the frontend voltage without stealing too much charge, must bias into a solvable operating point, and must create enough output difference for the latch.",
        "still_not_done_after_replacement": [
            "clocked latch resolution",
            "kickback into the sampled frontend",
            "comparator offset and noise",
            "SAR bit cycling",
            "DAC switching",
            "full converter energy",
            "DRC/LVS-clean extracted area",
            "same-run strict converter payload",
        ],
        "same_run_strict_payload_ready": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "defines the exact next replacement for the active gain macro using current passing and failing evidence",
            "not_allowed": "does not prove the transistor handoff, latch, SAR, full converter, accepted post-layout evidence, or replacement economics",
        },
        "reference_input_stage_gain_v_per_v": input_stage["rows"][0]["gain_v_per_v"],
    }


def write_markdown(report: dict[str, Any]) -> None:
    obj = report["replacement_object"]
    passed = report["current_passed_boundary"]
    failed = report["current_failed_boundary"]
    lines = [
        "# Sky130 Transistor Handoff Replacement Work Order",
        "",
        f"- status: `{report['status']}`",
        f"- candidate id: `{report['candidate_id']}`",
        f"- replacement object: `{obj['name']}`",
        f"- active-macro status: `{passed['status']}`",
        f"- macro minimum output diff V: `{passed['minimum_output_diff_v']:.9e}`",
        f"- macro sign pass count: `{passed['sign_pass_count']}` of `{passed['case_count']}`",
        f"- direct transistor proxy status: `{failed['status']}`",
        f"- direct transistor timed-out case count: `{failed['timed_out_case_count']}` of `{failed['case_count']}`",
        f"- same-run strict payload ready: `{report['same_run_strict_payload_ready']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        report["first_principle"],
        "",
        "A voltage gain macro can show that the sign and size of the signal are enough in equations. A transistor replacement must show that real devices can do the same job while adding capacitance, needing bias current, and forcing ngspice to find a physical operating point.",
        "",
        "## Replacement Object",
        "",
        f"`{obj['name']}`",
        "",
        obj["purpose"],
        "",
        "Must keep from the macro run:",
    ]
    lines.extend(f"- {item}" for item in obj["must_keep_from_macro_run"])
    lines.extend(["", "Must replace:"])
    lines.extend(f"- {item}" for item in obj["must_replace"])
    lines.extend(["", "Must add:"])
    lines.extend(f"- {item}" for item in obj["must_add"])
    lines.extend(["", "## Acceptance Tests", ""])
    lines.extend(f"- {item}" for item in report["acceptance_tests"])
    lines.extend(["", "## Expected Outputs", ""])
    lines.extend(f"- `{item}`" for item in report["expected_outputs"])
    lines.extend(["", "## Still Not Done After Replacement", ""])
    lines.extend(f"- {item}" for item in report["still_not_done_after_replacement"])
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("sky130_transistor_handoff_replacement_work_order")
    print(f"status,{report['status']}")
    print(f"replacement_object,{report['replacement_object']['name']}")
    print(f"acceptance_tests,{len(report['acceptance_tests'])}")
    print(f"expected_outputs,{len(report['expected_outputs'])}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
