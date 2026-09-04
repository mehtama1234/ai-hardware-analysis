#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
SOURCES = {
    "work_order": EVIDENCE / "sky130-polarity-named-isolated-latch-work-order.json",
    "source_follower": EVIDENCE / "sky130-source-follower-isolated-latch-candidate.json",
    "sampled_decision_cap": EVIDENCE / "sky130-sampled-internal-decision-cap-latch-candidate.json",
    "two_phase": EVIDENCE / "sky130-two-phase-preamp-latch-candidate.json",
}
OUT_JSON = EVIDENCE / "sky130-isolated-latch-debug-ladder.json"
OUT_MD = EVIDENCE / "sky130-isolated-latch-debug-ladder.md"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def build_report() -> dict[str, Any]:
    source = {name: load(path) for name, path in SOURCES.items()}
    work_order = source["work_order"]
    failures = [
        {
            "name": "source_follower_input_buffer",
            "status": source["source_follower"]["status"],
            "case_count": source["source_follower"]["case_count"],
            "measured_case_count": source["source_follower"]["measured_case_count"],
            "timed_out_case_count": source["source_follower"]["timed_out_case_count"],
            "failure_reading": "combined buffer plus latch fixture did not produce measured signal cases",
        },
        {
            "name": "sampled_internal_decision_capacitor",
            "status": source["sampled_decision_cap"]["status"],
            "case_count": source["sampled_decision_cap"]["case_count"],
            "measured_case_count": source["sampled_decision_cap"]["measured_case_count"],
            "timed_out_case_count": source["sampled_decision_cap"]["timed_out_case_count"],
            "failure_reading": "copy-switch decision-cap fixture was timeout-heavy before kickback could be judged",
        },
        {
            "name": "two_phase_preamp_then_latch",
            "status": source["two_phase"]["status"],
            "case_count": source["two_phase"]["case_count"],
            "measured_case_count": source["two_phase"]["measured_case_count"],
            "timed_out_case_count": source["two_phase"]["timed_out_case_count"],
            "failure_reading": "preamp plus delayed latch did not produce measured target-edge cases",
        },
    ]
    total_cases = sum(int(item["case_count"]) for item in failures)
    measured_cases = sum(int(item["measured_case_count"]) for item in failures)
    timeout_cases = sum(int(item["timed_out_case_count"]) for item in failures)

    ladder = [
        {
            "step": 1,
            "name": "preamp_alone_dc_and_transient",
            "question": "can the preamp or buffer stage settle from the target-edge input without any regenerative latch attached?",
            "must_measure": ["input differential voltage", "output differential voltage", "settling time", "common-mode range"],
            "pass_gate": "both signs produce measurable settled output before latch clock time",
            "stop_if_fails": "fix bias, load, common-mode, or initial condition before reconnecting the latch",
        },
        {
            "step": 2,
            "name": "latch_alone_from_measured_preamp_voltages",
            "question": "can the latch resolve when driven by ideal voltage sources equal to the preamp-alone outputs?",
            "must_measure": ["output polarity", "decision time", "minimum input needed for full output"],
            "pass_gate": "both signs resolve with the polarity contract and full output swing",
            "stop_if_fails": "resize latch or change latch common-mode before adding sampled-node coupling",
        },
        {
            "step": 3,
            "name": "clock_timing_ladder",
            "question": "which copy, preamp, and latch clock order avoids timeout and stale initial conditions?",
            "must_measure": ["pre-latch internal differential voltage", "post-latch sampled-node movement", "ngspice convergence status"],
            "pass_gate": "same topology measures under at least three clock spacings without timeout",
            "stop_if_fails": "separate clock phases further or add explicit precharge/reset nodes",
        },
        {
            "step": 4,
            "name": "coupled_kickback_rejoin",
            "question": "after the pieces work alone, does the coupled circuit keep sampled-node kickback below the line?",
            "must_measure": ["sampled differential before latch", "sampled differential after latch", "kickback", "final output polarity"],
            "pass_gate": f"kickback <= {work_order['half_lsb_12b_v']:.9e} V hard line, preferably <= {work_order['recommended_kickback_target_v']:.9e} V",
            "stop_if_fails": "return to isolation mechanism; do not proceed to SAR",
        },
        {
            "step": 5,
            "name": "sar_threshold_wrong_code_proxy",
            "question": "does the measured decision stay correct at the SAR threshold after offset, noise, and kickback budgets are applied?",
            "must_measure": ["input-referred offset", "output noise RMS", "wrong-code margin", "decision-time spread"],
            "pass_gate": "both signs stay correct under the same budget used by placement and converter acceptance",
            "stop_if_fails": "keep digital fallback; do not create accepted post-layout converter evidence",
        },
    ]

    return {
        "result_type": "sky130_isolated_latch_debug_ladder",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "isolated_latch_debug_ladder_ready_after_timeout_failures",
        "source_artifacts": {name: rel(path) for name, path in SOURCES.items()},
        "polarity_contract": work_order["polarity_contract"],
        "best_transistor_setting": work_order["best_transistor_setting"],
        "half_lsb_12b_v": work_order["half_lsb_12b_v"],
        "recommended_kickback_target_v": work_order["recommended_kickback_target_v"],
        "failed_candidate_count": len(failures),
        "failed_candidate_case_count": total_cases,
        "failed_candidate_measured_case_count": measured_cases,
        "failed_candidate_timed_out_case_count": timeout_cases,
        "failure_pattern": "combined isolated-latch topologies are timing out before useful kickback or resolution measurements",
        "failures": failures,
        "debug_ladder": ladder,
        "next_executable_step": "write preamp-alone dc/transient fixture before reconnecting the regenerative latch",
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "strict_payload_ready": False,
        "claim_boundary": {
            "allowed": "turns three failed isolated-latch candidate runs into a smaller debug sequence with measurable stop gates",
            "not_allowed": "does not prove a new circuit, SAR bit cycling, noise, offset statistics, extracted layout, DRC/LVS, or accepted post-layout converter evidence",
        },
    }


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Isolated Latch Debug Ladder",
        "",
        f"- status: `{report['status']}`",
        f"- polarity contract: `{report['polarity_contract']}`",
        f"- best transistor setting: `{report['best_transistor_setting']}`",
        f"- failed candidate count: `{report['failed_candidate_count']}`",
        f"- failed candidate case count: `{report['failed_candidate_case_count']}`",
        f"- measured failed-candidate cases: `{report['failed_candidate_measured_case_count']}`",
        f"- timed-out failed-candidate cases: `{report['failed_candidate_timed_out_case_count']}`",
        f"- half LSB 12b V: `{report['half_lsb_12b_v']:.9e}`",
        f"- recommended kickback target V: `{report['recommended_kickback_target_v']:.9e}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "A timeout is not a circuit measurement. It tells us the combined deck is too hard to judge as one object. The correct response is to split the circuit into smaller objects whose voltages, timing, and state can each be measured.",
        "",
        "The polarity contract is already known. The remaining question is where the latch path loses measurability: the preamp, the latch, the clock order, or the coupled kickback. The debug ladder tests those in that order.",
        "",
        "## Failed Candidate Pattern",
        "",
        "| candidate | measured | timed out | reading |",
        "|---|---:|---:|---|",
    ]
    for item in report["failures"]:
        lines.append(f"| `{item['name']}` | `{item['measured_case_count']}` | `{item['timed_out_case_count']}` | {item['failure_reading']} |")
    lines.extend(["", "## Debug Ladder", "", "| step | name | question | pass gate | stop if fails |", "|---:|---|---|---|---|"])
    for item in report["debug_ladder"]:
        lines.append(f"| `{item['step']}` | `{item['name']}` | {item['question']} | {item['pass_gate']} | {item['stop_if_fails']} |")
    lines.extend(
        [
            "",
            "## Next Executable Step",
            "",
            report["next_executable_step"],
            "",
            "## Boundary",
            "",
            report["claim_boundary"]["not_allowed"],
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print("sky130_isolated_latch_debug_ladder")
    print(f"status,{report['status']}")
    print(f"failed_candidate_count,{report['failed_candidate_count']}")
    print(f"failed_candidate_measured_case_count,{report['failed_candidate_measured_case_count']}")
    print(f"failed_candidate_timed_out_case_count,{report['failed_candidate_timed_out_case_count']}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
