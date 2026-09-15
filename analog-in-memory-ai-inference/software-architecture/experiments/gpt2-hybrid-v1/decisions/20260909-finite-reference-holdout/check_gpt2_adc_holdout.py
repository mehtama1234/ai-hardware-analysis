#!/usr/bin/env python3
"""Verify held-out selection, frozen profile, numerical controls and metrics."""
import argparse
import hashlib
import json
import math
from pathlib import Path


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check(root):
    manifest=json.loads((root/"manifest.json").read_text())
    required={"result.json","rows.jsonl","frozen_plan/plan.json","frozen_plan/manifest.json",
              "frozen_plan/calibration_inputs.pt","source_snapshot/run_gpt2_adc_holdout.py",
              "source_snapshot/calibrated_adc_projection.py","source_snapshot/projection_numerical_control.py",
              "source_snapshot/tiled_projection_model.py","source_snapshot/run_gpt2_hybrid_evaluation.py"}
    assert required <= set(manifest)
    for name,expected in manifest.items():
        path=root/name
        assert path.resolve().is_relative_to(root.resolve())
        assert digest(path)==expected,name
    frozen=root/"frozen_plan"
    for name,expected in json.loads((frozen/"manifest.json").read_text()).items():
        assert digest(frozen/name)==expected
    plan=json.loads((frozen/"plan.json").read_text())
    result=json.loads((root/"result.json").read_text())
    assert result["frozen_plan_sha256"]==digest(frozen/"plan.json")
    for source in plan["sources"].values(): assert digest(source["path"])==source["sha256"]
    validation=json.loads(Path(plan["sources"]["validation_result"]["path"]).read_text())
    assert validation["protocol"]["evaluation_split"]=="validation"
    eligible=sorted((v["contract"]["profile"]["adc_bits"],name) for name,v in validation["variants"].items()
                    if name.startswith("calibrated_") and v["screen_pass"])
    selected=plan["selected_variant"]
    assert eligible and eligible[0][1]==selected
    assert plan["selected_contract"]==validation["variants"][selected]["contract"]
    assert digest(frozen/"calibration_inputs.pt")==plan["sources"]["calibration_inputs"]["sha256"]
    assert plan["screen"]==validation["protocol"]["screen"]
    previous=json.loads(Path(plan["sources"]["previous_test_protocol"]["path"]).read_text())
    assert plan["excluded_previous_test_windows"]==previous["test"]["windows"]
    width=plan["predictions_per_window"]+1
    windows=plan["windows"]
    assert len(windows)>=2
    for window in windows:
        assert len(window["ids"])==width
        assert window["start"]>=0 and window["start"]+width<=previous["test"]["total_tokens"]
        for old in plan["excluded_previous_test_windows"]:
            assert window["start"]+width<=old["start"] or old["start"]+len(old["ids"])<=window["start"]
    assert all(a["start"]+width<=b["start"] for a,b in zip(windows,windows[1:]))
    rows=[json.loads(line) for line in (root/"rows.jsonl").read_text().splitlines()]
    assert len(rows)==2*len(windows)
    assert set(result["variants"])=={"ideal",selected}
    controls=plan["numerical_control"]
    assert controls["version"]=="projection-and-log-probability-v2"
    assert controls["maximum_log_probability_error"]==.001
    assert controls["maximum_absolute_mean_target_nll_change"]==1e-5
    for name,summary in result["variants"].items():
        subset=[r for r in rows if r["variant"]==name]
        assert sorted(r["window"] for r in subset)==list(range(len(windows)))
        for row in subset:
            assert row["tokens"]==width-1 and row["start"]==windows[row["window"]]["start"]
            assert 0<=row["argmax_matches"]<=row["tokens"]
            if name=="ideal":
                c=row["numerical_control"]
                assert all(c[key] is True for key in ["pass","finite","projection_close","identical_argmax"])
                assert c["maximum_log_probability_error"]<controls["maximum_log_probability_error"]
                assert abs(c["mean_target_nll_change"])<controls["maximum_absolute_mean_target_nll_change"]
                assert row["argmax_matches"]==row["tokens"]
        n=sum(r["tokens"] for r in subset)
        a=sum(r["baseline_nll_sum"] for r in subset)/n;b=sum(r["candidate_nll_sum"] for r in subset)/n
        agreement=sum(r["argmax_matches"] for r in subset)/n
        assert summary["tokens"]==n
        for key,value in [("baseline_nll",a),("candidate_nll",b),("nll_increase",b-a),("argmax_agreement",agreement),
                          ("baseline_sample_perplexity",math.exp(a)),("candidate_sample_perplexity",math.exp(b))]:
            assert math.isclose(summary[key],value,rel_tol=1e-12,abs_tol=1e-12),key
        assert summary["screen_pass"]==(b-a<=plan["screen"]["maximum_nll_increase_nats"] and agreement>=plan["screen"]["minimum_argmax_agreement"])
        assert sum(t["vectors"] for t in summary["trace"])==len(windows)*width
    for index in range(len(windows)):
        assert len({r["baseline_nll_sum"] for r in rows if r["window"]==index})==1
    assert result["variants"][selected]["contract"]==plan["selected_contract"]
    assert sorted(c["window"] for c in result["fallback_controls"])==list(range(len(windows)))
    assert all(c["exact"] is True for c in result["fallback_controls"])
    assert result["ideal_control_pass"] is True
    assert not result["analog_authorized"] and not result["physical_profile_calibrated"] and not result["task_acceptance_established"]
    print(f"Verified {len(manifest)} hashes, {len(windows)} disjoint contexts and {n} predictions per variant")


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package",type=Path)
    check(parser.parse_args().package)
