"""Check the OpenLane save-DEF replay report."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
def digest(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
def main():
    parser = argparse.ArgumentParser(); parser.add_argument("report", type=Path); args = parser.parse_args(); report = json.loads(args.report.read_text()); errors = []
    expected = {"schema_version":"openlane-historical-save-def-agent-repair-report-v1","repository":"OpenLane","historical_fix_commit":"11dcdbbcd221ed65fc697ff0bcbb1b40b4392ff4","baseline_status":"failed","agent_status":"available","patch_candidate_status":"review_required","repaired_status":"passed","canonical_unchanged":True,"status":"passed"}
    for key, value in expected.items():
        if report.get(key) != value: errors.append(f"{key} mismatch")
    unsigned = dict(report); actual = unsigned.pop("report_sha256", None)
    if actual != digest(unsigned): errors.append("digest mismatch")
    result = {"schema_version":"openlane-historical-save-def-agent-repair-check-v1","status":"passed" if not errors else "blocked","errors":errors,"report":str(args.report)}; result["check_sha256"] = digest(result); print(json.dumps(result, sort_keys=True)); return 0 if not errors else 1
if __name__ == "__main__": raise SystemExit(main())
