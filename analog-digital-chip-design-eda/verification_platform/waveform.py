"""Minimal VCD value extraction for evidence checks."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def signal_values(path: str | Path, signal: str) -> list[tuple[int, str]]:
    """Return ``(timestamp, value)`` pairs for the first VCD signal declaration."""
    text = Path(path).read_text(encoding="utf-8")
    identifier = None
    for line in text.splitlines():
        match = re.match(r"\$var\s+\S+\s+\d+\s+(\S+)\s+([^\s\[]+)", line)
        if match and match.group(2) == signal:
            identifier = match.group(1)
            break
    if identifier is None:
        raise ValueError(f"signal {signal!r} not found in VCD")
    timestamp = 0
    values: list[tuple[int, str]] = []
    for line in text.splitlines():
        if line.startswith("#"):
            timestamp = int(line[1:])
        elif line.endswith(identifier) and line.startswith("b"):
            values.append((timestamp, line[1:-len(identifier)].strip()))
        elif line.endswith(identifier) and line[:1] in "01xXzZ":
            values.append((timestamp, line[:1]))
    return values


def waveform_contains(path: str | Path, signal: str, value: str) -> bool:
    return any(observed == value for _, observed in signal_values(path, signal))


def assess_vacuity(path: str | Path, signal: str, trigger_value: str = "1") -> dict[str, Any]:
    """Report whether a waveform ever exercised an assertion trigger."""
    samples = signal_values(path, signal)
    occurrences = sum(value == trigger_value for _, value in samples)
    return {"signal": signal, "trigger_value": trigger_value, "occurrences": occurrences, "status": "active" if occurrences else "vacuous"}


def compare_traces(failing: str | Path, passing: str | Path, signal: str) -> dict[str, Any]:
    """Find the first timestamp where two traces differ for one signal."""
    left, right = signal_values(failing, signal), signal_values(passing, signal)
    for (left_time, left_value), (right_time, right_value) in zip(left, right):
        if left_value != right_value or left_time != right_time:
            return {"signal": signal, "status": "diverged", "failing": {"time": left_time, "value": left_value}, "passing": {"time": right_time, "value": right_value}}
    if len(left) != len(right):
        return {"signal": signal, "status": "length_mismatch", "failing_samples": len(left), "passing_samples": len(right)}
    return {"signal": signal, "status": "identical", "samples": len(left)}
