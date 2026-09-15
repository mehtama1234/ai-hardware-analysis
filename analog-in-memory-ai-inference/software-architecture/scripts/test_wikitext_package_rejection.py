#!/usr/bin/env python3
"""Mutation checks against a completed package, using isolated temporary copies."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

from check_gpt2_wikitext_projection import check


def rewrite(root, name, value):
    path = root / name
    path.write_text(json.dumps(value, indent=2)+"\n")
    manifest = json.loads((root / "manifest.json").read_text())
    manifest[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (root / "manifest.json").write_text(json.dumps(manifest)+"\n")


def run(package):
    check(package)
    modes = ["metric_arithmetic", "numerical_control", "analog_claim", "source_change"]
    if json.loads((package / "protocol.json").read_text()).get("experiment") == "adc_range_calibration_validation_v1":
        modes += ["range_refit", "validation_as_test"]
    for mode in modes:
        with tempfile.TemporaryDirectory(prefix="wikitext-rejection-") as temporary:
            root = Path(temporary) / "package"
            shutil.copytree(package, root)
            result = json.loads((root / "result.json").read_text())
            if mode == "metric_arithmetic":
                result["variants"]["adc12"]["candidate_nll"] += 1
                rewrite(root, "result.json", result)
            elif mode == "analog_claim":
                result["analog_authorized"] = True
                rewrite(root, "result.json", result)
            elif mode == "range_refit":
                result["variants"]["calibrated_adc8"]["contract"]["adc_range"]["ranges"][0]["selected_bound"] *= 1.2
                rewrite(root, "result.json", result)
            elif mode == "validation_as_test":
                protocol = result["protocol"]
                protocol["evaluation_split"] = "test"
                rewrite(root, "protocol.json", protocol)
                rewrite(root, "result.json", result)
            elif mode == "numerical_control":
                rows = [json.loads(x) for x in (root / "rows.jsonl").read_text().splitlines()]
                next(x for x in rows if x["variant"] == "ideal")["numerical_control"]["maximum_log_probability_error"] = .01
                path = root / "rows.jsonl"
                path.write_text("".join(json.dumps(x)+"\n" for x in rows))
                manifest = json.loads((root / "manifest.json").read_text())
                manifest["rows.jsonl"] = hashlib.sha256(path.read_bytes()).hexdigest()
                (root / "manifest.json").write_text(json.dumps(manifest)+"\n")
            else:
                with (root / "source_snapshot/projection_numerical_control.py").open("a") as stream:
                    stream.write("\n# modified after execution\n")
            try:
                check(root)
            except AssertionError:
                print(f"Correctly rejected {mode}")
            else:
                raise RuntimeError(f"Verifier accepted {mode}")


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package",type=Path)
    run(parser.parse_args().package)
