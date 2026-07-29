"""
Session 07 — Kimi K3: the assembly.

Everything so far was one rung. K3 puts them together and adds capacity only where
it does a job. The language backbone: 23 four-layer macrocycles, each 3 KDA layers
(constant-state recurrent memory, Sessions 03–06) + 1 MLA layer (full softmax
retrieval). On top of that spine, three ideas we can each run for real:

  A. Latent MoE sparsity — 898 experts (2 shared + 896 routed), router picks 16.
     Measure how few experts fire per token, and the compute that buys.
  B. SiTU activation — the report's activation; a soft-BOUNDED SiLU. We compute both
     curves and show where they diverge.
  C. Attention Residuals (AttnRes) — attend over DEPTH: a later block selectively
     pulls an earlier block's representation instead of getting a uniform blend.

Ground truth: Kimi K3 tech report (2.8T total, ~104B active, KDA+AttnRes,
Stable LatentMoE 16/896, native vision, 1M context). Pure torch, CPU.
"""
import json, os, math
import torch
import torch.nn.functional as F

torch.manual_seed(0)
OUT = {}
def cos(a, b): return float(F.cosine_similarity(a, b, dim=0))

# the backbone shape (from the thread's reading of the report)
OUT["backbone"] = {
    "macrocycles": 23, "layers_per_macrocycle": 4, "kda_per_cycle": 3, "mla_per_cycle": 1,
    "total_layers": 23 * 4, "kda_layers": 23 * 3, "mla_layers": 23 * 1,
    "attnres_every": 12, "attnres_blocks": math.ceil((23 * 4) / 12),   # 7 full + 1 partial = 8 (matches the report)
    "total_params": "2.8T", "active_params": "~104B", "experts": 898, "context": "1M", "vision": True,
}

# ----------------------------------------------------------------------------
# A. Latent MoE — how sparse is the compute?
# ----------------------------------------------------------------------------
def moe(E_routed=896, shared=2, k=16, T=1024, dm=64):
    g = torch.Generator().manual_seed(11)
    Wg = torch.randn(dm, E_routed, generator=g) / math.sqrt(dm)
    x = torch.randn(T, dm, generator=g)
    idx = (x @ Wg).topk(k, dim=-1).indices        # each token -> its top-k routed experts
    load = torch.bincount(idx.reshape(-1), minlength=E_routed).float()
    total = shared + E_routed
    active = shared + k
    return {
        "experts_total": total, "shared": shared, "routed": E_routed, "top_k": k, "tokens": T,
        "active_experts_per_token": active,
        "expert_fire_fraction_pct": round(active / total * 100, 2),
        "moe_flop_vs_dense_pct": round(active / total * 100, 2),
        "reported_active_params_pct": round(104 / 2800 * 100, 2),   # 104B of 2.8T
        "load_balance_cv": round(float(load.std() / load.mean()), 3),  # 0 = perfectly even
        "busiest_expert_tokens": int(load.max()), "quietest_expert_tokens": int(load.min()),
    }
OUT["moe"] = {**moe(),
    "point": "Of 898 specialists, each word wakes only 18 (2 always-on + 16 chosen) — under 2% of the crowd, so "
             "the specialist stage does about 2% of an ordinary model's work there. Across the whole model that's the "
             "report's ~104 billion of 2.8 trillion parts active per word (~3.7%). Enormous total ability, a sliver "
             "used per word. The chooser isn't perfectly even — keeping it balanced is a big focus of the real design.",
}

# ----------------------------------------------------------------------------
# B. SiTU activation — a soft-bounded SiLU (from the report's formula).
# ----------------------------------------------------------------------------
def situ_gate(gate, beta=1.0):
    return beta * torch.tanh(gate / beta) * torch.sigmoid(gate)   # replaces gate·σ(gate)
def silu_gate(gate):
    return gate * torch.sigmoid(gate)                              # SiLU

xs = torch.linspace(-6, 6, 25)
OUT["situ"] = {
    "x": [round(float(v), 2) for v in xs],
    "silu": [round(float(v), 3) for v in silu_gate(xs)],
    "situ": [round(float(v), 3) for v in situ_gate(xs)],
    "silu_at_6": round(float(silu_gate(torch.tensor(6.0))), 2),
    "situ_at_6": round(float(situ_gate(torch.tensor(6.0))), 2),
    "point": "The new squash wraps the old one in a soft cap, so instead of climbing forever it levels off (far out, "
             "the old one is near 6 and rising while the new one has settled near 1). A squash that can't run away keeps "
             "the numbers steady in a model this size. The report notes the plain version is about 3× slower to compute "
             "— offset because the specialists work in a compressed form that roughly halves their work.",
}

# ----------------------------------------------------------------------------
# C. Attention Residuals — attend over DEPTH, not just time.
#    Plain residual = uniform sum of earlier blocks. AttnRes = softmax over blocks,
#    so a layer can selectively pull the earlier representation it actually needs.
# ----------------------------------------------------------------------------
def attnres(N=8, Dm=64, trials=32):
    ra, rm = [], []
    for s in range(trials):
        g = torch.Generator().manual_seed(400 + s)
        signal = torch.randn(Dm, generator=g)
        blocks = torch.randn(N, Dm, generator=g) * 0.7
        blocks[2] = signal                              # one earlier block holds what we need
        mean_out = blocks.mean(0)                       # plain residual: everything weighted equally
        K = F.normalize(blocks, dim=-1)
        query = F.normalize(signal, dim=-1)             # a learned query that looks for the signal
        w = (K @ query).softmax(0)                      # softmax over the DEPTH (block) axis
        attn_out = (w[:, None] * blocks).sum(0)         # selective depth-wise retrieval
        ra.append(cos(attn_out, signal)); rm.append(cos(mean_out, signal))
    m = lambda z: round(sum(z) / len(z), 3)
    return {"N_blocks": N, "attnres_recovery": m(ra), "plain_residual_recovery": m(rm)}
OUT["attnres"] = {**attnres(),
    "point": "Normally a deep layer just gets an equal blend of everything the earlier layers produced, so one useful "
             "earlier result is watered down among all the rest. Reaching back scores the earlier layers and pulls out "
             "the one that matters — the same look-up trick, but across layers instead of across words — recovering it "
             "far better than the equal blend. The model does this every 12 layers, for a small speed gain at tiny extra "
             "cost, and to keep useful earlier results from getting lost in the blend.",
}

here = os.path.dirname(os.path.abspath(__file__))
json.dump(OUT, open(os.path.join(here, "out_k3.json"), "w"), indent=2)

b = OUT["backbone"]
print(f"backbone: {b['macrocycles']}×({b['kda_per_cycle']} KDA + {b['mla_per_cycle']} MLA) = {b['total_layers']} layers, AttnRes every {b['attnres_every']} → {b['attnres_blocks']} blocks")
print(f"A. MoE: {OUT['moe']['active_experts_per_token']} of {OUT['moe']['experts_total']} experts fire = {OUT['moe']['expert_fire_fraction_pct']}% (whole-model active {OUT['moe']['reported_active_params_pct']}%); load CV {OUT['moe']['load_balance_cv']}")
print(f"B. SiTU vs SiLU at x=6: SiTU {OUT['situ']['situ_at_6']} (bounded) vs SiLU {OUT['situ']['silu_at_6']} (unbounded)")
print(f"C. AttnRes recovery {OUT['attnres']['attnres_recovery']} vs plain residual {OUT['attnres']['plain_residual_recovery']}")
print("wrote out_k3.json")
