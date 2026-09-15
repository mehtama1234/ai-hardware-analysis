"""Run native Yosys compilation over multiple OpenROAD designs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
REPO = Path("/home/mehtama1/eda-tools/OpenROAD-flow-scripts")
PLAN = ROOT / "benchmarks/repository_scale/openroad_native_compile_suite.json"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/repository-scale-real/openroad-native")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    if not REPO.is_dir():
        print(json.dumps({"status": "blocked", "reason": "OpenROAD checkout missing"}, sort_keys=True))
        return 1
    revision = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], text=True).strip()
    if revision != plan["repository_revision"]:
        print(json.dumps({"status": "blocked", "reason": "OpenROAD revision mismatch", "expected": plan["repository_revision"], "actual": revision}, sort_keys=True))
        return 1
    results = []
    for design in plan["designs"]:
        source_files = [str(path) for path in design["source_files"]]
        command = ["yosys", "-p", f"read_verilog {' '.join(source_files)}; hierarchy -top {design['top']}; proc; check; stat"]
        completed = subprocess.run(command, cwd=REPO, capture_output=True, text=True, check=False)
        (args.output / f"{design['design_id']}.stdout.log").write_text(completed.stdout, encoding="utf-8")
        (args.output / f"{design['design_id']}.stderr.log").write_text(completed.stderr, encoding="utf-8")
        results.append({
            "design_id": design["design_id"], "top": design["top"], "source_files": source_files,
            "returncode": completed.returncode, "status": "pass" if completed.returncode == 0 else "fail",
            "stdout_sha256": sha(completed.stdout.encode()), "stderr_sha256": sha(completed.stderr.encode()),
        })
    report = {
        "schema_version": "native-repository-compile-report-v1",
        "repository": str(REPO), "repository_revision": revision, "results": results,
        "status": "passed" if all(item["status"] == "pass" for item in results) else "blocked",
        "claim_boundary": "native Yosys syntax/elaboration checks for the declared OpenROAD designs; not functional regression or physical signoff",
    }
    report["report_sha256"] = hashlib.sha256(json.dumps(report, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    path = args.output / "openroad-native-compile-report.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "designs": len(results), "passed": sum(item["status"] == "pass" for item in results), "repository_revision": revision, "report": str(path)}, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
