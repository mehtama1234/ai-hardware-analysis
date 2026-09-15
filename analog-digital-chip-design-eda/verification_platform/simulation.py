"""Open-source event-driven simulation adapter."""
from __future__ import annotations
from pathlib import Path
from dataclasses import asdict
import hashlib
import json
import shutil
from .runner import ToolRun, run_command

def run_iverilog_vvp(*sources: str | Path, run_root: str | Path, source_revision: str, binary_name: str, tool_prefix: str, timeout_seconds: float = 180.0) -> tuple[ToolRun, ToolRun | None]:
    """Compile and run a source set, preserving both adapter runs and VCD evidence."""
    root = Path(run_root)
    binary = root / "compile" / binary_name
    compile_run = run_command(["iverilog", "-g2012", "-o", str(binary), *(str(Path(source)) for source in sources)], tool=f"iverilog-{tool_prefix}", run_root=root / "compile", source_revision=source_revision, expected_artifacts=[binary_name], run_id="compile", timeout_seconds=timeout_seconds)
    if compile_run.status != "passed":
        return compile_run, None
    sim_run = run_command(["vvp", str(binary)], tool=f"vvp-{tool_prefix}", run_root=root / "simulation", source_revision=source_revision, expected_artifacts=["waveform.vcd"], run_id="simulation", timeout_seconds=timeout_seconds)
    waveform = root / "simulation" / "waveform.vcd"
    if waveform.is_file():
        shutil.copyfile(waveform, root / "waveform.vcd")
    return compile_run, sim_run

def run_verilator_lint(*sources: str | Path, run_root: str | Path, source_revision: str, top: str) -> ToolRun:
    """Run Verilator's static front end without claiming simulation support."""
    return run_command(["verilator", "--lint-only", "--language", "1800-2012", "--top-module", top, *(str(Path(source).resolve()) for source in sources)], tool="verilator-lint", run_root=run_root, source_revision=source_revision, run_id="lint")


def probe_verilator_options(
    options: list[str],
    *,
    run_root: str | Path,
    source_revision: str,
    timeout_seconds: float = 15.0,
) -> dict[str, object]:
    """Probe optional Verilator flags without treating unsupported flags as passes."""
    if not options or any(not isinstance(option, str) or not option.startswith("-") for option in options):
        raise ValueError("options must contain at least one flag")
    run = run_command(["verilator", *options, "--version"], tool="verilator-option-probe", run_root=run_root, source_revision=source_revision, timeout_seconds=timeout_seconds, run_id="option-probe")
    result: dict[str, object] = {
        "schema_version": "verilator-option-probe-v1",
        "status": "available" if run.status == "passed" else "unsupported",
        "options": list(options),
        "tool_run": asdict(run),
        "source_revision": source_revision,
        "claim_boundary": "flag capability probe only; does not prove timing, coroutine, UVM, or simulation correctness",
    }
    result["result_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    Path(run_root).mkdir(parents=True, exist_ok=True)
    (Path(run_root) / "verilator-option-probe.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def probe_verilator_capability_matrix(
    sources: list[str | Path],
    *,
    top: str,
    options: list[str],
    run_root: str | Path,
    source_revision: str,
    timeout_seconds: float = 30.0,
) -> dict[str, object]:
    """Probe requested Verilator flags against a real RTL lint invocation."""
    if not sources or not top or not options or not source_revision:
        raise ValueError("sources, top, options, and source_revision are required")
    if any(not isinstance(option, str) or not option.startswith("-") for option in options):
        raise ValueError("options must contain only flag strings")
    paths = [Path(source).resolve() for source in sources]
    if any(not path.is_file() for path in paths):
        raise ValueError("all Verilator capability sources must exist")
    root = Path(run_root)
    probes: list[dict[str, object]] = []
    for index, option in enumerate(options):
        run = run_command(
            ["verilator", "--lint-only", "--language", "1800-2012", "--top-module", top, option, *[str(path) for path in paths]],
            tool="verilator-capability-probe", run_root=root / f"option-{index}", source_revision=source_revision,
            timeout_seconds=timeout_seconds, run_id=f"capability-{index}",
        )
        probes.append({"option": option, "status": "available" if run.status == "passed" else "unsupported", "tool_run": asdict(run)})
    available = [item["option"] for item in probes if item["status"] == "available"]
    unsupported = [item["option"] for item in probes if item["status"] == "unsupported"]
    result: dict[str, object] = {
        "schema_version": "verilator-capability-matrix-v1",
        "status": "passed" if not unsupported else "blocked",
        "top": top,
        "source_revision": source_revision,
        "sources": [{"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in paths],
        "probes": probes,
        "available_options": available,
        "unsupported_options": unsupported,
        "claim_boundary": "flag compatibility against the supplied RTL lint invocation only; does not prove timing, coroutine, UVM, or simulation correctness",
    }
    if unsupported:
        result["blocked_reason"] = "one or more requested Verilator flags are unsupported by the installed toolchain"
    result["result_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    root.mkdir(parents=True, exist_ok=True)
    (root / "verilator-capability-matrix.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result
