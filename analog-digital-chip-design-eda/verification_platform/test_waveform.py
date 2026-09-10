from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.waveform import assess_vacuity, compare_traces, signal_values, waveform_contains


def test_vcd_values_are_extracted(tmp_path):
    path = tmp_path / "trace.vcd"
    path.write_text("$var wire 1 ! flag $end\n$enddefinitions $end\n#0\n0!\n#5\n1!\n", encoding="utf-8")
    assert signal_values(path, "flag") == [(0, "0"), (5, "1")]
    assert waveform_contains(path, "flag", "1")
    assert assess_vacuity(path, "flag", "1")["status"] == "active"
    assert assess_vacuity(path, "flag", "x")["status"] == "vacuous"
    passing = tmp_path / "passing.vcd"
    passing.write_text("$var wire 1 ! flag $end\n$enddefinitions $end\n#0\n0!\n#5\n0!\n", encoding="utf-8")
    comparison = compare_traces(path, passing, "flag")
    assert comparison["status"] == "diverged" and comparison["failing"]["time"] == 5
