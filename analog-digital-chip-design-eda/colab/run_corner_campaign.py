#!/usr/bin/env python3
"""Run the open continuous-SAR corners in one prepared Colab VM.

The pinned Sky130 archives must already be present at /content.  This script
does not turn a failed or rejected corner into a pass; it preserves each child
receipt and emits a campaign summary for the model-to-chip qualification gate.
"""
from __future__ import annotations

import json
import hashlib
import os
import shutil
import subprocess
import tarfile
from pathlib import Path


ROOT = Path("/content/ai-hardware-analysis")
COLAB = ROOT / "analog-digital-chip-design-eda/colab"
EVIDENCE = ROOT / "analog-digital-chip-design-eda/evidence/aimc-simulator-adapters"
OUT = Path("/content/sky130-corner-campaign")


def run(command: list[str], *, env: dict[str, str] | None = None) -> dict:
    proc = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True, check=False)
    return {"command": command, "returncode": proc.returncode, "stdout": proc.stdout[-12000:], "stderr": proc.stderr[-12000:]}


def main() -> int:
    archive = Path("/content/ai-hardware-analysis.tgz")
    if not ROOT.exists() and archive.exists():
        with tarfile.open(archive, "r:gz") as bundle:
            bundle.extractall("/content")
    if not ROOT.exists():
        raise SystemExit("repository archive is missing or could not be extracted")
    settings_path = Path("/content/sky130-campaign-settings.json")
    bundled_settings = COLAB / "sky130-sequential-control-campaign-settings.json"
    if os.environ.get("AIMC_USE_BUNDLED_TOP_PLATE_SETTINGS") == "1":
        bundled_settings = COLAB / "sky130-top-plate-acquisition-settings.json"
    if not settings_path.exists() and bundled_settings.exists() and os.environ.get("AIMC_USE_BUNDLED_SEQUENTIAL_SETTINGS") == "1":
        settings_path = bundled_settings
    if not settings_path.exists() and bundled_settings.exists() and os.environ.get("AIMC_USE_BUNDLED_TOP_PLATE_SETTINGS") == "1":
        settings_path = bundled_settings
    campaign_settings = json.loads(settings_path.read_text()) if settings_path.exists() else {}
    settings_sha256 = hashlib.sha256(settings_path.read_bytes()).hexdigest() if settings_path.exists() else None
    OUT.mkdir(parents=True, exist_ok=True)
    preflight = run(["python3", str(COLAB / "bootstrap_continuous_sar.py")])
    (OUT / "preflight-run.json").write_text(json.dumps(preflight, indent=2) + "\n")
    preflight_report = Path("/content/sky130-preflight.json")
    if not preflight_report.exists() or json.loads(preflight_report.read_text()).get("status") != "ready":
        summary = {"result_type": "colab_sky130_corner_campaign", "status": "blocked_preflight", "preflight": preflight}
        (OUT / "campaign-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        print(json.dumps(summary, indent=2))
        return 2
    sequential_preflight = None
    if str(campaign_settings.get("env", {}).get("AIMC_CONTINUOUS_SEQUENTIAL_CONTROL", "0")) == "1":
        sequential_preflight = run(["python3", str(COLAB / "validate_sequential_control_deck.py")])
        (OUT / "sequential-control-preflight-run.json").write_text(json.dumps(sequential_preflight, indent=2) + "\n")
        if sequential_preflight["returncode"] != 0:
            summary = {"result_type": "colab_sky130_corner_campaign", "status": "blocked_sequential_control_preflight", "preflight": preflight, "sequential_preflight": sequential_preflight}
            (OUT / "campaign-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
            print(json.dumps(summary, indent=2))
            return 2

    # Keep a conservative finite edge as the default, but allow the campaign
    # contract to request a calibrated edge. Previously this value was
    # hard-coded after settings were loaded, silently invalidating calibration
    # screens that asked for a different PWL rise time.
    requested_pwl_rise = str(campaign_settings.get("env", {}).get("AIMC_CONTINUOUS_PWL_RISE_NS", "0.2"))
    cases = {
        "fs": {"AIMC_SKY130_CORNER": "fs", "AIMC_CONTINUOUS_PWL_RISE_NS": requested_pwl_rise, "AIMC_CONTINUOUS_OUTPUT_STEM": "colab-campaign-fs"},
        "ff": {"AIMC_SKY130_CORNER": "ff", "AIMC_CONTINUOUS_PWL_RISE_NS": requested_pwl_rise, "AIMC_CONTINUOUS_OUTPUT_STEM": "colab-campaign-ff"},
    }
    results = {}
    def persist(status: str) -> dict:
        snapshot = {"result_type": "colab_sky130_corner_campaign", "status": status, "settings": campaign_settings, "settings_path": str(settings_path), "settings_sha256": settings_sha256, "cases_settings": cases, "preflight": preflight, "sequential_preflight": sequential_preflight, "cases": results, "claim_boundary": "FS/FF receipts are accepted only when their measured code map passes the unchanged qualification contract."}
        (OUT / "campaign-summary.json").write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n")
        return snapshot
    persist("campaign_running")
    for name, case_settings in cases.items():
        env = os.environ.copy()
        env.update(case_settings)
        if "sample_reset" in campaign_settings:
            env["AIMC_CONTINUOUS_SAMPLE_RESET"] = "1" if campaign_settings["sample_reset"] else "0"
        for key, value in campaign_settings.get("env", {}).items():
            env[str(key)] = str(value)
        env.setdefault("AIMC_COUPLED_TIMEOUT_S", "1200")
        results[name] = run(["python3", str(COLAB / "run_persistent_continuous_trial.py")], env=env)
        child = EVIDENCE / f"{case_settings['AIMC_CONTINUOUS_OUTPUT_STEM']}.json"
        if child.exists():
            destination = OUT / child.name
            shutil.copy2(child, destination)
            results[name]["artifact"] = str(destination)
            results[name]["report"] = json.loads(child.read_text())
        persist("campaign_running")
    summary = persist("campaign_completed")
    compact = {name: {"returncode": value.get("returncode"), "runner_returncode": value.get("report", {}).get("returncode"), "status": value.get("report", {}).get("status")} for name, value in results.items()}
    print(json.dumps({"status": summary["status"], "output": str(OUT), "cases": compact}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
