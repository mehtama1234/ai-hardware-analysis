#!/usr/bin/env python3
"""Verify saved source identities and bounded GPT-2 evaluation invariants."""

import argparse
import hashlib
import json
from pathlib import Path


def check_source(record, path_maps=()):
    path = Path(record["path"])
    for remote, local in path_maps:
        if str(path).startswith(remote):
            path = Path(local) / str(path)[len(remote):].lstrip("/")
            break
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    assert h.hexdigest() == record["sha256"], f"source changed: {path}"


def resolve_path(path, path_maps):
    path = Path(path)
    for remote, local in path_maps:
        if str(path).startswith(remote):
            return Path(local) / str(path)[len(remote):].lstrip("/")
    return path


def check(package, path_maps=()):
    report = json.loads((package / "evaluation.json").read_text())
    for entry in json.loads((package / "manifest.json").read_text())["files"]:
        check_source(entry, path_maps)
    for key, record in report["sources"].items():
        for entry in record if isinstance(record, list) else [record]:
            check_source(entry, path_maps)
    fixture = json.loads(resolve_path(report["sources"]["fixture"]["path"], path_maps).read_text())
    assert fixture == report["fixture"]
    assert not set(fixture["calibration"]) & set(fixture["evaluation"])
    assert report["model"]["revision"] == fixture["revision"]
    assert report["model"]["target_module"] == fixture["target_module"]
    assert report["placement"]["authorized_analog_modules"] == []
    assert report["placement"]["execution"] == "native_digital_fallback"
    assert report["decision"] == "hybrid_hardware_benefit_unproven"
    assert report["physical_converter"]["used_as_numeric_error_profile"] is False
    check_source(report["physical_converter"]["source"], path_maps)
    check_source(report["measured_gpu_reference"]["source"], path_maps)
    assert len(report["variants"]) == 4
    for variant in report["variants"]:
        quality = variant["quality"]
        assert len(quality["rows"]) == len(fixture["evaluation"])
        total = sum(row["predicted_tokens"] for row in quality["rows"])
        assert total > 0 and quality["predicted_tokens"] == total
        assert quality["teacher_forced_argmax_agreement"] == sum(row["argmax_matches"] for row in quality["rows"]) / total
        assert quality["generation_exact_match_count"] == sum(row["baseline_generated_ids"] == row["candidate_generated_ids"] for row in quality["rows"])
        assert abs(quality["nll_increase_nats"] - (quality["candidate_nll_nats_per_token"] - quality["baseline_nll_nats_per_token"])) < 1e-12
        screen = fixture["exploratory_screen"]
        assert variant["exploratory_quality_screen_pass"] == (quality["nll_increase_nats"] <= screen["maximum_nll_increase_nats"] and quality["teacher_forced_argmax_agreement"] >= screen["minimum_teacher_forced_argmax_agreement"])
        assert variant["contract"]["weight_shape_input_output"] == [768, 3072]
        assert variant["contract"]["per_vector"]["adc_conversions_after_differential_subtraction"] == 18432
        assert variant["contract"]["per_vector"]["dac_conversions_without_column_tile_broadcast"] == 18432
        assert variant["contract"]["energy_latency"]["status"] == "not_identifiable_without_matched_cost_coefficients"
        prefill_vectors = sum(row["vectors"] for row in variant["trace"] if row["phase"] == "teacher_forced_prefill")
        assert prefill_vectors == total + len(fixture["evaluation"])
    for row in report["variants"][0]["quality"]["rows"]:
        assert row["maximum_logit_abs_error"] < 1e-3 and row["generation_exact_match"]
    for row in report["controls"]["fallback_quality"]["rows"]:
        assert row["maximum_logit_abs_error"] == 0 and row["generation_exact_match"]
    return {"status": "passed", "scope": "source hashes, counts, quality screen arithmetic, ideal control, fallback, and claim boundaries; not independent hardware qualification"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--path-map", action="append", default=[], metavar="REMOTE=LOCAL",
                        help="rewrite an archived source prefix before hashing")
    args = parser.parse_args()
    path_maps = []
    for item in args.path_map:
        if "=" not in item:
            raise SystemExit("--path-map must be REMOTE=LOCAL")
        path_maps.append(tuple(item.split("=", 1)))
    print(json.dumps(check(args.package, path_maps), indent=2))
