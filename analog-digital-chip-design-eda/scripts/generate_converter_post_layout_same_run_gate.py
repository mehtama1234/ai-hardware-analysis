#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from generate_converter_post_layout_positive_path_report import write_positive_fixture


ROOT = Path(__file__).resolve().parents[1]
CURRENT_PAYLOAD = ROOT / "evidence" / "aimc-simulator-adapters" / "candidate-post-layout" / "payload.json"
SAME_RUN = ROOT / "scripts" / "validate_converter_post_layout_same_run.py"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-same-run-gate.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-same-run-gate.md"


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def add_run_ids(payload_path: Path, run_id: str) -> None:
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    for section_name in ["simulation", "energy", "latency", "noise", "area", "break_even_rerun"]:
        payload[section_name]["run_id"] = run_id
    payload["provenance"]["run_id"] = run_id
    payload_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    current = run(["python3", str(SAME_RUN), "--expect-reject", str(CURRENT_PAYLOAD)])
    with tempfile.TemporaryDirectory(prefix="aimc-post-layout-same-run-") as tmp:
        payload_path, _ = write_positive_fixture(Path(tmp))
        add_run_ids(payload_path, "same-run-positive-fixture")
        positive = run(["python3", str(SAME_RUN), str(payload_path)])

    current_rejected = current.returncode == 0 and "PASS converter_post_layout_same_run_rejected" in current.stdout
    positive_accepted = positive.returncode == 0 and "PASS converter_post_layout_same_run" in positive.stdout
    report = {
        "result_type": "converter_post_layout_same_run_gate",
        "status": "same_run_gate_passed" if current_rejected and positive_accepted else "same_run_gate_failed",
        "current_payload": str(CURRENT_PAYLOAD.relative_to(ROOT)),
        "current_scaffold_rejected": current_rejected,
        "temporary_same_run_fixture_accepted": positive_accepted,
        "required_run_id_fields": [
            "provenance.run_id",
            "simulation.run_id",
            "energy.run_id",
            "latency.run_id",
            "noise.run_id",
            "area.run_id",
            "break_even_rerun.run_id",
        ],
        "claim_boundary": {
            "allowed": "proves the same-run consistency gate rejects the current scaffold and accepts a temporary complete fixture with one run id",
            "not_allowed": "does not create real post-layout evidence, does not submit evidence, and does not prove analog replacement",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Converter Post-Layout Same-Run Gate",
        "",
        f"- status: `{report['status']}`",
        f"- current scaffold rejected: `{report['current_scaffold_rejected']}`",
        f"- temporary same-run fixture accepted: `{report['temporary_same_run_fixture_accepted']}`",
        "",
        "This gate checks one simple rule: the converter values must come from one named run. Energy, latency, noise, area, simulation conditions, and the break-even rerun cannot be mixed from unrelated sources.",
        "",
        "## First Principle",
        "",
        "A converter payload is a claim about one physical path. If the energy is from one run, the noise is from another run, and the area is from a third source, the project cannot know what converter it is judging. The same-run id is the thread that ties those values back to one experiment or one post-layout simulation.",
        "",
        "The current scaffold is rejected because it has no real run identity. A temporary complete fixture is accepted only after every value section carries the same run id as provenance.",
        "",
        "## Required Run Id Fields",
        "",
        *[f"- `{field}`" for field in report["required_run_id_fields"]],
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    if report["status"] != "same_run_gate_passed":
        raise SystemExit("converter post-layout same-run gate failed")
    print("converter_post_layout_same_run_gate")
    print(f"status,{report['status']}")
    print(f"current_scaffold_rejected,{report['current_scaffold_rejected']}")
    print(f"temporary_same_run_fixture_accepted,{report['temporary_same_run_fixture_accepted']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
