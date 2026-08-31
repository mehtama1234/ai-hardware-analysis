#!/usr/bin/env python3
"""Programmatic GPU systems workbench API.

This module sits on top of the generated GPUMODE curriculum/workbench artifacts
and exposes one cohesive diagnosis path for scripts, notebooks, and CLI use.
"""

from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from build_workbench import OUT_JSON, PROFILES, build, score_text, text_blob


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
LAB_ROOT = REPO_ROOT / "gpu-kernels-serving-lab"
ANALYSIS = ROOT / "analysis"
GRAPH_JSON = ANALYSIS / "curriculum-graph.json"
BRIDGES_JSON = ANALYSIS / "lesson-corpus-bridges.json"
MEASUREMENTS_JSON = ANALYSIS / "latest-measurements-index.json"
GENERATED_TUTORIALS = ROOT / "generated-tutorials"
PROGRAM_OUTPUTS = ROOT / "program-outputs"


def read_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def terms(query: str) -> list[str]:
    return [term for term in re.findall(r"[a-z0-9.+_-]+", query.lower()) if len(term) > 1]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:80] or "gpu-workbench-tutorial"


def load_workbench() -> dict[str, Any]:
    if not OUT_JSON.exists():
        build()
    return read_json(OUT_JSON)


def _profile_defs() -> dict[str, dict[str, Any]]:
    return {profile["id"]: profile for profile in PROFILES}


def _profile_query_score(profile_def: dict[str, Any], generated_profile: dict[str, Any], query: str) -> int:
    query_terms = terms(query.replace("/", " ").replace("-", " "))
    score = score_text(query, profile_def["query_terms"])
    score += score_text(text_blob(profile_def["query_terms"]), query_terms)
    score += score_text(text_blob(profile_def["lesson_topics"]), query_terms)
    score += score_text(text_blob(profile_def["lesson_concepts"]), query_terms)
    score += score_text(profile_def["label"], query_terms)
    score += score_text(text_blob(generated_profile.get("recommended_lessons", [])[:5]), query_terms)
    score += score_text(text_blob(generated_profile.get("recommended_labs", [])[:5]), query_terms)
    score += score_text(text_blob(generated_profile.get("tutorial_sources", [])[:5]), query_terms)
    return score


def diagnose(query: str, limit: int = 5) -> dict[str, Any]:
    """Return the best workbench profile and related context for a query."""
    workbench = load_workbench()
    profile_defs = _profile_defs()
    ranked = []
    for profile in workbench.get("profiles", []):
        profile_def = profile_defs.get(profile["id"], {})
        score = _profile_query_score(profile_def, profile, query) if profile_def else 0
        ranked.append((score, profile))
    ranked.sort(key=lambda item: (-item[0], item[1]["id"]))
    score, profile = ranked[0] if ranked else (0, {})
    if score <= 0 and workbench.get("profiles"):
        profile = workbench["profiles"][0]

    result = {
        "query": query,
        "matched_bottleneck_class": profile.get("id", ""),
        "label": profile.get("label", ""),
        "diagnosis": profile.get("diagnosis", ""),
        "next_action": profile.get("next_action", ""),
        "lessons": profile.get("recommended_lessons", [])[:limit],
        "labs": profile.get("recommended_labs", [])[:limit],
        "measurements": profile.get("latest_measurements", [])[:limit],
        "tutorial_sources": profile.get("tutorial_sources", [])[:limit],
        "exercise_path": profile.get("exercise_path", {}),
        "papers": profile.get("related_papers", [])[:limit],
        "profile_score": score,
        "coverage": workbench.get("coverage", {}),
    }
    result["graph"] = graph_context(query, limit=limit)
    result["corpus"] = corpus_context(query, limit=limit)
    result["measurement_context"] = measurement_context(query, limit=limit)
    return result


def _score_row(row: dict[str, Any], query_terms: list[str]) -> int:
    blob = text_blob(row).lower()
    return sum(1 for term in query_terms if term in blob)


def compact_lesson(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "index": row.get("index"),
        "title": row.get("title", ""),
        "url": row.get("url", ""),
        "topics": row.get("topics", [])[:8],
        "concepts": row.get("concepts", [])[:8],
        "score": row.get("score", 0),
    }


def compact_paper(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row.get("id") or row.get("paper_id", ""),
        "title": row.get("title", ""),
        "venue": row.get("venue", ""),
        "theme": row.get("theme") or row.get("primary_theme", ""),
        "confidence": row.get("confidence", ""),
        "path": row.get("path", ""),
        "score": row.get("score", 0),
    }


def graph_context(query: str, limit: int = 5) -> dict[str, Any]:
    graph = read_json(GRAPH_JSON, {"nodes": [], "edges": [], "node_count": 0, "edge_count": 0})
    query_terms = terms(query)
    matches = []
    for node in graph.get("nodes", []):
        score = _score_row(node, query_terms)
        if score > 0:
            matches.append({"score": score, **node})
    matches.sort(key=lambda row: (-row["score"], row.get("kind", ""), row.get("id", "")))
    return {
        "node_count": graph.get("node_count", 0),
        "edge_count": graph.get("edge_count", 0),
        "matches": matches[:limit],
    }


def corpus_context(query: str, limit: int = 5) -> dict[str, Any]:
    data = read_json(BRIDGES_JSON, {"papers": [], "lessons": [], "paper_count": 0, "lesson_count": 0, "link_count": 0})
    query_terms = terms(query)
    papers = []
    lessons = []
    for paper in data.get("papers", []):
        score = _score_row(paper, query_terms)
        if score > 0:
            papers.append(compact_paper({"score": score, **paper}))
    for lesson in data.get("lessons", []):
        score = _score_row(lesson, query_terms)
        if score > 0:
            lessons.append(compact_lesson({"score": score, **lesson}))
    papers.sort(key=lambda row: (-row["score"], row.get("venue", ""), row.get("title", "")))
    lessons.sort(key=lambda row: (-row["score"], row.get("index", 0)))
    return {
        "coverage": {
            "paper_count": data.get("paper_count", 0),
            "lesson_count": data.get("lesson_count", 0),
            "link_count": data.get("link_count", 0),
        },
        "papers": papers[:limit],
        "lessons": lessons[:limit],
    }


def measurement_context(query: str, limit: int = 5) -> dict[str, Any]:
    data = read_json(MEASUREMENTS_JSON, {"rows": [], "artifact_count": 0, "passed_correctness": 0, "skipped_runtime_count": 0})
    query_terms = terms(query)
    matches = []
    for row in data.get("rows", []):
        score = _score_row(row, query_terms)
        if score > 0:
            matches.append({"score": score, **row})
    matches.sort(key=lambda row: (-row["score"], row.get("session", ""), row.get("path", "")))
    return {
        "coverage": {
            "artifact_count": data.get("artifact_count", 0),
            "passed_correctness": data.get("passed_correctness", 0),
            "skipped_runtime_count": data.get("skipped_runtime_count", 0),
        },
        "matches": matches[:limit],
    }


def _python_module_status(module: str) -> dict[str, Any]:
    spec = importlib.util.find_spec(module)
    return {
        "status": "available" if spec else "missing",
        "module": module,
    }


def runtime_readiness() -> dict[str, Any]:
    """Inspect local GPU/programming runtime readiness without requiring a GPU."""
    tools = {
        "nvidia_smi": shutil.which("nvidia-smi"),
        "nvcc": shutil.which("nvcc"),
        "ncu": shutil.which("ncu"),
        "nsys": shutil.which("nsys"),
        "hipcc": shutil.which("hipcc"),
        "rocminfo": shutil.which("rocminfo"),
    }
    modules = {
        "torch": _python_module_status("torch"),
        "triton": _python_module_status("triton"),
        "vllm": _python_module_status("vllm"),
        "jax": _python_module_status("jax"),
    }
    cuda_status: dict[str, Any] = {"status": "unknown", "reason": "torch is not importable"}
    if modules["torch"]["status"] == "available":
        try:
            import torch

            cuda_available = bool(torch.cuda.is_available())
            cuda_status = {
                "status": "available" if cuda_available else "missing",
                "torch_version": getattr(torch, "__version__", ""),
                "device_count": torch.cuda.device_count() if cuda_available else 0,
                "reason": "" if cuda_available else "torch is installed, but no CUDA-visible device is available",
            }
        except Exception as exc:  # pragma: no cover - environment-specific guard.
            cuda_status = {"status": "error", "reason": str(exc)}

    jax_status: dict[str, Any] = {
        "status": modules["jax"]["status"],
        "reason": "module probe only; run the JAX scaling lab for device-level proof",
    }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tools": {
            name: {"status": "available" if path else "missing", "path": path or ""}
            for name, path in tools.items()
        },
        "python_modules": modules,
        "cuda": cuda_status,
        "jax_runtime": jax_status,
        "lab_runtime_groups": {
            "cuda_source": "ready" if tools["nvcc"] and cuda_status.get("status") == "available" else "blocked",
            "triton": "ready" if modules["triton"]["status"] == "available" and cuda_status.get("status") == "available" else "blocked",
            "vllm": "ready" if modules["vllm"]["status"] == "available" and cuda_status.get("status") == "available" else "blocked",
            "rocm_hip": "ready" if tools["hipcc"] else "blocked",
            "jax": "ready" if modules["jax"]["status"] == "available" else "blocked",
            "profiler_imports": "ready",
            "cpu_proxy": "ready",
        },
    }


def recommended_lab_dir(result: dict[str, Any]) -> Path | None:
    path = result.get("exercise_path", {}).get("lab", {}).get("path", "")
    if not path:
        for lab in result.get("labs", []):
            path = lab.get("implemented_as", "")
            if path:
                break
    if not path:
        return None
    lab_dir = (REPO_ROOT / path).resolve()
    try:
        lab_dir.relative_to(LAB_ROOT.resolve())
    except ValueError:
        return None
    return lab_dir


def run_recommended_lab(query: str, dry_run: bool = False) -> dict[str, Any]:
    result = diagnose(query)
    lab_dir = recommended_lab_dir(result)
    if lab_dir is None:
        return {"status": "missing-lab", "query": query, "commands": []}
    commands = [
        [sys.executable, "run.py"],
        [sys.executable, "build_page.py"],
    ]
    payload = {
        "status": "dry-run" if dry_run else "running",
        "query": query,
        "lab_dir": str(lab_dir.relative_to(REPO_ROOT)),
        "commands": [" ".join(command) for command in commands],
        "runs": [],
    }
    if dry_run:
        return payload
    for command in commands:
        proc = subprocess.run(command, cwd=lab_dir, capture_output=True, text=True, check=False)
        payload["runs"].append(
            {
                "command": " ".join(command),
                "returncode": proc.returncode,
                "stdout_tail": proc.stdout[-2000:],
                "stderr_tail": proc.stderr[-2000:],
            }
        )
        if proc.returncode != 0:
            payload["status"] = "failed"
            return payload
    payload["status"] = "passed"
    return payload


def build_tutorial(query: str, output_dir: Path = GENERATED_TUTORIALS) -> dict[str, Any]:
    result = diagnose(query, limit=6)
    profile = result["matched_bottleneck_class"]
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{slugify(profile + '-' + query)}.md"
    exercise = result.get("exercise_path", {})
    lines = [
        f"# {result['label']}",
        "",
        f"Query: `{query}`",
        "",
        "## Diagnosis",
        "",
        result.get("diagnosis", ""),
        "",
        f"Next action: {result.get('next_action', '')}",
        "",
        "## Read First",
    ]
    for source in result.get("tutorial_sources", [])[:4]:
        lines.append(f"- {source.get('provider', '')}: [{source.get('title', '')}]({source.get('url', '')})")
        lines.append(f"  - {source.get('why', '')}")
    lines += ["", "## GPUMODE Anchors"]
    for lesson in result.get("lessons", [])[:5]:
        lines.append(f"- Lesson {lesson.get('index')}: [{lesson.get('title', '')}]({lesson.get('url', '')})")
    lab = exercise.get("lab", {})
    measurement = exercise.get("measurement", {})
    lines += [
        "",
        "## Run The Lab",
        "",
        f"Lab: `{lab.get('path', '')}`",
        "",
        "```bash",
        lab.get("command", ""),
        "```",
        "",
        "## Measurement To Inspect",
        "",
        f"- Artifact: `{measurement.get('path', '')}`",
        f"- Summary: {measurement.get('summary', '')}",
        "",
        "## Steps",
    ]
    for step in exercise.get("steps", []):
        lines.append(f"- {step}")
    lines += ["", "## Success Checks"]
    for check in exercise.get("success_checks", []):
        lines.append(f"- {check}")
    lines += ["", "## Research Cross-Checks"]
    for paper in result.get("papers", [])[:4]:
        lines.append(f"- {paper.get('venue', '')}: {paper.get('title', '')}")
        if paper.get("path"):
            lines.append(f"  - `{paper.get('path')}`")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return {
        "status": "written",
        "path": str(path.relative_to(ROOT)),
        "profile": profile,
        "query": query,
    }


def build_batch_triage(queries: list[str], output_dir: Path = PROGRAM_OUTPUTS) -> dict[str, Any]:
    """Diagnose multiple GPU questions and write a compact JSON work queue."""
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for query in queries:
        result = diagnose(query, limit=3)
        lab = result.get("exercise_path", {}).get("lab", {})
        measurement = result.get("exercise_path", {}).get("measurement", {})
        rows.append(
            {
                "query": query,
                "profile": result.get("matched_bottleneck_class", ""),
                "label": result.get("label", ""),
                "next_action": result.get("next_action", ""),
                "lab_path": lab.get("path", ""),
                "lab_command": lab.get("command", ""),
                "measurement": measurement.get("path", ""),
                "top_lessons": [
                    {"index": lesson.get("index"), "title": lesson.get("title", ""), "url": lesson.get("url", "")}
                    for lesson in result.get("lessons", [])[:3]
                ],
                "top_tutorial_sources": [
                    {"provider": source.get("provider", ""), "title": source.get("title", ""), "url": source.get("url", "")}
                    for source in result.get("tutorial_sources", [])[:3]
                ],
                "top_papers": [compact_paper(paper) for paper in result.get("papers", [])[:3]],
            }
        )
    coverage = load_workbench().get("coverage", {})
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "query_count": len(rows),
        "coverage": coverage,
        "rows": rows,
    }
    path = output_dir / "batch-triage.json"
    write_json(path, payload)
    return {"status": "written", "path": str(path.relative_to(ROOT)), **payload}


def build_learning_roadmap(query: str, output_dir: Path = PROGRAM_OUTPUTS) -> dict[str, Any]:
    """Write a Markdown roadmap from source reading to lab and measurement checks."""
    output_dir.mkdir(parents=True, exist_ok=True)
    result = diagnose(query, limit=6)
    path = output_dir / f"{slugify(result['matched_bottleneck_class'] + '-' + query)}-roadmap.md"
    exercise = result.get("exercise_path", {})
    lab = exercise.get("lab", {})
    measurement = exercise.get("measurement", {})
    lines = [
        f"# {result.get('label', '')} Roadmap",
        "",
        f"Query: `{query}`",
        "",
        "## Outcome",
        "",
        result.get("diagnosis", ""),
        "",
        "## Phase 1: Source Model",
    ]
    for source in result.get("tutorial_sources", [])[:3]:
        lines.append(f"- {source.get('provider', '')}: [{source.get('title', '')}]({source.get('url', '')})")
    lines += ["", "## Phase 2: GPUMODE Lessons"]
    for lesson in result.get("lessons", [])[:6]:
        concepts = ", ".join(lesson.get("concepts", [])[:5])
        lines.append(f"- Lesson {lesson.get('index')}: [{lesson.get('title', '')}]({lesson.get('url', '')})")
        if concepts:
            lines.append(f"  - concepts: {concepts}")
    lines += [
        "",
        "## Phase 3: Program And Run",
        "",
        f"- Lab: `{lab.get('path', '')}`",
        "",
        "```bash",
        lab.get("command", ""),
        "```",
        "",
        "## Phase 4: Evidence",
        "",
        f"- Measurement artifact: `{measurement.get('path', '')}`",
        f"- Measurement summary: {measurement.get('summary', '')}",
        "",
        "## Phase 5: Research Cross-Check",
    ]
    for paper in result.get("papers", [])[:5]:
        lines.append(f"- {paper.get('venue', '')}: {paper.get('title', '')}")
        if paper.get("path"):
            lines.append(f"  - `{paper.get('path')}`")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return {
        "status": "written",
        "path": str(path.relative_to(ROOT)),
        "query": query,
        "profile": result.get("matched_bottleneck_class", ""),
    }


def build_evidence_report(query: str, output_dir: Path = PROGRAM_OUTPUTS) -> dict[str, Any]:
    """Write a compact JSON report for a single GPU workbench investigation."""
    output_dir.mkdir(parents=True, exist_ok=True)
    result = diagnose(query, limit=5)
    doctor = runtime_readiness()
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "profile": result.get("matched_bottleneck_class", ""),
        "label": result.get("label", ""),
        "diagnosis": result.get("diagnosis", ""),
        "next_action": result.get("next_action", ""),
        "runtime_groups": doctor.get("lab_runtime_groups", {}),
        "recommended_lab": result.get("exercise_path", {}).get("lab", {}),
        "measurement": result.get("exercise_path", {}).get("measurement", {}),
        "latest_measurement_matches": result.get("measurement_context", {}).get("matches", [])[:5],
        "graph_matches": result.get("graph", {}).get("matches", [])[:5],
        "paper_cross_checks": [compact_paper(paper) for paper in result.get("papers", [])[:5]],
        "tutorial_sources": result.get("tutorial_sources", [])[:5],
    }
    path = output_dir / f"{slugify(result['matched_bottleneck_class'] + '-' + query)}-evidence.json"
    write_json(path, payload)
    return {"status": "written", "path": str(path.relative_to(ROOT)), **payload}
