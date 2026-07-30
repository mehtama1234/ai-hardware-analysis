"""
Session 07 extra — why the crowd of specialists needs a balancing nudge.

A mixture-of-experts routes each word to a few of many specialists. Real text is
lopsided: some kinds of word are far more common than others, so if the router
just follows demand, a few popular experts get swamped while many sit nearly idle.
That uneven load wastes the capacity you paid to build and clogs the hardware.
The fix is a small "spread the load" incentive added during training. We run a
real (small) router BOTH ways on deliberately lopsided data and measure the load.

Pure torch, CPU.
"""
import json, os
import torch
import torch.nn.functional as F

torch.manual_seed(0)
E = 24          # experts
K = 2           # picked per token
D = 32          # token width
STEPS = 500
BATCH = 512

g = torch.Generator().manual_seed(1)
skill = F.normalize(torch.randn(E, D, generator=g), dim=-1)   # each expert's specialty
# lopsided demand: expert i is chosen with Zipf-ish popularity 1/(i+1)
pop = 1.0 / torch.arange(1, E + 1).float(); pop = pop / pop.sum()

def sample(B, gen):
    who = torch.multinomial(pop, B, replacement=True, generator=gen)   # which specialty this word needs
    x = F.normalize(skill[who] + 0.35 * torch.randn(B, D, generator=gen), dim=-1)
    return x, who

def train(balance):
    gen = torch.Generator().manual_seed(2)
    router = (torch.randn(D, E, generator=gen) * 0.02).requires_grad_(True)
    opt = torch.optim.Adam([router], lr=0.03)
    for step in range(STEPS):
        x, who = sample(BATCH, gen)
        logits = x @ router
        task = F.cross_entropy(logits, who)                  # route each word to the expert it needs
        loss = task
        if balance:
            load = logits.softmax(-1).mean(0)                # average routed mass per expert
            loss = task + 0.5 * (load * load).sum() * E      # penalty is 1 at uniform, larger if peaked
        opt.zero_grad(); loss.backward(); opt.step()
    with torch.no_grad():
        x, who = sample(8192, gen)
        topi = (x @ router).topk(K, -1).indices
        used = torch.bincount(topi.reshape(-1), minlength=E).float()
        acc = (topi[:, 0] == who).float().mean().item()      # top-1 routing accuracy
    frac = used / used.sum()
    active = int((used > (used.sum() * 0.005)).sum())         # "alive" = >0.5% of traffic
    return {"experts_used": active, "experts_total": E, "dead_experts": E - active,
            "busiest_expert_share_pct": round(float(frac.max()) * 100, 1),
            "max_over_mean_load": round(float(frac.max() / frac.mean()), 1),
            "routing_acc": round(acc, 3),
            "usage_per_expert": [round(float(f), 4) for f in frac]}

OUT = {"experts": E, "top_k": K, "steps": STEPS, "data": "lopsided (Zipf) demand"}
OUT["no_balance"]   = train(balance=False)
OUT["with_balance"] = train(balance=True)
nb, wb = OUT["no_balance"], OUT["with_balance"]
OUT["point"] = (f"On lopsided data with no balancing, the router just follows demand: the busiest single expert "
                f"handles {nb['busiest_expert_share_pct']}% of all traffic ({nb['max_over_mean_load']}× its fair share) "
                f"and only {nb['experts_used']} of {E} experts carry real load — the rest are nearly idle capacity you "
                f"still paid to build and run. Add a small 'spread the load' incentive and the busiest drops to "
                f"{wb['busiest_expert_share_pct']}% ({wb['max_over_mean_load']}× fair share) with {wb['experts_used']} of {E} "
                f"active, trading a little routing precision ({nb['routing_acc']:.0%}→{wb['routing_acc']:.0%}) for even load. "
                "That trade is exactly why a real mixture-of-experts ships with a stability trick.")

here = os.path.dirname(os.path.abspath(__file__))
json.dump(OUT, open(os.path.join(here, "out_moe.json"), "w"), indent=2)
print(f"MoE load after {STEPS} steps ({E} experts, top-{K}, lopsided demand):")
for name in ("no_balance", "with_balance"):
    r = OUT[name]
    print(f"  {name:>13}: busiest {r['busiest_expert_share_pct']}% ({r['max_over_mean_load']}x fair), {r['experts_used']}/{E} active, routing acc {r['routing_acc']}")
print("wrote out_moe.json")
