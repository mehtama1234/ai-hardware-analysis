#!/usr/bin/env python3
"""Generate Jupyter notebooks for GPU programming projects."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "programming-projects"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def markdown_cell(source: str) -> dict[str, Any]:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def code_cell(source: str) -> dict[str, Any]:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


def notebook_for(project: dict[str, Any], metadata: dict[str, Any], tasks: dict[str, Any], measurement: dict[str, Any]) -> dict[str, Any]:
    lessons = "\n".join(
        f"- Lesson {lesson.get('index')}: [{lesson.get('title', '')}]({lesson.get('url', '')})"
        for lesson in metadata.get("lessons", [])[:5]
    )
    sources = "\n".join(
        f"- {source.get('provider', '')}: [{source.get('title', '')}]({source.get('url', '')})"
        for source in metadata.get("tutorial_sources", [])[:5]
    )
    task_lines = "\n".join(
        f"- `{task.get('id')}` ({task.get('kind')}): {task.get('description')}"
        for task in tasks.get("tasks", [])
    )
    cells = [
        markdown_cell(
            f"""# {metadata.get('track', project['track'])}: {metadata.get('label', '')}

Query: `{metadata.get('query', '')}`

{metadata.get('diagnosis', '')}
"""
        ),
        markdown_cell(f"## Read First\n\n{sources}"),
        markdown_cell(f"## GPUMODE Anchors\n\n{lessons}"),
        markdown_cell(f"## Project Tasks\n\n{task_lines}"),
        code_cell(
            """from pathlib import Path
import json

HERE = Path.cwd()
print("project dir:", HERE)
print(json.dumps(json.loads(Path("project.json").read_text()), indent=2)[:1200])
"""
        ),
        code_cell(
            """import subprocess, sys

proc = subprocess.run([sys.executable, "starter.py"], capture_output=True, text=True)
print(proc.stdout)
print(proc.stderr)
assert proc.returncode == 0
"""
        ),
        code_cell(
            """import subprocess, sys, json
from pathlib import Path

proc = subprocess.run([sys.executable, "measure.py"], capture_output=True, text=True)
print(proc.stdout)
print(proc.stderr)
assert proc.returncode == 0
measurement = json.loads(Path("measurements.json").read_text())
assert measurement["correctness"]["status"] == "passed"
measurement
"""
        ),
        markdown_cell(
            f"""## Latest Local Evidence

- Status: `{measurement.get('status', 'unknown')}`
- Correctness: `{measurement.get('correctness', {}).get('status', 'unknown')}`
- Baseline lab artifact: `{metadata.get('measurement', {}).get('path', '')}`
"""
        ),
    ]
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "pygments_lexer": "ipython3",
            },
            "gpu_workbench": {
                "project_id": project["id"],
                "track": project["track"],
                "profile": project["profile"],
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def build() -> dict[str, Any]:
    index = load_json(PROJECTS / "index.json")
    notebooks = []
    for project in index.get("projects", []):
        project_dir = ROOT / project["path"]
        metadata = load_json(project_dir / "project.json")
        tasks = load_json(project_dir / metadata.get("tasks", "tasks.json"))
        measurement_path = project_dir / metadata.get("local_measurement", "measurements.json")
        measurement = load_json(measurement_path) if measurement_path.exists() else {}
        notebook = notebook_for(project, metadata, tasks, measurement)
        path = project_dir / f"{project['id']}.ipynb"
        write_json(path, notebook)
        notebooks.append(
            {
                "project_id": project["id"],
                "track": project["track"],
                "profile": project["profile"],
                "path": str(path.relative_to(ROOT)),
                "cell_count": len(notebook["cells"]),
            }
        )
    notebook_index = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "notebook_count": len(notebooks),
        "notebooks": notebooks,
    }
    write_json(PROJECTS / "notebook-index.json", notebook_index)
    return notebook_index


def main() -> None:
    index = build()
    print(f"wrote programming-projects/notebook-index.json with {index['notebook_count']} notebooks")


if __name__ == "__main__":
    main()
