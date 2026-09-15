#!/usr/bin/env python3
"""Check benchmark provenance, token accounting, metrics and claim boundaries."""
import argparse
import hashlib
import json
import math
from pathlib import Path


def check(root):
    manifest = json.loads((root / "manifest.json").read_text())
    required = {"result.json", "protocol.json", "rows.jsonl", "train.parquet", "test.parquet", "DATASET_CARD.md",
                "source_snapshot/run_gpt2_wikitext_projection.py",
                "source_snapshot/run_gpt2_hybrid_evaluation.py", "source_snapshot/tiled_projection_model.py"}
    assert required <= set(manifest), "Manifest omits required evidence"
    for relative, expected in manifest.items():
        path = root / relative
        assert path.resolve().is_relative_to(root.resolve()), relative
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, relative
    result = json.loads((root / "result.json").read_text())
    protocol = json.loads((root / "protocol.json").read_text())
    assert result["protocol"] == protocol
    control_contract = protocol.get("numerical_control")
    if control_contract:
        assert "source_snapshot/projection_numerical_control.py" in manifest
        assert control_contract["version"] == "projection-and-log-probability-v2"
        assert control_contract["projection_atol"] == control_contract["projection_rtol"] == 1e-5
        assert control_contract["maximum_log_probability_error"] == .001
        assert control_contract["maximum_absolute_mean_target_nll_change"] == 1e-5
    assert protocol["calibration_split"] == "train"
    assert protocol["evaluation_split"] == "test"
    assert protocol["train"]["sha256"] != protocol["test"]["sha256"]
    length = protocol["predictions_per_window"]
    for split, count in [("train", protocol["calibration_windows"]), ("test", protocol["evaluation_windows"])]:
        items = protocol[split]["windows"]
        assert len(items) == count
        assert all(len(w["ids"]) == length + 1 for w in items)
        assert all(a["start"] + length < b["start"] for a,b in zip(items, items[1:]))
        assert items[-1]["start"] + length < protocol[split]["total_tokens"]
        assert manifest[split + ".parquet"] == protocol[split]["sha256"]
    rows = [json.loads(line) for line in (root / "rows.jsonl").read_text().splitlines()]
    assert len(rows) == 4 * protocol["evaluation_windows"]
    for index in range(protocol["evaluation_windows"]):
        assert len({r["baseline_nll_sum"] for r in rows if r["window"] == index}) == 1
    expected_variants = {"ideal", "adc8", "adc12", "adc12_noise001"}
    assert set(result["variants"]) == expected_variants
    for name, summary in result["variants"].items():
        subset = [r for r in rows if r["variant"] == name]
        assert sorted(r["window"] for r in subset) == list(range(protocol["evaluation_windows"]))
        for row in subset:
            assert row["start"] == protocol["test"]["windows"][row["window"]]["start"]
            assert row["tokens"] == length
            assert 0 <= row["argmax_matches"] <= length
        count = sum(r["tokens"] for r in subset)
        baseline = sum(r["baseline_nll_sum"] for r in subset) / count
        candidate = sum(r["candidate_nll_sum"] for r in subset) / count
        agreement = sum(r["argmax_matches"] for r in subset) / count
        assert summary["tokens"] == count
        for key, value in [("baseline_nll", baseline), ("candidate_nll", candidate),
                           ("nll_increase", candidate-baseline), ("argmax_agreement", agreement),
                           ("baseline_sample_perplexity", math.exp(baseline)),
                           ("candidate_sample_perplexity", math.exp(candidate))]:
            assert math.isclose(summary[key], value, rel_tol=1e-12, abs_tol=1e-12), key
        assert summary["screen_pass"] == (candidate-baseline <= protocol["screen"]["maximum_nll_increase_nats"]
                                            and agreement >= protocol["screen"]["minimum_argmax_agreement"])
        assert sum(t["vectors"] for t in summary["trace"]) == protocol["evaluation_windows"] * (length+1)
    assert result["ideal_control_pass"]
    if control_contract:
        for row in rows:
            if row["variant"] == "ideal":
                c = row["numerical_control"]
                assert c["pass"] and c["finite"] and c["projection_close"] and c["identical_argmax"]
                assert c["maximum_log_probability_error"] < control_contract["maximum_log_probability_error"]
                assert abs(c["mean_target_nll_change"]) < control_contract["maximum_absolute_mean_target_nll_change"]
    else:
        assert result["variants"]["ideal"]["maximum_logit_error"] < .001
    assert result["digital_fallback_exact_all_windows"]
    assert not result["analog_authorized"] and not result["physical_profile_calibrated"]
    print(f"Verified {len(manifest)} hashes and {len(rows)} benchmark rows; {count} predictions per variant")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    check(parser.parse_args().package)
