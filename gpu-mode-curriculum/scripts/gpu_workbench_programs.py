#!/usr/bin/env python3
"""Example programs built on the GPU workbench API."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from gpu_workbench_api import (
    build_batch_triage,
    build_evidence_report,
    build_learning_roadmap,
    read_json,
)


DEFAULT_QUERIES = [
    "kv cache decode latency",
    "triton fused softmax",
    "tensor core quantization",
    "rocm hip cuda portability",
    "nccl all reduce bandwidth",
]


def load_queries(path: str | None, inline: list[str]) -> list[str]:
    queries = list(inline)
    if path:
        source = Path(path)
        if source.suffix == ".json":
            data = read_json(source)
            if isinstance(data, list):
                queries.extend(str(item) for item in data)
            elif isinstance(data, dict):
                queries.extend(str(item) for item in data.get("queries", []))
        else:
            queries.extend(line.strip() for line in source.read_text(encoding="utf-8").splitlines() if line.strip())
    return queries or DEFAULT_QUERIES


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    batch = sub.add_parser("batch-triage", help="Build a JSON work queue for multiple GPU questions.")
    batch.add_argument("queries", nargs="*", help="Queries to diagnose. Uses a default representative set if omitted.")
    batch.add_argument("--queries-file", help="Text file or JSON file containing queries.")

    roadmap = sub.add_parser("roadmap", help="Build a Markdown learning/programming roadmap for one query.")
    roadmap.add_argument("query")

    report = sub.add_parser("evidence-report", help="Build a JSON evidence report for one query.")
    report.add_argument("query")

    args = parser.parse_args()
    if args.command == "batch-triage":
        result = build_batch_triage(load_queries(args.queries_file, args.queries))
    elif args.command == "roadmap":
        result = build_learning_roadmap(args.query)
    elif args.command == "evidence-report":
        result = build_evidence_report(args.query)
    else:  # pragma: no cover - argparse prevents this.
        raise AssertionError(args.command)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
