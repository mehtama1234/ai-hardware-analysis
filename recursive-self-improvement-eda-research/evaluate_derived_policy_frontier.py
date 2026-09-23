#!/usr/bin/env python3
"""Evaluate coverage-first versus cost-aware policy choices on derived evidence."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DERIVED = HERE / "derived-ledger-transfer.json"
POPULATION = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/converter-to-inference-v1/results/selector-population.json"
OUT = HERE / "derived-policy-frontier.json"
DIGITAL_ENERGY = 3072.0


def normalize_base(row: dict) -> dict:
    return {"placement": row["placement"], "reliable": row["reliable"],
            "cost": row["cost"], "source": "frozen_population"}


def normalize_fresh(row: dict) -> dict:
    return {"placement": row["proposal"]["placement"], "reliable": row["reliable"],
            "cost": row["cost"], "source": "fresh_proposal", "proposal": row["proposal"]}


def choose(rows: list[dict], objective: str) -> dict:
    safe = [row for row in rows if row["reliable"]]
    if objective == "cost_aware":
        cheaper = [row for row in safe if float(row["cost"]["estimated_energy"]) < DIGITAL_ENERGY]
        if not cheaper:
            return {"placement": [], "reliable": True, "cost": {"estimated_energy": DIGITAL_ENERGY}, "source": "digital_fallback"}
        return min(cheaper, key=lambda row: float(row["cost"]["estimated_energy"]))
    if not safe:
        return {"placement": [], "reliable": True, "cost": {"estimated_energy": DIGITAL_ENERGY}, "source": "digital_fallback"}
    return max(safe, key=lambda row: (len(row["placement"]), -float(row["cost"]["estimated_energy"])))


def main() -> int:
    derived = json.loads(DERIVED.read_text())
    population = json.loads(POPULATION.read_text())
    rows_by_case: dict[str, list[dict]] = defaultdict(list)
    for row in population["rows"]:
        if row["seed"] >= 6:
            rows_by_case[row["case_id"]].append(normalize_base(row))
    for row in derived["derived_ledger"]["fresh_trials"]["rows"]:
        rows_by_case[row["case_id"]].append(normalize_fresh(row))

    decisions = {"coverage_first": [], "cost_aware": []}
    for case_id in sorted(rows_by_case):
        for objective in decisions:
            selected = choose(rows_by_case[case_id], objective)
            decisions[objective].append({"case_id": case_id, "selected": selected})

    summaries = {}
    for objective, items in decisions.items():
        summaries[objective] = {
            "cases": len(items),
            "safe_cases": sum(item["selected"]["reliable"] for item in items),
            "analog_cases": sum(bool(item["selected"]["placement"]) for item in items),
            "fallback_cases": sum(not item["selected"]["placement"] for item in items),
            "estimated_energy": sum(float(item["selected"]["cost"]["estimated_energy"]) for item in items),
        }

    result = {
        "schema_version": "recursive_derived_policy_frontier.v1",
        "source": "derived-ledger-transfer.json plus selector-population.json held-out cases",
        "objectives": {"coverage_first": ["maximize analog operator count", "minimize modeled energy"],
                       "cost_aware": ["require modeled energy below digital baseline", "minimize modeled energy"]},
        "decisions": decisions,
        "summary": summaries,
        "status": "passed" if all(item["safe_cases"] == item["cases"] for item in summaries.values()) else "blocked",
        "claim_boundary": "Derived simulator policy frontier only; cost is a declared proxy and does not establish measured hardware benefit.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summaries, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
