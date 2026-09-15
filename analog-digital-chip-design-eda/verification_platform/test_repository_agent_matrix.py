import json
from pathlib import Path


def test_seeded_repository_agent_matrix_is_current_and_unambiguous():
    root = Path(__file__).resolve().parents[1]
    plan = json.loads((root / "benchmarks/repository_scale/seeded_repository_agent_matrix.json").read_text(encoding="utf-8"))
    tasks = plan["tasks"]
    assert len(tasks) == 8
    assert len({task["task_id"] for task in tasks}) == len(tasks)
    for task in tasks:
        source = root / task["source"]
        text = source.read_text(encoding="utf-8")
        assert text.count(task["repair_before"]) == 1
        assert task["repair_before"] != task["repair_after"]
