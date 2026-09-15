#!/usr/bin/env python3
"""Deterministic local backend fixture for exercising the LLM contract."""
from __future__ import annotations
import json
import sys

for line in sys.stdin:
    if not line.strip():
        continue
    request = json.loads(line)
    if request.get("task") == "generate_assertion":
        print(json.dumps({
            "proposal_id": f"mock-assertion-{request.get('requirement_id', 'requirement')}",
            "kind": "check", "source_revision": request["allowed_source_revision"],
            "action": "generate the supplied reviewable assertion", "rationale": "Fixture returns the explicitly supplied bounded assertion.",
            "evidence": request["evidence"], "status": "review_required", "assertion": request["assertion"],
        }), flush=True)
        continue
    failure = request["failure"]
    signal = failure["signal"]
    cycle = failure["cycle"]
    if request.get("task") == "propose_repair":
        payload = {
            "proposal_id": f"mock-repair-{request.get('design_id', signal)}-{cycle}",
            "kind": "repair",
            "source_revision": request["allowed_source_revision"],
            "action": "apply the supplied bounded repair choice",
            "rationale": "Fixture selects only the explicitly supplied bounded repair; review and retest required.",
            "evidence": request["evidence"],
            "status": "review_required",
            "requirement_id": request.get("requirement_id") or "",
        }
        operators = request.get("repair_operator_choices")
        context = request.get("repair_context", [])
        seeded_line = next((item.get("text", "") for item in context if isinstance(item, dict) and "SEEDED_BUG" in str(item.get("text", ""))), "")
        if signal == "grant" and context:
            payload["before"] = "  assign grant = rst ? 2'b00 : (req[0] ? 2'b01 : 2'b00);"
            payload["after"] = "  assign grant = rst ? 2'b00 : req; // repaired one-hot request mapping"
            payload["edit_operator"] = "exact_text_replace"
        elif signal == "decode" and context:
            payload["before"] = "        2'd3: decode = 4'b1000;"
            payload["after"] = "        2'd2: decode = 4'b0100;\n        2'd3: decode = 4'b1000;"
            payload["edit_operator"] = "exact_text_replace"
        elif signal == "count" and context:
            payload["before"] = "        2'b10: count <= count + 3'd1;"
            payload["after"] = "        2'b10: if (count < DEPTH) count <= count + 3'd1;"
            payload["edit_operator"] = "exact_text_replace"
        elif signal == "counter_q" and context:
            payload["before"] = "counter_q <= counter_q + 4'd1;"
            payload["after"] = "if (enable) counter_q <= counter_q + 4'd1;"
            payload["edit_operator"] = "exact_text_replace"
        elif isinstance(operators, list) and operators:
            payload["edit_operator"] = operators[0]
        else:
            payload["before"] = request.get("repair_before", "")
            payload["after"] = request.get("repair_after", "")
        print(json.dumps(payload), flush=True)
    else:
        print(json.dumps({
            "proposal_id": f"mock-diagnosis-{signal}-{cycle}",
            "kind": "diagnosis",
            "source_revision": request["allowed_source_revision"],
            "action": f"inspect {signal} at cycle {cycle}",
            "rationale": f"Fixture observed {signal}={failure['actual']}, expected {failure['expected']}; review and retest required.",
            "evidence": request["evidence"],
            "status": "review_required",
        }), flush=True)
