#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
CONFIRM = EVIDENCE / "sky130-capacitive-isolation-both-polarity-confirm.json"
CELL_GATE = EVIDENCE / "analog-converter-physical-cell-gate.json"
READINESS = EVIDENCE / "converter-post-layout-readiness.json"
OUT_JSON = EVIDENCE / "sky130-capacitive-isolation-post-layout-handoff.json"
OUT_MD = EVIDENCE / "sky130-capacitive-isolation-post-layout-handoff.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing input artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    confirm = load_json(CONFIRM)
    cell_gate = load_json(CELL_GATE)
    readiness = load_json(READINESS)

    confirmed_caps = confirm.get("confirmed_coupling_caps_ff")
    if not isinstance(confirmed_caps, list):
        confirmed_caps = []
    required_layout_objects = [
        "capacitive-isolation comparator schematic or extracted subcell naming the coupling capacitor value",
        "extracted comparator-plus-sample-node netlist including latch input gates, isolation capacitors, sample capacitors, and clock devices",
        "Sky130 model and corner file path used by the rerun",
        "post-layout both-polarity kickback rerun using the same target input edge",
        "post-layout offset/noise stress record or explicit statement that the result is still kickback-only",
        "DRC/LVS report for the comparator sample front end if it is claimed as a physical candidate",
        "same-run break-even rerun showing whether the converter still beats fallback after extracted capacitance and timing are included",
    ]
    physical_ready = bool(cell_gate.get("ready_for_candidate_post_layout_payload"))
    post_layout_ready = bool((readiness.get("validation") or {}).get("claim_ready_to_replace_break_even")) if isinstance(readiness.get("validation"), dict) else False
    all_confirmed = confirm.get("all_cases_pass") is True and confirm.get("passing_case_count") == confirm.get("case_count")
    accepted_ready = all_confirmed and physical_ready and post_layout_ready
    payload = {
        "result_type": "sky130_capacitive_isolation_post_layout_handoff",
        "status": "confirmed_schematic_candidate_waiting_for_extracted_layout",
        "source_confirmation": str(CONFIRM.relative_to(ROOT)),
        "source_physical_cell_gate": str(CELL_GATE.relative_to(ROOT)),
        "source_post_layout_readiness": str(READINESS.relative_to(ROOT)),
        "schematic_confirmation": {
            "all_cases_pass": all_confirmed,
            "case_count": confirm.get("case_count"),
            "passing_case_count": confirm.get("passing_case_count"),
            "confirmed_coupling_caps_ff": confirmed_caps,
            "worst_kickback_v": confirm.get("worst_kickback_v"),
            "hard_kickback_limit_v": confirm.get("hard_kickback_limit_v"),
        },
        "post_layout_gate": {
            "physical_cell_gate_ready": physical_ready,
            "post_layout_ready_to_replace_break_even": post_layout_ready,
            "accepted_ready_now": accepted_ready,
            "candidate_post_layout_written": False,
            "accepted_post_layout_written": False,
        },
        "required_layout_objects": required_layout_objects,
        "claim_boundary": {
            "allowed": "promotes the confirmed schematic capacitive-isolation result into a concrete post-layout handoff list",
            "not_allowed": "does not create extracted layout, does not prove comparator offset or noise, does not write candidate post-layout evidence, and does not write accepted converter evidence",
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Sky130 Capacitive Isolation Post-Layout Handoff",
        "",
        f"- status: `{payload['status']}`",
        f"- source confirmation: `{payload['source_confirmation']}`",
        f"- all schematic cases pass: `{all_confirmed}`",
        f"- confirmed coupling caps fF: `{', '.join(f'{float(cap):g}' for cap in confirmed_caps)}`",
        f"- worst schematic kickback V: `{confirm.get('worst_kickback_v')}`",
        f"- hard kickback limit V: `{confirm.get('hard_kickback_limit_v')}`",
        f"- physical cell gate ready: `{physical_ready}`",
        f"- post-layout ready to replace break-even: `{post_layout_ready}`",
        f"- accepted ready now: `{accepted_ready}`",
        f"- candidate post-layout written: `False`",
        f"- accepted post-layout written: `False`",
        "",
        "## First Principle",
        "",
        "The both-polarity run proves a schematic behavior: a tiny isolation capacitor lets the latch read either sign while keeping sampled-node kickback under the half-LSB line. That is useful, but it is still not a physical converter.",
        "",
        "Layout changes the object being measured. Wires add capacitance and resistance. Device placement changes matching. Clock routing changes charge injection. The isolation capacitor itself must become a drawn or extracted object, not only a value in a generated deck.",
        "",
        "So the next gate is not another wording pass. It is a handoff from a confirmed schematic candidate to named extracted objects.",
        "",
        "## Required Layout Objects",
        "",
    ]
    lines.extend(f"- {item}" for item in required_layout_objects)
    lines.extend(
        [
            "",
            "## Refused Claim",
            "",
            payload["claim_boundary"]["not_allowed"],
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("sky130_capacitive_isolation_post_layout_handoff")
    print(f"status,{payload['status']}")
    print(f"all_schematic_cases_pass,{all_confirmed}")
    print(f"accepted_ready_now,{accepted_ready}")
    print(f"required_layout_objects,{len(required_layout_objects)}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
