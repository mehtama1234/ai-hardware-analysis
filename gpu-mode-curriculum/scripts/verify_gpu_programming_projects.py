#!/usr/bin/env python3
"""Verify generated GPU programming project artifacts."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "programming-projects"
SITE = ROOT / "site"
REQUIRED_TRACKS = {
    "CUDA kernels",
    "Triton kernels",
    "ROCm/HIP portability",
    "vLLM-style serving",
    "JAX scaling and roofline",
    "Hugging Face serving baseline",
    "Profiler-to-roofline evidence",
    "Distributed communication",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not (PROJECTS / "index.json").exists():
        subprocess.run([sys.executable, "scripts/build_gpu_programming_projects.py"], cwd=ROOT, check=True)
    if not (PROJECTS / "project-run-report.json").exists():
        subprocess.run([sys.executable, "scripts/run_gpu_programming_projects.py"], cwd=ROOT, check=True)
    if not (PROJECTS / "capstone-portfolio.json").exists():
        subprocess.run([sys.executable, "scripts/build_gpu_project_capstone.py"], cwd=ROOT, check=True)
    if not (PROJECTS / "notebook-index.json").exists():
        subprocess.run([sys.executable, "scripts/build_gpu_project_notebooks.py"], cwd=ROOT, check=True)
    index = load_json(PROJECTS / "index.json")
    run_report = load_json(PROJECTS / "project-run-report.json")
    capstone = load_json(PROJECTS / "capstone-portfolio.json")
    notebook_index = load_json(PROJECTS / "notebook-index.json")
    projects = index.get("projects", [])
    require(index.get("project_count") == len(projects), "project_count does not match project rows")
    require(len(projects) >= 8, "expected at least eight generated programming projects")
    require(REQUIRED_TRACKS.issubset({row.get("track") for row in projects}), "missing required project tracks")
    require(run_report.get("project_count") == len(projects), "run report project count does not match project index")
    require(run_report.get("failed_contracts") == 0, "run report has failed contracts")
    require(run_report.get("passed_contracts") == len(projects), "not every project contract passed")
    require((PROJECTS / "project-run-report.md").exists(), "missing Markdown project run report")
    require(capstone.get("project_count") == len(projects), "capstone project count does not match project index")
    require(capstone.get("graph", {}).get("edge_count", 0) >= len(projects) - 1, "capstone dependency graph is too small")
    require(len(capstone.get("execution_order", [])) == len(projects), "capstone execution order does not cover every project")
    require(capstone.get("passed_contracts") == len(projects), "capstone does not record every passing contract")
    require((PROJECTS / "capstone-portfolio.md").exists(), "missing Markdown capstone portfolio")
    require(notebook_index.get("notebook_count") == len(projects), "notebook index does not cover every project")
    notebooks_by_project = {row.get("project_id"): row for row in notebook_index.get("notebooks", [])}

    if (SITE / "projects.html").exists():
        projects_html = (SITE / "projects.html").read_text(encoding="utf-8")
        require("GPU programming projects" in projects_html, "projects.html missing project title")
        require("Project Index" in projects_html, "projects.html missing project table")
        require("capstone.html" in projects_html, "projects.html missing capstone link")
    if (SITE / "capstone.html").exists():
        capstone_html = (SITE / "capstone.html").read_text(encoding="utf-8")
        require("GPU programming capstone" in capstone_html, "capstone.html missing title")
        require("Execution Order" in capstone_html, "capstone.html missing execution order")

    starter_results = {}
    for row in projects:
        project_dir = ROOT / row["path"]
        metadata = load_json(project_dir / "project.json")
        contract = load_json(project_dir / "measurement-contract.json")
        tasks = load_json(project_dir / metadata.get("tasks", "tasks.json"))
        readme = (project_dir / "README.md").read_text(encoding="utf-8")
        source = project_dir / metadata["source"]
        starter = project_dir / metadata["starter"]
        measure = project_dir / metadata.get("measure", "measure.py")
        local_measurement = project_dir / metadata.get("local_measurement", "measurements.json")
        require(source.exists(), f"missing source for {row['id']}")
        require(starter.exists(), f"missing starter for {row['id']}")
        require(measure.exists(), f"missing measure.py for {row['id']}")
        require(local_measurement.exists(), f"missing measurements.json for {row['id']}")
        notebook_row = notebooks_by_project.get(row["id"], {})
        notebook_path = ROOT / notebook_row.get("path", "")
        require(notebook_path.exists(), f"missing notebook for {row['id']}")
        notebook = load_json(notebook_path)
        require(notebook.get("nbformat") == 4, f"{row['id']} notebook has wrong nbformat")
        require(len(notebook.get("cells", [])) >= 7, f"{row['id']} notebook has too few cells")
        require(
            notebook.get("metadata", {}).get("gpu_workbench", {}).get("project_id") == row["id"],
            f"{row['id']} notebook missing gpu_workbench metadata",
        )
        measurement_artifact = load_json(local_measurement)
        require(metadata.get("lessons"), f"{row['id']} missing GPUMODE lessons")
        require(metadata.get("tutorial_sources"), f"{row['id']} missing tutorial sources")
        require(metadata.get("lab", {}).get("path"), f"{row['id']} missing lab link")
        require(metadata.get("measurement", {}).get("path"), f"{row['id']} missing measurement link")
        require(contract.get("required_fields"), f"{row['id']} missing measurement contract fields")
        require(len(tasks.get("tasks", [])) >= 5, f"{row['id']} missing task milestones")
        require(measurement_artifact.get("correctness", {}).get("status") == "passed", f"{row['id']} measurement correctness did not pass")
        require(measurement_artifact.get("measurement", {}).get("rows"), f"{row['id']} measurement rows missing")
        require("## Local Run" in readme and "## Existing Lab To Compare Against" in readme, f"{row['id']} README missing runnable sections")
        require("python3 measure.py" in readme, f"{row['id']} README missing measure command")

        proc = subprocess.run(
            [sys.executable, str(starter)],
            cwd=project_dir,
            capture_output=True,
            text=True,
            check=False,
        )
        require(proc.returncode == 0, f"{row['id']} starter failed: {proc.stderr}")
        payload = json.loads(proc.stdout)
        require(payload.get("status") in {"ready", "ran", "source-only"}, f"{row['id']} starter returned bad status")
        starter_results[row["id"]] = payload.get("status")
        site_page = SITE / f"project-{row['id']}.html"
        if site_page.exists():
            page = site_page.read_text(encoding="utf-8")
            require(row["track"] in page, f"{site_page.name} missing project track")
            require("Contract Fields" in page, f"{site_page.name} missing contract section")
            require(".ipynb" in page, f"{site_page.name} missing notebook link")

    print(
        json.dumps(
            {
                "facts": {
                    "project_count": len(projects),
                    "tracks": sorted({row.get("track") for row in projects}),
                    "run_report_passed_contracts": run_report.get("passed_contracts"),
                    "capstone_edges": capstone.get("graph", {}).get("edge_count"),
                    "notebook_count": notebook_index.get("notebook_count"),
                    "starter_statuses": starter_results,
                },
                "failures": [],
            },
            indent=2,
        )
    )
    print("GPU programming project verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
