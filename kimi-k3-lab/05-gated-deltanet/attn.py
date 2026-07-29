"""
Session 05 — Gated DeltaNet: let the board forget, not just overwrite.

DeltaNet (03/04) can REPLACE a fact it has an address for. What it can't do is
clear the board for a new topic, or let old memories fade on their own — the
delta rule only touches keys it's currently writing. Gated DeltaNet borrows one
idea from Mamba-2: a decay dial α that gently fades the WHOLE board each step,
before the delta write:

    S = α · S_old + kᵀ u          # decay everything a little, then write the delta

α=1 is pure DeltaNet (nothing fades); α=0 wipes the board. A value written at
step t and read Δ steps later has been multiplied by α·α·…·α = α^Δ — a
multiplicative running discount on the past.

We run into out_gated.json:
  A. Context switch — write a batch of topic-A facts, then a batch of topic-B
     facts, then recall. As α drops below 1, the stale early topic FADES (good —
     it freed capacity) and the fresh recent topic comes back CLEANER.
  B. Cumulative decay — a value written then left for Δ pure-decay steps comes
     back scaled by exactly α^Δ. We verify the running-discount law numerically.

Pure torch, CPU, tiny tensors.
"""
import json, math, os
import torch
import torch.nn.functional as F

torch.manual_seed(0)
OUT = {}

def proc(x): return F.normalize(F.silu(x), dim=-1)
def cos(a, b): return float(F.cosine_similarity(a, b, dim=0))

def gated_delta(q, k, v, beta, alpha):
    """Gated delta rule. beta = per-token write strength; alpha = per-token decay."""
    N, d = q.shape
    fq, fk = proc(q), proc(k)
    b = beta if torch.is_tensor(beta) else torch.full((N,), float(beta))
    a = alpha if torch.is_tensor(alpha) else torch.full((N,), float(alpha))
    S = torch.zeros(d, d); O = torch.zeros(N, d)
    for t in range(N):
        v_old = fk[t] @ S
        u = b[t] * (v[t] - v_old)
        S = a[t] * S + torch.outer(fk[t], u)     # decay, then write
        O[t] = fq[t] @ S
    return O

# ----------------------------------------------------------------------------
# A. Context switch — old topic should fade, new topic should sharpen.
#    Needle A is written early (topic A); needle B is written late (topic B).
# ----------------------------------------------------------------------------
def context_switch(alpha, d=64, N=64, trials=24):
    rA = []; rB = []
    pA, pB = 2, N - 5                              # early vs late needle
    for s in range(trials):
        g = torch.Generator().manual_seed(200 + s)
        k = torch.randn(N, d, generator=g); v = torch.randn(N, d, generator=g)
        beta = torch.ones(N)
        # query A: ask for the early needle's key at the end
        qA = k.clone(); qA[-1] = k[pA]
        rA.append(cos(gated_delta(qA, k, v, beta, alpha)[-1], v[pA]))
        # query B: ask for the late needle's key at the end
        qB = k.clone(); qB[-1] = k[pB]
        rB.append(cos(gated_delta(qB, k, v, beta, alpha)[-1], v[pB]))
    m = lambda xs: round(sum(xs) / len(xs), 3)
    return m(rA), m(rB)

rows = []
for alpha in [1.0, 0.99, 0.97, 0.94, 0.90, 0.80]:
    a_recall, b_recall = context_switch(alpha)
    rows.append({"alpha": alpha, "stale_A_recall": a_recall, "fresh_B_recall": b_recall})
OUT["context_switch"] = {
    "d": 64, "N": 64, "needle_A_pos": 2, "needle_B_pos": 59, "rows": rows,
    "point": "With forgetting off, the stale early topic is still fully on the page, cluttering the fresh "
             "later one. As you turn forgetting up, the old topic fades (its recall falls — that is the page "
             "letting go) and the recent topic comes back cleaner, because the early clutter has faded away. "
             "Turn it up too far and even the fresh topic starts to fade — forgetting is a dial, and its best "
             "setting depends on the text, which is exactly what the model learns.",
}

# ----------------------------------------------------------------------------
# B. Cumulative decay — verify the α^Δ running-discount law.
#    Write a needle, then take Δ pure-decay steps (β=0 → no writes), read it back.
# ----------------------------------------------------------------------------
def decay_law(alpha, Delta, d=48, trials=16):
    ratios = []
    for s in range(trials):
        g = torch.Generator().manual_seed(300 + s)
        N = 1 + Delta
        k = torch.randn(N, d, generator=g); v = torch.randn(N, d, generator=g)
        beta = torch.zeros(N); beta[0] = 1.0             # write only at t=0
        alp = torch.ones(N); alp[1:] = alpha             # decay on every step after
        q = k.clone(); q[-1] = k[0]                      # ask for the t=0 needle at the end
        # magnitude of recalled value vs the value written at t=0
        outN = gated_delta(q, k, v, beta, alp)[-1]
        # reference: same but read immediately at t=0 (no decay)
        out0 = gated_delta(k[:1], k[:1], v[:1], torch.ones(1), torch.ones(1))[0]
        ratios.append(float(outN.norm() / (out0.norm() + 1e-9)))
    return round(sum(ratios) / len(ratios), 4)

decay_rows = []
for alpha, Delta in [(0.9, 5), (0.9, 10), (0.9, 20), (0.95, 10), (0.99, 20)]:
    measured = decay_law(alpha, Delta)
    predicted = round(alpha ** Delta, 4)
    decay_rows.append({"alpha": alpha, "Delta": Delta, "measured_ratio": measured,
                       "predicted_alpha_pow_Delta": predicted})
OUT["decay_law"] = {
    "d": 48, "rows": decay_rows,
    "point": "A value written and then left untouched comes back scaled by the fade multiplied together once "
             "for every step waited — here a steady fade, so it's simply the fade raised to the number of steps. "
             "Measured matches predicted to a few thousandths. It's a running discount: a word's influence shrinks "
             "steadily the longer ago it was written, unless it keeps getting refreshed.",
}

here = os.path.dirname(os.path.abspath(__file__))
json.dump(OUT, open(os.path.join(here, "out_gated.json"), "w"), indent=2)

print("A. context switch (early topic-A needle vs late topic-B needle):")
for r in rows:
    print(f"   α={r['alpha']:.2f}  stale-A recall {r['stale_A_recall']:.3f}   fresh-B recall {r['fresh_B_recall']:.3f}")
print("B. cumulative decay law (measured vs α^Δ):")
for r in decay_rows:
    print(f"   α={r['alpha']}, Δ={r['Delta']:>2}  measured {r['measured_ratio']:.4f}   predicted {r['predicted_alpha_pow_Delta']:.4f}")
print("wrote out_gated.json")
