"""Run syntax/elaboration checks over multiple designs in an OpenLane checkout."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
REPO = Path("/home/mehtama1/eda-tools/OpenLane")
PLAN = ROOT / "benchmarks/repository_scale/openlane_native_compile_suite.json"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/repository-scale-real/openlane-native")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    if not REPO.is_dir():
        print(json.dumps({"status": "blocked", "reason": "OpenLane checkout missing"}, sort_keys=True))
        return 1
    revision = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], text=True).strip()
    if revision != plan["repository_revision"]:
        print(json.dumps({"status": "blocked", "reason": "OpenLane revision mismatch", "expected": plan["repository_revision"], "actual": revision}, sort_keys=True))
        return 1
    results = []
    for design in plan["designs"]:
        command = ["yosys", "-p", f"read_verilog -sv {' '.join(design['source_files'])}; hierarchy -top {design['top']}; proc; check; stat"]
        completed = subprocess.run(command, cwd=REPO, capture_output=True, text=True, check=False)
        (args.output / f"{design['design_id']}.stdout.log").write_text(completed.stdout, encoding="utf-8")
        (args.output / f"{design['design_id']}.stderr.log").write_text(completed.stderr, encoding="utf-8")
        results.append({
            "design_id": design["design_id"], "top": design["top"], "source_files": design["source_files"],
            "returncode": completed.returncode, "status": "pass" if completed.returncode == 0 else "fail",
            "stdout_sha256": sha256(completed.stdout.encode()), "stderr_sha256": sha256(completed.stderr.encode()),
        })
    report = {
        "schema_version": "native-repository-compile-report-v1", "repository": str(REPO),
        "repository_revision": revision, "results": results,
        "status": "passed" if all(item["status"] == "pass" for item in results) else "blocked",
        "claim_boundary": "native Yosys syntax/elaboration checks for the declared OpenLane designs; not full OpenLane physical signoff",
    }
    report["report_sha256"] = sha256(json.dumps(report, sort_keys=True, separators=(",", ":")).encode())
    report_path = args.output / "openlane-native-compile-report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "designs": len(results), "passed": sum(item["status"] == "pass" for item in results), "repository_revision": revision, "report": str(report_path)}, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
