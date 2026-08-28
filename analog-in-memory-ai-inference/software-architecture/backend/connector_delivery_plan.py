CONNECTOR_DELIVERY_PLAN_SCHEMA_VERSION = "connector-delivery-plan-v0.1"


MILESTONE_RULES = [
    {
        "id": "M1",
        "name": "Unblock connector probes",
        "task_types": {"fix connection probe"},
        "goal": "Every build-first connector has deterministic probe output and no missing required configuration.",
    },
    {
        "id": "M2",
        "name": "Produce importable evidence",
        "task_types": {"produce importable evidence", "run connector and import evidence"},
        "goal": "Each connector can emit its normalized artifact with raw references and provenance.",
    },
    {
        "id": "M3",
        "name": "Harden validation behavior",
        "task_types": {"add negative validation test"},
        "goal": "Incomplete payloads fail validation before import, so bad connector output cannot upgrade claims.",
    },
    {
        "id": "M4",
        "name": "Run failure-safety drills",
        "task_types": {"run failure-safety drill"},
        "goal": "Failed connector runs leave claims blocked or needs review and keep raw logs for audit.",
    },
]


def _tasks_for_rule(tasks, rule):
    task_types = rule["task_types"]
    return [task for task in tasks if task.get("task_type") in task_types]


def _owners(tasks):
    owners = []
    for task in tasks:
        owner = task.get("owner")
        if owner and owner not in owners:
            owners.append(owner)
    return owners


def _milestone(rule, tasks):
    selected = _tasks_for_rule(tasks, rule)
    return {
        "id": rule["id"],
        "name": rule["name"],
        "goal": rule["goal"],
        "status": "not started" if selected else "no open tasks",
        "task_count": len(selected),
        "owners": _owners(selected),
        "task_ids": [task.get("id") for task in selected],
        "done_when": [
            "All listed backlog tasks are closed by new probe, evidence, validation, import, or failure-drill results.",
            "The connector acceptance report is regenerated and no longer shows those cases as blocked or pending.",
            "Claim readiness is refreshed after imports; claim language changes only from claim readiness.",
        ],
    }


def build_connector_delivery_plan(connector_backlog, package_report=None):
    tasks = (connector_backlog or {}).get("tasks", [])
    milestones = [_milestone(rule, tasks) for rule in MILESTONE_RULES]
    open_milestones = [item for item in milestones if item["task_count"]]
    return {
        "result_type": "connector_delivery_plan",
        "schema_version": CONNECTOR_DELIVERY_PLAN_SCHEMA_VERSION,
        "provenance": "derived from connector backlog",
        "confidence": "medium" if tasks else "low",
        "package_id": (package_report or {}).get("package_id") or (connector_backlog or {}).get("package_id"),
        "summary": {
            "total_milestones": len(milestones),
            "open_milestones": len(open_milestones),
            "total_tasks": len(tasks),
            "first_open_milestone": open_milestones[0]["name"] if open_milestones else "none",
            "plain_reading": "This delivery plan groups connector backlog tasks into the order a team should execute them.",
        },
        "milestones": milestones,
        "handoff_order": [
            "Unblock probes before running expensive tools.",
            "Produce normalized artifacts before discussing measured claims.",
            "Prove validation rejects broken payloads before broad import use.",
            "Run failure drills before treating connector output as an accepted integration path.",
        ],
        "delivery_rule": "The delivery plan coordinates work. It is not evidence and cannot upgrade claims by itself.",
    }
