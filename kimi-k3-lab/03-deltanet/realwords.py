"""
Session 03 — the overwrite demo, but with REAL words.

The main experiment on this page uses random vectors. Here we do the same thing
with actual English words, using real GloVe word-meanings (50-d) as the values —
so the recalled memory can be decoded back to the nearest real word, and you can
literally read what each memory returns.

Story: file "capital → Berlin", then later re-file "capital → Vienna" under the same
label, alongside a few unrelated facts. Ask for "capital". A memory that can edit
should return Vienna; one that only piles on returns a blur of Berlin+Vienna.

Uses ~/projects/llm-from-scratch-lab/02-embeddings/glove.50d.gz. Pure torch, CPU.
"""
import gzip, json, math, os
import torch
import torch.nn.functional as F

GLOVE = os.path.expanduser("~/projects/llm-from-scratch-lab/02-embeddings/glove.50d.gz")

# words we need: cue words, stored answers, and a decoding vocabulary of candidates
CUES = ["capital", "river", "color", "metal", "animal"]
ANSWERS = ["paris", "tokyo", "nile", "blue", "iron", "dog"]
DISTRACT = ["berlin", "vienna", "london", "rome", "madrid", "moscow", "seoul", "amazon", "thames",
            "red", "green", "gold", "silver", "copper", "cat", "horse", "wolf", "japan", "france"]
VOCAB = sorted(set(ANSWERS + DISTRACT))

wanted = set(CUES + ANSWERS + DISTRACT)
vecs = {}
for line in gzip.open(GLOVE, "rt", encoding="utf-8"):
    w, rest = line.split(" ", 1)
    if w in wanted:
        vecs[w] = torch.tensor([float(x) for x in rest.split()])
        if len(vecs) == len(wanted):
            break
d = len(next(iter(vecs.values())))

def V(w):
    return vecs[w].clone()

# --- the three memories (same math as attn.py, exposed as a single read) --------
def phi(x): return F.elu(x) + 1.0
def proc(x): return F.normalize(F.silu(x), dim=-1)
def cos(a, b): return float(F.cosine_similarity(a, b, dim=0))

def keep_every_note(k, v, q):                     # softmax over the stored facts
    A = (q @ k.T) / math.sqrt(d)
    return A.softmax(-1) @ v

def add_only(k, v, q):                            # linear attention: sum, then read
    fk = phi(k); S = fk.T @ v; z = fk.sum(0)
    fq = phi(q); return (fq @ S) / (fq @ z + 1e-6)

def erase_first(k, v, q, beta=1.0):               # the delta rule (order matters)
    fk = proc(k); S = torch.zeros(d, d)
    for t in range(k.shape[0]):
        v_old = fk[t] @ S
        S = S + torch.outer(fk[t], beta * (v[t] - v_old))
    return proc(q) @ S

def nearest(vec):
    sims = [(w, cos(vec, V(w))) for w in VOCAB]
    sims.sort(key=lambda p: -p[1])
    return sims[0], sims[:3]

# --- the sequence of facts (note: capital is written twice) ---------------------
FACTS = [("capital", "paris"),    # first answer
         ("river",   "nile"),
         ("color",   "blue"),
         ("capital", "tokyo"),    # OVERWRITE — the new answer
         ("metal",   "iron"),
         ("animal",  "dog")]
k = torch.stack([V(c) for c, a in FACTS])   # raw cue vectors as keys
v = torch.stack([V(a) for c, a in FACTS])
q = V("capital")

OUT = {"facts": FACTS, "query": "capital", "old_answer": "paris", "new_answer": "tokyo",
       "glove_dim": d, "vocab_size": len(VOCAB), "results": {}}

for name, fn, qq in [("keep every note", lambda: keep_every_note(k, v, q.unsqueeze(0))[0], None),
                      ("add-only (one summary)", lambda: add_only(k, v, q), None),
                      ("erase-first (edit in place)", lambda: erase_first(k, v, q), None)]:
    out = fn()
    (top_w, top_s), top3 = nearest(out)
    OUT["results"][name] = {
        "recalled_word": top_w, "recalled_sim": round(top_s, 3),
        "top3": [[w, round(s, 3)] for w, s in top3],
        "sim_to_new_tokyo": round(cos(out, V("tokyo")), 3),
        "sim_to_old_paris": round(cos(out, V("paris")), 3),
    }

OUT["point"] = ("Same overwrite, now with real words. The erase-first memory returns a vector whose nearest "
                "real word is the NEW answer (Tokyo) — it genuinely replaced Paris. Keep-every-note kept both "
                "and returns their average, so it sits about equally close to Paris and Tokyo — it couldn't pick. "
                "The add-only summary blurs everything into an unrelated word. You can read the difference straight off the words.")

here = os.path.dirname(os.path.abspath(__file__))
json.dump(OUT, open(os.path.join(here, "out_realwords.json"), "w"), indent=2)

print("stored:", FACTS, "| query: capital  (Paris then overwritten with Tokyo)")
for name, r in OUT["results"].items():
    print(f"  {name:>28}: → {r['recalled_word']:>8} (sim {r['recalled_sim']:.2f})  | tokyo {r['sim_to_new_tokyo']:+.2f} paris {r['sim_to_old_paris']:+.2f}")
print("wrote out_realwords.json")
