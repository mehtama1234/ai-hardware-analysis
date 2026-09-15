"""Run the first non-seeded repository-scale OpenROAD task locally."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analog-digital-chip-design-eda"))

from verification_platform.repository_benchmark import run_repository_task, validate_task_manifest


SOURCE_RELATIVE = Path("flow/designs/src/gcd/gcd.v")
SOURCE = Path("/home/mehtama1/eda-tools/OpenROAD-flow-scripts") / SOURCE_RELATIVE
OLD = "  assign req_rdy         = ctrl$req_rdy;"
NEW = "  assign req_rdy         = ctrl$req_rdy_missing;"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/repository-scale-real/openroad-gcd")
    args = parser.parse_args()
    manifest = json.loads((ROOT / "benchmarks/repository_scale/openroad_gcd_compile_task.json").read_text(encoding="utf-8"))
    validate_task_manifest(manifest)
    if not SOURCE.is_file():
        print(json.dumps({"status": "blocked", "reason": f"OpenROAD checkout missing: {SOURCE}"}, sort_keys=True))
        return 1
    with tempfile.TemporaryDirectory(prefix="openroad-task-") as directory:
        staging = Path(directory)
        roots = {name: staging / name for name in ("baseline", "candidate")}
        for root in roots.values():
            destination = root / SOURCE_RELATIVE
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SOURCE, destination)
        candidate_source = roots["candidate"] / SOURCE_RELATIVE
        text = candidate_source.read_text(encoding="utf-8")
        if text.count(OLD) != 1:
            raise RuntimeError("OpenROAD GCD source did not contain the expected mutation anchor")
        candidate_source.write_text(text.replace(OLD, NEW), encoding="utf-8")
        record = run_repository_task(
            manifest["tasks"][0], canonical_root=Path("/home/mehtama1/eda-tools/OpenROAD-flow-scripts"),
            baseline_root=roots["baseline"], candidate_root=roots["candidate"], output_root=args.output,
        )
    print(json.dumps({"status": record["status"], "task_id": record["task_id"], "baseline": record["result"]["baseline_status"], "repaired": record["result"]["repaired_status"], "candidate_changed": record["result"]["checks"]["candidate_changed"], "canonical_unchanged": record["result"]["checks"]["source_unchanged"], "claim_boundary": "compile-only repository task"}, sort_keys=True))
    return 0 if record["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
