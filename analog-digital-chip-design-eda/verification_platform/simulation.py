"""Open-source event-driven simulation adapter."""
from __future__ import annotations
from pathlib import Path
import shutil
from .runner import ToolRun, run_command

def run_iverilog_vvp(*sources: str | Path, run_root: str | Path, source_revision: str, binary_name: str, tool_prefix: str) -> tuple[ToolRun, ToolRun | None]:
    """Compile and run a source set, preserving both adapter runs and VCD evidence."""
    root = Path(run_root)
    binary = root / "compile" / binary_name
    compile_run = run_command(["iverilog", "-g2012", "-o", str(binary), *(str(Path(source)) for source in sources)], tool=f"iverilog-{tool_prefix}", run_root=root / "compile", source_revision=source_revision, expected_artifacts=[binary_name], run_id="compile")
    if compile_run.status != "passed":
        return compile_run, None
    sim_run = run_command(["vvp", str(binary)], tool=f"vvp-{tool_prefix}", run_root=root / "simulation", source_revision=source_revision, expected_artifacts=["waveform.vcd"], run_id="simulation")
    waveform = root / "simulation" / "waveform.vcd"
    if waveform.is_file():
        shutil.copyfile(waveform, root / "waveform.vcd")
    return compile_run, sim_run

def run_verilator_lint(*sources: str | Path, run_root: str | Path, source_revision: str, top: str) -> ToolRun:
    """Run Verilator's static front end without claiming simulation support."""
    return run_command(["verilator", "--lint-only", "--language", "1800-2012", "--top-module", top, *(str(Path(source)) for source in sources)], tool="verilator-lint", run_root=run_root, source_revision=source_revision, run_id="lint")
