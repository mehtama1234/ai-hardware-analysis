"""Small synthesizable verification-model execution boundary."""

from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import re

from .ledger import sha256_file
from .runner import run_command


def run_synthesizable_checker(
    rtl_sources: list[str | Path],
    checker_source: str | Path,
    harness: str | Path,
    *,
    top: str,
    run_root: str | Path,
    source_revision: str,
    timeout_seconds: float = 60.0,
    pass_marker: str = "SVM_PASS",
    mismatch_marker: str = "SVM_MISMATCH",
    cycle_marker: str = "SVM_CYCLES",
) -> dict[str, object]:
    """Compile and run a synthesizable checker plus a deterministic harness.

    The checker is supplied as synthesizable SystemVerilog and is compiled
    together with the DUT.  The harness is the simulation-only top that drives
    inputs and emits ``pass_marker`` only after it has observed the checker's
    mismatch output remain clear.  This proves the software execution boundary
    and checker semantics; it does not prove FPGA timing, utilization, or
    system-level emulation.
    """
    if not rtl_sources or not top or not source_revision or not checker_source or not harness:
        raise ValueError("rtl_sources, checker_source, harness, top, and source_revision are required")
    sources = [Path(source).resolve() for source in rtl_sources]
    checker = Path(checker_source).resolve()
    harness_path = Path(harness).resolve()
    if any(not source.is_file() for source in sources) or not checker.is_file() or not harness_path.is_file():
        raise ValueError("all RTL, checker, and harness sources must exist")
    root = Path(run_root)
    (root / "compile").mkdir(parents=True, exist_ok=True)
    binary = root / "compile" / "svm.vvp"
    compile_run = run_command(
        ["iverilog", "-g2012", "-s", top, "-o", str(binary.resolve()), *[str(source) for source in sources], str(checker), str(harness_path)],
        tool="svm-iverilog-compile", run_root=root / "compile-run", source_revision=source_revision,
        timeout_seconds=timeout_seconds, run_id="svm-compile",
    )
    result: dict[str, object] = {
        "schema_version": "synthesizable-verification-model-v1",
        "status": "blocked",
        "top": top,
        "source_revision": source_revision,
        "rtl_sources": [{"path": str(source), "sha256": sha256_file(source)} for source in sources],
        "checker": {"path": str(checker), "sha256": sha256_file(checker)},
        "harness": {"path": str(harness_path), "sha256": sha256_file(harness_path)},
        "compile": asdict(compile_run),
        "simulation": None,
        "pass_marker": pass_marker,
        "mismatch_marker": mismatch_marker,
        "cycle_marker": cycle_marker,
        "claim_boundary": "synthesizable checker compile/run evidence only; no FPGA timing, utilization, or system-level emulation claim",
    }
    if compile_run.status != "passed" or not binary.is_file():
        result["blocked_reason"] = "SVM compile did not produce the expected executable"
    else:
        simulation_run = run_command(
            ["vvp", str(binary.resolve())], tool="svm-simulation", run_root=root / "simulation",
            source_revision=source_revision, timeout_seconds=timeout_seconds, run_id="svm-simulation",
        )
        stdout_path = root / "simulation" / "stdout.log"
        stdout = stdout_path.read_text(encoding="utf-8") if stdout_path.is_file() else ""
        result["simulation"] = asdict(simulation_run)
        result["pass_marker_present"] = pass_marker in stdout
        result["mismatch_marker_present"] = mismatch_marker in stdout
        result["mismatch_records"] = [
            {key: int(value) if key == "cycle" else value for key, value in match.groupdict().items() if value is not None}
            for match in re.finditer(
                rf"{re.escape(mismatch_marker)}(?:\s+cycle=(?P<cycle>\d+))?(?:\s+actual=(?P<actual>[^\s]+))?(?:\s+expected=(?P<expected>[^\s]+))?",
                stdout,
            )
        ]
        result["mismatch_count"] = len(result["mismatch_records"])
        cycle_match = re.search(rf"{re.escape(cycle_marker)}\s+cycles=(?P<cycles>\d+)", stdout)
        if cycle_match:
            cycles = int(cycle_match["cycles"])
            duration = float(simulation_run.metadata.get("duration_seconds", 0.0))
            result["performance"] = {
                "status": "measured", "cycles": cycles,
                "host_seconds": duration,
                "host_cycles_per_second": round(cycles / duration, 6) if duration > 0 else None,
                "claim_boundary": "host-observed simulated cycles only; not FPGA clock frequency or hardware throughput",
            }
        else:
            result["performance"] = {"status": "not_measured", "claim_boundary": "SVM harness did not emit a cycle-count marker"}
        if simulation_run.status == "passed" and result["pass_marker_present"] and not result["mismatch_marker_present"]:
            result["status"] = "passed"
        else:
            result["blocked_reason"] = "SVM harness did not produce a clean pass marker"
    result["result_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    root.mkdir(parents=True, exist_ok=True)
    (root / "svm-result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result
