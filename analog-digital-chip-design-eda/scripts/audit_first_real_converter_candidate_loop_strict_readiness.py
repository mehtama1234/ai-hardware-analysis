#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
CANDIDATE = EVIDENCE / "candidate-post-layout"

INPUTS = {
    "physical_object": EVIDENCE / "first-real-converter-physical-object-audit.json",
    "energy": EVIDENCE / "first-real-converter-energy-candidate.json",
    "latency": EVIDENCE / "first-real-converter-latency-candidate.json",
    "noise": EVIDENCE / "first-real-converter-noise-candidate.json",
    "area": EVIDENCE / "first-real-converter-area-candidate.json",
    "break_even": EVIDENCE / "first-real-converter-break-even-candidate.json",
}

OUT_JSON = EVIDENCE / "first-real-converter-candidate-loop-strict-readiness.json"
OUT_MD = EVIDENCE / "first-real-converter-candidate-loop-strict-readiness.md"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing input artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_report() -> dict[str, Any]:
    artifacts = {name: load_json(path) for name, path in INPUTS.items()}
    candidate_ids = {
        name: artifact.get("candidate_id")
        for name, artifact in artifacts.items()
    }
    run_ids = {
        name: artifact.get("run_id")
        for name, artifact in artifacts.items()
        if artifact.get("run_id") is not None
    }
    expected_candidate = "aimc_readout_candidate_001"
    same_candidate = set(candidate_ids.values()) == {expected_candidate}
    same_run = len(set(run_ids.values())) == 1
    candidate_loop_complete = (
        artifacts["physical_object"].get("ready_for_b1") is True
        and artifacts["energy"].get("status") == "b2_energy_candidate_written_not_strict_extracted_energy"
        and artifacts["latency"].get("status") == "b3_latency_candidate_written_not_strict_extracted_timing"
        and artifacts["noise"].get("status") == "b4_noise_candidate_written_not_strict_extracted_noise"
        and artifacts["area"].get("status") == "b5_area_candidate_written_not_strict_extracted_area"
        and artifacts["break_even"].get("status") == "b6_break_even_candidate_written_not_strict_replacement"
    )
    strict_blockers = []
    if not same_run:
        strict_blockers.append("B2-B6 do not share one run id.")
    strict_blockers.extend([
        "B2 energy is simple-load SPICE tied to the candidate, not extracted candidate supply integration.",
        "B3 latency is simple-load timing tied to the candidate, not extracted full-candidate timing.",
        "B4 noise is behavioral circuit noise tied to the candidate, not extracted or silicon noise.",
        "B5 area is a starter boundary estimate tied to the candidate, not DRC/LVS-clean extracted signoff area.",
        "B6 uses those mixed-level candidate values, so it cannot replace the accepted break-even result.",
    ])
    return {
        "result_type": "first_real_converter_candidate_loop_strict_readiness",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "candidate_loop_complete_not_strict_accepted_evidence",
        "candidate_id": expected_candidate,
        "same_candidate": same_candidate,
        "candidate_loop_complete": candidate_loop_complete,
        "same_run": same_run,
        "run_ids": run_ids,
        "input_artifacts": {name: rel(path) for name, path in INPUTS.items()},
        "strict_ready": False,
        "accepted_post_layout_ready": False,
        "strict_blockers": strict_blockers,
        "next_real_work": [
            "Run one extracted candidate deck that measures energy through the assembled netlist.",
            "Measure full conversion latency through the same extracted candidate run.",
            "Measure readout noise or input-referred noise for that same run.",
            "Compute area from the same candidate layout boundary with DRC/LVS status recorded.",
            "Rerun break-even from those same-run extracted values.",
            "Only then build and submit the canonical strict payload.",
        ],
        "claim_boundary": {
            "allowed": "proves the B1-B6 candidate loop exists and names the exact strict-readiness gap",
            "not_allowed": "does not fill the canonical strict payload, does not submit evidence, and does not write accepted post-layout evidence",
        },
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# First Real Converter Candidate Loop Strict Readiness",
        "",
        f"- status: `{report['status']}`",
        f"- candidate id: `{report['candidate_id']}`",
        f"- same candidate: `{report['same_candidate']}`",
        f"- candidate loop complete: `{report['candidate_loop_complete']}`",
        f"- same run: `{report['same_run']}`",
        f"- strict ready: `{report['strict_ready']}`",
        f"- accepted post-layout ready: `{report['accepted_post_layout_ready']}`",
        "",
        "## First Principle",
        "",
        "An end-to-end candidate loop is not the same as accepted evidence. The candidate loop answers whether every required kind of fact has a place: object, energy, latency, noise, area, and break-even. Accepted evidence asks a harder question: did those facts come from one real extracted or measured run of the same converter?",
        "",
        "The current loop is useful because all six facts point to one candidate name. It is not final because the facts do not yet come from one strict extracted run.",
        "",
        "## Run IDs",
        "",
    ]
    for name, run_id in report["run_ids"].items():
        lines.append(f"- `{name}`: `{run_id}`")
    lines.extend(["", "## Strict Blockers", ""])
    lines.extend(f"- {item}" for item in report["strict_blockers"])
    lines.extend(["", "## Next Real Work", ""])
    lines.extend(f"- {item}" for item in report["next_real_work"])
    lines.extend([
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("first_real_converter_candidate_loop_strict_readiness")
    print(f"status,{report['status']}")
    print(f"candidate_loop_complete,{report['candidate_loop_complete']}")
    print(f"same_run,{report['same_run']}")
    print(f"strict_ready,{report['strict_ready']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
