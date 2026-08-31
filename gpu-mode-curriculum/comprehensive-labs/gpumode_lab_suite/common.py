from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
MEASUREMENTS = ROOT / "measurements"


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str


def timed(fn: Callable[[], Any]) -> tuple[Any, float]:
    start = time.perf_counter()
    value = fn()
    return value, time.perf_counter() - start


def close(a: float, b: float, tol: float = 1e-6) -> bool:
    return abs(a - b) <= tol


def dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def matmul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    cols = list(zip(*b))
    return [[dot(row, list(col)) for col in cols] for row in a]


def transpose(a: list[list[float]]) -> list[list[float]]:
    return [list(col) for col in zip(*a)]


def softmax(xs: list[float]) -> list[float]:
    m = max(xs)
    exps = [math.exp(x - m) for x in xs]
    s = sum(exps)
    return [x / s for x in exps]


def write_measurement(lab_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    MEASUREMENTS.mkdir(parents=True, exist_ok=True)
    checks = payload.get("checks", [])
    artifact = {
        "lab_id": lab_id,
        "status": "passed" if checks and all(row.get("passed") for row in checks) else "failed",
        "measurement": payload,
        "runtime_caveats": [
            "Local run uses CPU/model implementations where GPU compiler/runtime support is unavailable."
        ],
    }
    path = MEASUREMENTS / f"{lab_id}.json"
    path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return artifact


def emit(lab_id: str, payload: dict[str, Any]) -> int:
    artifact = write_measurement(lab_id, payload)
    print(json.dumps(artifact, indent=2, ensure_ascii=False))
    return 0 if artifact["status"] == "passed" else 1
