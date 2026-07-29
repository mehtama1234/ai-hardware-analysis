# Sources for the Kimi K3 lab

Two kinds of source: **ali's explainer** (the narrative spine) and the **official
Moonshot papers** (ground truth for configs, math, and benchmark numbers). Where they
differ, the official reports win; ali's thread is the pedagogy.

## 1 — The explainer (narrative spine)
- **ali (@waterloo_intern)** — *"22580: From GPT-2 to Kimi K3, Explained"*, X, Jul 27 2026.
  Archived: `ali-on-X-original.mht`, `ali-thread-extracted.txt`.
  https://x.com/waterloo_intern/status/2081762065392541951

## 2 — Official Moonshot reports (ground truth)

### Kimi Linear (the KDA paper) — backs Sessions 03–06
- **arXiv 2510.26692** — *Kimi Linear: An Expressive, Efficient Attention Architecture*.
  https://arxiv.org/abs/2510.26692 · code https://github.com/MoonshotAI/Kimi-Linear
- Ground-truth claims to hold the lab to:
  - **KDA extends Gated DeltaNet with a finer-grained (per-channel) gating mechanism** — better use of finite-state RNN memory.
  - Chunkwise algorithm uses a specialized **Diagonal-Plus-Low-Rank (DPLR)** transition-matrix variant; cheaper than general DPLR, closer to the classical delta rule.
  - Config: **3B activated / 48B total**, layerwise **hybrid of KDA + Multi-Head Latent Attention (MLA)**.
  - Results: **first linear-attn to beat full attention under fair comparison** (short, long, RL); **KV cache −75%**; **up to 6× decode throughput at 1M context**.

### Kimi K3 technical report — backs Session 07
- **k3_tech_report.pdf** — https://github.com/MoonshotAI/Kimi-K3/blob/main/k3_tech_report.pdf
  · weights https://huggingface.co/moonshotai/Kimi-K3
- Ground-truth claims:
  - **2.8T-param MoE, ~104B active per token**; native vision; **1M-token context**.
  - Built on **Kimi Delta Attention (KDA)** + **Attention Residuals (AttnRes)**.
  - **Stable LatentMoE**: activates **16 of 896 experts** (2 shared).
  - **~2.5× intelligence per unit compute vs Kimi K2** — "not just more params."
  - Algorithm–system co-design; progressive context-length training; **Multi-Teacher On-Policy Distillation (MOPD)** merging 9 expert RL models.

## Cross-check notes (ali ↔ official)
- ali says "898 experts, 2 shared, router picks 16 of 896" → matches K3 report's "16 of 896 (+2 shared)". ✓
- ali's "per-channel decay" for KDA → matches paper's "finer-grained gating." ✓
- ali's chunked/Householder DeltaNet story → the paper's DPLR chunkwise variant is the productionized form. (Session 04/06 should note DPLR by name.)
- TODO when building 05–07: mine `k3_tech_report.pdf` + arXiv 2510.26692 full text for exact SiTU formula, AttnRes math, macrocycle layout (ali: 23×(3 KDA+1 MLA)).
