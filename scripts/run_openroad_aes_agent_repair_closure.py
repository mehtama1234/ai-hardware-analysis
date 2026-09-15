"""Run the bounded agent-repair loop on the native OpenROAD AES block."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SUBREPO = ROOT / "analog-digital-chip-design-eda"
REPO = Path("/home/mehtama1/eda-tools/OpenROAD-flow-scripts")
REVISION = "be0dca0b1"
SOURCE_RELATIVE = Path("flow/designs/src/aes/aes_cipher_top.v")
OLD = "always @(posedge clk) text_out[127:120] <= #1 sa00_sr ^ w0[31:24];"
NEW = "always @(posedge clk) text_out[127:120] <= #1 sa00_sr ^ w0[23:16];"
SOURCES = [
    Path("flow/designs/src/aes/timescale.v"), Path("flow/designs/src/aes/aes_rcon.v"),
    Path("flow/designs/src/aes/aes_sbox.v"), Path("flow/designs/src/aes/aes_inv_sbox.v"),
    Path("flow/designs/src/aes/aes_key_expand_128.v"), SOURCE_RELATIVE,
]

sys.path.insert(0, str(SUBREPO))
from verification_platform.repository_agent import run_repository_agent  # noqa: E402
from verification_platform.repair import RepairProposal, apply_to_copy  # noqa: E402
from verification_platform.runner import run_command  # noqa: E402


def sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/repository-scale-real/openroad-aes-agent-repair")
    parser.add_argument("--backend", choices=("mock", "local"), default="mock")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.backend == "mock":
        os.environ["VERIFICATION_LLM_COMMAND"] = f"{sys.executable} {SUBREPO / 'scripts/mock_repository_agent_backend.py'}"
    source = REPO / SOURCE_RELATIVE
    if not REPO.is_dir() or not source.is_file():
        print(json.dumps({"status": "blocked", "reason": "OpenROAD AES source or checkout missing"}, sort_keys=True)); return 1
    revision = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], text=True).strip()
    if revision != REVISION:
        print(json.dumps({"status": "blocked", "reason": "OpenROAD revision mismatch", "expected": REVISION, "actual": revision}, sort_keys=True)); return 1
    with tempfile.TemporaryDirectory(prefix="openroad-aes-agent-repair-") as directory:
        staging = Path(directory)
        mutated_root = staging / "mutated"
        repaired_root = staging / "repaired"
        for root in (mutated_root, repaired_root):
            for relative in SOURCES:
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(REPO / relative, destination)
            tb = root / "openroad_aes_tb.sv"
            shutil.copy2(ROOT / "benchmarks/repository_scale/openroad_aes_tb.sv", tb)
        mutated_source = mutated_root / SOURCE_RELATIVE
        repaired_source = repaired_root / SOURCE_RELATIVE
        text = mutated_source.read_text(encoding="utf-8")
        if text.count(OLD) != 1:
            raise RuntimeError("OpenROAD AES source did not contain the mutation anchor")
        mutated_source.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
        include_dir = str(mutated_root / "flow/designs/src/aes")
        command = ["iverilog", "-g2012", "-I", include_dir, "-o", str(mutated_root / "aes.vvp"), *[str(mutated_root / item) for item in SOURCES], str(mutated_root / "openroad_aes_tb.sv")]
        task_output = args.output / "openroad-aes-output-byte"
        baseline_compile = run_command(command, tool="openroad-aes-agent-mutated-compile", run_root=task_output / "baseline-compile", source_revision=REVISION)
        baseline = subprocess.run(["vvp", str(mutated_root / "aes.vvp")], cwd=mutated_root, capture_output=True, text=True, check=False) if baseline_compile.status == "passed" else None
        baseline_status = "passed" if baseline is not None and baseline.returncode == 0 and "PASS aes known-answer" in (baseline.stdout + baseline.stderr) else "failed"
        agent = run_repository_agent(
            task_id="openroad-aes-output-byte",
            source_revision=REVISION,
            evidence=[str(SOURCE_RELATIVE), "native OpenROAD checkout", "AES known-answer failure"],
            failure_context="the native AES datapath uses the wrong round-key byte for the first ciphertext byte",
            repair_before=NEW, repair_after=OLD, repair_source=mutated_source,
            backend="local", output_root=task_output / "agent",
        )
        candidate = agent.get("patch_candidate", {})
        repaired_status = "blocked"
        canonical_unchanged = False
        if candidate.get("status") == "review_required":
            proposal = RepairProposal(
                requirement_id=str(candidate.get("requirement_id") or "openroad-aes-output-byte"),
                file=str(candidate["source"]), line=int(candidate["line"]),
                before=str(candidate["before"]), after=str(candidate["after"]),
                rationale="benchmark-only native AES repair evaluation", edit_operator=str(candidate.get("edit_operator", "exact_text_replace")),
            )
            canonical_hash = hashlib.sha256(source.read_bytes()).hexdigest()
            apply_to_copy(mutated_source, repaired_source, proposal, human_approved=True)
            repaired_command = [str(repaired_source) if item == str(mutated_source) else item.replace(str(mutated_root), str(repaired_root)) for item in command]
            repaired_compile = run_command(repaired_command, tool="openroad-aes-agent-repair-compile", run_root=task_output / "repaired-compile", source_revision=REVISION)
            repaired = subprocess.run(["vvp", str(repaired_root / "aes.vvp")], cwd=repaired_root, capture_output=True, text=True, check=False) if repaired_compile.status == "passed" else None
            repaired_status = "passed" if repaired is not None and repaired.returncode == 0 and "PASS aes known-answer" in (repaired.stdout + repaired.stderr) else "failed"
            canonical_unchanged = canonical_hash == hashlib.sha256(source.read_bytes()).hexdigest()
        report = {
            "schema_version": "openroad-aes-agent-repair-closure-report-v1", "repository": "OpenROAD-flow-scripts",
            "repository_revision": revision, "backend": args.backend, "task_id": "openroad-aes-output-byte",
            "baseline_status": baseline_status, "agent_status": agent["team"]["status"],
            "patch_candidate_status": candidate.get("status", agent.get("patch_candidate_status")),
            "repaired_status": repaired_status, "canonical_unchanged": canonical_unchanged,
            "status": "passed" if baseline_status == "failed" and repaired_status == "passed" and canonical_unchanged else "blocked",
            "claim_boundary": "one native AES mutation and bounded repair; not exhaustive cryptographic verification or production signoff",
        }
    report["report_sha256"] = sha(report)
    path = args.output / "openroad-aes-agent-repair-closure-report.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "repository_revision": revision, "report": str(path)}, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
