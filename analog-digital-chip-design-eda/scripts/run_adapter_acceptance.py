#!/usr/bin/env python3
"""Run the reference adapter acceptance matrix with bounded evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from verification_platform.adapter import AdapterSpec, execute_adapter


CASES = (
    ("pass", ["-c", "from pathlib import Path; Path('result.json').write_text('pass\\n')"], ("result.json",), "passed"),
    ("fail", ["-c", "raise SystemExit(3)"], (), "failed"),
    ("timeout", ["-c", "import time; time.sleep(3)"], (), "blocked"),
    ("missing-artifact", ["-c", "print('completed without output')"], ("result.json",), "blocked"),
)


def run_acceptance(output_root: Path, *, timeout_seconds: float = 1.5) -> dict[str, object]:
    output_root.mkdir(parents=True, exist_ok=True)
    results = []
    for name, args, expected, expected_status in CASES:
        run_root = output_root / name
        run = execute_adapter(
            AdapterSpec(f"reference-{name}", sys.executable, expected_artifacts=expected),
            args,
            run_root=run_root,
            source_revision="adapter-acceptance-v1",
            timeout_seconds=timeout_seconds,
        )
        results.append({"case": name, "status": run.status, "expected_status": expected_status, "tool": run.tool, "metadata": run.metadata})
    verified = all(item["status"] == item["expected_status"] for item in results)
    result = {
        "schema_version": "verification-adapter-acceptance-v1",
        "cases": results,
        "case_count": len(results),
        "verified": verified,
        "claim_boundary": "Reference adapter contract matrix only; customer simulator, formal, regression, and artifact adapters still require deployment-specific validation.",
    }
    (output_root / "acceptance-summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(tempfile.mkdtemp(prefix="verification-adapter-acceptance-")))
    args = parser.parse_args()
    result = run_acceptance(args.output)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
