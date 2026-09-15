#!/usr/bin/env python3
"""Independently verify an agentic hardware closure summary."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def required_file(raw: str, *, base: Path, errors: list[str]) -> Path | None:
    path = Path(raw)
    if not path.is_absolute():
        path = base / path
    path = path.resolve()
    if not path.is_file():
        errors.append(f"missing artifact: {raw}")
        return None
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", type=Path)
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    summary_path = args.summary.resolve()
    errors: list[str] = []
    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"ERROR: cannot read summary: {error}")
        return 1
    if summary.get("schema_version") != "agentic-hardware-closure-run-v1":
        errors.append("unexpected closure summary schema")
    benchmark_path = required_file(summary.get("benchmark", ""), base=summary_path.parent, errors=errors)
    review_path = required_file(summary.get("repair_review", ""), base=summary_path.parent, errors=errors)
    held_out_review_path = required_file(summary.get("held_out_repair_review", ""), base=summary_path.parent, errors=errors)
    source_path = args.source.resolve()
    if not source_path.is_file():
        errors.append("canonical source is missing")
    elif summary.get("canonical_source_sha256") != digest(source_path):
        errors.append("canonical source digest does not match summary")
    if benchmark_path:
        if summary.get("artifacts", {}).get("benchmark_sha256") != digest(benchmark_path):
            errors.append("benchmark digest does not match summary")
        try:
            benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
            metrics = benchmark.get("metrics", {})
            if benchmark.get("schema_version") != "llm-verification-agent-benchmark-v1":
                errors.append("benchmark schema is invalid")
            if benchmark.get("design_count") != 11 or metrics.get("grounded_proposals") != 11 or metrics.get("unsafe_rejected") != 3:
                errors.append("benchmark acceptance metrics are incomplete")
            execution = summary.get("model_execution", {})
            if execution.get("benchmark_sha256") != digest(benchmark_path):
                errors.append("model execution is not bound to the benchmark digest")
            if execution.get("kind") == "real_model":
                if not isinstance(benchmark.get("model_provenance"), dict) or execution.get("provenance") != benchmark.get("model_provenance"):
                    errors.append("real-model provenance is missing or not bound to the benchmark")
            elif execution.get("kind") != "provider_free_fixture":
                errors.append("model execution kind is invalid")
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"cannot read benchmark: {error}")
    review = None
    if review_path:
        if summary.get("artifacts", {}).get("repair_review_sha256") != digest(review_path):
            errors.append("repair-review digest does not match summary")
        try:
            review = json.loads(review_path.read_text(encoding="utf-8"))
            if review.get("approval", {}).get("status") not in {"required", "approved", "rejected"}:
                errors.append("repair review has no valid approval state")
            if review.get("source", {}).get("sha256") != digest(source_path):
                errors.append("repair review is not bound to the current canonical source")
            retest = review.get("retest", {})
            if review.get("approval", {}).get("status") == "approved":
                if retest.get("status") != "passed" or retest.get("original_unchanged") is not True:
                    errors.append("approved repair retest is not passed and source-safe")
                if summary.get("status") != "passed":
                    errors.append("approved repair must produce a passed summary")
            elif review.get("approval", {}).get("status") == "rejected":
                if summary.get("status") != "rejected":
                    errors.append("rejected repair must produce a rejected summary")
            elif summary.get("status") != "review_required":
                errors.append("unapproved repair must remain review_required")
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"cannot read repair review: {error}")
    if held_out_review_path:
        if summary.get("artifacts", {}).get("held_out_repair_review_sha256") != digest(held_out_review_path):
            errors.append("held-out repair-review digest does not match summary")
        try:
            held_out = json.loads(held_out_review_path.read_text(encoding="utf-8"))
            if held_out.get("schema_version") != "llm-approved-timeout-repair-v1" or held_out.get("design_id") != "seeded_timeout":
                errors.append("held-out review is not the seeded_timeout repair contract")
            if held_out.get("approval", {}).get("status") not in {"required", "approved", "rejected"}:
                errors.append("held-out repair has no valid approval state")
            timeout_source = source_path.parent.parent / "seeded_timeout" / "timeout.sv"
            if not timeout_source.is_file() or held_out.get("source", {}).get("sha256") != digest(timeout_source):
                errors.append("held-out repair is not bound to the timeout source")
            retest = held_out.get("retest", {})
            if held_out.get("approval", {}).get("status") == "approved":
                if retest.get("status") != "passed" or retest.get("original_unchanged") is not True:
                    errors.append("approved held-out retest is not passed and source-safe")
                if retest.get("formal", {}).get("status") != "passed":
                    errors.append("approved held-out formal retest did not pass")
                scope = held_out.get("verification_scope", {})
                if held_out.get("approval", {}).get("source_sha256") != held_out.get("source", {}).get("sha256"):
                    errors.append("held-out approval is not bound to source")
                if held_out.get("approval", {}).get("scope_sha256") != scope.get("scope_sha256"):
                    errors.append("held-out approval is not bound to scope")
            elif held_out.get("approval", {}).get("status") == "rejected":
                if summary.get("status") != "rejected":
                    errors.append("rejected held-out repair must produce a rejected summary")
            elif summary.get("status") != "review_required":
                errors.append("unapproved held-out repair must keep the summary review_required")
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"cannot read held-out repair review: {error}")
    physical = summary.get("physical_handoff")
    if physical:
        physical_path = required_file(physical.get("path", ""), base=summary_path.parent, errors=errors)
        if physical_path:
            if physical.get("sha256") != digest(physical_path):
                errors.append("physical handoff digest does not match summary")
            try:
                handoff = json.loads(physical_path.read_text(encoding="utf-8"))
                if handoff.get("status") != "passed" or handoff.get("physical", {}).get("lvs_errors") != 0:
                    errors.append("physical handoff is not clean")
                if physical.get("same_run") is True and handoff.get("source", {}).get("physical_staged_sha256") is None:
                    errors.append("same-run physical handoff has no staged-source digest")
                if handoff.get("source", {}).get("physical_staged_sha256") != review.get("retest", {}).get("repaired_sha256"):
                    errors.append("physical handoff does not match repaired-source hash")
            except (OSError, json.JSONDecodeError) as error:
                errors.append(f"cannot read physical handoff: {error}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(json.dumps({"status": "passed", "summary": str(summary_path), "approval": review["approval"]["status"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
