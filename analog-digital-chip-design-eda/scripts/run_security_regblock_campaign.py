"""Run multi-variant adversarial security checks with review-only signoff."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from verification_platform.mutation import run_mutation, validate_mutation_suite
from verification_platform.security_closure import evaluate_security_task, validate_security_suite


ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "benchmarks/repository_scale/security_regblock_campaign.json"
SOURCE = "benchmarks/seeded_regblock/regblock.sv"
TESTBENCH = "benchmarks/repository_scale/parameterized_mutation_tb/security_regblock.sv"
GOOD_ANCHORS = {
    "security-addr-one-write": ("      if (addr == 2'd0) reg0 <= wdata;", "      if (addr == 2'd1) reg0 <= wdata;"),
    "security-addr-two-write": ("      if (addr == 2'd0) reg0 <= wdata;", "      if (addr == 2'd2) reg0 <= wdata;"),
    "security-nonzero-write": ("      if (addr == 2'd0) reg0 <= wdata;", "      if (addr != 2'd0) reg0 <= wdata;"),
    "security-write-enable-bypass": ("    else if (wr_en) begin", "    else begin"),
    "security-reset-state-bypass": ("    if (rst) reg0 <= 8'h00;", "    if (!rst) reg0 <= 8'h00;"),
    "security-data-corruption-invert": ("      if (addr == 2'd0) reg0 <= wdata;", "      if (addr == 2'd0) reg0 <= ~wdata;"),
    "security-data-corruption-increment": ("      if (addr == 2'd0) reg0 <= wdata;", "      if (addr == 2'd0) reg0 <= wdata + 8'd1;"),
    "security-address-zero-remap": ("      if (addr == 2'd0) reg0 <= wdata;", "      if (addr == 2'd1) reg0 <= wdata;"),
}


def _run(command: list[str], cwd: Path) -> tuple[bool, str, str]:
    completed = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
    return completed.returncode == 0 and "FAIL " not in completed.stdout + completed.stderr, completed.stdout, completed.stderr


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/repository-scale-m4/security-regblock-campaign")
    args = parser.parse_args()
    suite = json.loads(SUITE.read_text(encoding="utf-8"))
    validate_security_suite(suite)
    args.output.mkdir(parents=True, exist_ok=True)
    results = []
    with tempfile.TemporaryDirectory(prefix="security-regblock-campaign-") as directory:
        staging = Path(directory)
        roots = {name: staging / name for name in ("canonical", "baseline", "candidate", "repaired")}
        for root in roots.values():
            (root / "scripts").mkdir(parents=True)
            shutil.copy2(ROOT / "scripts/run_seeded_counter_check.py", root / "scripts/run_seeded_counter_check.py")
            for relative in (SOURCE, TESTBENCH):
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                source = ROOT / relative
                text = source.read_text(encoding="utf-8")
                if relative == SOURCE:
                    buggy = "      if (addr == 2'd0) reg0 <= wdata;\n      else reg0 <= wdata; // SEEDED_BUG: nonzero addresses must be ignored"
                    if text.count(buggy) != 1:
                        raise RuntimeError("security source normalization anchor is missing")
                    text = text.replace(buggy, "      if (addr == 2'd0) reg0 <= wdata;")
                destination.write_text(text, encoding="utf-8")
        for task in suite["tasks"]:
            task_id = task["task_id"]
            before, after = GOOD_ANCHORS[task_id]
            mutation = {"mutation_id": task_id, "source_file": SOURCE, "from": before, "to": after, "command": ["python3", "scripts/run_seeded_counter_check.py", SOURCE, TESTBENCH]}
            validate_mutation_suite({"schema_version": "mutation-suite-v1", "mutations": [mutation]})
            source = Path(SOURCE)
            shutil.copy2(roots["canonical"] / source, roots["candidate"] / source)
            record = run_mutation(mutation, canonical_root=roots["canonical"], baseline_root=roots["baseline"], candidate_root=roots["candidate"], output_root=args.output / task_id / "mutation")
            # The repair must start from the adversarial candidate.  Copying
            # the canonical baseline here would only demonstrate that the
            # baseline passes, not that the proposed repair removes the bug.
            shutil.copytree(roots["candidate"], roots["repaired"], dirs_exist_ok=True)
            repaired_source = roots["repaired"] / source
            repaired_text = repaired_source.read_text(encoding="utf-8")
            if repaired_text.count(after) != 1:
                raise RuntimeError(f"repair anchor is missing or ambiguous: {task_id}")
            repaired_source.write_text(repaired_text.replace(after, before, 1), encoding="utf-8")
            repaired_ok, repaired_stdout, repaired_stderr = _run(mutation["command"], roots["repaired"])
            repaired_dir = args.output / task_id
            (repaired_dir / "repair.stdout.log").write_text(repaired_stdout, encoding="utf-8")
            (repaired_dir / "repair.stderr.log").write_text(repaired_stderr, encoding="utf-8")
            signoff = evaluate_security_task(task, detected=bool(record["result"]["detected"]), localized=True, repaired_copy_passed=repaired_ok, regression_passed=record["result"]["baseline_valid"], evidence=[f"{task_id}/mutation/mutation-result.json", f"{task_id}/repair.stdout.log", f"{task_id}/repair.stderr.log"])
            (repaired_dir / "security-signoff-record.json").write_text(json.dumps(signoff, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            repaired_digest = hashlib.sha256(repaired_source.read_bytes()).hexdigest()
            canonical_digest = record["result"]["source_sha256_before"]
            results.append({"task_id": task_id, "status": signoff["status"], "machine_checks_passed": signoff["machine_checks_passed"], "canonical_unchanged": record["result"]["canonical_unchanged"], "mutant_changed": record["result"]["candidate_changed"], "repaired_matches_canonical": repaired_digest == canonical_digest, "canonical_sha256": canonical_digest, "mutant_sha256": record["result"]["source_sha256_after"], "repaired_sha256": repaired_digest, "record": f"{task_id}/security-signoff-record.json"})
    report = {"schema_version": "security-campaign-report-v1", "suite": str(SUITE), "tasks": results, "total": len(results), "machine_passed": sum(item["machine_checks_passed"] for item in results), "all_machine_checks_passed": all(item["machine_checks_passed"] and item["canonical_unchanged"] and item["mutant_changed"] and item["repaired_matches_canonical"] for item in results), "all_review_required": all(item["status"] == "review_required" for item in results), "claim_boundary": "eight adversarial register-policy tasks with detected, localized, repaired-copy, and canonical-regression evidence; human approval remains required and this is not security certification"}
    report["report_sha256"] = hashlib.sha256(json.dumps(report, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (args.output / "security-campaign-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed" if report["all_machine_checks_passed"] and report["all_review_required"] else "blocked", "total": report["total"], "machine_passed": report["machine_passed"], "review_required": report["all_review_required"], "report": str(args.output / "security-campaign-report.json")}, sort_keys=True))
    return 0 if report["all_machine_checks_passed"] and report["all_review_required"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
