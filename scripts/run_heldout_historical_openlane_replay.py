#!/usr/bin/env python3
"""Replay the first held-out OpenLane historical fix in an isolated Tcl harness.

This is a regression reconstruction, not a claim that the historical item is
an RTL or model-generalization result.  The upstream parent silently checks a
different netlist path; the corrected revision checks the active netlist.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = Path("/home/mehtama1/eda-tools/OpenLane")
COMMIT = "000c992a07a3b45db65db2e6559125fd94dd77df"
PARENT = f"{COMMIT}^"
FILES = {
    "parent-checkers.tcl": (PARENT, "scripts/tcl_commands/checkers.tcl"),
    "fixed-checkers.tcl": (COMMIT, "scripts/tcl_commands/checkers.tcl"),
    "parent-synthesis.tcl": (PARENT, "scripts/tcl_commands/synthesis.tcl"),
    "fixed-synthesis.tcl": (COMMIT, "scripts/tcl_commands/synthesis.tcl"),
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def git_show(revision: str, path: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(UPSTREAM), "show", f"{revision}:{path}"],
        capture_output=True,
        check=True,
    ).stdout


def run_tcl(checkers: Path, netlist: Path, wrong_netlist_base: Path, *, fixed: bool) -> dict[str, object]:
    call = f"check_assign_statements {{{netlist}}}" if fixed else "check_assign_statements"
    harness = f"""
proc count_matches {{needle path}} {{
    set fh [open $path r]
    set body [read $fh]
    close $fh
    set count 0
    foreach line [split $body "\\n"] {{
        if {{[string first $needle $line] >= 0}} {{ incr count }}
    }}
    return $count
}}
proc puts_err {{message}} {{ puts stderr $message }}
proc puts_verbose {{message}} {{ puts stdout $message }}
proc throw_error {{}} {{ error "checker rejected netlist" }}
set ::env(synthesis_results) {{{wrong_netlist_base}}}
set ::env(CURRENT_NETLIST) {{{netlist}}}
source {{{checkers}}}
set rc [catch {{{call}}} message options]
puts [json::write object [list rc $rc message $message]]
exit $rc
"""
    # Avoid depending on Tcl's optional json package: emit a tab-separated
    # result from the harness and parse it here.
    harness = harness.replace(
        'puts [json::write object [list rc $rc message $message]]',
        'puts "RESULT\\t$rc\\t$message"',
    )
    script = checkers.parent / ("fixed-harness.tcl" if fixed else "parent-harness.tcl")
    script.write_text(harness, encoding="utf-8")
    completed = subprocess.run(["tclsh", str(script)], capture_output=True, text=True, check=False)
    result_line = next((line for line in completed.stdout.splitlines() if line.startswith("RESULT\t")), "")
    parts = result_line.split("\t", 2)
    return {
        "process_returncode": completed.returncode,
        "catch_returncode": int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None,
        "message": parts[2] if len(parts) > 2 else "",
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    snapshots: dict[str, bytes] = {name: git_show(rev, path) for name, (rev, path) in FILES.items()}
    for name, content in snapshots.items():
        (output / name).write_bytes(content)
    with tempfile.TemporaryDirectory(prefix="heldout-openlane-replay-") as td:
        work = Path(td)
        parent_checkers = work / "parent-checkers.tcl"
        fixed_checkers = work / "fixed-checkers.tcl"
        parent_checkers.write_bytes(snapshots["parent-checkers.tcl"])
        fixed_checkers.write_bytes(snapshots["fixed-checkers.tcl"])
        active = work / "active-netlist.v"
        wrong = work / "wrong-netlist"
        active.write_text("module top; assign observed = source; endmodule\n", encoding="utf-8")
        (work / "wrong-netlist.v").write_text("module top; wire observed; endmodule\n", encoding="utf-8")
        baseline = run_tcl(parent_checkers, active, wrong, fixed=False)
        repaired = run_tcl(fixed_checkers, active, wrong, fixed=True)

    source_summary = {
        name: {"path": name, "sha256": sha256_bytes(content), "size_bytes": len(content)}
        for name, content in snapshots.items()
    }
    report = {
        "schema_version": "heldout-openlane-historical-replay-v1",
        "repository": "OpenLane",
        "commit": COMMIT,
        "parent": "11537018d7cb288ff983f8023d97a81154a4e3cb",
        "subject": "fix wrong reference to check_assign_statements",
        "candidate_files": ["scripts/tcl_commands/checkers.tcl", "scripts/tcl_commands/synthesis.tcl"],
        "source_snapshots": source_summary,
        "regression_contract": {
            "active_netlist_contains_assign": True,
            "synthesis_results_netlist_contains_assign": False,
            "parent_call_uses_active_netlist": False,
            "fixed_call_uses_active_netlist": True,
        },
        "baseline": baseline,
        "repaired": repaired,
        "status": "passed" if baseline["catch_returncode"] == 0 and repaired["catch_returncode"] != 0 else "blocked",
        "claim_boundary": "one upstream OpenLane held-out regression reconstructed in an isolated Tcl harness; not an agent repair, RTL correctness, complete OpenLane qualification, or model-generalization result",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    report["report_sha256"] = digest(report)
    (output / "replay-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "output": str(output), "baseline_catch": baseline["catch_returncode"], "repaired_catch": repaired["catch_returncode"]}, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
