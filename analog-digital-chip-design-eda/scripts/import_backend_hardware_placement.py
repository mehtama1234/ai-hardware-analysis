#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import socket
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
MEASURE = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "measurements"
DEFAULT_PACKAGE_ID = "pkg-e931662a01293df2"
DEFAULT_URL = f"http://127.0.0.1:8025/deployment-packages/{DEFAULT_PACKAGE_ID}/hardware-placement"
JSON_OUT = MEASURE / "backend-hardware-placement.json"
CSV_OUT = MEASURE / "backend-hardware-placement-governor-input.csv"
MD_OUT = MEASURE / "backend-hardware-placement-governor-input.md"


def fetch_json(url: str) -> dict[str, object]:
    last_exc: Exception | None = None
    for attempt in range(1, 4):
        try:
            with urlopen(url, timeout=10) as response:
                return json.loads(response.read().decode("utf-8"))
        except (TimeoutError, socket.timeout, URLError) as exc:
            last_exc = exc
            if attempt == 3:
                break
            time.sleep(1.5 * attempt)
    raise RuntimeError(f"GET {url} failed after 3 attempts: {last_exc}") from last_exc


def load_existing() -> dict[str, object] | None:
    if not JSON_OUT.exists():
        return None
    return json.loads(JSON_OUT.read_text(encoding="utf-8"))


def rows_from_placement(payload: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for row in payload.get("placement_rows", []):
        if not isinstance(row, dict):
            continue
        governor = row.get("governor_fields") if isinstance(row.get("governor_fields"), dict) else {}
        rows.append(
            {
                "operator_id": row.get("operator_id"),
                "operator_kind": row.get("operator_kind"),
                "placement": row.get("placement"),
                "analog_candidate": 1 if row.get("analog_candidate") else 0,
                "model_sensitivity_class": row.get("model_sensitivity_class"),
                "residual_q8": governor.get("residual_q8", 0),
                "sensitivity_q8": governor.get("sensitivity_q8", 0),
                "allow_analog": 1 if governor.get("allow_analog") else 0,
                "fallback_action": governor.get("fallback_action"),
                "dac_boundary": row.get("dac_boundary"),
                "adc_boundary": row.get("adc_boundary"),
                "expected_error_source": row.get("expected_error_source"),
                "fallback_point": row.get("fallback_point"),
            }
        )
    return rows


def write_csv(rows: list[dict[str, object]]) -> None:
    fieldnames = [
        "operator_id",
        "operator_kind",
        "placement",
        "analog_candidate",
        "model_sensitivity_class",
        "residual_q8",
        "sensitivity_q8",
        "allow_analog",
        "fallback_action",
        "dac_boundary",
        "adc_boundary",
        "expected_error_source",
        "fallback_point",
    ]
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(payload: dict[str, object], rows: list[dict[str, object]], source: str) -> None:
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    lines = [
        "# Backend Hardware Placement Governor Input",
        "",
        "This file is the hardware lab's local copy of the old backend's `hardware_placement` package artifact.",
        "",
        f"Source: `{source}`",
        "",
        "## Summary",
        "",
        f"- operators: {summary.get('operators', len(rows))}",
        f"- analog candidates: {summary.get('analog_candidates', 0)}",
        f"- converter boundaries: {summary.get('converter_boundaries', 0)}",
        f"- fallback points: {summary.get('fallback_points', 0)}",
        "",
        "## First-Principles Reading",
        "",
        "The backend sees the model graph. The hardware lab sees physical limits. This artifact is the handoff between them. Each operator is translated into the fields that a hardware controller can understand: whether analog is even a candidate, where DAC and ADC boundaries appear, what error source is expected, how sensitive the model location is, and what fallback action the controller should take.",
        "",
        "This does not prove that the hardware lab has consumed the rows in RTL yet. It proves the first connection: model graph facts can be reduced to hardware-control fields without losing the reason for the decision.",
        "",
        "## Rows",
        "",
        "| operator | kind | placement | analog candidate | sensitivity | residual q8 | sensitivity q8 | action |",
        "| --- | --- | --- | ---: | --- | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['operator_id']} | {row['operator_kind']} | {row['placement']} | "
            f"{row['analog_candidate']} | {row['model_sensitivity_class']} | {row['residual_q8']} | "
            f"{row['sensitivity_q8']} | {row['fallback_action']} |"
        )
    MD_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    url = argv[1] if len(argv) > 1 else DEFAULT_URL
    source = url
    try:
        payload = fetch_json(url)
    except (URLError, TimeoutError, OSError) as exc:
        existing = load_existing()
        if not existing:
            print(f"missing backend hardware placement and no local snapshot exists: {exc}", file=sys.stderr)
            return 1
        payload = existing
        source = f"existing local snapshot after fetch failed: {exc}"
    rows = rows_from_placement(payload)
    if not rows:
        print("backend hardware placement has no placement_rows", file=sys.stderr)
        return 1
    MEASURE.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(rows)
    write_markdown(payload, rows, source)
    print("backend_hardware_placement_import")
    print(f"operators,{len(rows)}")
    print(f"csv,{CSV_OUT}")
    print(f"markdown,{MD_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
