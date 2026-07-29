"""
Session 06 — KDA / Kimi Linear: give every channel its own decay.

Gated DeltaNet (05) fades the whole board by one scalar α. That's blunt: some
kinds of information should linger (a name, a task instruction) while others
should vanish fast (a passing detail). Kimi Delta Attention (KDA) — the core of
Moonshot's Kimi Linear (arXiv 2510.26692) — replaces the single α with a VECTOR:
one decay rate per channel. The board can now hold some dimensions steady while
clearing others in the same step. Kimi Linear pairs this with a few full-attention
(MLA) layers, and is the first linear-attention model to beat full attention under
fair comparison.

We run into out_kda.json:
  A. Per-channel vs scalar — a task that needs BOTH "keep these channels" and
     "forget those channels" at once. Per-channel decay does both; no single
     scalar can (it must either keep everything or forget everything).
  B. The hybrid arithmetic — interleaving 3 KDA layers per 1 MLA layer means only
     1/4 of layers keep a growing KV cache → a 75% KV-cache cut, reproducing the
     paper's headline number from first principles.

Pure torch, CPU, tiny tensors.
"""
import json, os
import torch

torch.manual_seed(0)
OUT = {}

# ----------------------------------------------------------------------------
# A. Per-channel vs scalar decay. Split the stored value's channels into a group
#    we want to KEEP (slow decay) and a group we want to FORGET (fast decay).
#    Retention of a channel after T steps = its decay-rate^T.
# ----------------------------------------------------------------------------
def retain(decay_vec, T):
    return decay_vec ** T                     # per-channel survival after T steps

d = 64; T = 15
keep = slice(0, d // 2); forget = slice(d // 2, d)

# per-channel: 0.99 on the "keep" channels, 0.70 on the "forget" channels
a_perchan = torch.empty(d); a_perchan[keep] = 0.99; a_perchan[forget] = 0.70
# scalar options: one number for ALL channels
scalars = {"one dial: 0.99": 0.99, "one dial: 0.90": 0.90, "one dial: 0.70": 0.70}

def score(surv):
    # goal: KEEP-channels survive (→1) AND FORGET-channels vanish (→0)
    keep_ret = float(surv[keep].mean()); forget_ret = float(surv[forget].mean())
    return keep_ret, forget_ret, round(keep_ret * (1 - forget_ret), 3)

results = {}
kk, ff, sc = score(retain(a_perchan, T))
results["a dial per slot"] = {"keep_retention": round(kk, 3), "forget_retention": round(ff, 3), "goal_score": sc}
for name, a in scalars.items():
    kk, ff, sc = score(retain(torch.full((d,), a), T))
    results[name] = {"keep_retention": round(kk, 3), "forget_retention": round(ff, 3), "goal_score": sc}

OUT["per_channel"] = {
    "d": d, "steps": T,
    "keep_channels": "0.99 decay", "forget_channels": "0.70 decay",
    "goal": "keep_retention high AND forget_retention low  → goal_score = keep × (1 − forget)",
    "results": results,
    "point": "The task needs two things at once: hold the 'keep' slots and clear the 'forget' slots. Giving each "
             "slot its own dial does both (keep stays high, forget drops to near zero) for a goal score far above "
             "any single dial. One shared dial is forced to choose: set it to 0.99 and it keeps everything (never "
             "clears the clutter); set it to 0.70 and it forgets everything (loses what mattered). Per-slot control "
             "is simply more capable — the exact gain that lets this cheap memory match the keep-everything kind.",
}

# ----------------------------------------------------------------------------
# B. The hybrid arithmetic — why 3 KDA : 1 MLA gives −75% KV cache.
#    Only the full-attention (MLA) layers keep a growing KV cache; KDA layers hold
#    a fixed-size state (negligible vs a long-context cache).
# ----------------------------------------------------------------------------
def kv_bytes(n_full_layers, N, n_head=64, d_head=128, bytes_per=2):
    return 2 * n_full_layers * n_head * d_head * N * bytes_per

TOTAL = 48                      # layers
MLA = TOTAL // 4                # 1 in 4 is full attention (3 KDA : 1 MLA)
KDA = TOTAL - MLA
Ns = [8192, 32768, 131072, 1048576]
rows = []
for N in Ns:
    full = kv_bytes(TOTAL, N)               # every layer keeps a KV cache
    hybrid = kv_bytes(MLA, N)               # only the MLA layers do
    rows.append({"context": N,
                 "full_attention_GB": round(full / 1e9, 2),
                 "hybrid_GB": round(hybrid / 1e9, 2),
                 "reduction_pct": round((1 - hybrid / full) * 100, 1)})
OUT["hybrid"] = {
    "total_layers": TOTAL, "mla_layers": MLA, "kda_layers": KDA, "ratio": "3 cheap : 1 full",
    "rows": rows,
    "point": "The cheap layers keep a fixed-size page, so only the 1-in-4 full layers hold a store that grows with "
             "the text. That's a flat 75% cut in memory at every length — exactly the up-to-75% smaller memory the "
             "Kimi Linear report gives, and the same structure behind its up-to-6× faster generation on very long "
             "text. The full layers are the 'keep a little perfect memory' hedge; the cheap ones carry the rest.",
}

here = os.path.dirname(os.path.abspath(__file__))
json.dump(OUT, open(os.path.join(here, "out_kda.json"), "w"), indent=2)

print("A. per-channel vs scalar decay (keep g1 @0.99, forget g2 @0.70, T=15):")
for name, r in results.items():
    print(f"   {name:>20}: keep {r['keep_retention']:.3f}  forget {r['forget_retention']:.3f}  goal {r['goal_score']:.3f}")
print(f"B. hybrid KV cache ({KDA} KDA : {MLA} MLA of {TOTAL} layers):")
for r in rows:
    print(f"   ctx {r['context']:>8}  full {r['full_attention_GB']:>7.2f}GB  hybrid {r['hybrid_GB']:>6.2f}GB  → −{r['reduction_pct']:.0f}%")
print("wrote out_kda.json")
