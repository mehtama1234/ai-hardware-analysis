"""Run a functional repository-scale task against OpenROAD-flow-scripts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analog-digital-chip-design-eda"))

from verification_platform.repository_benchmark import run_repository_task, validate_task_manifest


REPO = Path("/home/mehtama1/eda-tools/OpenROAD-flow-scripts")
SOURCE_RELATIVE = Path("flow/designs/src/gcd/gcd.v")
OLD = "  assign dpath$req_msg_a = req_msg[31:16];"
NEW = "  assign dpath$req_msg_a = req_msg[15:0];"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/repository-scale-real/openroad-gcd-functional")
    args = parser.parse_args()
    manifest = json.loads((ROOT / "benchmarks/repository_scale/openroad_gcd_functional_task.json").read_text(encoding="utf-8"))
    validate_task_manifest(manifest)
    source = REPO / SOURCE_RELATIVE
    if not source.is_file():
        print(json.dumps({"status": "blocked", "reason": f"OpenROAD checkout missing: {source}"}, sort_keys=True))
        return 1
    actual_revision = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], text=True).strip()
    expected_revision = manifest.get("repository_revision")
    if actual_revision != expected_revision:
        print(json.dumps({"status": "blocked", "reason": "OpenROAD checkout revision does not match manifest", "expected": expected_revision, "actual": actual_revision}, sort_keys=True))
        return 1
    with tempfile.TemporaryDirectory(prefix="openroad-gcd-functional-") as directory:
        staging = Path(directory)
        roots = {name: staging / name for name in ("baseline", "candidate")}
        for root in roots.values():
            destination = root / SOURCE_RELATIVE
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            (root / "scripts").mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / "scripts/run_openroad_gcd_check.py", root / "scripts/run_openroad_gcd_check.py")
            tb = root / "verification_tb/openroad_gcd_tb.sv"
            tb.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / "benchmarks/repository_scale/openroad_gcd_tb.sv", tb)
        candidate_source = roots["candidate"] / SOURCE_RELATIVE
        text = candidate_source.read_text(encoding="utf-8")
        if text.count(OLD) != 1:
            raise RuntimeError("OpenROAD GCD source did not contain the expected functional mutation anchor")
        candidate_source.write_text(text.replace(OLD, NEW), encoding="utf-8")
        record = run_repository_task(manifest["tasks"][0], canonical_root=REPO, baseline_root=roots["baseline"], candidate_root=roots["candidate"], output_root=args.output)
    result = record["result"]
    print(json.dumps({"status": record["status"], "task_id": record["task_id"], "repository_revision": actual_revision, "baseline": result["baseline_status"], "repaired": result["repaired_status"], "candidate_changed": result["checks"]["candidate_changed"], "canonical_unchanged": result["checks"]["source_unchanged"], "claim_boundary": "repository-scale functional result for three GCD transactions"}, sort_keys=True))
    return 0 if record["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
