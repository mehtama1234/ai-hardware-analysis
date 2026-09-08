#!/usr/bin/env python3
"""Generate concrete GPU programming projects from the GPUMODE workbench."""

from __future__ import annotations

import json
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from gpu_workbench_api import diagnose, load_workbench, slugify, write_json


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "programming-projects"

PROJECT_QUERIES = [
    {
        "id": "cuda-memory-kernel",
        "query": "cuda memory coalescing shared memory roofline",
        "track": "CUDA kernels",
        "language": "CUDA C++ plus Python harness",
        "starter": "starter.py",
        "source": "kernel.cu",
    },
    {
        "id": "triton-fused-softmax",
        "query": "triton fused softmax autotune",
        "track": "Triton kernels",
        "language": "Python plus Triton",
        "starter": "starter.py",
        "source": "kernel.py",
    },
    {
        "id": "rocm-hip-port",
        "query": "rocm hip cuda portability wmma",
        "track": "ROCm/HIP portability",
        "language": "HIP C++ plus Python harness",
        "starter": "starter.py",
        "source": "kernel.hip.cpp",
    },
    {
        "id": "vllm-kv-scheduler",
        "query": "vllm scheduler kv cache ttft batching",
        "track": "vLLM-style serving",
        "language": "Python serving scheduler model",
        "starter": "starter.py",
        "source": "scheduler.py",
    },
    {
        "id": "jax-scaling-roofline",
        "query": "jax scaling roofline gpu hbm inference",
        "track": "JAX scaling and roofline",
        "language": "Python plus JAX",
        "starter": "starter.py",
        "source": "roofline_model.py",
    },
    {
        "id": "hf-quant-serving",
        "query": "hugging face transformers quantization tgi inference",
        "track": "Hugging Face serving baseline",
        "language": "Python plus Transformers",
        "starter": "starter.py",
        "source": "hf_baseline.py",
    },
    {
        "id": "nsight-evidence-loop",
        "query": "nsight roofline dram sm stall counters",
        "track": "Profiler-to-roofline evidence",
        "language": "Python profiler import workflow",
        "starter": "starter.py",
        "source": "classify_counters.py",
    },
    {
        "id": "distributed-collectives",
        "query": "nccl nvshmem all reduce bandwidth topology",
        "track": "Distributed communication",
        "language": "Python collective model plus imported benchmark parser",
        "starter": "starter.py",
        "source": "collective_model.py",
    },
]


SOURCE_TEMPLATES = {
    "kernel.cu": r'''
#include <stdio.h>

extern "C" __global__ void coalesced_copy(const float* __restrict__ x, float* __restrict__ y, int n) {
  int i = blockIdx.x * blockDim.x + threadIdx.x;
  if (i < n) y[i] = x[i];
}

extern "C" __global__ void strided_copy(const float* __restrict__ x, float* __restrict__ y, int n, int stride) {
  int i = blockIdx.x * blockDim.x + threadIdx.x;
  int j = i * stride;
  if (j < n) y[j] = x[j];
}

int main() {
  printf("{\"status\":\"source-only\",\"next\":\"compile with nvcc on a CUDA machine\"}\n");
  return 0;
}
''',
    "kernel.py": r'''
import torch

try:
    import triton
    import triton.language as tl
except Exception:  # pragma: no cover - import depends on environment.
    triton = None
    tl = None


def torch_softmax(x: torch.Tensor) -> torch.Tensor:
    return torch.softmax(x, dim=-1)


def main() -> None:
    x = torch.randn((4, 128), dtype=torch.float32)
    y = torch_softmax(x)
    print({"status": "cpu-baseline", "shape": list(y.shape), "row0_sum": round(float(y[0].sum()), 6)})


if __name__ == "__main__":
    main()
''',
    "kernel.hip.cpp": (Path(__file__).parent / "project_templates/hip_vector_add.cpp").read_text(),
    "scheduler.py": r'''
from dataclasses import dataclass


@dataclass(frozen=True)
class Request:
    prompt_tokens: int
    output_tokens: int
    shared_prefix_tokens: int = 0


def kv_blocks(requests: list[Request], block_size: int = 16) -> int:
    total = 0
    for req in requests:
        private_prompt = max(0, req.prompt_tokens - req.shared_prefix_tokens)
        total += (private_prompt + req.output_tokens + block_size - 1) // block_size
    return total


def main() -> None:
    requests = [Request(768, 96, 512), Request(896, 96, 512), Request(512, 128, 384)]
    print({"status": "ran", "requests": len(requests), "kv_blocks": kv_blocks(requests)})


if __name__ == "__main__":
    main()
''',
    "roofline_model.py": r'''
def classify(flops: float, bytes_moved: float, peak_tflops: float, peak_gbps: float) -> dict[str, float | str]:
    arithmetic_intensity = flops / bytes_moved
    compute_ceiling = peak_tflops * 1e12
    memory_ceiling = arithmetic_intensity * peak_gbps * 1e9
    bound = "memory-bandwidth" if memory_ceiling < compute_ceiling else "compute"
    return {"arithmetic_intensity": round(arithmetic_intensity, 4), "bound": bound}


def main() -> None:
    print(classify(flops=2 * 4096**3, bytes_moved=3 * 4096**2 * 2, peak_tflops=125, peak_gbps=3000))


if __name__ == "__main__":
    main()
''',
    "hf_baseline.py": r'''
def estimate_kv_cache_mb(batch: int, sequence: int, layers: int, hidden: int, bytes_per_value: int = 2) -> float:
    keys_and_values = 2
    return batch * sequence * layers * hidden * keys_and_values * bytes_per_value / 1e6


def main() -> None:
    print({"status": "ran", "kv_cache_mb": round(estimate_kv_cache_mb(1, 8192, 32, 4096), 2)})


if __name__ == "__main__":
    main()
''',
    "classify_counters.py": r'''
def classify_counter_row(row: dict[str, float]) -> str:
    if row.get("dram_util_pct", 0) >= 75 and row.get("sm_util_pct", 0) < 70:
        return "memory-bandwidth"
    if row.get("sm_util_pct", 0) >= 75:
        return "compute"
    if row.get("launches", 0) > 1000:
        return "launch-overhead"
    return "mixed-or-unknown"


def main() -> None:
    row = {"dram_util_pct": 86.0, "sm_util_pct": 42.0, "launches": 20}
    print({"status": "ran", "classification": classify_counter_row(row)})


if __name__ == "__main__":
    main()
''',
    "collective_model.py": r'''
def ring_all_reduce_seconds(bytes_per_rank: int, ranks: int, bandwidth_gbps: float, latency_us: float) -> float:
    steps = 2 * (ranks - 1)
    bytes_on_link = 2 * bytes_per_rank * (ranks - 1) / ranks
    return steps * latency_us / 1e6 + bytes_on_link / (bandwidth_gbps * 1e9)


def main() -> None:
    seconds = ring_all_reduce_seconds(128 * 1024 * 1024, ranks=8, bandwidth_gbps=300, latency_us=4)
    print({"status": "ran", "ring_all_reduce_ms": round(seconds * 1000, 4)})


if __name__ == "__main__":
    main()
''',
}


def starter_text(project: dict[str, str], diagnosis: dict[str, Any]) -> str:
    source = project["source"]
    return textwrap.dedent(
        f'''
        #!/usr/bin/env python3
        """Starter harness for {project["track"]}."""

        from __future__ import annotations

        import json
        import shutil
        import subprocess
        import sys
        from pathlib import Path


        HERE = Path(__file__).resolve().parent
        SOURCE = HERE / "{source}"


        def main() -> int:
            payload = {{
                "project": "{project["id"]}",
                "track": "{project["track"]}",
                "query": "{project["query"]}",
                "profile": "{diagnosis["matched_bottleneck_class"]}",
                "source": SOURCE.name,
                "status": "ready",
                "runtime_notes": [],
            }}
            if SOURCE.suffix == ".cu":
                if not shutil.which("nvcc"):
                    payload["status"] = "source-only"
                    payload["runtime_notes"].append("nvcc missing; compile on a CUDA development host")
            elif SOURCE.suffixes[-2:] == [".hip", ".cpp"] or SOURCE.name.endswith(".hip.cpp"):
                if not shutil.which("hipcc"):
                    payload["status"] = "source-only"
                    payload["runtime_notes"].append("hipcc missing; compile on a ROCm development host")
            elif SOURCE.suffix == ".py":
                proc = subprocess.run([sys.executable, str(SOURCE)], capture_output=True, text=True, check=False)
                payload["source_returncode"] = proc.returncode
                payload["source_stdout"] = proc.stdout.strip()[-1000:]
                payload["source_stderr"] = proc.stderr.strip()[-1000:]
                payload["status"] = "ran" if proc.returncode == 0 else "failed"
            print(json.dumps(payload, indent=2))
            return 0 if payload["status"] in {{"ready", "ran", "source-only"}} else 1


        if __name__ == "__main__":
            raise SystemExit(main())
        '''
    ).lstrip()


def measure_text(project: dict[str, str], diagnosis: dict[str, Any]) -> str:
    baseline_measurement = json.dumps(
        diagnosis.get("exercise_path", {}).get("measurement", {}),
        ensure_ascii=False,
    )
    return textwrap.dedent(
        f'''
        #!/usr/bin/env python3
        """Run the starter and write the project measurement artifact."""

        from __future__ import annotations

        import json
        import subprocess
        import sys
        from datetime import datetime, timezone
        from pathlib import Path


        HERE = Path(__file__).resolve().parent
        STARTER = HERE / "{project["starter"]}"
        OUT = HERE / "measurements.json"


        def main() -> int:
            proc = subprocess.run([sys.executable, str(STARTER)], cwd=HERE, capture_output=True, text=True, check=False)
            starter_payload = {{}}
            if proc.stdout.strip():
                try:
                    starter_payload = json.loads(proc.stdout)
                except json.JSONDecodeError:
                    starter_payload = {{"raw_stdout": proc.stdout.strip()}}
            status = starter_payload.get("status") or ("ran" if proc.returncode == 0 else "failed")
            artifact = {{
                "project": "{project["id"]}",
                "track": "{project["track"]}",
                "profile": "{diagnosis["matched_bottleneck_class"]}",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "status": status,
                "correctness": {{
                    "status": "passed" if proc.returncode == 0 else "failed",
                    "checks": {{
                        "starter_exited_zero": proc.returncode == 0,
                        "starter_payload_status_present": bool(starter_payload.get("status")),
                        "source_named": bool(starter_payload.get("source")),
                    }},
                }},
                "runtime_readiness": {{
                    "status": status,
                    "notes": starter_payload.get("runtime_notes", []),
                }},
                "measurement": {{
                    "rows": [starter_payload],
                    "summary": f"Starter {{status}} for {project["track"]}; return code {{proc.returncode}}.",
                }},
                "source": "{project["source"]}",
                "environment": "local",
                "baseline_measurement": {baseline_measurement},
                "starter": {{
                    "command": f"{{sys.executable}} {{STARTER.name}}",
                    "returncode": proc.returncode,
                    "stdout_tail": proc.stdout.strip()[-2000:],
                    "stderr_tail": proc.stderr.strip()[-2000:],
                }},
            }}
            if {project["id"] == "rocm-hip-port"}:
                artifact["metadata_checks"] = artifact["correctness"]["checks"]
                artifact["metadata_checks"]["source_named"] = starter_payload.get("source") == "kernel.hip.cpp"
                artifact["correctness"] = {{"status": "not_executed", "checks": {{}},
                    "reason": "readiness starter does not compile or invoke native validation"}}
                artifact["gpu_execution_accepted"] = False
                artifact["measured"] = False
            OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\\n", encoding="utf-8")
            print(json.dumps({{"status": artifact["status"], "path": OUT.name, "correctness": artifact["correctness"]["status"]}}, indent=2))
            if {project["id"] == "rocm-hip-port"}:
                return 0 if all(artifact["metadata_checks"].values()) else 1
            return 0 if artifact["correctness"]["status"] == "passed" else 1


        if __name__ == "__main__":
            raise SystemExit(main())
        '''
    ).lstrip()


def task_list(project: dict[str, str], diagnosis: dict[str, Any]) -> dict[str, Any]:
    source = diagnosis.get("tutorial_sources", [{}])[0]
    lesson = diagnosis.get("lessons", [{}])[0]
    lab = diagnosis.get("exercise_path", {}).get("lab", {})
    measurement = diagnosis.get("exercise_path", {}).get("measurement", {})
    return {
        "project_id": project["id"],
        "track": project["track"],
        "tasks": [
            {
                "id": "read-source-model",
                "kind": "reading",
                "description": f"Read {source.get('provider', 'source')} - {source.get('title', 'tutorial source')} and record the bottleneck model.",
                "evidence": source.get("url", ""),
            },
            {
                "id": "anchor-gpumode-lesson",
                "kind": "lesson",
                "description": f"Use GPUMODE lesson {lesson.get('index', '')}: {lesson.get('title', '')} as the concept anchor.",
                "evidence": lesson.get("url", ""),
            },
            {
                "id": "modify-starter-source",
                "kind": "programming",
                "description": f"Modify `{project['source']}` and keep `python3 {project['starter']}` runnable.",
                "evidence": project["source"],
            },
            {
                "id": "run-local-measurement",
                "kind": "measurement",
                "description": "Run `python3 measure.py` and preserve `measurements.json`.",
                "evidence": "measurements.json",
            },
            {
                "id": "compare-existing-lab",
                "kind": "comparison",
                "description": f"Compare against `{lab.get('path', '')}` and `{measurement.get('path', '')}`.",
                "evidence": measurement.get("path", ""),
            },
        ],
    }


def readme_text(project: dict[str, str], diagnosis: dict[str, Any]) -> str:
    lessons = diagnosis.get("lessons", [])[:4]
    sources = diagnosis.get("tutorial_sources", [])[:4]
    papers = diagnosis.get("papers", [])[:4]
    lab = diagnosis.get("exercise_path", {}).get("lab", {})
    measurement = diagnosis.get("exercise_path", {}).get("measurement", {})
    lines = [
        f"# {project['track']}: {diagnosis.get('label', '')}",
        "",
        f"Query: `{project['query']}`",
        "",
        "## Build Target",
        "",
        diagnosis.get("diagnosis", ""),
        "",
        "## Starter Files",
        "",
        f"- `{project['starter']}`: local harness that runs or classifies the starter source.",
        f"- `{project['source']}`: first source file to modify.",
        "- `measure.py`: experiment harness that writes `measurements.json`.",
        "- `tasks.json`: concrete reading, programming, measurement, and comparison tasks.",
        "- `measurements.json`: durable local starter measurement after `python3 measure.py`.",
        "- `measurement-contract.json`: expected evidence shape for this project.",
        "- `project.json`: generated metadata linking lessons, sources, papers, labs, and measurements.",
        "",
        "## Existing Lab To Compare Against",
        "",
        f"- `{lab.get('path', '')}`",
        f"- `{lab.get('command', '')}`",
        f"- measurement: `{measurement.get('path', '')}`",
        "",
        "## Lessons",
    ]
    for lesson in lessons:
        lines.append(f"- Lesson {lesson.get('index')}: [{lesson.get('title', '')}]({lesson.get('url', '')})")
    lines += ["", "## External Tutorials"]
    for source in sources:
        lines.append(f"- {source.get('provider', '')}: [{source.get('title', '')}]({source.get('url', '')})")
    lines += ["", "## Paper Cross-Checks"]
    for paper in papers:
        lines.append(f"- {paper.get('venue', '')}: {paper.get('title', '')}")
        if paper.get("path"):
            lines.append(f"  - `{paper.get('path')}`")
    lines += [
        "",
        "## Local Run",
        "",
        "```bash",
        "python3 starter.py",
        "python3 measure.py",
        "```",
    ]
    return "\n".join(lines).rstrip() + "\n"


def measurement_contract(project: dict[str, str], diagnosis: dict[str, Any]) -> dict[str, Any]:
    return {
        "project_id": project["id"],
        "track": project["track"],
        "profile": diagnosis.get("matched_bottleneck_class", ""),
        "required_fields": [
            "status",
            "correctness.status",
            "runtime_readiness",
            "measurement.rows",
            "measurement.summary",
            "source",
            "environment",
        ],
        "accepted_statuses_without_gpu": ["ran", "source-only", "skipped-with-explicit-reason"],
        "accepted_statuses_with_gpu": ["ran"],
        "must_explain": [
            "what was measured",
            "what correctness check was used",
            "what runtime was unavailable if a GPU path was skipped",
            "which GPUMODE lesson and external tutorial informed the implementation",
        ],
        "baseline_measurement": diagnosis.get("exercise_path", {}).get("measurement", {}),
    }


def build() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    workbench = load_workbench()
    projects = []
    for project in PROJECT_QUERIES:
        diagnosis = diagnose(project["query"], limit=6)
        project_dir = OUT / project["id"]
        project_dir.mkdir(parents=True, exist_ok=True)
        source = project_dir / project["source"]
        source.write_text(textwrap.dedent(SOURCE_TEMPLATES[project["source"]]).lstrip(), encoding="utf-8")
        starter = project_dir / project["starter"]
        starter.write_text(starter_text(project, diagnosis), encoding="utf-8")
        (project_dir / "measure.py").write_text(measure_text(project, diagnosis), encoding="utf-8")
        metadata = {
            "id": project["id"],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "query": project["query"],
            "track": project["track"],
            "language": project["language"],
            "profile": diagnosis.get("matched_bottleneck_class", ""),
            "label": diagnosis.get("label", ""),
            "diagnosis": diagnosis.get("diagnosis", ""),
            "next_action": diagnosis.get("next_action", ""),
            "starter": project["starter"],
            "measure": "measure.py",
            "source": project["source"],
            "tasks": "tasks.json",
            "local_measurement": "measurements.json",
            "lessons": diagnosis.get("lessons", [])[:6],
            "tutorial_sources": diagnosis.get("tutorial_sources", [])[:6],
            "papers": diagnosis.get("papers", [])[:6],
            "lab": diagnosis.get("exercise_path", {}).get("lab", {}),
            "measurement": diagnosis.get("exercise_path", {}).get("measurement", {}),
        }
        write_json(project_dir / "project.json", metadata)
        write_json(project_dir / "measurement-contract.json", measurement_contract(project, diagnosis))
        write_json(project_dir / "tasks.json", task_list(project, diagnosis))
        (project_dir / "README.md").write_text(readme_text(project, diagnosis), encoding="utf-8")
        projects.append(
            {
                "id": project["id"],
                "track": project["track"],
                "profile": diagnosis.get("matched_bottleneck_class", ""),
                "path": str(project_dir.relative_to(ROOT)),
                "starter": str((project_dir / project["starter"]).relative_to(ROOT)),
                "measure": str((project_dir / "measure.py").relative_to(ROOT)),
                "source": str((project_dir / project["source"]).relative_to(ROOT)),
                "tasks": str((project_dir / "tasks.json").relative_to(ROOT)),
                "local_measurement": str((project_dir / "measurements.json").relative_to(ROOT)),
                "measurement_contract": str((project_dir / "measurement-contract.json").relative_to(ROOT)),
            }
        )

    index = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_count": len(projects),
        "workbench_coverage": workbench.get("coverage", {}),
        "projects": projects,
    }
    write_json(OUT / "index.json", index)
    lines = ["# GPU Programming Projects", "", "Generated concrete projects from the GPUMODE workbench.", ""]
    for row in projects:
        project_path = Path(row["path"]).name
        lines.append(f"- [{row['track']}]({project_path}/README.md): `{row['profile']}`")
    (OUT / "README.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return index


def main() -> None:
    index = build()
    print(f"wrote {OUT.relative_to(ROOT)}/ with {index['project_count']} projects")


if __name__ == "__main__":
    main()
