"""Formal-tool adapter primitives."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import re
from typing import Literal

from .ledger import ToolRun
from .runner import run_command
from .ledger import ProvenanceLedger
from .triage import Failure


def parse_yosys_sat_result(log: str) -> Literal["proven", "counterexample", "unknown"]:
    """Classify Yosys SAT output using its explicit terminal markers."""
    if "SAT proof finished - no model found" in log:
        return "proven"
    if "SAT proof finished - model found" in log or "FAIL!" in log:
        return "counterexample"
    return "unknown"


def parse_yosys_counterexample(log: str) -> list[dict[str, str | int]]:
    """Extract the compact ``sat -show`` model table from a failed proof.

    Yosys prints one row per time step.  The parser intentionally returns only
    scalar values and preserves the special ``init`` row; unsupported output is
    represented by an empty list rather than being mistaken for a proof.
    """
    if parse_yosys_sat_result(log) != "counterexample":
        return []
    rows: list[dict[str, str | int]] = []
    pattern = re.compile(r"^\s*(init|\d+)\s+\\?([^\s]+)\s+(-?\d+)\s+([0-9a-fA-FxXzZ]+)\s+([01xXzZ]+)\s*$")
    for line in log.splitlines():
        match = pattern.match(line)
        if not match:
            continue
        time_token, signal, decimal, _hex, binary = match.groups()
        rows.append({
            "time": time_token if time_token == "init" else int(time_token),
            "signal": signal,
            "decimal": int(decimal),
            "binary": binary,
        })
    return rows


def counterexample_to_failure(log: str, *, signal: str, expected_value: str) -> Failure | None:
    """Project the first violating shown value into the common failure schema."""
    if not signal or not expected_value:
        raise ValueError("signal and expected_value are required")
    try:
        expected = int(expected_value, 0)
    except ValueError as exc:
        raise ValueError("expected_value must be an integer literal") from exc
    for row in parse_yosys_counterexample(log):
        if row["signal"] != signal or row["time"] == "init":
            continue
        actual = int(row["decimal"])
        if actual != expected:
            return Failure(int(row["time"]), signal, str(expected), str(actual))
    return None


def yosys_syntax_check(
    rtl: str | Path,
    *,
    run_root: str | Path,
    top: str | None = None,
    source_revision: str = "unknown",
    timeout_seconds: float = 60.0,
) -> ToolRun:
    """Run Yosys parsing/elaboration and record it as a distinct formal-stage run."""
    command = ["yosys", "-p", f"read_verilog -sv {Path(rtl)}"]
    if top:
        command[-1] += f"; hierarchy -top {top}"
    return run_command(command, tool="yosys-formal-preflight", run_root=run_root, source_revision=source_revision, timeout_seconds=timeout_seconds)


def yosys_sat_prove(
    rtl: str | Path,
    *,
    top: str,
    signal: str,
    expected_value: str,
    run_root: str | Path,
    sequence: int = 3,
    source_revision: str = "unknown",
    timeout_seconds: float = 60.0,
) -> ToolRun:
    """Run a bounded SAT proof for a simple signal invariant."""
    if sequence < 1 or not top or not signal or not expected_value:
        raise ValueError("top, signal, expected_value, and positive sequence are required")
    script = f"read_verilog -sv {Path(rtl)}; prep -top {top}; sat -seq {sequence} -prove {signal} {expected_value} -show {signal}"
    run = run_command(["yosys", "-p", script], tool="yosys-sat", run_root=run_root, source_revision=source_revision, timeout_seconds=timeout_seconds)
    log_path = Path(run_root) / "stdout.log"
    proof_result = parse_yosys_sat_result(log_path.read_text(encoding="utf-8")) if log_path.is_file() else "unknown"
    run = replace(run, metadata={**run.metadata, "proof_result": proof_result})
    ProvenanceLedger(runs=[run]).write(Path(run_root) / "provenance-ledger.json")
    return run
