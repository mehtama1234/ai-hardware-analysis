"""Predeclared repeated training/holdout protocols; retain every result."""
import json
from pathlib import Path
from statistics import mean

from run_digits_quality import PROTOCOL, ROOT, run_case
from common.provenance import source_provenance

# The original protocol plus two new pairs chosen before running this experiment.
# Neither failing runs nor negative deltas are filtered out.
SEED_PAIRS = ((141, 142), (171, 172), (201, 202))


def main():
    cases = []
    for model_seed, split_seed in SEED_PAIRS:
        print("running", model_seed, split_seed, flush=True)
        cases.append(run_case(model_seed=model_seed, split_seed=split_seed))
    rows = [{"model_seed": c["protocol"]["model_seed"], "split_seed": c["protocol"]["split_seed"],
             "fp32_accuracy": c["rows"][0]["accuracy"], "packed_accuracy": c["rows"][1]["accuracy"],
             "accuracy_drop": c["rows"][0]["accuracy"] - c["rows"][1]["accuracy"],
             "checks": c["checks"], "status": c["status"]} for c in cases]
    passed = all(c["status"] == "task_gate_passed" for c in cases)
    report = {"status": "task_gate_passed" if passed else "task_gate_failed",
              "seed_pairs": SEED_PAIRS, "fixed_protocol": PROTOCOL, "rows": rows, "cases": cases,
              "mean_accuracy_drop": mean(r["accuracy_drop"] for r in rows),
              "maximum_accuracy_drop": max(r["accuracy_drop"] for r in rows),
              "evidence_kind": "measured_cpu", "gpu_execution_accepted": False,
              "scope": "three predeclared model/split seed pairs on bundled digits; same thresholds for every run; test sets overlap across splits and are not pooled as independent observations; no confidence interval, LLM quality or native INT4 compute claim",
              "provenance": source_provenance(ROOT.parent, [Path(__file__)])}
    output = Path(__file__).with_name("out_digits_repeats.json")
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    for row in rows:
        print(row)
    print(report["status"], output)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
