#!/usr/bin/env python3
"""Unified CLI for the GPUMODE GPU systems workbench."""

from __future__ import annotations

import argparse
import json
from typing import Any

from gpu_workbench_api import build_tutorial, diagnose, run_recommended_lab, runtime_readiness


def print_runtime_doctor(result: dict[str, Any]) -> None:
    print("# GPU Workbench Runtime Doctor")
    print()
    print("## Tools")
    for name, row in result["tools"].items():
        suffix = f" -> {row['path']}" if row.get("path") else ""
        print(f"- {name}: {row['status']}{suffix}")
    print()
    print("## Python Modules")
    for name, row in result["python_modules"].items():
        print(f"- {name}: {row['status']}")
    print()
    cuda = result["cuda"]
    print("## CUDA")
    print(f"- status: {cuda.get('status')}")
    if cuda.get("torch_version"):
        print(f"- torch: {cuda.get('torch_version')}")
    if cuda.get("reason"):
        print(f"- reason: {cuda.get('reason')}")
    print()
    print("## Lab Runtime Groups")
    for name, status in result["lab_runtime_groups"].items():
        print(f"- {name}: {status}")


def print_lab(lab: dict[str, Any]) -> None:
    impl = f" -> {lab.get('implemented_as')}" if lab.get("implemented_as") else ""
    print(f"- {lab.get('id', '')} [{lab.get('status', '')}]{impl}")
    if lab.get("deliverable"):
        print(f"  deliverable: {lab['deliverable']}")


def print_markdown(result: dict[str, Any]) -> None:
    print(f"# {result['label']}")
    print()
    print(f"Query: {result['query']}")
    print(f"Bottleneck class: {result['matched_bottleneck_class']}")
    print()
    print(result["diagnosis"])
    print()
    print(f"Next action: {result['next_action']}")
    print()
    print("## Recommended Lab")
    path = result.get("exercise_path", {})
    lab = path.get("lab", {})
    if lab:
        print(f"- {lab.get('title', lab.get('id', ''))}: `{lab.get('path', '')}`")
        print(f"  command: `{lab.get('command', '')}`")
    else:
        for row in result.get("labs", [])[:1]:
            print_lab(row)
    print()
    print("## Labs")
    for row in result.get("labs", []):
        print_lab(row)
    print()
    print("## Lessons")
    for lesson in result.get("lessons", []):
        print(f"- #{lesson.get('index')}: {lesson.get('title')} ({lesson.get('url')})")
    print()
    print("## Tutorial Sources")
    for source in result.get("tutorial_sources", []):
        print(f"- {source.get('provider')}: {source.get('title')} ({source.get('url')})")
    print()
    print("## Measurements")
    for measurement in result.get("measurements", []):
        cuda = f", cuda={measurement.get('cuda_status')}" if measurement.get("cuda_status") else ""
        print(f"- {measurement.get('path')} [{measurement.get('status')}{cuda}]")
        print(f"  {measurement.get('summary')}")
    print()
    print("## Papers")
    for paper in result.get("papers", []):
        print(f"- {paper.get('venue')}: {paper.get('title')} [{paper.get('confidence')}]")
    print()
    graph = result.get("graph", {})
    corpus = result.get("corpus", {}).get("coverage", {})
    measurements = result.get("measurement_context", {}).get("coverage", {})
    print("## Coverage")
    print(f"- graph: {graph.get('node_count', 0)} nodes, {graph.get('edge_count', 0)} edges")
    print(f"- corpus bridge: {corpus.get('paper_count', 0)} papers, {corpus.get('link_count', 0)} links")
    print(
        "- measurements: "
        f"{measurements.get('artifact_count', 0)} artifacts, "
        f"{measurements.get('passed_correctness', 0)} correctness-passed, "
        f"{measurements.get('skipped_runtime_count', 0)} runtime skips"
    )
    if result.get("tutorial_file"):
        print()
        print(f"Generated tutorial: `{result['tutorial_file']['path']}`")
    if result.get("lab_run"):
        print()
        print("## Lab Run")
        run = result["lab_run"]
        print(f"- status: {run.get('status')}")
        print(f"- lab: {run.get('lab_dir')}")
        for command in run.get("commands", []):
            print(f"- command: `{command}`")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="?", help="GPU bottleneck, kernel, serving, or tutorial question.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown.")
    parser.add_argument("--doctor", action="store_true", help="Inspect local CUDA/Triton/vLLM/ROCm/JAX readiness.")
    parser.add_argument("--tutorial", action="store_true", help="Write an end-to-end Markdown tutorial for the query.")
    parser.add_argument("--run-lab", action="store_true", help="Run the recommended known local lab.")
    parser.add_argument("--dry-run", action="store_true", help="Show the lab command without executing it.")
    parser.add_argument("--limit", type=int, default=5, help="Maximum rows per section.")
    args = parser.parse_args()

    if args.doctor and not args.query:
        result = runtime_readiness()
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print_runtime_doctor(result)
        return 0

    if not args.query:
        parser.error("query is required unless --doctor is used by itself")

    result = diagnose(args.query, limit=max(1, args.limit))
    result["runtime_readiness"] = runtime_readiness()
    if args.tutorial:
        result["tutorial_file"] = build_tutorial(args.query)
    if args.run_lab:
        result["lab_run"] = run_recommended_lab(args.query, dry_run=args.dry_run)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_markdown(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
