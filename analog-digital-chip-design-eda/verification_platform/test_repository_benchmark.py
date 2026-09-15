from pathlib import Path
import json
import subprocess
import sys

import pytest

from .repository_benchmark import evaluate_task_result, repository_snapshot, run_repository_task, validate_task_manifest


def _manifest():
    return {
        "schema_version": "repository-scale-task-manifest-v1",
        "tasks": [{
            "task_id": "counter-hold",
            "source_files": ["rtl/counter.sv"],
            "baseline_command": ["run", "baseline"],
            "repaired_command": ["run", "repaired"],
            "baseline_expected": "fail",
            "repaired_expected": "pass",
        }],
    }


def test_manifest_and_snapshot_are_structured(tmp_path: Path):
    source = tmp_path / "rtl" / "counter.sv"
    source.parent.mkdir()
    source.write_text("assign q = d;\n", encoding="utf-8")
    validate_task_manifest(_manifest())
    snapshot = repository_snapshot(tmp_path, ["rtl/counter.sv"])
    assert snapshot["files"][0]["path"] == "rtl/counter.sv"
    assert len(snapshot["snapshot_sha256"]) == 64


def test_snapshot_rejects_escape(tmp_path: Path):
    with pytest.raises(ValueError, match="escapes root"):
        repository_snapshot(tmp_path, [Path("/etc/hosts")])


def test_fail_to_pass_result_requires_integrity_and_declared_patch():
    task = _manifest()["tasks"][0]
    before = {"files": [{"path": "rtl/counter.sv", "sha256": "old"}]}
    after = {"files": [{"path": "rtl/counter.sv", "sha256": "old"}]}
    candidate = {"files": [{"path": "rtl/counter.sv", "sha256": "new"}]}
    result = evaluate_task_result(task, baseline_status="fail", repaired_status="pass", before=before, after=after, candidate=candidate, patch_files=["rtl/counter.sv"])
    assert result["status"] == "passed"
    assert result["checks"]["source_unchanged"] is True


def test_unexpected_change_blocks_result():
    task = _manifest()["tasks"][0]
    before = {"files": [{"path": "rtl/counter.sv", "sha256": "old"}]}
    after = {"files": [{"path": "rtl/counter.sv", "sha256": "new"}]}
    result = evaluate_task_result(task, baseline_status="fail", repaired_status="pass", before=before, after=after, patch_files=["work/counter.sv"])
    assert result["status"] == "blocked"
    assert result["checks"]["source_unchanged"] is False


def test_runner_executes_isolated_baseline_and_candidate(tmp_path: Path):
    canonical = tmp_path / "canonical"
    baseline = tmp_path / "baseline"
    candidate = tmp_path / "candidate"
    for root in (canonical, baseline):
        (root / "rtl").mkdir(parents=True)
        (root / "rtl" / "counter.sv").write_text("assign q = d;\n", encoding="utf-8")
    (candidate / "rtl").mkdir(parents=True)
    (candidate / "rtl" / "counter.sv").write_text("assign q = d + 1;\n", encoding="utf-8")
    task = {
        **_manifest()["tasks"][0],
        "baseline_command": ["python3", "-c", "import sys; sys.exit(1)"],
        "repaired_command": ["python3", "-c", "print('PASS')"],
        "patch_files": ["rtl/counter.sv"],
    }
    result = run_repository_task(task, canonical_root=canonical, baseline_root=baseline, candidate_root=candidate, output_root=tmp_path / "out")
    assert result["status"] == "passed"
    assert result["result"]["source_unchanged"] is True
    assert (tmp_path / "out" / "baseline" / "stderr.log").is_file()


def test_repository_scale_cli_writes_report(tmp_path: Path):
    roots = {}
    for name in ("canonical", "baseline"):
        roots[name] = tmp_path / name
        (roots[name] / "rtl").mkdir(parents=True)
        (roots[name] / "rtl" / "counter.sv").write_text("assign q = d;\n", encoding="utf-8")
    roots["candidate"] = tmp_path / "candidate"
    (roots["candidate"] / "rtl").mkdir(parents=True)
    (roots["candidate"] / "rtl" / "counter.sv").write_text("assign q = d + 1;\n", encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(_manifest() | {"tasks": [{**_manifest()["tasks"][0], "patch_files": ["rtl/counter.sv"], "baseline_command": [sys.executable, "-c", "import sys; sys.exit(1)"], "repaired_command": [sys.executable, "-c", "pass"]}]}), encoding="utf-8")
    output = tmp_path / "report"
    result = subprocess.run([
        sys.executable, "scripts/run_repository_scale_benchmark.py", "--manifest", str(manifest),
        "--canonical-root", str(roots["canonical"]), "--baseline-root", str(roots["baseline"]),
        "--candidate-root", str(roots["candidate"]), "--output", str(output),
    ], capture_output=True, text=True, check=False)
    assert result.returncode == 0
    assert json.loads((output / "benchmark-report.json").read_text())["status"] == "passed"


def test_seeded_repository_manifest_is_valid():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "benchmarks/repository_scale/seeded_counter_task.json").read_text(encoding="utf-8"))
    validate_task_manifest(manifest)
