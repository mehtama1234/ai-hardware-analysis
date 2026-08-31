"""Verify the generated GPUMODE curriculum/workbench end to end."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
LAB_ROOT = REPO_ROOT / "gpu-kernels-serving-lab"

REQUIRED_PROFILES = {
    "memory-bandwidth",
    "profiling-roofline",
    "warp-synchronization",
    "triton-autotune",
    "tensor-core-cutlass",
    "rocm-hip-portability",
    "pytorch-compiler-fusion",
    "attention-serving",
    "serving-scheduler",
    "quantized-numerics",
    "distributed-communication",
}

REQUIRED_LAB_ARTIFACTS = [
    "15-gpumode-coalescing/out_gpumode_coalescing.json",
    "16-gpumode-warp-reductions/out_gpumode_warp_reductions.json",
    "17-gpumode-triton-autotune/out_gpumode_triton_autotune.json",
    "18-gpumode-online-softmax/out_gpumode_online_softmax.json",
    "19-gpumode-torch-compile/out_gpumode_torch_compile.json",
    "20-gpumode-vllm-scheduler/out_gpumode_vllm_scheduler.json",
    "21-gpumode-quantized-kernels/out_gpumode_quantized_kernels.json",
    "22-gpumode-nsight-roofline/out_gpumode_nsight_roofline.json",
    "23-gpumode-shared-memory-gemm/out_gpumode_shared_memory_gemm.json",
    "24-gpumode-tensor-core-cutlass/out_gpumode_tensor_core_cutlass.json",
    "25-gpumode-rocm-hip-portability/out_gpumode_rocm_hip_portability.json",
    "26-gpumode-distributed-communication/out_gpumode_distributed_communication.json",
]


@dataclass
class CheckState:
    failures: list[str]
    facts: dict[str, Any]

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.failures.append(message)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def require_file(state: CheckState, path: Path) -> bool:
    exists = path.exists()
    state.require(exists, f"missing required file: {path.relative_to(REPO_ROOT)}")
    return exists


def verify_curriculum(state: CheckState) -> None:
    required = [
        ROOT / "analysis/gpumode-curriculum.json",
        ROOT / "analysis/curriculum-graph.json",
        ROOT / "analysis/end-to-end-audit.json",
        ROOT / "analysis/end-to-end-audit.md",
        ROOT / "analysis/lesson-intelligence.json",
        ROOT / "analysis/topic-map.json",
        ROOT / "analysis/gpu-systems-workbench.json",
        ROOT / "analysis/lesson-corpus-bridges.json",
        ROOT / "analysis/latest-measurements-index.json",
        ROOT / "analysis/tutorial-sources.json",
        ROOT / "analysis/tutorial-exercise-paths.json",
        ROOT / "raw-material/youtube/transcript-index.json",
        ROOT / "site/index.html",
        ROOT / "site/workbench.html",
    ]
    for path in required:
        require_file(state, path)

    curriculum = load_json(ROOT / "analysis/gpumode-curriculum.json")
    audit = load_json(ROOT / "analysis/end-to-end-audit.json")
    graph = load_json(ROOT / "analysis/curriculum-graph.json")
    intelligence = load_json(ROOT / "analysis/lesson-intelligence.json")
    transcript_index = load_json(ROOT / "raw-material/youtube/transcript-index.json")

    lessons = curriculum.get("lessons", [])
    available_transcripts = [
        item for item in transcript_index if item.get("transcript_status") == "available"
    ]
    missing_transcripts = [
        item for item in transcript_index if item.get("transcript_status") != "available"
    ]

    state.facts["lessons"] = len(lessons)
    state.facts["lesson_intelligence_records"] = len(intelligence)
    state.facts["transcript_index_records"] = len(transcript_index)
    state.facts["available_transcripts"] = len(available_transcripts)
    state.facts["missing_transcripts"] = len(missing_transcripts)
    state.facts["audit_status"] = audit.get("overall_status")
    state.facts["graph_nodes"] = graph.get("node_count")
    state.facts["graph_edges"] = graph.get("edge_count")

    state.require(len(lessons) >= 100, "expected at least 100 GPUMODE lessons")
    state.require(
        len(lessons) == len(intelligence),
        "lesson count does not match lesson-intelligence records",
    )
    state.require(
        len(lessons) == len(transcript_index),
        "lesson count does not match transcript index records",
    )
    state.require(available_transcripts, "expected at least one available transcript")
    state.require(
        audit.get("overall_status") == "proven-with-runtime-caveats",
        "end-to-end audit status is not proven-with-runtime-caveats",
    )
    state.require(
        all(item.get("status") != "missing-or-incomplete" for item in audit.get("items", [])),
        "end-to-end audit has missing/incomplete items",
    )
    state.require(
        all(item.get("topics") for item in intelligence),
        "every intelligence record must have topic labels",
    )
    state.require(
        all(item.get("exercise_candidates") for item in intelligence),
        "every intelligence record must have candidate exercises",
    )
    graph_nodes = graph.get("nodes", [])
    graph_edges = graph.get("edges", [])
    node_kinds = {node.get("kind") for node in graph_nodes}
    edge_relations = {edge.get("relation") for edge in graph_edges}
    state.require(graph.get("node_count") == len(graph_nodes), "graph node_count does not match nodes")
    state.require(graph.get("edge_count") == len(graph_edges), "graph edge_count does not match edges")
    state.require(graph.get("node_count", 0) >= len(lessons), "graph should include at least lesson nodes")
    state.require(graph.get("edge_count", 0) >= len(lessons) * 3, "graph should include lesson/topic/concept/prerequisite edges")
    state.require(
        {"lesson", "topic", "concept", "prerequisite", "lab"}.issubset(node_kinds),
        f"graph missing node kinds: {sorted({'lesson', 'topic', 'concept', 'prerequisite', 'lab'} - node_kinds)}",
    )
    state.require(
        {"covers_topic", "teaches_concept", "prerequisite_for", "has_runnable_lab", "prepares_topic"}.issubset(edge_relations),
        "graph missing required curriculum edge relations",
    )
    state.require(graph.get("practical_topic_order"), "graph missing practical topic order")
    graph_query = subprocess.run(
        [
            sys.executable,
            "scripts/query_curriculum_graph.py",
            "cuda memory coalescing",
            "--json",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    state.require(graph_query.returncode == 0, "query_curriculum_graph.py failed")
    if graph_query.returncode == 0:
        result = json.loads(graph_query.stdout)
        state.require(result.get("matches"), "graph query produced no matches")
        state.require(result.get("profiles"), "graph query produced no workbench profile matches")
        state.require(
            result.get("graph", {}).get("node_count") == graph.get("node_count"),
            "graph query node count does not match graph artifact",
        )
    lab_graph_query = subprocess.run(
        [
            sys.executable,
            "scripts/query_curriculum_graph.py",
            "triton fused softmax lab",
            "--json",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    state.require(lab_graph_query.returncode == 0, "query_curriculum_graph.py lab query failed")
    if lab_graph_query.returncode == 0:
        result = json.loads(lab_graph_query.stdout)
        lab_matches = [
            row
            for row in result.get("matches", [])
            if row.get("node", {}).get("kind") == "lab"
        ]
        state.require(lab_matches, "graph lab query produced no lab matches")
        state.require(
            any(row.get("candidate_lessons") for row in lab_matches),
            "graph lab query did not expose candidate lesson anchors",
        )
    corpus_query = subprocess.run(
        [
            sys.executable,
            "scripts/query_corpus_bridge.py",
            "llm inference gpu memory",
            "--json",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    state.require(corpus_query.returncode == 0, "query_corpus_bridge.py failed")
    if corpus_query.returncode == 0:
        result = json.loads(corpus_query.stdout)
        state.require(result.get("papers"), "corpus bridge query produced no paper matches")
        state.require(result.get("lessons"), "corpus bridge query produced no lesson matches")
    measurement_query = subprocess.run(
        [
            sys.executable,
            "scripts/query_measurements.py",
            "cuda skipped triton vllm",
            "--json",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    state.require(measurement_query.returncode == 0, "query_measurements.py failed")
    if measurement_query.returncode == 0:
        result = json.loads(measurement_query.stdout)
        state.require(result.get("matches"), "measurement query produced no matches")
    index_html = (ROOT / "site/index.html").read_text(encoding="utf-8")
    state.require("Curriculum Graph" in index_html, "index.html missing curriculum graph section")

    sampled_pages = [
        ROOT / "site/lesson-001.html",
        ROOT / f"site/lesson-{len(lessons):03d}.html",
    ]
    for path in sampled_pages:
        if require_file(state, path):
            html = path.read_text(encoding="utf-8")
            state.require("Candidate Runnable Labs" in html, f"{path.name} missing lab links")
            state.require(
                "Workbench Bridge Matches" in html,
                f"{path.name} missing bridge matches",
            )

    missing_pages = [
        idx
        for idx in range(1, len(lessons) + 1)
        if not (ROOT / f"site/lesson-{idx:03d}.html").exists()
    ]
    state.require(not missing_pages, f"missing lesson pages: {missing_pages[:10]}")


def verify_workbench(state: CheckState) -> None:
    workbench = load_json(ROOT / "analysis/gpu-systems-workbench.json")
    graph = load_json(ROOT / "analysis/curriculum-graph.json")
    corpus_bridges = load_json(ROOT / "analysis/lesson-corpus-bridges.json")
    latest_measurements = load_json(ROOT / "analysis/latest-measurements-index.json")
    tutorial_sources = load_json(ROOT / "analysis/tutorial-sources.json")
    exercise_paths = load_json(ROOT / "analysis/tutorial-exercise-paths.json")
    profiles = workbench.get("profiles", [])
    profile_by_id = {profile.get("id"): profile for profile in profiles}
    coverage = workbench.get("coverage", {})

    state.facts["profile_count"] = len(profiles)
    state.facts["implemented_labs"] = coverage.get("implemented_labs")
    state.facts["measurement_artifacts"] = coverage.get("measurement_artifacts")
    state.facts["paper_json"] = coverage.get("paper_json")
    state.facts["tutorial_sources"] = coverage.get("tutorial_sources")
    state.facts["tutorial_exercise_paths"] = coverage.get("tutorial_exercise_paths")
    state.facts["lesson_corpus_bridge_papers"] = coverage.get("lesson_corpus_bridge_papers")
    state.facts["lesson_corpus_bridge_lessons"] = coverage.get("lesson_corpus_bridge_lessons")
    state.facts["lesson_corpus_bridge_links"] = coverage.get("lesson_corpus_bridge_links")
    state.facts["latest_measurement_index_rows"] = coverage.get("latest_measurement_index_rows")
    state.facts["latest_measurement_correctness_passed"] = coverage.get("latest_measurement_correctness_passed")
    state.facts["latest_measurement_runtime_skips"] = coverage.get("latest_measurement_runtime_skips")

    state.require(
        coverage.get("profile_count") == len(profiles),
        "coverage.profile_count does not match profile list",
    )
    state.require(len(profiles) >= 11, "expected at least 11 workbench profiles")
    state.require(
        coverage.get("implemented_labs", 0) >= 12,
        "expected at least 12 implemented deep labs",
    )
    state.require(
        coverage.get("measurement_artifacts", 0) >= 28,
        "expected at least 28 measurement artifacts",
    )
    state.require(
        coverage.get("graph_nodes") == graph.get("node_count"),
        "coverage.graph_nodes does not match curriculum graph",
    )
    state.require(
        coverage.get("graph_edges") == graph.get("edge_count"),
        "coverage.graph_edges does not match curriculum graph",
    )
    state.require(
        coverage.get("tutorial_sources") == len(tutorial_sources),
        "coverage.tutorial_sources does not match tutorial source registry",
    )
    state.require(
        coverage.get("tutorial_exercise_paths") == len(exercise_paths),
        "coverage.tutorial_exercise_paths does not match generated exercise paths",
    )
    state.require(
        coverage.get("lesson_corpus_bridge_papers") == corpus_bridges.get("paper_count"),
        "coverage.lesson_corpus_bridge_papers does not match bridge artifact",
    )
    state.require(
        coverage.get("lesson_corpus_bridge_lessons") == corpus_bridges.get("lesson_count"),
        "coverage.lesson_corpus_bridge_lessons does not match bridge artifact",
    )
    state.require(
        coverage.get("lesson_corpus_bridge_links") == corpus_bridges.get("link_count"),
        "coverage.lesson_corpus_bridge_links does not match bridge artifact",
    )
    state.require(corpus_bridges.get("paper_count", 0) >= 100, "expected at least 100 GPU-relevant corpus paper bridges")
    state.require(corpus_bridges.get("lesson_count", 0) >= 50, "expected at least 50 lessons with corpus paper bridges")
    state.require(corpus_bridges.get("link_count", 0) >= 300, "expected at least 300 lesson-paper bridge links")
    state.require(
        coverage.get("latest_measurement_index_rows") == latest_measurements.get("artifact_count"),
        "coverage.latest_measurement_index_rows does not match measurement index",
    )
    state.require(
        latest_measurements.get("artifact_count") == coverage.get("measurement_artifacts"),
        "measurement index artifact count does not match workbench measurement_artifacts",
    )
    state.require(
        latest_measurements.get("passed_correctness", 0) >= 12,
        "expected at least 12 correctness-passed measurement artifacts",
    )
    state.require(
        latest_measurements.get("skipped_runtime_count", 0) >= 1,
        "expected explicit runtime skip records in measurement index",
    )
    state.require(
        any(row.get("source_gpumode_lab_id") for row in latest_measurements.get("rows", [])),
        "measurement index has no GPUMODE lab source links",
    )
    state.require(
        len(exercise_paths) == len(profiles),
        "expected one tutorial exercise path per workbench profile",
    )
    state.require(
        len(tutorial_sources) >= 16,
        "expected at least 16 external tutorial sources",
    )
    providers = {source.get("provider") for source in tutorial_sources}
    state.require("JAX Scaling Book" in providers, "missing JAX Scaling Book tutorial sources")
    state.require("Hugging Face" in providers, "missing Hugging Face tutorial sources")
    state.require("NVIDIA" in providers, "missing NVIDIA CUDA tutorial sources")
    state.require("Triton" in providers, "missing Triton tutorial sources")
    state.require("AMD ROCm" in providers, "missing AMD ROCm/HIP tutorial sources")
    state.require(
        REQUIRED_PROFILES.issubset(profile_by_id),
        f"missing required profiles: {sorted(REQUIRED_PROFILES - set(profile_by_id))}",
    )

    for profile in profiles:
        profile_id = profile["id"]
        for key in (
            "recommended_lessons",
            "recommended_labs",
            "latest_measurements",
            "related_papers",
            "tutorial_sources",
            "exercise_path",
        ):
            state.require(profile.get(key), f"profile {profile_id} has no {key}")
        path = profile.get("exercise_path", {})
        state.require(path.get("source_reading", {}).get("url"), f"profile {profile_id} exercise path has no source URL")
        state.require(path.get("gpumode_anchor", {}).get("url"), f"profile {profile_id} exercise path has no GPUMODE anchor")
        state.require(path.get("lab", {}).get("command"), f"profile {profile_id} exercise path has no lab command")
        state.require(path.get("measurement", {}).get("path"), f"profile {profile_id} exercise path has no measurement artifact")
        state.require(len(path.get("steps", [])) >= 5, f"profile {profile_id} exercise path has too few steps")
        state.require(len(path.get("success_checks", [])) >= 4, f"profile {profile_id} exercise path has too few success checks")
        bridge = ROOT / f"site/bridge-{profile_id}.html"
        if require_file(state, bridge):
            html = bridge.read_text(encoding="utf-8")
            state.require("End-To-End Exercise Path" in html, f"bridge {profile_id} missing exercise path section")

    linked_papers = 0
    for profile in profiles:
        for paper in profile.get("related_papers", []):
            if paper.get("linked_lessons"):
                linked_papers += 1
            else:
                state.failures.append(
                    f"profile {profile['id']} paper lacks linked lessons: {paper.get('title')}"
                )
    state.facts["profile_papers_with_lesson_links"] = linked_papers

    profiling = profile_by_id.get("profiling-roofline", {})
    distributed = profile_by_id.get("distributed-communication", {})
    state.require(
        any(
            item.get("session") == "22-gpumode-nsight-roofline"
            for item in profiling.get("latest_measurements", [])
        ),
        "profiling-roofline profile does not expose session 22 measurements",
    )
    state.require(
        any(
            item.get("session") == "26-gpumode-distributed-communication"
            for item in distributed.get("latest_measurements", [])
        ),
        "distributed-communication profile does not expose session 26 measurements",
    )
    state.require(
        any(
            lab.get("id") == "gpumode-lab-12-distributed-communication"
            for lab in distributed.get("recommended_labs", [])
        ),
        "distributed-communication profile does not recommend lab 12",
    )
    state.require(
        any(source.get("provider") == "JAX Scaling Book" for source in profiling.get("tutorial_sources", [])),
        "profiling-roofline profile does not include JAX Scaling Book sources",
    )
    state.require(
        any(source.get("provider") == "Hugging Face" for source in profile_by_id.get("serving-scheduler", {}).get("tutorial_sources", [])),
        "serving-scheduler profile does not include Hugging Face sources",
    )


def verify_labs(state: CheckState) -> None:
    passed = 0
    for rel in REQUIRED_LAB_ARTIFACTS:
        artifact = LAB_ROOT / rel
        if not require_file(state, artifact):
            continue
        data = load_json(artifact)
        session_dir = artifact.parent.name
        state.require(
            data.get("correctness", {}).get("status") == "passed",
            f"{rel} correctness status is not passed",
        )
        if data.get("correctness", {}).get("status") == "passed":
            passed += 1
        state.require(
            bool(data.get("source", {}).get("gpumode_lessons")),
            f"{rel} has no GPUMODE lesson links",
        )
        state.require(
            (artifact.parent / "out/index.html").exists(),
            f"{session_dir} missing generated tutorial page",
        )

    state.facts["verified_lab_artifacts"] = len(REQUIRED_LAB_ARTIFACTS)
    state.facts["lab_correctness_passed"] = passed

    nsight = load_json(
        LAB_ROOT / "22-gpumode-nsight-roofline/out_gpumode_nsight_roofline.json"
    )
    imports = nsight.get("profiler_roofline", {}).get("imported_reports", {})
    imported_rows = imports.get("rows", [])
    imported_classifications = imports.get("classifications", [])
    state.facts["nsight_import_rows"] = len(imported_rows)
    state.require(imports.get("status") == "ran", "Nsight import parser did not run")
    state.require(len(imported_rows) >= 2, "expected at least two imported Nsight rows")
    state.require(
        len(imported_classifications) == len(imported_rows)
        and all(row.get("bottleneck") for row in imported_classifications),
        "imported Nsight rows must have bottleneck classifications",
    )

    collectives = load_json(
        LAB_ROOT
        / "26-gpumode-distributed-communication/out_gpumode_distributed_communication.json"
    )
    imported = collectives.get("imported_benchmarks", {})
    imported_bench_rows = imported.get("rows", [])
    best_tools = {item.get("tool") for item in imported.get("best_by_tool", [])}
    state.facts["collective_import_rows"] = len(imported_bench_rows)
    state.facts["collective_best_tools"] = sorted(best_tools)
    state.require(
        imported.get("status") == "ran",
        "collective benchmark import parser did not run",
    )
    state.require(
        len(imported_bench_rows) >= 6,
        "expected at least six imported collective benchmark rows",
    )
    state.require(
        {"nccl-tests", "nvshmem"}.issubset(best_tools),
        "collective imports must include nccl-tests and nvshmem best rows",
    )
    state.require(
        all(row.get("errors", 0) == 0 for row in imported_bench_rows),
        "imported collective rows include benchmark errors",
    )


def main() -> int:
    state = CheckState(failures=[], facts={})
    verify_curriculum(state)
    verify_workbench(state)
    verify_labs(state)

    print(json.dumps({"facts": state.facts, "failures": state.failures}, indent=2))
    if state.failures:
        return 1
    print("GPUMODE workbench verification passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
