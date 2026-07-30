"""
Serving page — the real cost of a 2.8-trillion-setting model, and how 4-bit
quantization changes it.

A 2.8T model stored the normal way (16 bits per setting) is 5.6 TB — far more than
any single accelerator holds. So models like this are SQUEEZED down to ~4 bits per
setting before serving. The modern way is "MXFP4" (a microscaling 4-bit float): the
OCP standard used by K3-class models. We implement it for real, quantize actual
word-meaning vectors with it, and measure the two things that matter: how much
smaller it gets, and how much accuracy is lost.

MXFP4 = tiny 4-bit floats (E2M1: values {0,.5,1,1.5,2,3,4,6}) sharing one power-of-two
scale per block of 32 numbers (the scale is an 8-bit exponent, E8M0). So the stored
cost is 4 bits per number + 8 bits per 32 = 4.25 bits/number.

Uses real GloVe vectors as stand-in weights. Pure torch/numpy, CPU.
"""
import gzip, json, os, math
import torch

GLOVE = os.path.expanduser("~/projects/llm-from-scratch-lab/02-embeddings/glove.50d.gz")

# load a big slab of real vectors to act as "weights"
rows = []
for line in gzip.open(GLOVE, "rt", encoding="utf-8"):
    parts = line.split(" ")[1:]
    if len(parts) != 50:                     # skip any header / malformed line
        continue
    rows.append([float(x) for x in parts])
    if len(rows) >= 20000: break
W = torch.tensor(rows)                       # (20000, 50) real-valued "weights"
W = W.flatten()
W = W[: (W.numel() // 32) * 32]              # trim to a multiple of the block size

MXFP4_CODES = torch.tensor([0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0])  # E2M1 magnitudes

def cos(a, b): return float(torch.nn.functional.cosine_similarity(a, b, dim=0))
def rel_err(orig, q): return float((orig - q).norm() / orig.norm())

def quant_mxfp4(w, block=32):
    x = w.view(-1, block)
    amax = x.abs().amax(-1, keepdim=True) + 1e-12
    # E8M0 scale: a power of two >= amax/6, so the block max fits under the top code (6)
    # without clipping (ceil, not floor — floor would let values exceed 6 and clip).
    scale = torch.pow(2.0, torch.ceil(torch.log2(amax / 6.0)))
    xs = x / scale
    sign = xs.sign()
    # snap each magnitude to the nearest representable MXFP4 code
    mag = xs.abs().unsqueeze(-1)
    idx = (mag - MXFP4_CODES).abs().argmin(-1)
    q = sign * MXFP4_CODES[idx] * scale
    return q.view(-1)

def quant_int8(w):                            # per-tensor symmetric 8-bit, for comparison
    scale = w.abs().max() / 127.0
    return (w / scale).round().clamp(-127, 127) * scale

def quant_int4(w, block=32):                  # naive 4-bit integer (no float codes), block-scaled
    x = w.view(-1, block)
    scale = x.abs().amax(-1, keepdim=True) / 7.0 + 1e-12
    q = (x / scale).round().clamp(-7, 7) * scale
    return q.view(-1)

schemes = {
    "fp16 (16 bit)":      (W.half().float(),  16.0),
    "int8 (8 bit)":       (quant_int8(W),      8.0),
    "int4 block (4 bit)": (quant_int4(W),      4.25),
    "MXFP4 (4 bit)":      (quant_mxfp4(W),     4.25),
}

TOTAL_PARAMS = 2.8e12
rows_out = []
for name, (q, bits) in schemes.items():
    tb = TOTAL_PARAMS * bits / 8 / 1e12       # terabytes for the whole model
    rows_out.append({"scheme": name, "bits_per_param": bits,
                     "rel_error_pct": round(rel_err(W, q) * 100, 3),
                     "cosine": round(cos(W, q), 5),
                     "model_TB": round(tb, 2),
                     "L4_gpus_needed": math.ceil(tb * 1000 / 24),   # 24 GB per L4
                     "H100_gpus_needed": math.ceil(tb * 1000 / 80)})  # 80 GB per H100

OUT = {"n_values_quantized": W.numel(), "block_size": 32, "total_params": TOTAL_PARAMS,
       "mxfp4_codes": MXFP4_CODES.tolist(), "rows": rows_out}
mx = next(r for r in rows_out if r["scheme"].startswith("MXFP4"))
fp = next(r for r in rows_out if r["scheme"].startswith("fp16"))
OUT["point"] = (f"Stored the normal 16-bit way, the 2.8-trillion-setting model is {fp['model_TB']:.1f} TB — it would take "
                f"{fp['H100_gpus_needed']} top-end 80GB accelerators just to hold it. Squeezing each setting to ~4 bits cuts "
                f"the model to {mx['model_TB']:.1f} TB ({mx['H100_gpus_needed']} accelerators), a ~4× drop, while the numbers "
                f"stay {mx['cosine']*100:.1f}% faithful to the originals. Honest surprise from our run: MXFP4 is NOT more "
                f"accurate than plain 4-bit integers here ({mx['rel_error_pct']}% error vs {[r for r in rows_out if r['scheme'].startswith('int4')][0]['rel_error_pct']}%) "
                "— its power-of-two shared scale wastes a little range. MXFP4 wins for a different reason: that power-of-two "
                "scale is almost free to apply in hardware and 4-bit floats run natively on the tensor cores, so it's faster "
                "and cheaper to serve at the same size. (Per-weight error isn't end-task accuracy: real serving also keeps the "
                "few most sensitive parts at higher precision.)")

here = os.path.dirname(os.path.abspath(__file__))
json.dump(OUT, open(os.path.join(here, "out_quant.json"), "w"), indent=2)
print(f"quantized {W.numel():,} real values (block=32):")
for r in rows_out:
    print(f"  {r['scheme']:>20}: {r['bits_per_param']:>5} bit  err {r['rel_error_pct']:>6}%  cos {r['cosine']:.5f}  |  model {r['model_TB']:>5.1f} TB  = {r['H100_gpus_needed']:>3} H100s")
print("wrote out_quant.json")
