#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen

from validate_analog_simulator_adapter_contract import (
    CONTRACT,
    OLD_BACKEND,
    backend_readiness,
    load_json,
    validate_contract_shape,
    validate_payload_against_contract,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BACKEND = "http://127.0.0.1:8025"
DEFAULT_PACKAGE_ID = "pkg-e931662a01293df2"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def post_json(url: str, payload: dict[str, object]) -> dict[str, object]:
    data = json.dumps(payload).encode("utf-8")
    request = Request(url, data=data, method="POST", headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def validate_payload(path: Path) -> tuple[dict[str, object], dict[str, object]]:
    contract = load_json(CONTRACT)
    validate_contract_shape(contract)
    payload = load_json(path)
    require(payload.get("dry_run") is not True, "dry-run payloads must not be imported as simulator evidence")
    issues = validate_payload_against_contract(payload, contract)
    require(not issues, f"payload does not satisfy adapter contract: {issues}")
    readiness = backend_readiness(payload)
    require(not readiness["structural_errors"], f"payload failed backend structure: {readiness['structural_errors']}")
    require(readiness["tool_ready"] is True, f"payload failed backend tool readiness: {readiness['issues']}")
    return payload, readiness


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate or import a real analog simulator adapter payload.")
    parser.add_argument("payload", type=Path, help="Path to an analog_error_simulation payload JSON file.")
    parser.add_argument("--backend", default=DEFAULT_BACKEND, help="Backend base URL.")
    parser.add_argument("--package-id", default=DEFAULT_PACKAGE_ID, help="Deployment package id.")
    parser.add_argument("--import", dest="do_import", action="store_true", help="Post the payload to the backend strict tool import endpoint.")
    parser.add_argument("--expect-reject", action="store_true", help="Return success only if the guard rejects the payload.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload_path = args.payload.resolve()
    if not payload_path.exists():
        raise SystemExit(f"payload not found: {payload_path}")
    try:
        payload, readiness = validate_payload(payload_path)
    except Exception as exc:
        if args.expect_reject:
            print("PASS analog_simulator_payload_guard_rejection")
            print(f"payload,{payload_path}")
            print(f"reason,{exc}")
            return 0
        raise
    require(not args.expect_reject, "payload was accepted but --expect-reject was set")
    imported = None
    if args.do_import:
        imported = post_json(
            f"{args.backend}/evidence/import-tool?source_id=analog_error_simulation&package_id={args.package_id}",
            payload,
        )
        require(imported.get("source_id") == "analog_error_simulation", "backend import returned the wrong source_id")
        imported_readiness = imported.get("tool_readiness") if isinstance(imported.get("tool_readiness"), dict) else {}
        require(imported_readiness.get("tool_ready") is True, "backend import did not preserve tool readiness")

    print("PASS analog_simulator_payload_guard")
    print(f"payload,{payload_path}")
    print(f"backend_tool_ready,{readiness['tool_ready']}")
    print(f"mode,{'import' if args.do_import else 'validate-only'}")
    if imported:
        print(f"import_id,{imported.get('import_id')}")
        print(f"package_id,{imported.get('package_id')}")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(OLD_BACKEND))
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL analog_simulator_payload_guard: {exc}", file=sys.stderr)
        raise
