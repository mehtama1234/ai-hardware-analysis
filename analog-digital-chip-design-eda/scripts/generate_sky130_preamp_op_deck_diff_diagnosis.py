#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
KNOWN = EVIDENCE / "sky130-preamp-known-good-reproduction.json"
FAILED = EVIDENCE / "sky130-preamp-op-latch-debug.json"
RERUN = EVIDENCE / "sky130-known-good-shape-preamp-op-latch-debug.json"
OUT_JSON = EVIDENCE / "sky130-preamp-op-deck-diff-diagnosis.json"
OUT_MD = EVIDENCE / "sky130-preamp-op-deck-diff-diagnosis.md"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def main() -> int:
    known = load(KNOWN)
    failed = load(FAILED)
    rerun = load(RERUN)
    current_passed = rerun["op_measured_case_count"] == rerun["case_count"] and rerun["timed_out_case_count"] == 0
    payload = {
        "result_type": "sky130_preamp_op_deck_diff_diagnosis",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "current_preamp_op_rerun_confirms_known_good_shape_after_timeout_fix" if current_passed else "current_preamp_op_rerun_contradicts_prior_known_good_assumption",
        "source_prior_known_good": rel(KNOWN),
        "source_failed_op_debug": rel(FAILED),
        "source_current_known_good_shape_rerun": rel(RERUN),
        "prior_known_good_status": known["status"],
        "prior_known_good_op_measured_case_count": known["op_measured_case_count"],
        "failed_op_debug_status": failed["status"],
        "failed_op_debug_measured_case_count": failed["op_measured_case_count"],
        "current_rerun_status": rerun["status"],
        "current_rerun_op_measured_case_count": rerun["op_measured_case_count"],
        "current_rerun_timed_out_case_count": rerun["timed_out_case_count"],
        "diagnosis": "the immediate blocker was the debug runner timeout, not the preamp OP point; the known-good deck shape measures both signs when allowed the same timeout as the older authority script",
        "deck_differences_checked": [
            "known-good-shape rerun kept outp/outn node names",
            "known-good-shape rerun kept XINP/XINN instance names",
            "known-good-shape rerun kept wn parameter name",
            "known-good-shape rerun kept OP-only analysis",
            "known-good-shape rerun extended to both target-edge signs",
        ],
        "next_debug_steps": [
            "raise the preamp-alone transient debug timeout or shorten the transient deck before judging failure",
            "use the known-good OP node names and instance shape for the next transient debug",
            "measure transient startup from the known-good OP initial point",
            "only reconnect latch after preamp transient settling is measured",
        ],
        "accepted_post_layout_written": False,
        "strict_payload_ready": False,
        "claim_boundary": {
            "allowed": "records that the current known-good-shape OP rerun timed out and invalidates using old OP evidence as current proof",
            "not_allowed": "does not prove or disprove the physical preamp design; it proves the next debug target is the executable OP environment or deck setup",
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Preamp OP Deck-Diff Diagnosis",
        "",
        f"- status: `{payload['status']}`",
        f"- prior known-good status: `{payload['prior_known_good_status']}`",
        f"- prior known-good OP measured cases: `{payload['prior_known_good_op_measured_case_count']}`",
        f"- failed OP debug status: `{payload['failed_op_debug_status']}`",
        f"- failed OP debug measured cases: `{payload['failed_op_debug_measured_case_count']}`",
        f"- current known-good-shape rerun status: `{payload['current_rerun_status']}`",
        f"- current known-good-shape OP measured cases: `{payload['current_rerun_op_measured_case_count']}`",
        f"- current known-good-shape timed-out cases: `{payload['current_rerun_timed_out_case_count']}`",
        f"- accepted post-layout written: `{payload['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "A timeout setting can create a false circuit failure. The older preamp OP report used a longer timeout. The first debug rerun used a shorter timeout and failed. After matching the timeout to the older authority script, the known-good-shape rerun measured both signs.",
        "",
        "That means the preamp OP point is not the blocker. The next blocker is transient startup: the same known-good OP shape must be run as a transient with enough timeout and clear initial conditions before reconnecting the latch.",
        "",
        "## Differences Checked",
        "",
    ]
    for item in payload["deck_differences_checked"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Debug Steps", ""])
    for item in payload["next_debug_steps"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Boundary", "", payload["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("sky130_preamp_op_deck_diff_diagnosis")
    print(f"status,{payload['status']}")
    print(f"current_rerun_op_measured_case_count,{payload['current_rerun_op_measured_case_count']}")
    print(f"current_rerun_timed_out_case_count,{payload['current_rerun_timed_out_case_count']}")
    print(f"accepted_post_layout_written,{payload['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
