#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OLD_ROOT = ROOT.parent / "ai-hardware-analysis" / "analog-in-memory-ai-inference" / "software-architecture"
ONNX_PYTHON = OLD_ROOT / "backend" / ".venv" / "bin" / "python"
SAMPLES = OLD_ROOT / "samples"
OUT_DIR = ROOT / "evidence" / "aimc-hardware-lab"
OUT_JSON = OUT_DIR / "onnx-fixture-inventory.json"
OUT_MD = OUT_DIR / "onnx-fixture-inventory.md"


def inspect_model(path: Path) -> dict[str, object]:
    code = r"""
import json
import onnx
from onnx import numpy_helper
from pathlib import Path
model_path = Path(__import__("sys").argv[1])
model = onnx.shape_inference.infer_shapes(onnx.load(model_path))
nodes = []
initializers = {}
for init in model.graph.initializer:
    arr = numpy_helper.to_array(init)
    initializers[init.name] = {"shape": list(arr.shape), "size": int(arr.size)}
for node in model.graph.node:
    nodes.append({
        "name": node.name,
        "op_type": node.op_type,
        "inputs": list(node.input),
        "outputs": list(node.output),
        "uses_initializer": any(item in initializers for item in node.input),
    })
print(json.dumps({"nodes": nodes, "initializers": initializers}))
"""
    result = subprocess.run([str(ONNX_PYTHON), "-c", code, str(path)], text=True, capture_output=True, check=True)
    data = json.loads(result.stdout)
    nodes = data.get("nodes", [])
    initializers = data.get("initializers", {})
    matmul_nodes = [node for node in nodes if node.get("op_type") == "MatMul"]
    fixed_weight_matmuls = [node for node in matmul_nodes if node.get("uses_initializer") is True]
    return {
        "name": path.name,
        "path": str(path),
        "size_bytes": path.stat().st_size,
        "node_count": len(nodes),
        "initializer_count": len(initializers),
        "initializer_parameter_count": sum(int(item.get("size", 0)) for item in initializers.values() if isinstance(item, dict)),
        "matmul_count": len(matmul_nodes),
        "fixed_weight_matmul_count": len(fixed_weight_matmuls),
        "operator_kinds": sorted({str(node.get("op_type")) for node in nodes}),
        "matmul_nodes": [
            {
                "name": node.get("name"),
                "inputs": node.get("inputs"),
                "outputs": node.get("outputs"),
                "fixed_weight": node.get("uses_initializer") is True,
            }
            for node in matmul_nodes
        ],
    }


def classify(item: dict[str, object]) -> dict[str, object]:
    name = str(item["name"])
    fixed = int(item["fixed_weight_matmul_count"])
    if name == "deep-transformer-mlp-stack.onnx":
        status = "selected_current_best_fixture"
        reason = "largest existing fixed-weight MatMul family and current residual-aware placement source"
    elif fixed >= 4:
        status = "usable_larger_fixture"
        reason = "larger than tiny MLP and usable for guarded simulator payloads"
    else:
        status = "small_fixture"
        reason = "useful for smoke or tiny trained-weight checks, not enough for the next larger-slice claim"
    return {**item, "selection_status": status, "selection_reason": reason}


def write_markdown(items: list[dict[str, object]]) -> None:
    selected = next((item for item in items if item["selection_status"] == "selected_current_best_fixture"), None)
    lines = [
        "# ONNX Fixture Inventory",
        "",
        "This file is generated from the actual ONNX sample files in the restored backend.",
        "",
        "It answers a narrow question: what model slices do we already have, and which one is the strongest local candidate before a real uploaded model slice exists?",
        "",
        "## Current Selection",
        "",
    ]
    if selected:
        lines.extend(
            [
                f"- selected fixture: `{selected['name']}`",
                f"- fixed-weight MatMul rows: `{selected['fixed_weight_matmul_count']}`",
                f"- reason: {selected['selection_reason']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Inventory",
            "",
            "| model | nodes | initializers | parameters | MatMul | fixed-weight MatMul | status |",
            "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for item in items:
        lines.append(
            f"| {item['name']} | {item['node_count']} | {item['initializer_count']} | "
            f"{item['initializer_parameter_count']} | {item['matmul_count']} | "
            f"{item['fixed_weight_matmul_count']} | {item['selection_status']} |"
        )
    lines.extend(
        [
            "",
            "## First-Principles Reading",
            "",
            "The useful analog object is not an ONNX file by itself. The useful object is a fixed matrix multiply whose weights are known and reused.",
            "",
            "A larger slice is stronger when it has more fixed-weight MatMul rows, real initializer tensors, and digital support operators around those rows. That tests whether analog placement still makes sense when MatMul is only part of a graph, not the whole graph.",
            "",
            "The current best local fixture is still a fixture. It is larger and model-shaped, but it is not a pretrained foundation-model slice and not a user-uploaded deployment model.",
            "",
            "## Refused Claim",
            "",
            "This inventory does not prove full model accuracy, measured latency, measured energy, calibrated silicon, analog macro signoff, or production readiness.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    models = sorted(SAMPLES.glob("*.onnx"))
    if not models:
        raise SystemExit(f"no ONNX fixtures found in {SAMPLES}")
    items = [classify(inspect_model(path)) for path in models]
    payload = {
        "result_type": "onnx_fixture_inventory",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_directory": str(SAMPLES),
        "models": items,
        "summary": {
            "models": len(items),
            "selected_current_best_fixture": next((item["name"] for item in items if item["selection_status"] == "selected_current_best_fixture"), "missing"),
            "max_fixed_weight_matmul_count": max(int(item["fixed_weight_matmul_count"]) for item in items),
            "usable_larger_fixtures": sum(1 for item in items if item["selection_status"] in {"selected_current_best_fixture", "usable_larger_fixture"}),
        },
        "claim_boundary": {
            "allowed": "records actual ONNX fixture inventory and selects the strongest local fixed-weight MatMul slice",
            "not_allowed": "does not turn a fixture into a real uploaded pretrained model or measured hardware evidence",
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(items)
    print("onnx_fixture_inventory")
    print(f"models,{payload['summary']['models']}")
    print(f"selected,{payload['summary']['selected_current_best_fixture']}")
    print(f"max_fixed_weight_matmuls,{payload['summary']['max_fixed_weight_matmul_count']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
