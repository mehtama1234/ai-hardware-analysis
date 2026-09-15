#!/usr/bin/env python3
"""Verify that a customer pilot packet is eligible for production promotion."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from deployment.pilot_scorecard import validate_scorecard
from deployment.signoff_service import verify_signoff
from scripts.verify_pilot_scorecard_evidence import verify as verify_evidence


def _under_root(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _nonnegative_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def verify_packet(*, readiness_path: Path, scorecard_path: Path, root: Path, signoff_path: Path | None = None) -> dict[str, object]:
    errors: list[str] = []
    if not _under_root(readiness_path, root):
        errors.append("readiness report is outside packet root")
    if not _under_root(scorecard_path, root):
        errors.append("scorecard is outside packet root")
    if signoff_path is not None and not _under_root(signoff_path, root):
        errors.append("signoff receipt is outside packet root")
    readiness = {}
    if _under_root(readiness_path, root):
        try:
            readiness = json.loads(readiness_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"cannot read readiness report: {error}")
    if readiness.get("schema_version") != "verification-production-readiness-v1":
        errors.append("readiness report has unsupported schema_version")
    readiness_digest = readiness.get("readiness_sha256")
    readiness_payload = {key: value for key, value in readiness.items() if key != "readiness_sha256"}
    computed_readiness_digest = sha256(json.dumps(readiness_payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if not isinstance(readiness_digest, str) or readiness_digest != computed_readiness_digest:
        errors.append("readiness report self-digest does not match")
    if type(readiness.get("customer_production_ready")) is not bool:
        errors.append("readiness report ready flag must be boolean")
    elif readiness.get("customer_production_ready") is not True:
        errors.append("customer production readiness is not true")
    if not _nonnegative_int(readiness.get("open_count")) or readiness.get("open_count") != 0 or not isinstance(readiness.get("open_controls"), list) or readiness.get("open_controls"):
        errors.append("readiness report still contains open controls")
    if not _nonnegative_int(readiness.get("control_count")) or readiness.get("control_count") < 1 or not _nonnegative_int(readiness.get("verified_count")) or readiness.get("control_count") != readiness.get("verified_count"):
        errors.append("readiness control counts do not show complete verification")
    if type(readiness.get("pilot_controls_verified")) is not bool or readiness.get("pilot_controls_verified") is not True:
        errors.append("readiness report pilot_controls_verified must be true")
    checklist_raw = readiness.get("checklist")
    checklist_digest = readiness.get("checklist_sha256")
    if not isinstance(checklist_raw, str) or not checklist_raw or Path(checklist_raw).is_absolute() or "\\" in checklist_raw or any(part in {"", ".", ".."} for part in checklist_raw.split("/")):
        errors.append("readiness report has an unsafe checklist path")
    else:
        checklist_path = (root / checklist_raw).resolve()
        if not _under_root(checklist_path, root) or not checklist_path.is_file():
            errors.append("readiness checklist is missing")
        elif not isinstance(checklist_digest, str) or len(checklist_digest) != 64 or sha256(checklist_path.read_bytes()).hexdigest() != checklist_digest:
            errors.append("readiness checklist digest does not match")
    if _under_root(scorecard_path, root):
        try:
            scorecard = json.loads(scorecard_path.read_text(encoding="utf-8"))
            errors.extend(validate_scorecard(scorecard, finalized=True))
            errors.extend(verify_evidence(scorecard_path, root))
        except (OSError, json.JSONDecodeError, TypeError) as error:
            errors.append(f"cannot read scorecard: {error}")
    if signoff_path is None:
        errors.append("customer pilot packet requires a signoff receipt")
    elif not _under_root(signoff_path, root):
        pass
    else:
        try:
            signoff = json.loads(signoff_path.read_text(encoding="utf-8"))
            if signoff.get("status") != "approved":
                errors.append("signoff receipt must have approved status")
            if not str(signoff.get("reviewer_subject", "")).strip():
                errors.append("signoff receipt requires an authenticated reviewer subject")
            report_path = Path(str(signoff.get("report_path", ""))).resolve()
            if report_path != scorecard_path.resolve():
                errors.append("signoff receipt is bound to a different scorecard")
            elif not verify_signoff(signoff_path):
                errors.append("signoff receipt does not verify against its report")
        except (OSError, json.JSONDecodeError, TypeError):
            errors.append("signoff receipt is not readable")
    return {
        "schema_version": "verification-customer-pilot-packet-v1",
        "readiness": str(readiness_path),
        "scorecard": str(scorecard_path),
        "signoff": str(signoff_path) if signoff_path else None,
        "verified": not errors,
        "errors": errors,
        "claim_boundary": "Promotion gate only; a passing packet proves supplied artifacts are mutually valid, not semiconductor design correctness or business ROI beyond the signed measurements.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readiness", type=Path, required=True)
    parser.add_argument("--scorecard", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--signoff", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = verify_packet(readiness_path=args.readiness, scorecard_path=args.scorecard, root=args.root, signoff_path=args.signoff)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if result["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
