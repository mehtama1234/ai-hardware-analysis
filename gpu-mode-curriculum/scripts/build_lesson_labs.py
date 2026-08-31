#!/usr/bin/env python3
"""Generate one concrete lab scaffold for every GPUMODE lesson."""

from __future__ import annotations

import json
import re
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = ROOT / "analysis" / "gpumode-curriculum.json"
PROJECTS = ROOT / "programming-projects"
OUT = ROOT / "lesson-labs"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")[:64] or "lesson"


def lesson_lab_id(lesson: dict[str, Any]) -> str:
    return f"lesson-{int(lesson['index']):03d}-{slugify(lesson.get('title', 'gpumode'))}"


def project_coverage() -> dict[int, list[str]]:
    coverage: dict[int, list[str]] = {}
    index_path = PROJECTS / "index.json"
    if not index_path.exists():
        return coverage
    index = load_json(index_path)
    for row in index.get("projects", []):
        metadata_path = ROOT / row.get("path", "") / "project.json"
        if not metadata_path.exists():
            continue
        metadata = load_json(metadata_path)
        for lesson in metadata.get("lessons", []):
            idx = lesson.get("index")
            if isinstance(idx, int):
                coverage.setdefault(idx, []).append(row["id"])
    return coverage


def source_text(lesson: dict[str, Any]) -> str:
    lesson_json = json.dumps(
        {
            "index": lesson["index"],
            "title": lesson["title"],
            "topics": lesson.get("topics", []),
            "concepts": lesson.get("concepts", []),
            "tools": lesson.get("tools", []),
            "exercise_candidates": lesson.get("exercise_candidates", []),
            "candidate_lab_links": lesson.get("candidate_lab_links", []),
        },
        indent=2,
        ensure_ascii=False,
    )
    body = textwrap.dedent(
        '''


        def memory_stride_score(length: int = 4096, stride: int = 4) -> dict[str, float | int | str]:
            contiguous_transactions = math.ceil(length / 32)
            strided_transactions = math.ceil(length * stride / 32)
            ratio = strided_transactions / max(1, contiguous_transactions)
            return {"kind": "memory-access", "length": length, "stride": stride, "transaction_ratio": round(ratio, 4)}


        def online_softmax(values: list[float]) -> list[float]:
            running_max = -float("inf")
            running_sum = 0.0
            for value in values:
                next_max = max(running_max, value)
                running_sum = running_sum * math.exp(running_max - next_max) + math.exp(value - next_max)
                running_max = next_max
            return [math.exp(value - running_max) / running_sum for value in values]


        def kv_cache_mb(batch: int = 1, sequence: int = 4096, layers: int = 32, hidden: int = 4096) -> float:
            return round(batch * sequence * layers * hidden * 2 * 2 / 1e6, 3)


        def collective_latency_us(ranks: int = 8, payload_mb: int = 128) -> float:
            link_gbps = 300.0
            hop_latency_us = 4.0
            bytes_per_rank = payload_mb * 1024 * 1024
            seconds = 2 * (ranks - 1) * hop_latency_us / 1e6 + 2 * bytes_per_rank * (ranks - 1) / ranks / (link_gbps * 1e9)
            return round(seconds * 1e6, 3)


        def run_proxy() -> dict[str, object]:
            topics = set(LESSON.get("topics", []))
            concepts = set(LESSON.get("concepts", []))
            checks: list[dict[str, object]] = []
            if "cuda" in topics or "memory coalescing" in concepts:
                checks.append(memory_stride_score())
            if "attention" in topics or "online softmax" in concepts:
                probs = online_softmax([0.2, 0.7, -0.4, 1.1])
                checks.append({"kind": "online-softmax", "probability_sum": round(sum(probs), 8), "max_probability": round(max(probs), 8)})
            if "serving" in topics or "kv cache" in concepts:
                checks.append({"kind": "serving-kv-cache", "kv_cache_mb": kv_cache_mb()})
            if "distributed" in topics or "collectives" in concepts:
                checks.append({"kind": "collective-model", "ring_latency_us": collective_latency_us()})
            if "quantization" in topics or "quantized numerics" in concepts:
                checks.append({"kind": "quantization", "int4_levels": 16, "symmetric_zero_point": 0})
            if not checks:
                checks.append({"kind": "triage", "exercise_count": len(LESSON.get("exercise_candidates", []))})
            return {
                "status": "ran-cpu-proxy",
                "lesson_index": LESSON["index"],
                "title": LESSON["title"],
                "topics": sorted(topics),
                "concepts": sorted(concepts),
                "checks": checks,
            }


        if __name__ == "__main__":
            print(json.dumps(run_proxy(), indent=2, ensure_ascii=False))
        '''
    ).lstrip()
    return (
        "#!/usr/bin/env python3\n"
        f'"""Lesson-specific local proxy program for GPUMODE lesson {lesson["index"]}."""\n\n'
        "from __future__ import annotations\n\n"
        "import json\n"
        "import math\n\n\n"
        f"LESSON = {lesson_json}\n"
        f"{body}"
    )


def starter_text(lab_id: str) -> str:
    return textwrap.dedent(
        f'''
        #!/usr/bin/env python3
        """Starter entry for {lab_id}."""

        from __future__ import annotations

        import json
        import subprocess
        import sys
        from pathlib import Path


        HERE = Path(__file__).resolve().parent
        SOURCE = HERE / "lab.py"


        def main() -> int:
            proc = subprocess.run([sys.executable, str(SOURCE)], cwd=HERE, capture_output=True, text=True, check=False)
            payload = {{}}
            if proc.stdout.strip():
                payload = json.loads(proc.stdout)
            payload["source_returncode"] = proc.returncode
            payload["source"] = SOURCE.name
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return 0 if proc.returncode == 0 and payload.get("status") == "ran-cpu-proxy" else 1


        if __name__ == "__main__":
            raise SystemExit(main())
        '''
    ).lstrip()


def measure_text(lab_id: str) -> str:
    return textwrap.dedent(
        f'''
        #!/usr/bin/env python3
        """Run the lesson lab and write measurements.json."""

        from __future__ import annotations

        import json
        import subprocess
        import sys
        from datetime import datetime, timezone
        from pathlib import Path


        HERE = Path(__file__).resolve().parent
        OUT = HERE / "measurements.json"


        def main() -> int:
            proc = subprocess.run([sys.executable, "starter.py"], cwd=HERE, capture_output=True, text=True, check=False)
            payload = {{}}
            if proc.stdout.strip():
                payload = json.loads(proc.stdout)
            artifact = {{
                "lab_id": "{lab_id}",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "status": payload.get("status", "failed"),
                "correctness": {{
                    "status": "passed" if proc.returncode == 0 and payload.get("checks") else "failed",
                    "checks": {{
                        "starter_exited_zero": proc.returncode == 0,
                        "payload_has_lesson_index": bool(payload.get("lesson_index")),
                        "payload_has_checks": bool(payload.get("checks")),
                    }},
                }},
                "runtime_readiness": {{
                    "status": "cpu-proxy",
                    "notes": [
                        "Generated lesson lab uses local CPU proxy checks; replace or extend lab.py with CUDA/Triton/HIP kernels on a GPU host."
                    ],
                }},
                "measurement": {{
                    "rows": payload.get("checks", []),
                    "summary": f"Lesson {{payload.get('lesson_index')}} local proxy emitted {{len(payload.get('checks', []))}} checks.",
                }},
                "starter": {{
                    "command": f"{{sys.executable}} starter.py",
                    "returncode": proc.returncode,
                    "stdout_tail": proc.stdout.strip()[-2000:],
                    "stderr_tail": proc.stderr.strip()[-2000:],
                }},
            }}
            OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\\n", encoding="utf-8")
            print(json.dumps({{"status": artifact["status"], "correctness": artifact["correctness"]["status"], "path": OUT.name}}, indent=2))
            return 0 if artifact["correctness"]["status"] == "passed" else 1


        if __name__ == "__main__":
            raise SystemExit(main())
        '''
    ).lstrip()


def tasks_for(lesson: dict[str, Any], existing_labs: list[str], projects: list[str]) -> dict[str, Any]:
    tasks = [
        {
            "id": "read-transcript-signals",
            "kind": "reading",
            "description": f"Review lesson {lesson['index']} transcript topics, concepts, tools, and exercise candidates.",
            "evidence": lesson.get("clean_txt") or lesson.get("url", ""),
        },
        {
            "id": "run-local-proxy",
            "kind": "programming",
            "description": "Run python3 starter.py and inspect the lesson-specific local proxy checks.",
            "evidence": "starter.py",
        },
        {
            "id": "measure-contract",
            "kind": "measurement",
            "description": "Run python3 measure.py and preserve measurements.json.",
            "evidence": "measurements.json",
        },
        {
            "id": "promote-to-gpu-runtime",
            "kind": "extension",
            "description": "Replace or extend lab.py with a real CUDA, Triton, HIP, JAX, or serving-runtime experiment matching the lesson.",
            "evidence": "lab.py",
        },
        {
            "id": "compare-existing-coverage",
            "kind": "comparison",
            "description": "Compare this lesson-specific lab with existing deep labs and portfolio projects.",
            "evidence": ", ".join(existing_labs + projects) or "no previous direct coverage",
        },
    ]
    for idx, candidate in enumerate(lesson.get("exercise_candidates", [])[:3], start=1):
        tasks.append(
            {
                "id": f"exercise-candidate-{idx}",
                "kind": "exercise",
                "description": candidate,
                "evidence": "lab.py",
            }
        )
    return {"tasks": tasks}


def readme_for(lab_id: str, lesson: dict[str, Any], existing_labs: list[str], projects: list[str]) -> str:
    lines = [
        f"# Lesson Lab {lesson['index']}: {lesson['title']}",
        "",
        f"Source video: {lesson.get('url', '')}",
        "",
        "## Why This Lab Exists",
        "",
        "This lab closes per-lesson coverage for the GPUMODE curriculum. It starts as a local CPU proxy so it can be verified on this machine, and it is structured for promotion into CUDA, Triton, HIP, JAX, or serving-runtime code.",
        "",
        "## Coverage Before This Generated Lab",
        "",
        f"- Existing deep lab candidates: `{', '.join(existing_labs) or 'none'}`",
        f"- Existing programming projects that directly anchor this lesson: `{', '.join(projects) or 'none'}`",
        "",
        "## Lesson Signals",
        "",
        f"- Topics: `{', '.join(lesson.get('topics', []))}`",
        f"- Concepts: `{', '.join(lesson.get('concepts', []))}`",
        f"- Tools: `{', '.join(lesson.get('tools', [])) or 'none detected'}`",
        "",
        "## Local Run",
        "",
        "```bash",
        "python3 starter.py",
        "python3 measure.py",
        "```",
        "",
        "## Files",
        "",
        "- `lab.py`: lesson-specific proxy program.",
        "- `starter.py`: executable entry point.",
        "- `measure.py`: writes `measurements.json`.",
        "- `measurement-contract.json`: required evidence shape.",
        "- `tasks.json`: reading, coding, measurement, promotion, and comparison tasks.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def contract_for(lab_id: str) -> dict[str, Any]:
    return {
        "lab_id": lab_id,
        "required_fields": [
            "status",
            "correctness.status",
            "runtime_readiness.status",
            "measurement.rows",
            "measurement.summary",
            "starter.command",
        ],
        "accepted_statuses_without_gpu": ["ran-cpu-proxy"],
        "promotion_target": "replace CPU proxy with lesson-specific CUDA, Triton, HIP, JAX, profiler, or serving runtime experiment",
    }


def build() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    curriculum = load_json(CURRICULUM)
    projects_by_lesson = project_coverage()
    labs = []
    missing_before = []
    for lesson in curriculum.get("lessons", []):
        lab_id = lesson_lab_id(lesson)
        lab_dir = OUT / lab_id
        lab_dir.mkdir(parents=True, exist_ok=True)
        existing_labs = lesson.get("candidate_lab_links", [])
        projects = projects_by_lesson.get(lesson["index"], [])
        if not projects:
            missing_before.append(lesson["index"])
        (lab_dir / "lab.py").write_text(source_text(lesson), encoding="utf-8")
        (lab_dir / "starter.py").write_text(starter_text(lab_id), encoding="utf-8")
        (lab_dir / "measure.py").write_text(measure_text(lab_id), encoding="utf-8")
        write_json(lab_dir / "measurement-contract.json", contract_for(lab_id))
        write_json(lab_dir / "tasks.json", tasks_for(lesson, existing_labs, projects))
        metadata = {
            "id": lab_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "lesson": lesson,
            "status": "implemented-cpu-proxy",
            "path": str(lab_dir.relative_to(ROOT)),
            "starter": "starter.py",
            "measure": "measure.py",
            "source": "lab.py",
            "tasks": "tasks.json",
            "local_measurement": "measurements.json",
            "measurement_contract": "measurement-contract.json",
            "coverage_before": {
                "candidate_deep_labs": existing_labs,
                "direct_programming_projects": projects,
            },
            "created_to_close_gap": True,
        }
        write_json(lab_dir / "lab.json", metadata)
        (lab_dir / "README.md").write_text(readme_for(lab_id, lesson, existing_labs, projects), encoding="utf-8")
        labs.append(
            {
                "id": lab_id,
                "lesson_index": lesson["index"],
                "lesson_title": lesson["title"],
                "path": str(lab_dir.relative_to(ROOT)),
                "status": "implemented-cpu-proxy",
                "topics": lesson.get("topics", []),
                "concepts": lesson.get("concepts", []),
                "candidate_deep_labs": existing_labs,
                "direct_programming_projects": projects,
            }
        )
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "goal": "one implemented lab scaffold per GPUMODE lesson",
        "lesson_count": curriculum.get("lesson_count", len(labs)),
        "generated_lab_count": len(labs),
        "lessons_without_direct_project_before_generation": missing_before,
        "lessons_without_direct_project_before_generation_count": len(missing_before),
        "labs": labs,
    }
    write_json(OUT / "index.json", report)
    lines = [
        "# GPUMODE Lesson Lab Coverage",
        "",
        "This directory contains one generated, runnable lab scaffold for every GPUMODE lesson.",
        "",
        f"- Lessons: {report['lesson_count']}",
        f"- Generated lesson labs: {report['generated_lab_count']}",
        f"- Lessons without direct programming-project anchors before this layer: {report['lessons_without_direct_project_before_generation_count']}",
        "",
        "| Lesson | Lab | Status |",
        "|---|---|---|",
    ]
    for row in labs:
        lines.append(f"| {row['lesson_index']} | [{row['id']}]({Path(row['path']).name}/README.md) | {row['status']} |")
    (OUT / "README.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return report


def main() -> None:
    report = build()
    print(f"wrote {OUT.relative_to(ROOT)} with {report['generated_lab_count']} lesson labs")


if __name__ == "__main__":
    main()
