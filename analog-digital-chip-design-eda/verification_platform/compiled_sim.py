"""Compiled Verilator simulation with explicit runtime evidence."""

from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
from pathlib import Path

from .ledger import ToolRun, sha256_file
from .runner import run_command


def run_verilator_compiled_simulation(
    rtl_sources: list[str | Path],
    harness: str | Path,
    *,
    top: str,
    run_root: str | Path,
    source_revision: str,
    timeout_seconds: float = 120.0,
) -> dict[str, object]:
    """Compile RTL plus a C++ harness with Verilator and execute the binary.

    The harness owns the test oracle and must emit ``VERILATOR_SMOKE_PASS``.
    A successful C++ build alone is never reported as a simulation pass.
    """
    if not rtl_sources or not top or not source_revision:
        raise ValueError("rtl_sources, top, and source_revision are required")
    harness_path = Path(harness).resolve()
    sources = [Path(source).resolve() for source in rtl_sources]
    if not harness_path.is_file() or any(not source.is_file() for source in sources):
        raise ValueError("all RTL and harness sources must exist")
    root = Path(run_root)
    obj_dir = root / "obj_dir"
    binary = obj_dir / "verilator_smoke"
    compile_run = run_command(
        ["verilator", "--cc", "--exe", "--build", "--language", "1800-2012", "--top-module", top,
         "--Mdir", str(obj_dir.resolve()), "-o", binary.name, *[str(source) for source in sources], str(harness_path)],
        tool="verilator-compiled-build", run_root=root / "compile", source_revision=source_revision,
        timeout_seconds=timeout_seconds, run_id="verilator-build",
    )
    result: dict[str, object] = {
        "schema_version": "verilator-compiled-simulation-v1",
        "status": "blocked",
        "top": top,
        "source_revision": source_revision,
        "sources": [{"path": str(source), "sha256": sha256_file(source)} for source in sources],
        "harness": {"path": str(harness_path), "sha256": sha256_file(harness_path)},
        "compile": asdict(compile_run),
        "simulation": None,
        "claim_boundary": "compiled block-level Verilator smoke evidence only; not UVM compatibility, performance qualification, or system-level emulation",
    }
    if compile_run.status != "passed" or not binary.is_file():
        result["blocked_reason"] = "Verilator build did not produce the expected executable"
    else:
        simulation_run = run_command(
            [str(binary.resolve())], tool="verilator-compiled-simulation", run_root=root / "simulation",
            source_revision=source_revision, timeout_seconds=timeout_seconds, run_id="verilator-simulation",
        )
        stdout_path = root / "simulation" / "stdout.log"
        stdout = stdout_path.read_text(encoding="utf-8") if stdout_path.is_file() else ""
        result["simulation"] = asdict(simulation_run)
        result["pass_marker_present"] = "VERILATOR_SMOKE_PASS" in stdout
        if simulation_run.status == "passed" and result["pass_marker_present"]:
            result["status"] = "passed"
        else:
            result["blocked_reason"] = "compiled simulation did not emit VERILATOR_SMOKE_PASS"
    result["result_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    root.mkdir(parents=True, exist_ok=True)
    (root / "compiled-simulation-result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result
