#!/usr/bin/env python3
"""Provider-neutral fixture for repository-agent role handoffs."""

from __future__ import annotations

import json
import sys


for line in sys.stdin:
    request = json.loads(line)
    role = request["role"]
    kind = {"diagnostician": "diagnosis", "repair_proposer": "repair", "reviewer": "next_action", "invariant_generator": "lemma"}[role]
    payload = {
        "proposal_id": f"mock-{role}-{request['task_id']}",
        "kind": kind,
        "source_revision": request["allowed_source_revision"],
        "action": request["task"],
        "rationale": "Fixture proposal is bounded to the supplied repository evidence and requires review.",
        "evidence": request["evidence"],
        "status": "review_required",
    }
    if role == "repair_proposer" and "repair_before" in request and "repair_after" in request:
        payload["before"] = request["repair_before"]
        payload["after"] = request["repair_after"]
    print(json.dumps(payload), flush=True)
