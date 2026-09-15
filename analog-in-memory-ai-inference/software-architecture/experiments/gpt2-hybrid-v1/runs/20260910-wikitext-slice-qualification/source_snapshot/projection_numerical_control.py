"""Separate projection arithmetic checks from shift-invariant model outputs."""
import torch

CONTRACT = {
    "version": "projection-and-log-probability-v2",
    "projection_atol": 1e-5, "projection_rtol": 1e-5,
    "maximum_log_probability_error": .001,
    "maximum_absolute_mean_target_nll_change": 1e-5,
    "require_identical_argmax": True,
    "rationale": "Check local arithmetic directly; log probabilities remove arbitrary per-position logit offsets. Bound every vocabulary probability ratio by exp(0.001), plus exact decisions and tighter mean target loss.",
    "prior_run": "20260909-wikitext-sampled remains rejected under its original raw-logit criterion",
}


def assess(native_projection, tiled_projection, baseline, candidate, targets):
    if native_projection.shape != tiled_projection.shape or baseline.shape != candidate.shape:
        raise ValueError("Control tensors must have identical shapes")
    finite = all(bool(torch.isfinite(x).all()) for x in [native_projection, tiled_projection, baseline, candidate])
    local_pass = torch.allclose(native_projection, tiled_projection,
                                atol=CONTRACT["projection_atol"], rtol=CONTRACT["projection_rtol"])
    lp, lq = baseline.double().log_softmax(-1), candidate.double().log_softmax(-1)
    maximum = float((lp-lq).abs().max())
    delta = float((lp-lq).gather(-1, targets.reshape(*baseline.shape[:-1], 1)).mean())
    same = torch.equal(baseline.argmax(-1), candidate.argmax(-1))
    return {"finite": finite, "projection_close": local_pass,
            "maximum_projection_error": float((native_projection-tiled_projection).abs().max()),
            "maximum_log_probability_error": maximum, "mean_target_nll_change": delta,
            "identical_argmax": same,
            "pass": finite and local_pass and maximum < CONTRACT["maximum_log_probability_error"]
                    and abs(delta) < CONTRACT["maximum_absolute_mean_target_nll_change"] and same}
