"""Mutation-based verification closure contracts.

The mutation oracle gives credit only when the unmodified test passes and an
explicit source mutation makes that same test fail. A passing mutant is a
false pass, not coverage. The module intentionally keeps the mutation
application deterministic and records source digests for replay.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_mutation_suite(suite: dict[str, Any]) -> None:
    if not isinstance(suite, dict) or suite.get("schema_version") != "mutation-suite-v1":
        raise ValueError("mutation suite schema is unsupported")
    mutations = suite.get("mutations")
    if not isinstance(mutations, list) or not mutations:
        raise ValueError("mutation suite requires non-empty mutations")
    seen: set[str] = set()
    for mutation in mutations:
        if not isinstance(mutation, dict):
            raise ValueError("mutation must be an object")
        mutation_id = mutation.get("mutation_id")
        if not isinstance(mutation_id, str) or not mutation_id or mutation_id in seen:
            raise ValueError("mutation ids must be unique non-empty strings")
        seen.add(mutation_id)
        if not isinstance(mutation.get("source_file"), str) or not mutation["source_file"]:
            raise ValueError(f"mutation {mutation_id} requires source_file")
        if not isinstance(mutation.get("from"), str) or not isinstance(mutation.get("to"), str) or mutation["from"] == mutation["to"]:
            raise ValueError(f"mutation {mutation_id} requires string from/to replacements")
        command = mutation.get("command")
        if not isinstance(command, list) or not command or any(not isinstance(item, str) or not item for item in command):
            raise ValueError(f"mutation {mutation_id} requires a non-empty command")


@dataclass(frozen=True)
class MutationResult:
    mutation_id: str
    baseline_status: str
    mutant_status: str
    baseline_valid: bool
    detected: bool
    false_pass: bool
    candidate_changed: bool
    canonical_unchanged: bool
    source_sha256_before: str
    source_sha256_after: str
    claim_boundary: str = "same-command mutation detection; not exhaustive verification"

    def record(self) -> dict[str, Any]:
        body = {
            "schema_version": "mutation-result-v1",
            "mutation_id": self.mutation_id,
            "baseline_status": self.baseline_status,
            "mutant_status": self.mutant_status,
            "baseline_valid": self.baseline_valid,
            "detected": self.detected,
            "false_pass": self.false_pass,
            "candidate_changed": self.candidate_changed,
            "canonical_unchanged": self.canonical_unchanged,
            "source_sha256_before": self.source_sha256_before,
            "source_sha256_after": self.source_sha256_after,
            "claim_boundary": self.claim_boundary,
        }
        body["result_sha256"] = _digest(json.dumps(body, sort_keys=True, separators=(",", ":")).encode())
        return body


def _run(command: list[str], cwd: Path, timeout_seconds: float) -> tuple[str, int | None, str, str]:
    try:
        completed = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=timeout_seconds, check=False)
        return ("pass" if completed.returncode == 0 else "fail", completed.returncode, completed.stdout, completed.stderr)
    except subprocess.TimeoutExpired as error:
        stdout = error.stdout.decode() if isinstance(error.stdout, bytes) else (error.stdout or "")
        stderr = error.stderr.decode() if isinstance(error.stderr, bytes) else (error.stderr or "")
        return "blocked", None, stdout, stderr + "\nTIMEOUT\n"


def run_mutation(
    mutation: dict[str, Any],
    *,
    canonical_root: str | Path,
    baseline_root: str | Path,
    candidate_root: str | Path,
    output_root: str | Path,
    timeout_seconds: float = 300.0,
) -> dict[str, Any]:
    """Run the same command on baseline and one deterministically mutated copy."""
    validate_mutation_suite({"schema_version": "mutation-suite-v1", "mutations": [mutation]})
    canonical = Path(canonical_root).resolve()
    baseline = Path(baseline_root).resolve()
    candidate = Path(candidate_root).resolve()
    output = Path(output_root).resolve()
    source = Path(mutation["source_file"])
    if source.is_absolute() or not canonical.is_dir() or not baseline.is_dir() or not candidate.is_dir():
        raise ValueError("mutation roots must be directories and source_file must be relative")
    canonical_source = (canonical / source).resolve()
    baseline_source = (baseline / source).resolve()
    candidate_source = (candidate / source).resolve()
    for path, root in ((canonical_source, canonical), (baseline_source, baseline), (candidate_source, candidate)):
        try:
            path.relative_to(root)
        except ValueError as error:
            raise ValueError("mutation source escapes its root") from error
        if not path.is_file():
            raise ValueError(f"mutation source is missing: {path}")
    before = canonical_source.read_bytes()
    candidate_text = candidate_source.read_text(encoding="utf-8")
    old, new = mutation["from"], mutation["to"]
    if candidate_text.count(old) != 1:
        raise ValueError(f"mutation {mutation['mutation_id']} expected exactly one source match")
    candidate_source.write_text(candidate_text.replace(old, new), encoding="utf-8")
    after = candidate_source.read_bytes()
    baseline_status, baseline_code, baseline_stdout, baseline_stderr = _run(mutation["command"], baseline, timeout_seconds)
    mutant_status, mutant_code, mutant_stdout, mutant_stderr = _run(mutation["command"], candidate, timeout_seconds)
    canonical_after = canonical_source.read_bytes()
    output.mkdir(parents=True, exist_ok=True)
    (output / "baseline.stdout.log").write_text(baseline_stdout, encoding="utf-8")
    (output / "baseline.stderr.log").write_text(baseline_stderr, encoding="utf-8")
    (output / "mutant.stdout.log").write_text(mutant_stdout, encoding="utf-8")
    (output / "mutant.stderr.log").write_text(mutant_stderr, encoding="utf-8")
    result = MutationResult(
        mutation_id=str(mutation["mutation_id"]),
        baseline_status=baseline_status,
        mutant_status=mutant_status,
        baseline_valid=baseline_status == "pass",
        detected=baseline_status == "pass" and mutant_status == "fail" and before != after and before == canonical_after,
        false_pass=baseline_status == "pass" and mutant_status == "pass" and before != after,
        candidate_changed=before != after,
        canonical_unchanged=before == canonical_after,
        source_sha256_before=_digest(before),
        source_sha256_after=_digest(after),
    ).record()
    record = {
        "mutation": {key: mutation[key] for key in ("mutation_id", "source_file", "from", "to", "command")},
        "baseline": {"status": baseline_status, "returncode": baseline_code},
        "mutant": {"status": mutant_status, "returncode": mutant_code},
        "result": result,
    }
    record["record_sha256"] = _digest(json.dumps(record, sort_keys=True, separators=(",", ":")).encode())
    (output / "mutation-result.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record


def summarize_mutations(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate mutation score while separating invalid baselines and false passes."""
    if not results:
        raise ValueError("mutation results cannot be empty")
    records = [item["result"] for item in results]
    eligible = sum(bool(item["baseline_valid"]) for item in records)
    detected = sum(bool(item["detected"]) for item in records)
    false_passes = sum(bool(item["false_pass"]) for item in records)
    blocked = sum(
        item["mutant_status"] == "blocked"
        or item["baseline_status"] == "blocked"
        or not item["candidate_changed"]
        or not item["canonical_unchanged"]
        for item in records
    )
    by_source: dict[str, dict[str, int | float | None]] = {}
    for record, item in zip(results, records):
        mutation = record.get("mutation", {})
        source = str(mutation.get("source_file", "unknown"))
        metrics = by_source.setdefault(source, {"total": 0, "eligible": 0, "detected": 0, "false_passes": 0, "blocked": 0})
        metrics["total"] += 1
        metrics["eligible"] += int(bool(item["baseline_valid"]))
        metrics["detected"] += int(bool(item["detected"]))
        metrics["false_passes"] += int(bool(item["false_pass"]))
        metrics["blocked"] += int(item["mutant_status"] == "blocked" or item["baseline_status"] == "blocked" or not item["candidate_changed"] or not item["canonical_unchanged"])
    for metrics in by_source.values():
        metrics["mutation_score"] = round(metrics["detected"] / metrics["eligible"], 6) if metrics["eligible"] else None
    body = {
        "schema_version": "mutation-closure-report-v1",
        "total_mutations": len(records),
        "eligible_mutations": eligible,
        "detected_mutations": detected,
        "mutation_score": round(detected / eligible, 6) if eligible else None,
        "false_pass_count": false_passes,
        "blocked_count": blocked,
        "by_source": dict(sorted(by_source.items())),
        "status": "passed" if eligible == len(records) and detected == eligible and false_passes == 0 and blocked == 0 else "blocked",
        "claim_boundary": "mutation score over this declared suite; not exhaustive coverage or proof",
    }
    body["report_sha256"] = _digest(json.dumps(body, sort_keys=True, separators=(",", ":")).encode())
    return body
