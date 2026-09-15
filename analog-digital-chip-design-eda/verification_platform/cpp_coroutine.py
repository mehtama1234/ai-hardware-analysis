"""Bounded C++20 coroutine capability probe."""

from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
from pathlib import Path

from .ledger import sha256_file
from .runner import run_command


def run_cpp_coroutine_probe(
    source: str | Path,
    *,
    run_root: str | Path,
    source_revision: str,
    timeout_seconds: float = 30.0,
    pass_marker: str = "CPP_COROUTINE_PASS",
    required_markers: tuple[str, ...] | None = None,
) -> dict[str, object]:
    """Compile and run a real C++20 coroutine fixture with bounded evidence."""
    if not source_revision:
        raise ValueError("source_revision is required")
    required = tuple(dict.fromkeys(required_markers or (pass_marker,)))
    if not required or any(not marker for marker in required):
        raise ValueError("required_markers must contain non-empty markers")
    source_path = Path(source).resolve()
    if not source_path.is_file():
        raise ValueError("coroutine probe source must exist")
    root = Path(run_root)
    binary = root / "compile" / "coroutine-probe"
    binary.parent.mkdir(parents=True, exist_ok=True)
    compile_run = run_command(
        ["g++", "-std=c++20", "-fcoroutines", str(source_path), "-o", str(binary.resolve())],
        tool="cpp20-coroutine-compile", run_root=root / "compile-run", source_revision=source_revision,
        timeout_seconds=timeout_seconds, run_id="cpp20-coroutine-compile",
    )
    result: dict[str, object] = {
        "schema_version": "cpp20-coroutine-probe-v1",
        "status": "blocked",
        "source_revision": source_revision,
        "source": {"path": str(source_path), "sha256": sha256_file(source_path)},
        "compiler": "g++",
        "compile_flags": ["-std=c++20", "-fcoroutines"],
        "compile": asdict(compile_run),
        "simulation": None,
        "pass_marker": pass_marker,
        "required_markers": list(required),
        "claim_boundary": "C++20 coroutine compiler/runtime capability only; not Verilator timing, UVM compatibility, or simulation performance",
    }
    if compile_run.status != "passed" or not binary.is_file():
        result["blocked_reason"] = "C++20 coroutine probe did not compile"
    else:
        simulation_run = run_command(
            [str(binary.resolve())], tool="cpp20-coroutine-run", run_root=root / "simulation",
            source_revision=source_revision, timeout_seconds=timeout_seconds, run_id="cpp20-coroutine-run",
        )
        stdout_path = root / "simulation" / "stdout.log"
        stdout = stdout_path.read_text(encoding="utf-8") if stdout_path.is_file() else ""
        result["simulation"] = asdict(simulation_run)
        result["pass_marker_present"] = pass_marker in stdout
        missing = [marker for marker in required if marker not in stdout]
        result["required_markers_present"] = not missing
        result["missing_markers"] = missing
        if simulation_run.status == "passed" and not missing:
            result["status"] = "passed"
        else:
            result["blocked_reason"] = "C++20 coroutine executable did not emit all required scheduling markers"
    result["result_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    root.mkdir(parents=True, exist_ok=True)
    (root / "cpp-coroutine-result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result
