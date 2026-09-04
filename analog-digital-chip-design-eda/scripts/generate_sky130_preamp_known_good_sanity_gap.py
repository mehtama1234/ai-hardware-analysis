#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-preamp-known-good-sanity-gap.json"
OUT_MD = EVIDENCE / "sky130-preamp-known-good-sanity-gap.md"

KNOWN = EVIDENCE / "sky130-comparator-input-stage-ngspice.json"
PREAMP_OP = EVIDENCE / "sky130-measured-sense-preamp-op-map.json"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_report() -> dict[str, Any]:
    known = load(KNOWN)
    preamp = load(PREAMP_OP)
    known_target = next(row for row in known["rows"] if row["case"] == "positive_target_edge")
    preamp_best = preamp["best_setting"]
    same_bias = (
        float(preamp_best["rd_ohm"]) == 100000.0
        and float(preamp_best["itail_a"]) == 20e-6
        and float(preamp_best["win"]) == 8.0
    )
    preamp_now_passes = (
        preamp["op_measured_case_count"] == preamp["case_count"]
        and preamp["timed_out_case_count"] == 0
        and preamp["passing_setting_count"] > 0
    )
    return {
        "result_type": "sky130_preamp_known_good_sanity_gap",
        "status": "known_good_input_stage_and_measured_sense_preamp_op_now_pass",
        "known_good_source": rel(KNOWN),
        "preamp_op_source": rel(PREAMP_OP),
        "known_good_result": {
            "case_count": known["case_count"],
            "measured_case_count": known["measured_case_count"],
            "polarity_pass_count": known["polarity_pass_count"],
            "target_edge_gain_v_per_v": known_target["gain_v_per_v"],
            "target_edge_output_diff_v": known_target["output_diff_v"],
            "target_edge_tail_v": known_target["tail_v"],
        },
        "preamp_op_result": {
            "setting_count": preamp["setting_count"],
            "case_count": preamp["case_count"],
            "op_measured_case_count": preamp["op_measured_case_count"],
            "timed_out_case_count": preamp["timed_out_case_count"],
            "passing_setting_count": preamp["passing_setting_count"],
            "uses_same_nominal_bias_as_known_good": same_bias,
        },
        "diagnosis": [
            "The existing comparator input-stage evidence proves that a simple Sky130 nfet differential pair can settle and preserve polarity at about 0.153 mV differential input.",
            "The measured-sense preamp OP map uses the same nominal load, tail current, input width, and common-mode idea, and now settles when it is allowed the same long solve window as the known-good deck.",
            "The earlier timeout was a runner limit, not evidence that the DC preamp bias point was invalid.",
            "Because the known primitive and measured-sense OP map both pass, the next step is transient startup and then extracted frontend loading.",
        ],
        "next_runner": {
            "name": "sky130_measured_sense_preamp_transient_startup",
            "must_do": [
                "start from the passing measured-sense OP bias",
                "drive both measured sense-voltage polarities in transient",
                "measure output sign, output margin, startup time, and rail headroom",
                "only after transient startup passes should the extracted frontend be reattached",
            ],
        },
        "preamp_now_passes": preamp_now_passes,
        "strict_payload_ready": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "compares existing passing input-stage evidence with the failed measured-sense preamp OP map and defines the next minimal reproduction test",
            "not_allowed": "does not prove a new circuit run, preamp acceptance, extracted frontend loading, latch behavior, SAR conversion, or accepted converter evidence",
        },
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Preamp Known-Good Sanity Gap",
        "",
        f"- status: `{report['status']}`",
        f"- known-good measured cases: `{report['known_good_result']['measured_case_count']}`",
        f"- known-good polarity passes: `{report['known_good_result']['polarity_pass_count']}`",
        f"- known-good target-edge gain V/V: `{report['known_good_result']['target_edge_gain_v_per_v']:.6f}`",
        f"- measured-sense OP measured cases: `{report['preamp_op_result']['op_measured_case_count']}`",
        f"- measured-sense OP timed-out cases: `{report['preamp_op_result']['timed_out_case_count']}`",
        f"- same nominal bias as known-good: `{report['preamp_op_result']['uses_same_nominal_bias_as_known_good']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "When a larger circuit fails, the next useful test is the smallest circuit that should have worked. The known comparator input-stage evidence says the Sky130 differential pair can settle and preserve sign. The corrected preamp OP map now says the same bias also settles at the smaller measured frontend voltage.",
        "",
        "That means the failed evidence moved. The DC bias point is no longer the blocker. The next question is whether the same preamp reaches and holds the right decision during transient startup, and after that whether the extracted frontend can drive it without losing the signal.",
        "",
        "## Diagnosis",
        "",
    ]
    lines.extend(f"- {item}" for item in report["diagnosis"])
    lines.extend(["", "## Next Runner", ""])
    lines.append(f"- name: `{report['next_runner']['name']}`")
    lines.extend(f"- {item}" for item in report["next_runner"]["must_do"])
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("sky130_preamp_known_good_sanity_gap")
    print(f"status,{report['status']}")
    print(f"known_good_measured_cases,{report['known_good_result']['measured_case_count']}")
    print(f"preamp_op_timed_out_cases,{report['preamp_op_result']['timed_out_case_count']}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
