#!/usr/bin/env python3
"""Build a portfolio-level capstone from generated GPU programming projects."""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "programming-projects"
CAPSTONE_JSON = PROJECTS / "capstone-portfolio.json"
CAPSTONE_MD = PROJECTS / "capstone-portfolio.md"

DEPENDENCIES = {
    "cuda-memory-kernel": [],
    "triton-fused-softmax": ["cuda-memory-kernel"],
    "nsight-evidence-loop": ["cuda-memory-kernel", "triton-fused-softmax"],
    "hf-quant-serving": ["cuda-memory-kernel"],
    "vllm-kv-scheduler": ["hf-quant-serving", "triton-fused-softmax"],
    "jax-scaling-roofline": ["cuda-memory-kernel", "nsight-evidence-loop"],
    "rocm-hip-port": ["cuda-memory-kernel"],
    "distributed-collectives": ["jax-scaling-roofline", "vllm-kv-scheduler"],
}

PHASES = [
    {
        "id": "local-baselines",
        "title": "Local baselines and memory model",
        "projects": ["cuda-memory-kernel", "hf-quant-serving", "jax-scaling-roofline"],
    },
    {
        "id": "kernel-specialization",
        "title": "Kernel specialization and profiling",
        "projects": ["triton-fused-softmax", "nsight-evidence-loop"],
    },
    {
        "id": "serving-runtime",
        "title": "Serving runtime and portability",
        "projects": ["vllm-kv-scheduler", "rocm-hip-port"],
    },
    {
        "id": "scale-out",
        "title": "Scale-out communication",
        "projects": ["distributed-collectives"],
    },
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def topo_order(project_ids: list[str]) -> list[str]:
    remaining = set(project_ids)
    ordered = []
    while remaining:
        ready = sorted(
            project_id
            for project_id in remaining
            if all(dep in ordered or dep not in remaining for dep in DEPENDENCIES.get(project_id, []))
        )
        if not ready:
            raise RuntimeError(f"cyclic project dependencies: {sorted(remaining)}")
        ordered.extend(ready)
        remaining.difference_update(ready)
    return ordered


def build_graph(projects: list[dict[str, Any]]) -> dict[str, Any]:
    ids = {project["id"] for project in projects}
    nodes = [
        {
            "id": project["id"],
            "track": project["track"],
            "profile": project["profile"],
            "path": project["path"],
        }
        for project in projects
    ]
    edges = []
    for project_id, deps in DEPENDENCIES.items():
        if project_id not in ids:
            continue
        for dep in deps:
            if dep in ids:
                edges.append({"source": dep, "target": project_id, "relation": "prerequisite_for"})
    return {"node_count": len(nodes), "edge_count": len(edges), "nodes": nodes, "edges": edges}


def build_milestones(projects_by_id: dict[str, dict[str, Any]], runs_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    milestones = []
    for phase in PHASES:
        rows = []
        for project_id in phase["projects"]:
            project = projects_by_id.get(project_id, {})
            run = runs_by_id.get(project_id, {})
            rows.append(
                {
                    "project_id": project_id,
                    "track": project.get("track", ""),
                    "profile": project.get("profile", ""),
                    "status": run.get("run", {}).get("status", "not-run"),
                    "contract": run.get("contract", {}).get("status", "not-validated"),
                    "measurement_path": run.get("contract", {}).get("measurement_path", ""),
                    "next_artifact": project.get("local_measurement", ""),
                }
            )
        milestones.append({**phase, "projects": rows})
    return milestones


def build_markdown(portfolio: dict[str, Any]) -> str:
    lines = [
        "# GPU Programming Capstone Portfolio",
        "",
        f"Generated: `{portfolio['generated_at']}`",
        "",
        "## Summary",
        "",
        f"- Projects: {portfolio['project_count']}",
        f"- Dependency edges: {portfolio['graph']['edge_count']}",
        f"- Contracts passed: {portfolio['passed_contracts']}",
        f"- Runtime caveats: {len(portfolio['runtime_caveats'])}",
        "",
        "## Execution Order",
        "",
    ]
    for idx, project_id in enumerate(portfolio["execution_order"], start=1):
        project = portfolio["projects_by_id"][project_id]
        lines.append(f"{idx}. `{project_id}` - {project['track']} ({project['profile']})")
    lines += ["", "## Milestones"]
    for milestone in portfolio["milestones"]:
        lines += ["", f"### {milestone['title']}"]
        for project in milestone["projects"]:
            lines.append(
                f"- `{project['project_id']}`: starter={project['status']}, "
                f"contract={project['contract']}, measurement=`{project['measurement_path']}`"
            )
    lines += ["", "## Runtime Caveats"]
    if portfolio["runtime_caveats"]:
        for caveat in portfolio["runtime_caveats"]:
            lines.append(f"- `{caveat['project_id']}`: {caveat['note']}")
    else:
        lines.append("- None recorded.")
    lines += [
        "",
        "## Capstone Build",
        "",
        "The final capstone combines the memory/coalescing baseline, Triton fused-kernel path, profiler evidence loop,",
        "serving/KV scheduler, JAX roofline model, Hugging Face inference baseline, ROCm/HIP portability boundary,",
        "and distributed collective model into one portfolio. A GPU-enabled follow-up run should replace `source-only`",
        "CUDA/HIP artifacts with compiled measurements while preserving the same measurement contracts.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def build() -> dict[str, Any]:
    index = load_json(PROJECTS / "index.json")
    run_report = load_json(PROJECTS / "project-run-report.json")
    projects = index.get("projects", [])
    projects_by_id = {project["id"]: project for project in projects}
    runs_by_id = {row["id"]: row for row in run_report.get("projects", [])}
    runtime_caveats = []
    for project_id, run in runs_by_id.items():
        notes = run.get("contract", {}).get("evidence", {}).get("runtime_readiness", {}).get("notes", [])
        for note in notes:
            runtime_caveats.append({"project_id": project_id, "note": note})
    portfolio = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_count": len(projects),
        "passed_contracts": run_report.get("passed_contracts", 0),
        "failed_contracts": run_report.get("failed_contracts", 0),
        "execution_order": topo_order([project["id"] for project in projects]),
        "graph": build_graph(projects),
        "milestones": build_milestones(projects_by_id, runs_by_id),
        "runtime_caveats": runtime_caveats,
        "projects_by_id": projects_by_id,
    }
    write_json(CAPSTONE_JSON, portfolio)
    CAPSTONE_MD.write_text(build_markdown(portfolio), encoding="utf-8")
    return portfolio


def main() -> None:
    portfolio = build()
    print(
        f"wrote {CAPSTONE_JSON.relative_to(ROOT)} and {CAPSTONE_MD.relative_to(ROOT)} "
        f"({portfolio['project_count']} projects, {portfolio['graph']['edge_count']} edges)"
    )


if __name__ == "__main__":
    main()
