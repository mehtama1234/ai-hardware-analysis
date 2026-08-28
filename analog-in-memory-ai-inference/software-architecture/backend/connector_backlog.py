CONNECTOR_BACKLOG_SCHEMA_VERSION = "connector-backlog-v0.1"


OWNER_BY_ADAPTER = {
    "accuracy.local-task-check": "accuracy engineer",
    "compiler.tvm-mlir-iree": "compiler engineer",
    "board.runtime": "runtime engineer",
    "metrics.power-thermal": "lab measurement engineer",
    "analog.error-simulator": "analog modeling engineer",
    "quantization.onnxruntime": "quantization engineer",
}


def _priority(connector):
    status = connector.get("acceptance_status")
    if status == "blocked":
        return 1
    if status == "pending":
        return 2
    if status == "needs failure drill":
        return 3
    return 9


def _task_type(case):
    kind = case.get("kind")
    status = case.get("status")
    if status == "blocked" and kind == "probe":
        return "fix connection probe"
    if status == "blocked":
        return "produce importable evidence"
    if status == "pending evidence":
        return "run connector and import evidence"
    if status == "pending explicit negative test":
        return "add negative validation test"
    if status == "covered by rule, needs failure drill":
        return "run failure-safety drill"
    return "verify connector"


def _task(connector, case, index):
    adapter_id = connector.get("adapter_id")
    task_type = _task_type(case)
    return {
        "id": f"CB-{adapter_id.replace('.', '-').replace('_', '-')}-{index}",
        "adapter_id": adapter_id,
        "name": connector.get("name"),
        "owner": OWNER_BY_ADAPTER.get(adapter_id, "integration lead"),
        "priority": _priority(connector),
        "task_type": task_type,
        "acceptance_status": connector.get("acceptance_status"),
        "test_case": case.get("name"),
        "command": case.get("command"),
        "why": case.get("failure_means") or "Connector acceptance is incomplete.",
        "done_when": [
            case.get("expected"),
            "The connector acceptance report no longer shows this case as blocked or pending.",
            "Raw logs, tool version, target settings, and provenance are kept with the evidence package.",
        ],
        "claim_rule": "Do not update claims from this backlog task. Update claims only after evidence validates, imports, archives, and claim readiness changes.",
    }


def build_connector_backlog(connector_acceptance_report, package_report=None):
    tasks = []
    for connector in (connector_acceptance_report or {}).get("connectors", []):
        if connector.get("acceptance_status") == "accepted":
            continue
        actionable_cases = [
            case
            for case in connector.get("case_results", [])
            if case.get("status") != "passed" and case.get("status") != "informational"
        ]
        for index, case in enumerate(actionable_cases, start=1):
            tasks.append(_task(connector, case, index))
    tasks = sorted(tasks, key=lambda item: (item["priority"], item["adapter_id"], item["id"]))
    return {
        "result_type": "connector_backlog",
        "schema_version": CONNECTOR_BACKLOG_SCHEMA_VERSION,
        "provenance": "derived from connector acceptance report",
        "confidence": "medium" if tasks else "low",
        "package_id": (package_report or {}).get("package_id") or (connector_acceptance_report or {}).get("package_id"),
        "summary": {
            "total_tasks": len(tasks),
            "priority_1": sum(1 for item in tasks if item["priority"] == 1),
            "priority_2": sum(1 for item in tasks if item["priority"] == 2),
            "priority_3": sum(1 for item in tasks if item["priority"] == 3),
            "plain_reading": "This backlog turns connector acceptance gaps into owner-facing work. It is a task list, not evidence.",
        },
        "tasks": tasks,
        "backlog_rule": "Close a connector backlog task only when the acceptance report changes because real evidence, probes, or failure drills changed.",
    }
