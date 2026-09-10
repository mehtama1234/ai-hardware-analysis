from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.uvm import generate_uvm_agent


def test_uvm_scaffold_contains_interface_and_traceable_components():
    source = generate_uvm_agent("CounterAgent", ["enable", "counter_q"])
    assert "interface counteragent_if" in source
    assert "counteragent_transaction" in source
    assert "counteragent_agent" in source
    assert "counteragent_driver" in source
    assert "counteragent_monitor" in source
    assert "counteragent_scoreboard" in source
    assert "counteragent_env" in source
    assert source.index("counteragent_driver") < source.index("counteragent_scoreboard") < source.index("counteragent_env")


def test_uvm_scaffold_rejects_empty_signal_list():
    try:
        generate_uvm_agent("CounterAgent", [])
    except ValueError as exc:
        assert "at least one" in str(exc)
    else:
        raise AssertionError("empty UVM interfaces must be rejected")
