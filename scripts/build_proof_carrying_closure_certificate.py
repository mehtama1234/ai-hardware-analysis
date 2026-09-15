"""Build an independent, hash-bound certificate over the next-stage evidence."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

REQUIRED = {
    "repository-fail-to-pass": "simulation",
    "workstream2-mutation-1000": "mutation",
    "formal-proof-closure": "formal",
    "coverage-closure": "coverage",
    "security-policy-campaign": "security",
    "spec-grounded-assertion-matrix-integrity": "assertion_integrity",
}

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("aggregate", type=Path); parser.add_argument("--output", type=Path, required=True); args = parser.parse_args()
    aggregate = json.loads(args.aggregate.read_text(encoding="utf-8")); records = {item["name"]: item for item in aggregate.get("components", [])}
    evidence = {}; errors = []
    if aggregate.get("all_passed") is not True: errors.append("aggregate is not all_passed")
    for name, role in REQUIRED.items():
        record = records.get(name)
        if record is None or record.get("status") != "passed": errors.append(f"required component failed: {name}"); continue
        result = record.get("result", {}); report = result.get("report")
        if not report:
            # Some integrity components expose the validated report path.
            report = result.get("report")
        if not report or not Path(report).is_file(): errors.append(f"missing evidence report: {name}"); continue
        path = Path(report).resolve(); raw = path.read_bytes()
        evidence[role] = {"component": name, "path": str(path), "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw), "status": result.get("status", "present")}
    certificate = {
        "schema_version": "proof-carrying-closure-certificate-v1",
        "aggregate_report": str(args.aggregate.resolve()),
        "aggregate_sha256": hashlib.sha256(args.aggregate.read_bytes()).hexdigest(),
        "aggregate_all_passed": aggregate.get("all_passed"),
        "evidence": evidence,
        "required_roles": sorted(REQUIRED.values()),
        "status": "passed" if not errors and set(evidence) == set(REQUIRED.values()) else "blocked",
        "errors": sorted(errors),
        "claim_boundary": "hash-bound local closure certificate over the declared aggregate; not a silicon signoff, exhaustive proof, or production release",
    }
    certificate["certificate_sha256"] = digest(certificate)
    args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": certificate["status"], "roles": sorted(evidence), "certificate": str(args.output)}, sort_keys=True)); return 0 if certificate["status"] == "passed" else 1

if __name__ == "__main__": raise SystemExit(main())
