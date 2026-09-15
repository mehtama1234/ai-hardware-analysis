from pathlib import Path

from verification_platform.compiled_sim import run_verilator_compiled_simulation


def test_verilator_compiled_smoke_passes_reference_rtl(tmp_path: Path):
    root = Path(__file__).parents[1]
    result = run_verilator_compiled_simulation(
        [root / "benchmarks/seeded_counter/counter_reference.sv"],
        root / "benchmarks/seeded_counter/verilator_smoke.cpp",
        top="counter", run_root=tmp_path / "reference", source_revision="reference-v1",
    )
    assert result["status"] == "passed"
    assert result["pass_marker_present"] is True
    assert result["simulation"]["status"] == "passed"


def test_verilator_compiled_smoke_blocks_seeded_bug(tmp_path: Path):
    root = Path(__file__).parents[1]
    result = run_verilator_compiled_simulation(
        [root / "benchmarks/seeded_counter/counter.sv"],
        root / "benchmarks/seeded_counter/verilator_smoke.cpp",
        top="counter", run_root=tmp_path / "bug", source_revision="bug-v1",
    )
    assert result["status"] == "blocked"
    assert result["pass_marker_present"] is False
    assert result["simulation"]["status"] == "failed"
