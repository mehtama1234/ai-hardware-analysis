#!/usr/bin/env python3
"""Query the generated latest local measurement index."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "analysis" / "latest-measurements-index.json"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def text_blob(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(f"{key} {text_blob(val)}" for key, val in value.items())
    if isinstance(value, list):
        return " ".join(text_blob(item) for item in value)
    return str(value)


def terms(query: str) -> list[str]:
    return [term for term in re.findall(r"[a-z0-9.+_-]+", query.lower()) if len(term) > 1]


def score(row: dict[str, Any], query_terms: list[str]) -> int:
    blob = text_blob(row).lower()
    return sum(1 for term in query_terms if term in blob)


def compact(query: str, limit: int) -> dict[str, Any]:
    data = read_json(INDEX)
    query_terms = terms(query)
    matches = []
    for row in data.get("rows", []):
        row_score = score(row, query_terms)
        if row_score > 0:
            matches.append((row_score, row))
    matches.sort(key=lambda item: (-item[0], item[1]["session"], item[1]["path"]))
    return {
        "query": query,
        "coverage": {
            "artifact_count": data.get("artifact_count", 0),
            "passed_correctness": data.get("passed_correctness", 0),
            "skipped_runtime_count": data.get("skipped_runtime_count", 0),
        },
        "matches": [{"score": score, **row} for score, row in matches[:limit]],
    }


def print_markdown(result: dict[str, Any]) -> None:
    print("# Latest Measurements Query")
    print()
    print(f"Query: {result['query']}")
    coverage = result["coverage"]
    print(
        f"Coverage: {coverage['artifact_count']} artifacts, "
        f"{coverage['passed_correctness']} correctness-passed, "
        f"{coverage['skipped_runtime_count']} runtime skips"
    )
    print()
    for row in result["matches"]:
        correctness = f", correctness={row['correctness']}" if row.get("correctness") else ""
        print(f"- {row['session']} [{row['status']}{correctness}] score={row['score']}")
        print(f"  artifact: {row['path']}")
        if row.get("page"):
            print(f"  page: {row['page']}")
        print(f"  summary: {row['summary']}")
        readiness = row.get("runtime_readiness", {})
        skipped = [
            f"{name}: {value.get('reason')}"
            for name, value in readiness.items()
            if isinstance(value, dict) and value.get("status") == "skipped"
        ]
        if skipped:
            print(f"  skips: {'; '.join(skipped)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Measurement, runtime, status, session, or bottleneck phrase.")
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = compact(args.query, max(1, args.limit))
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_markdown(result)


if __name__ == "__main__":
    main()
