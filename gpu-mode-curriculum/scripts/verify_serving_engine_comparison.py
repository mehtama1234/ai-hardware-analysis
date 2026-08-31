#!/usr/bin/env python3
"""Verify serving engine comparison scenarios, recommendations, and site output."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "serving-engine-comparison" / "serving-engine-comparison.json"
REPORT_MD = ROOT / "serving-engine-comparison" / "reports" / "serving-engine-comparison.md"
SITE_PAGE = ROOT / "site" / "serving-engine-comparison.html"
REQUIRED_ENGINES = {"vllm", "tgi", "sglang", "tensorrt-llm", "hf-transformers"}
REQUIRED_SCENARIOS = {"interactive-chat", "long-context-rag", "mixed-prefill-decode", "offline-throughput", "portable-amd-nvidia"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not REPORT.exists():
        subprocess.run([sys.executable, "scripts/run_serving_engine_comparison.py"], cwd=ROOT, check=True)
    report = load_json(REPORT)
    require(report.get("status") == "comparison-ready", "serving engine comparison is not ready")
    require(set(report.get("engine_ids", [])) == REQUIRED_ENGINES, "unexpected engine set")
    require(report.get("scenario_count") == len(REQUIRED_SCENARIOS), "scenario count mismatch")
    require(report.get("engine_count") == len(REQUIRED_ENGINES), "engine count mismatch")
    scenarios = report.get("scenarios", [])
    require({row.get("scenario_id") for row in scenarios} == REQUIRED_SCENARIOS, "unexpected scenario ids")
    require(len(report.get("scenario_recommendations", [])) == len(REQUIRED_SCENARIOS), "missing scenario recommendations")
    for scenario in scenarios:
        engines = scenario.get("engines", [])
        require(len(engines) == len(REQUIRED_ENGINES), f"{scenario.get('scenario_id')} missing engine rows")
        require(scenario.get("baseline_policy") == "continuous-batching-prefix-cache", f"{scenario.get('scenario_id')} missing baseline policy")
        require(scenario.get("baseline_output_tokens_per_second", 0) > 0, f"{scenario.get('scenario_id')} missing baseline throughput")
        scores = [row.get("score", 0) for row in engines]
        require(scores == sorted(scores, reverse=True), f"{scenario.get('scenario_id')} engine rows are not sorted")
        for engine in engines:
            require(engine.get("estimated_output_tokens_per_second", 0) > 0, f"{engine.get('engine_id')} missing throughput estimate")
            require(engine.get("estimated_p50_ttft_ms", 0) > 0, f"{engine.get('engine_id')} missing TTFT estimate")
            require(engine.get("estimated_peak_kv_blocks", 0) > 0, f"{engine.get('engine_id')} missing KV estimate")
            require(engine.get("features"), f"{engine.get('engine_id')} missing features")
            require(engine.get("gpu_requirements"), f"{engine.get('engine_id')} missing GPU requirements")
    require(REPORT_MD.exists(), "serving engine Markdown report missing")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE serving engine comparison" in page, "serving engine site page missing title")
        require("vLLM" in page and "Hugging Face TGI" in page and "SGLang" in page, "serving engine site page missing engine names")
    facts = {
        "status": report["status"],
        "engines": report["engine_count"],
        "scenarios": report["scenario_count"],
        "recommendations": report["scenario_recommendations"],
    }
    print(json.dumps({"facts": facts, "failures": []}, indent=2))
    print("GPUMODE serving engine comparison verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
