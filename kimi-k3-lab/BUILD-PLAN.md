# Build plan — Kimi K3 lab, Sessions 03→07 (end to end)

Spec for the autonomous build. Sessions 00–02 are done and pushed. Each remaining
session follows the **same fixed pipeline**, and each ends in its own commit so progress
is durable and reviewable.

## Fixed per-session pipeline (do this for every session)
1. `NN-name/attn.py` — the REAL experiment(s). Pure torch, CPU, tiny tensors. Writes `out_*.json`.
   Print a legible console summary. Numbers must be produced, never transcribed.
2. Run it with `V=~/projects/llm-from-scratch-lab/.venv-torch; $V/bin/python attn.py`.
   Inspect the numbers. If the demo isn't crisp, fix the experiment (honestly) and rerun.
3. `NN-name/build_page.py` — render `out/index.html` in the lab style (dark serif, `--accent:#4FA8B8`,
   `.eye` eyebrows, `.why` boxes, `▶ We ran it` amber panels, one canvas/SVG visual, `.aha` closer,
   `.next` → next session). Embed the real numbers from the JSON.
4. Wire the session **live** in `build_site.py` (replace its `(None, …)` placeholder), run `build_site.py`.
5. Verify: `grep -c '{{'` == 0 (no leaked f-braces), `grep '�'` == 0, canvas/svg/table present,
   headline numbers present, `ast.parse` the builders.
6. Commit by explicit path: `git add kimi-k3-lab && git commit && git push origin master`.
   NEVER `git add -A` (repo has ~585 unrelated files). One commit per session.
7. Update README status checkbox + this plan.

## Sessions

### 03 — DeltaNet (the delta rule / Fast Weight Programmers)
- **Concept:** Session 02 showed a fixed board blurs. The delta rule fixes it: before writing key k's
  value, READ what's stored at k (`v_old = φ(k)·S`), and write only the correction `u = β(v_new − v_old)`.
  Erase-then-write instead of blind addition.
- **Real experiments:**
  - **Overwrite test (the killer demo):** write value v1 at key k, later write v2 at the SAME key, query k.
    Plain linear returns a blend (v1+v2); DeltaNet returns v2 cleanly. Measure recall of v2 (cos) for
    linear vs DeltaNet vs softmax.
  - **Needle-recall vs N:** rerun Session 02's needle for DeltaNet — show recall no longer fades (or fades
    far less) than plain linear.
- **Visual:** board where a write first erases the key's old cell, then writes the new (vs linear piling on).
- **Source:** ali §DeltaNet / Fast Weight Programmers (Schlag); grounds the "eviction" idea.

### 04 — Parallelizing DeltaNet (chunked / Householder / DPLR)
- **Concept:** the delta rule is sequential (each step needs the current S to compute v_old) → slow to train.
  Reparameterize `S_t = S_{t-1}(I − β kkᵀ) + β v kᵀ` → chunk-wise parallel. Chunk size C interpolates:
  C=1 pure recurrent, C=N full attention.
- **Real experiments:**
  - **Equivalence:** sequential DeltaNet vs chunked DeltaNet give identical output (Δ ≈ 0), like 02's re-association.
  - **Speed:** wall-clock of sequential vs chunked prefill across N — chunked wins on the same CPU. Show the
    FLOP split (fixed `2Ld²` state term + growing `2LCd` score term) and how C trades FLOPs for hardware use.
- **Visual:** chunk tiles — within-chunk real (masked) attention triangle + cross-chunk state carry.
- **Source:** ali §"Parallelizing Linear Transformers with Delta Rule"; note **DPLR** (Kimi Linear's production variant).

### 05 — Gated DeltaNet (Mamba-2 decay + delta)
- **Concept:** DeltaNet can replace a fact it has a key for, but can't clear the board for a new topic or fade
  memory generally. Add a scalar decay α: `S = α·S_old + write`. α=1 pure delta, α=0 clears.
- **Real experiments:**
  - **Context-switch test:** fill the board with topic-A facts, switch to topic-B, query a stale A needle.
    Ungated carries stale A (interference); gated (α<1) has faded A → cleaner B. Measure stale-vs-fresh recall.
  - **Cumulative decay:** a fact written at t, read at t+Δ, is scaled by α^Δ — verify the prefix-product behavior.
- **Visual:** board with a global fade dial; old cells dim over time.
- **Source:** ali §Gated Delta Net; Mamba-2 gating.

### 06 — KDA / Kimi Linear (per-channel gating + MLA hybrid)  ← ground truth: arXiv 2510.26692
- **Concept:** one scalar α fades everything equally — too blunt. KDA: **per-channel** decay (a vector, one rate
  per dimension). Fine-grained control; Kimi Linear's headline move.
- **Real experiments:**
  - **Per-channel vs scalar:** construct data where some channels should persist and others vanish fast; show
    per-channel KDA preserves the persistent channels while clearing volatile ones, beating scalar gating on a
    mixed recall task. Measure.
  - **Hybrid:** interleave MLA layers; show a hybrid stack matches full attention on the needle while keeping
    most layers cheap. Cross-check the paper's **−75% KV / up-to-6× decode** claims (cite, and reproduce the shape).
- **Visual:** board columns fading at independent rates (expand the overview's stage-4 viz).
- **Source:** Kimi Linear paper (DPLR, per-channel gating, 3B/48B hybrid).

### 07 — Kimi K3 (the assembly)  ← ground truth: k3_tech_report.pdf
- **Concept:** put it together. **23 four-layer macrocycles** (3 KDA + 1 MLA). **Latent MoE** (16 of 896 experts,
  +2 shared). **SiTU** activation. **Gated MLA**. **MLA query-LoRA**. **Blockwise AttnRes** every 12 layers (→ 8 blocks).
- **Real experiments (capstone — several minis):**
  - **MoE sparsity:** tiny router (16-of-896 scaled down); measure active/total ratio (~104B/2.8T ≈ 3.7%) and
    FLOPs saved vs dense.
  - **SiTU:** implement the report's SiTU formula (from the thread's pseudocode); plot SiTU vs SiLU; note the
    ~3× unfused slowdown and the latent-space ~½-FLOPs offset.
  - **AttnRes:** implement blockwise residual attention (softmax over block depth-representations); show a later
    layer selectively pulling an earlier block's representation. Measure the selective retrieval + the ~1.25× / ~2% figures.
  - **Macrocycle map:** a static diagram of 23×(3 KDA + 1 MLA), AttnRes every 12 layers → 8 blocks.
- **Source:** Kimi K3 tech report + ali §Kimi K3.

## Final polish (after 07)
- README: all 7 checked; landing page all-live.
- Add a "whole ladder" recap / capstone line to Session 07's closer.
- Re-verify every page (braces/FFFD/links), rebuild site, serve for viewing (screenshots blocked: no libnss3).
- Final commit. Announce the live site path.
