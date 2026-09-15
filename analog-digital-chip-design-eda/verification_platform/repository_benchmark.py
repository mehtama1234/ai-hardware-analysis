"""Repository-scale task manifests and fail-closed evaluation records.

This module is the first M1 layer of the next-stage benchmark.  It does not
decide whether an LLM explanation is correct; it binds that explanation and
the tool results to an immutable repository snapshot so larger real-project
evaluations cannot accidentally become a collection of untraceable runs.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Iterable


def _digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_digest(path: str | Path) -> str:
    return _digest_bytes(Path(path).read_bytes())


def repository_snapshot(root: str | Path, paths: Iterable[str | Path]) -> dict[str, Any]:
    """Hash an explicit set of files, rejecting paths outside *root*."""
    base = Path(root).resolve()
    entries = []
    for item in sorted((Path(path) for path in paths), key=lambda value: str(value)):
        path = item if item.is_absolute() else base / item
        resolved = path.resolve()
        try:
            relative = resolved.relative_to(base)
        except ValueError as error:
            raise ValueError(f"repository snapshot path escapes root: {path}") from error
        if not resolved.is_file():
            raise ValueError(f"repository snapshot file is missing: {path}")
        entries.append({"path": relative.as_posix(), "sha256": file_digest(resolved), "bytes": resolved.stat().st_size})
    body = {"root": str(base), "files": entries}
    body["snapshot_sha256"] = _digest_bytes(json.dumps(body, sort_keys=True, separators=(",", ":")).encode())
    return body


def validate_task_manifest(manifest: dict[str, Any]) -> None:
    """Validate the portable task contract before any tool is executed."""
    if not isinstance(manifest, dict) or manifest.get("schema_version") != "repository-scale-task-manifest-v1":
        raise ValueError("repository task manifest schema is unsupported")
    tasks = manifest.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("repository task manifest requires non-empty tasks")
    seen: set[str] = set()
    for task in tasks:
        if not isinstance(task, dict):
            raise ValueError("repository task must be an object")
        task_id = task.get("task_id")
        if not isinstance(task_id, str) or not task_id or task_id in seen:
            raise ValueError("repository task ids must be unique non-empty strings")
        seen.add(task_id)
        for key in ("source_files", "baseline_command", "repaired_command"):
            value = task.get(key)
            if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item for item in value):
                raise ValueError(f"repository task {task_id} requires a non-empty {key}")
        if task.get("baseline_expected") not in {"fail", "pass"} or task.get("repaired_expected") not in {"fail", "pass"}:
            raise ValueError(f"repository task {task_id} has invalid expected statuses")


@dataclass(frozen=True)
class RepositoryTaskResult:
    task_id: str
    baseline_status: str
    repaired_status: str
    source_unchanged: bool
    patch_files: tuple[str, ...]
    status: str
    claim_boundary: str = "native command outcomes and source-integrity checks; not proof of general correctness"

    def record(self) -> dict[str, Any]:
        body = {
            "schema_version": "repository-scale-task-result-v1",
            "task_id": self.task_id,
            "baseline_status": self.baseline_status,
            "repaired_status": self.repaired_status,
            "source_unchanged": self.source_unchanged,
            "patch_files": list(self.patch_files),
            "status": self.status,
            "claim_boundary": self.claim_boundary,
        }
        body["result_sha256"] = _digest_bytes(json.dumps(body, sort_keys=True, separators=(",", ":")).encode())
        return body


def evaluate_task_result(
    task: dict[str, Any],
    *,
    baseline_status: str,
    repaired_status: str,
    before: dict[str, Any],
    after: dict[str, Any],
    patch_files: Iterable[str],
    candidate: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Produce a fail-closed fail-to-pass result for one repository task."""
    task_id = str(task["task_id"])
    before_files = {item["path"]: item["sha256"] for item in before.get("files", [])}
    after_files = {item["path"]: item["sha256"] for item in after.get("files", [])}
    source_files = {str(Path(item).as_posix()) for item in task["source_files"]}
    source_unchanged = all(before_files.get(path) == after_files.get(path) for path in source_files)
    candidate_files = {item["path"]: item["sha256"] for item in (candidate or {}).get("files", [])}
    candidate_changed = bool(candidate) and any(before_files.get(path) != candidate_files.get(path) for path in source_files)
    patch_list = tuple(sorted(set(str(item) for item in patch_files)))
    unexpected = sorted(set(after_files) - set(before_files) - set(patch_list))
    baseline_ok = baseline_status == task["baseline_expected"]
    repaired_ok = repaired_status == task["repaired_expected"]
    passed = baseline_ok and repaired_ok and source_unchanged and candidate_changed and not unexpected and bool(patch_list)
    result = RepositoryTaskResult(task_id, baseline_status, repaired_status, source_unchanged, patch_list, "passed" if passed else "blocked").record()
    result["checks"] = {
        "baseline_expected": baseline_ok,
        "repaired_expected": repaired_ok,
        "source_unchanged": source_unchanged,
        "candidate_changed": candidate_changed,
        "unexpected_changed_files": unexpected,
        "patch_declared": bool(patch_list),
    }
    result["result_sha256"] = _digest_bytes(json.dumps({key: value for key, value in result.items() if key != "result_sha256"}, sort_keys=True, separators=(",", ":")).encode())
    return result


def run_repository_task(
    task: dict[str, Any],
    *,
    canonical_root: str | Path,
    baseline_root: str | Path,
    candidate_root: str | Path,
    output_root: str | Path,
    timeout_seconds: float = 300.0,
) -> dict[str, Any]:
    """Run one task's baseline and repaired-copy commands without a shell.

    The canonical checkout is never used as a command working directory.  A
    caller must provide isolated baseline and candidate roots, which is the
    same copy-only boundary used by the existing repair flow.
    """
    validate_task_manifest({"schema_version": "repository-scale-task-manifest-v1", "tasks": [task]})
    canonical = Path(canonical_root).resolve()
    baseline = Path(baseline_root).resolve()
    candidate = Path(candidate_root).resolve()
    output = Path(output_root).resolve()
    if not baseline.is_dir() or not candidate.is_dir() or not canonical.is_dir():
        raise ValueError("canonical, baseline, and candidate roots must be directories")
    before = repository_snapshot(canonical, task["source_files"])
    records: dict[str, Any] = {"task_id": task["task_id"], "source_snapshot_before": before}
    statuses: dict[str, str] = {}
    for label, command, cwd in (
        ("baseline", task["baseline_command"], baseline),
        ("repaired", task["repaired_command"], candidate),
    ):
        run_dir = output / label
        run_dir.mkdir(parents=True, exist_ok=True)
        try:
            completed = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=timeout_seconds, check=False)
            returncode = completed.returncode
            stdout, stderr = completed.stdout, completed.stderr
        except subprocess.TimeoutExpired as error:
            returncode = None
            stdout = error.stdout.decode() if isinstance(error.stdout, bytes) else (error.stdout or "")
            stderr = (error.stderr.decode() if isinstance(error.stderr, bytes) else (error.stderr or "")) + "\nTIMEOUT"
        (run_dir / "stdout.log").write_text(stdout, encoding="utf-8")
        (run_dir / "stderr.log").write_text(stderr, encoding="utf-8")
        statuses[label] = "pass" if returncode == 0 else "fail"
        records[f"{label}_run"] = {
            "command": list(command), "cwd": str(cwd), "returncode": returncode,
            "status": statuses[label],
            "stdout_sha256": _digest_bytes(stdout.encode()),
            "stderr_sha256": _digest_bytes(stderr.encode()),
            "stdout_path": str(run_dir / "stdout.log"),
            "stderr_path": str(run_dir / "stderr.log"),
        }
    after = repository_snapshot(canonical, task["source_files"])
    candidate_snapshot = repository_snapshot(candidate, task["source_files"])
    records["source_snapshot_after"] = after
    records["candidate_snapshot_after"] = candidate_snapshot
    result = evaluate_task_result(
        task, baseline_status=statuses["baseline"], repaired_status=statuses["repaired"],
        before=before, after=after, candidate=candidate_snapshot, patch_files=task.get("patch_files", []),
    )
    records["result"] = result
    records["status"] = result["status"]
    records["record_sha256"] = _digest_bytes(json.dumps(records, sort_keys=True, separators=(",", ":")).encode())
    output.mkdir(parents=True, exist_ok=True)
    (output / "task-result.json").write_text(json.dumps(records, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return records
