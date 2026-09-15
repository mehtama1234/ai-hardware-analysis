#!/usr/bin/env python3
"""Convert the production checklist into an auditable JSON readiness report."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys


ITEM = re.compile(r"^- \[([ xX])\] (.+)$")


def build_report(checklist: Path) -> dict[str, object]:
    text = checklist.read_text(encoding="utf-8")
    checklist_digest = sha256(text.encode("utf-8")).hexdigest()
    items = []
    for line in text.splitlines():
        match = ITEM.match(line.strip())
        if match:
            items.append({"title": match.group(2), "verified": match.group(1).lower() == "x"})
    if not items:
        raise ValueError("production checklist contains no checkbox controls")
    verified = sum(item["verified"] for item in items)
    open_items = [item["title"] for item in items if not item["verified"]]
    report = {"schema_version": "verification-production-readiness-v1", "checklist": str(checklist), "checklist_sha256": checklist_digest, "control_count": len(items), "verified_count": verified, "open_count": len(open_items), "pilot_controls_verified": verified > 0, "customer_production_ready": not open_items, "open_controls": open_items, "claim_boundary": "This report summarizes checklist state; customer production readiness requires all infrastructure gates and a signed measured pilot."}
    report["readiness_sha256"] = sha256(json.dumps(report, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checklist", type=Path, default=Path("deployment/PRODUCTION_CHECKLIST.md"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = build_report(args.checklist)
    except (OSError, ValueError) as error:
        print(f"cannot report readiness: {error}", file=sys.stderr)
        return 2
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
