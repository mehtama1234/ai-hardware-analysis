#!/usr/bin/env python3
"""HTTP-level regression for strict evidence import paths."""

from __future__ import annotations

import json
import shutil
import socket
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMPORT_TEMPLATES = ROOT.parent / "review-package-demo" / "import-templates"
CURRENT_LAB_EVIDENCE = (
    ROOT.parents[3] / "analog-digital-chip-design-eda" / "evidence" / "aimc-hardware-lab"
)
PACKAGE_ID = "pkg-e931662a01293df2"
LIVE_PACKAGE_DIR = ROOT / ".data" / "packages" / PACKAGE_ID
sys.path.insert(0, str(ROOT))

import main  # noqa: E402
import uvicorn  # noqa: E402
from model_store import ModelStore  # noqa: E402


def load_template(filename: str) -> dict:
    path = IMPORT_TEMPLATES / filename
    if not path.exists():
        raise SystemExit(f"missing import template: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_current_evidence(filename: str) -> dict:
    path = CURRENT_LAB_EVIDENCE / filename
    if not path.exists():
        raise SystemExit(f"missing current lab evidence: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def expect(name: str, condition: bool, details: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL {name}: {details}")
    print(f"PASS {name}: {details}")


def copy_demo_package(temp_root: Path) -> None:
    if not LIVE_PACKAGE_DIR.exists():
        raise SystemExit(f"missing live package fixture: {LIVE_PACKAGE_DIR}")
    packages = temp_root / "packages"
    packages.mkdir(parents=True, exist_ok=True)
    target = packages / PACKAGE_ID
    shutil.copytree(LIVE_PACKAGE_DIR, target)
    metadata_path = target / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["package_dir"] = str(target)
    metadata["archive_path"] = str(target / metadata["archive_filename"])
    imports = []
    for item in metadata.get("imported_evidence", []):
        path = Path(item["path"])
        rewritten = target / "imported-evidence" / path.name
        item["path"] = str(rewritten)
        imports.append(item)
    metadata["imported_evidence"] = imports
    runs = []
    for item in metadata.get("adapter_runs", []):
        path = Path(item["path"])
        rewritten = target / "adapter-runs" / path.name
        item["path"] = str(rewritten)
        runs.append(item)
    metadata["adapter_runs"] = runs
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def wait_for_server(port: int) -> None:
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/openapi.json", timeout=0.5):
                return
        except Exception:
            time.sleep(0.1)
    raise SystemExit(f"server did not start on port {port}")


def post_json(port: int, path: str, payload: dict) -> tuple[int, dict]:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            body = json.loads(response.read().decode("utf-8"))
            return response.status, body
    except urllib.error.HTTPError as exc:
        body = json.loads(exc.read().decode("utf-8"))
        return exc.code, body


def main_check() -> None:
    tool_payload = load_template("analog-simulator-tool-evidence.template.json")
    generated_tool_payload = load_current_evidence("analog_error_simulation_strict_tool.json")
    measured_runtime_payload = load_template("measured-board-runtime.template.json")
    measured_power_payload = load_template("measured-power-thermal.template.json")
    local_runtime_payload = load_current_evidence("board_runtime.json")
    local_power_payload = load_current_evidence("power_thermal.json")
    weak_tool_payload = load_current_evidence("analog_error_simulation.json")

    original_store = main.STORE
    with tempfile.TemporaryDirectory(prefix="strict-evidence-api-") as temp_dir:
        temp_root = Path(temp_dir)
        copy_demo_package(temp_root)
        main.STORE = ModelStore(temp_root)
        port = free_port()
        config = uvicorn.Config(main.app, host="127.0.0.1", port=port, log_level="warning")
        server = uvicorn.Server(config)
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        wait_for_server(port)

        status, body = post_json(
            port,
            f"/evidence/validate-tool?source_id=analog_error_simulation&package_id={PACKAGE_ID}",
            tool_payload,
        )
        expect("validate-tool status", status == 200, f"status={status}")
        expect("validate-tool readiness", body["tool_readiness"]["tool_ready"] is True, "strict simulator evidence accepted")
        expect("validate-tool preview", body["preview"]["package_id"] == PACKAGE_ID, "claim preview attached to package")

        status, body = post_json(
            port,
            f"/evidence/validate-tool?source_id=analog_error_simulation&package_id={PACKAGE_ID}",
            generated_tool_payload,
        )
        expect("validate-tool generated lab status", status == 200, f"status={status}")
        expect(
            "validate-tool generated lab readiness",
            body["tool_readiness"]["tool_ready"] is True,
            "generated SPICE-style lab payload accepted as bounded strict simulator/tool evidence",
        )

        status, body = post_json(
            port,
            f"/evidence/import-tool?source_id=analog_error_simulation&package_id={PACKAGE_ID}",
            tool_payload,
        )
        expect("import-tool status", status == 200, f"status={status}")
        expect("import-tool readiness", body["tool_readiness"]["tool_ready"] is True, "strict simulator import saved")
        expect("import-tool source", body["source_id"] == "analog_error_simulation", f"source_id={body.get('source_id')}")

        status, body = post_json(
            port,
            f"/deployment-packages/{PACKAGE_ID}/hardware-lab-evidence",
            {},
        )
        expect("hardware-lab strict sidecar import status", status == 200, f"status={status}")
        expect("hardware-lab accepted count", body["accepted_count"] >= 5, f"accepted_count={body.get('accepted_count')}")
        expect("hardware-lab rejection count", body["rejected_count"] == 0, f"rejected_count={body.get('rejected_count')}")
        expect(
            "hardware-lab strict sidecar imported",
            body["strict_tool_evidence"]["imported"] is True,
            "strict analog simulator/tool sidecar imported through package endpoint",
        )

        with urllib.request.urlopen(f"http://127.0.0.1:{port}/deployment-packages/{PACKAGE_ID}/evidence-audit", timeout=10) as response:
            audit = json.loads(response.read().decode("utf-8"))
        analog_source = next(item for item in audit["sources"] if item["source_id"] == "analog_error_simulation")
        expect(
            "strict simulator audit classification",
            analog_source["nonlocal_count"] >= 1 and analog_source["latest_is_local_generated"] is False,
            f"local={analog_source['local_generated_count']} nonlocal={analog_source['nonlocal_count']}",
        )
        expect(
            "strict simulator proof-level label",
            analog_source["latest_proof_level"] == "calibrated simulation",
            f"latest_proof_level={analog_source.get('latest_proof_level')}",
        )

        status, body = post_json(
            port,
            f"/evidence/import-tool?source_id=analog_error_simulation&package_id={PACKAGE_ID}",
            weak_tool_payload,
        )
        expect("import-tool weak rejection", status == 400, f"status={status}")
        detail = body.get("detail") or body.get("error") or body
        expect(
            "import-tool weak readiness payload",
            detail["tool_readiness"]["tool_ready"] is False and bool(detail["tool_readiness"]["issues"]),
            "weak simulator artifact remains ordinary evidence only",
        )

        status, body = post_json(
            port,
            f"/evidence/validate-measured?source_id=board_runtime&package_id={PACKAGE_ID}",
            measured_runtime_payload,
        )
        expect("validate-measured runtime status", status == 200, f"status={status}")
        expect("validate-measured runtime readiness", body["measured_readiness"]["measured_ready"] is True, "board runtime ready")

        status, body = post_json(
            port,
            f"/evidence/import-measured?source_id=board_runtime&package_id={PACKAGE_ID}",
            measured_runtime_payload,
        )
        expect("import-measured runtime status", status == 200, f"status={status}")
        expect("import-measured runtime readiness", body["measured_readiness"]["measured_ready"] is True, "runtime evidence saved")

        status, body = post_json(
            port,
            f"/evidence/import-measured?source_id=board_runtime&package_id={PACKAGE_ID}",
            local_runtime_payload,
        )
        expect("import-measured local runtime rejection", status == 400, f"status={status}")
        detail = body.get("detail") or body.get("error") or body
        runtime_issues = "\n".join(detail["measured_readiness"]["issues"])
        expect(
            "import-measured local runtime reason",
            "board_id must name a real board or instrumented runtime source" in runtime_issues
            and "provenance marks this runtime as local or not measured hardware" in runtime_issues,
            "local RTL runtime cannot upgrade measured latency",
        )

        status, body = post_json(
            port,
            f"/evidence/import-measured?source_id=power_thermal&package_id={PACKAGE_ID}",
            measured_power_payload,
        )
        expect("import-measured power status", status == 200, f"status={status}")
        expect("import-measured power readiness", body["measured_readiness"]["measured_ready"] is True, "power evidence saved")

        with urllib.request.urlopen(f"http://127.0.0.1:{port}/deployment-packages/{PACKAGE_ID}/claim-readiness", timeout=10) as response:
            claim_readiness = json.loads(response.read().decode("utf-8"))
        energy_claim = next(claim for claim in claim_readiness["lab_claims"] if claim["id"] == "C3")
        expect(
            "same-run measured energy claim",
            energy_claim["status"] == "supported",
            f"status={energy_claim['status']} issues={energy_claim['quality_issues']}",
        )
        expect(
            "same-run measured energy statement",
            "runtime trace ID" in energy_claim["safe_statement"],
            energy_claim["safe_statement"],
        )

        mismatched_power_payload = json.loads(json.dumps(measured_power_payload))
        mismatched_power_payload["runtime_trace_id"] = "different-runtime-trace"
        status, body = post_json(
            port,
            f"/evidence/import-measured?source_id=power_thermal&package_id={PACKAGE_ID}",
            mismatched_power_payload,
        )
        expect("import-measured mismatched power status", status == 200, f"status={status}")
        expect(
            "import-measured mismatched power readiness",
            body["measured_readiness"]["measured_ready"] is True,
            "mismatched power remains structurally measured evidence",
        )

        with urllib.request.urlopen(f"http://127.0.0.1:{port}/deployment-packages/{PACKAGE_ID}/claim-readiness", timeout=10) as response:
            mismatched_claim_readiness = json.loads(response.read().decode("utf-8"))
        mismatched_energy_claim = next(claim for claim in mismatched_claim_readiness["lab_claims"] if claim["id"] == "C3")
        expect(
            "mismatched measured energy claim",
            mismatched_energy_claim["status"] == "needs review",
            f"status={mismatched_energy_claim['status']}",
        )
        expect(
            "mismatched measured energy reason",
            any("do not describe the same run" in issue for issue in mismatched_energy_claim["quality_issues"]),
            "claim-readiness refuses cross-run energy merge",
        )

        status, body = post_json(
            port,
            f"/evidence/import-measured?source_id=power_thermal&package_id={PACKAGE_ID}",
            local_power_payload,
        )
        expect("import-measured local power rejection", status == 400, f"status={status}")
        detail = body.get("detail") or body.get("error") or body
        power_issues = "\n".join(detail["measured_readiness"]["issues"])
        expect(
            "import-measured local power reason",
            "measurement_setup.meter must name the meter or instrument source" in power_issues
            and "payload marks power/thermal as local estimate or not measured hardware" in power_issues
            and "power_trace must contain numeric time_ms, voltage_v, and current_a samples" in power_issues,
            "OpenLane-derived power cannot upgrade measured energy",
        )
        server.should_exit = True
        thread.join(timeout=5)
    main.STORE = original_store


if __name__ == "__main__":
    try:
        main_check()
    finally:
        main.STORE = main.ModelStore(main.BASE_DIR / ".data")
