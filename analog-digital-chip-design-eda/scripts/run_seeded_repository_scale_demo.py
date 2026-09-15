"""Run the first repository-scale benchmark against isolated baseline/candidate copies."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from verification_platform.repository_benchmark import run_repository_task, validate_task_manifest


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "benchmarks/repository_scale/seeded_counter_task.json"
SOURCE = ROOT / "benchmarks/seeded_counter/counter.sv"
BUGGY = "      counter_q <= counter_q + 4'd1; // SEEDED_BUG: missing enable guard"
FIXED = "      if (enable) counter_q <= counter_q + 4'd1; // SEEDED_BUG: missing enable guard"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/repository-scale-m1/seeded-counter")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    validate_task_manifest(manifest)
    task = manifest["tasks"][0]
    with tempfile.TemporaryDirectory(prefix="repository-scale-demo-") as directory:
        staging = Path(directory)
        baseline = staging / "baseline"
        candidate = staging / "candidate"
        # Materialize only the task's declared execution collateral. A real
        # project adapter can replace this with a checked-out repository
        # snapshot without copying unrelated research artifacts.
        for root in (baseline, candidate):
            (root / "scripts").mkdir(parents=True)
            (root / "benchmarks/seeded_counter").mkdir(parents=True)
            shutil.copy2(ROOT / "scripts/run_seeded_counter_check.py", root / "scripts/run_seeded_counter_check.py")
            for name in ("counter.sv", "tb.sv"):
                shutil.copy2(ROOT / "benchmarks/seeded_counter" / name, root / "benchmarks/seeded_counter" / name)
        candidate_source = candidate / "benchmarks/seeded_counter/counter.sv"
        text = candidate_source.read_text(encoding="utf-8")
        if text.count(BUGGY) != 1:
            raise RuntimeError("seeded counter source did not contain exactly one expected defect")
        candidate_source.write_text(text.replace(BUGGY, FIXED), encoding="utf-8")
        record = run_repository_task(
            task,
            canonical_root=ROOT,
            baseline_root=baseline,
            candidate_root=candidate,
            output_root=args.output,
        )
    print(json.dumps({
        "status": record["status"],
        "task_id": record["task_id"],
        "baseline_status": record["result"]["baseline_status"],
        "repaired_status": record["result"]["repaired_status"],
        "source_unchanged": record["result"]["checks"]["source_unchanged"],
        "candidate_changed": record["result"]["checks"]["candidate_changed"],
        "report": str(args.output / "task-result.json"),
    }, sort_keys=True))
    return 0 if record["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
