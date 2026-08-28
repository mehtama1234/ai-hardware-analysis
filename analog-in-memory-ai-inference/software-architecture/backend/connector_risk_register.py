CONNECTOR_RISK_REGISTER_SCHEMA_VERSION = "connector-risk-register-v0.1"


RISK_RULES = [
    {
        "id": "CR-1",
        "milestone_id": "M1",
        "risk": "Connector looks available but required configuration is missing.",
        "impact": "The team may schedule evidence runs before the tool path can actually run.",
        "severity": "high",
        "trigger": "Open probe-unblock tasks remain.",
        "mitigation": "Close probe tasks first and rerun the connector acceptance report.",
    },
    {
        "id": "CR-2",
        "milestone_id": "M2",
        "risk": "Raw tool output exists but no normalized evidence artifact is importable.",
        "impact": "Claims remain blocked even though the lab may have useful logs.",
        "severity": "high",
        "trigger": "Evidence-production tasks remain.",
        "mitigation": "Map raw outputs into the normalized artifact schema and validate before import.",
    },
    {
        "id": "CR-3",
        "milestone_id": "M3",
        "risk": "Validation accepts incomplete or malformed connector payloads.",
        "impact": "Bad evidence can move claim readiness in the wrong direction.",
        "severity": "high",
        "trigger": "Negative validation tasks remain.",
        "mitigation": "Add missing-field and malformed-payload tests for every connector artifact.",
    },
    {
        "id": "CR-4",
        "milestone_id": "M4",
        "risk": "Failed connector runs are not handled safely.",
        "impact": "Partial evidence may be imported or interpreted as successful evidence.",
        "severity": "medium",
        "trigger": "Failure-safety drill tasks remain.",
        "mitigation": "Run failure drills and verify failed runs leave claims blocked or needs review.",
    },
]


def _milestones_by_id(connector_delivery_plan):
    return {
        item.get("id"): item
        for item in (connector_delivery_plan or {}).get("milestones", [])
        if item.get("id")
    }


def _risk_status(milestone):
    if not milestone:
        return "not evaluated"
    if int(milestone.get("task_count") or 0) > 0:
        return "open"
    return "controlled"


def build_connector_risk_register(connector_delivery_plan, package_report=None):
    milestones = _milestones_by_id(connector_delivery_plan)
    risks = []
    for rule in RISK_RULES:
        milestone = milestones.get(rule["milestone_id"], {})
        risks.append({
            **rule,
            "status": _risk_status(milestone),
            "open_task_count": int(milestone.get("task_count") or 0),
            "owners": milestone.get("owners", []),
            "task_ids": milestone.get("task_ids", []),
            "evidence_needed": "Regenerate connector acceptance, claim readiness, and evidence audit after closing the related tasks.",
        })
    open_risks = [item for item in risks if item["status"] == "open"]
    high_open = [item for item in open_risks if item["severity"] == "high"]
    return {
        "result_type": "connector_risk_register",
        "schema_version": CONNECTOR_RISK_REGISTER_SCHEMA_VERSION,
        "provenance": "derived from connector delivery plan",
        "confidence": "medium" if risks else "low",
        "package_id": (package_report or {}).get("package_id") or (connector_delivery_plan or {}).get("package_id"),
        "summary": {
            "total_risks": len(risks),
            "open_risks": len(open_risks),
            "high_open_risks": len(high_open),
            "controlled_risks": sum(1 for item in risks if item["status"] == "controlled"),
            "plain_reading": "This risk register shows what can break the connector delivery path before evidence can safely affect claims.",
        },
        "risks": risks,
        "risk_rule": "A controlled risk is not evidence. Claims still move only from validated, imported, archived evidence.",
    }
