#!/usr/bin/env python3
"""Run the credential-free reference diagnosis agent on a typed failure."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from verification_platform.reference_agent import propose_failure_diagnosis
from verification_platform.triage import Failure


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("failure", type=Path, help="JSON file containing cycle, signal, expected, and actual")
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--evidence", nargs="+", required=True)
    parser.add_argument("--dependency-cone", nargs="*", default=[])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = json.loads(args.failure.read_text(encoding="utf-8"))
    failure = Failure(int(payload["cycle"]), str(payload["signal"]), str(payload["expected"]), str(payload["actual"]))
    proposal = propose_failure_diagnosis(failure, source_revision=args.source_revision, evidence=args.evidence, dependency_cone=args.dependency_cone)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(proposal.record(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "proposal_sha256": proposal.proposal_sha256, "status": proposal.status}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
