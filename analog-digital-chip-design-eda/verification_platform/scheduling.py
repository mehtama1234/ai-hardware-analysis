"""Static guardrails for time-zero and cooperative-scheduling hazards."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Iterable

from .runner import run_command


@dataclass(frozen=True)
class SchedulingFinding:
    path: str
    line: int
    rule_id: str
    severity: str
    message: str


RULES = (
    ("TIMEZERO-DYNAMIC-NEW", re.compile(r"\binitial\b.*\bnew\s*\(", re.I), "error", "dynamic construction in an unsequenced initial block can race time-zero registration"),
    ("TIMEZERO-CONSTRUCTOR-DELAY", re.compile(r"\bfunction\s+(?:automatic\s+)?new\b[\s\S]*?#\s*0", re.I), "error", "constructor contains a #0 delay"),
    ("TIMEZERO-OBJECTION-DELAY", re.compile(r"\b(drop_objection|raise_objection)\s*\(", re.I), "warning", "objection handling requires an explicit phase/timing review"),
)


def lint_time_zero(paths: Iterable[str | Path], *, root: str | Path | None = None) -> dict[str, object]:
    """Scan verification sources and return findings without executing them."""
    paths = list(paths)
    root_path = Path(root).resolve() if root is not None else None
    findings: list[SchedulingFinding] = []
    for raw_path in paths:
        path = Path(raw_path)
        text = path.read_text(encoding="utf-8")
        relative = path.resolve().relative_to(root_path).as_posix() if root_path is not None else path.as_posix()
        lines = text.splitlines()
        for rule_id, pattern, severity, message in RULES:
            if rule_id == "TIMEZERO-CONSTRUCTOR-DELAY":
                for match in pattern.finditer(text):
                    line = text[:match.start()].count("\n") + 1
                    findings.append(SchedulingFinding(relative, line, rule_id, severity, message))
                continue
            if rule_id == "TIMEZERO-OBJECTION-DELAY":
                for match in pattern.finditer(text):
                    findings.append(SchedulingFinding(relative, text[:match.start()].count("\n") + 1, rule_id, severity, message))
            else:
                for line_number, line in enumerate(lines, 1):
                    if pattern.search(line):
                        findings.append(SchedulingFinding(relative, line_number, rule_id, severity, message))
    findings.sort(key=lambda item: (item.path, item.line, item.rule_id))
    payload: dict[str, object] = {
        "schema_version": "time-zero-lint-v1",
        "status": "blocked" if any(item.severity == "error" for item in findings) else "passed",
        "files": sorted({str(Path(raw).resolve().relative_to(root_path).as_posix()) if root_path is not None else str(Path(raw)) for raw in paths}),
        "findings": [asdict(item) for item in findings],
    }
    payload["report_sha256"] = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return payload


def write_time_zero_lint(path: str | Path, report: dict[str, object]) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def run_scheduling_gate(
    paths: Iterable[str | Path],
    *,
    run_root: str | Path,
    source_revision: str,
    timeout_seconds: float = 30.0,
) -> dict[str, object]:
    """Lint time-zero hazards before invoking the open-source compiler."""
    paths = list(paths)
    lint = lint_time_zero(paths)
    result: dict[str, object] = {
        "schema_version": "time-zero-gate-v1",
        "lint": lint,
        "status": "blocked" if lint["status"] == "blocked" else "unknown",
        "compiler": None,
    }
    if lint["status"] == "blocked":
        result["blocked_reason"] = "time-zero lint errors must be reviewed before compilation"
    else:
        command = ["iverilog", "-g2012", "-t", "null", *[str(Path(path).resolve()) for path in paths]]
        run = run_command(command, tool="time-zero-gate-iverilog", run_root=run_root, source_revision=source_revision, timeout_seconds=timeout_seconds, run_id="time-zero-gate")
        result["compiler"] = asdict(run)
        result["status"] = "passed" if run.status == "passed" else "blocked"
        if run.status != "passed":
            result["blocked_reason"] = "time-zero-clean source did not compile"
    result["gate_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return result


def run_time_zero_regression(
    source: str | Path,
    *,
    run_root: str | Path,
    source_revision: str,
    timeout_seconds: float = 30.0,
    pass_marker: str = "TIMEZERO_REGRESSION_PASS",
    stimulus_marker: str = "TIMEZERO_STIMULUS",
    premature_marker: str = "TIMEZERO_PREMATURE_TERMINATION",
) -> dict[str, object]:
    """Execute a scheduling fixture and classify its terminal behavior."""
    source = Path(source)
    lint = lint_time_zero([source])
    result: dict[str, object] = {"schema_version": "time-zero-runtime-regression-v1", "source": str(source), "lint": lint, "status": "blocked", "outcome": "formal_or_test_failure", "compile": None, "simulation": None}
    if lint["status"] == "blocked":
        result["blocked_reason"] = "time-zero lint errors prevent regression execution"
    else:
        root = Path(run_root)
        compile_run = run_command(["iverilog", "-g2012", "-o", "sim.vvp", str(source.resolve())], tool="time-zero-regression-compile", run_root=root / "compile", source_revision=source_revision, timeout_seconds=timeout_seconds, expected_artifacts=["sim.vvp"], run_id="compile")
        result["compile"] = asdict(compile_run)
        if compile_run.status == "passed":
            simulation_run = run_command(["vvp", str((root / "compile" / "sim.vvp").resolve())], tool="time-zero-regression-simulation", run_root=root / "simulation", source_revision=source_revision, timeout_seconds=timeout_seconds, run_id="simulation")
            result["simulation"] = asdict(simulation_run)
            stdout = (root / "simulation" / "stdout.log").read_text(encoding="utf-8") if (root / "simulation" / "stdout.log").is_file() else ""
            stderr_path = root / "simulation" / "stderr.log"
            stderr = stderr_path.read_text(encoding="utf-8") if stderr_path.is_file() else ""
            result["markers"] = {
                "pass": pass_marker in stdout,
                "stimulus": stimulus_marker in stdout,
                "premature_termination": premature_marker in stdout or "OBJTN_CLEAR" in stdout + stderr,
            }
            if simulation_run.status == "blocked" and "TIMEOUT" in stderr:
                result["outcome"] = "timeout_or_deadlock"
                result["blocked_reason"] = "simulation exceeded its bounded runtime"
            elif result["markers"]["premature_termination"]:
                result["outcome"] = "premature_time_zero_termination"
                result["blocked_reason"] = "simulation terminated before the expected scheduling milestone"
            elif simulation_run.status == "passed" and result["markers"]["pass"]:
                result["status"] = "passed"
                result["outcome"] = "normal_completion"
            elif simulation_run.status == "passed" and not result["markers"]["stimulus"]:
                result["outcome"] = "missing_stimulus"
                result["blocked_reason"] = "simulation completed without the expected stimulus marker"
            else:
                result["outcome"] = "formal_or_test_failure"
                result["blocked_reason"] = "simulation exited without the required pass marker"
        else:
            result["outcome"] = "formal_or_test_failure"
            result["blocked_reason"] = "time-zero regression fixture did not compile"
    result["regression_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return result
