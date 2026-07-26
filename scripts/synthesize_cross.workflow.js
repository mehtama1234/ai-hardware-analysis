export const meta = {
  name: 'ai-hardware-cross-venue-synthesis',
  description: 'Cross-venue comparative synthesis: MLSys vs ISCA/MICRO/HPCA/ASPLOS 2025 (Opus)',
  phases: [{ title: 'Synthesize' }],
}

const ROOT = '/home/manishmehta/ui-projects/ai-hardware-analysis'
const SDIR = `${ROOT}/analysis/syntheses`
const PDIR = `${ROOT}/analysis/per-paper`

const prompt = [
  `You are a senior computer-architecture analyst writing the cross-venue synthesis for a 2025 corpus`,
  `spanning five top venues: MLSys, ISCA, MICRO, HPCA, ASPLOS (619 papers, 503 analyzed).`,
  ``,
  `READ these inputs first:`,
  `- ${SDIR}/mlsys-2025-digest.md, isca-2025-digest.md, micro-2025-digest.md, hpca-2025-digest.md,`,
  `  asplos-2025-digest.md  — per-venue deterministic roll-ups (normalized hardware_target & workloads`,
  `  counts; RAW technique_category / primary_theme / tags to cluster).`,
  `- ${SDIR}/mlsys-2025-themes.md  — the already-written 9-theme taxonomy for MLSys (your anchor / reference).`,
  `- Sample ~8-12 per-paper JSONs per venue from ${PDIR}/<venue>-2025-*.json (prefer confidence:"high")`,
  `  to ground claims in specific papers. IDs look like isca-2025-004.`,
  ``,
  `WRITE ${SDIR}/cross-venue-2025-themes.md — a comparative synthesis. Required sections:`,
  ``,
  `1. **The one-paragraph picture** — what the whole 2025 AI-hardware field is collectively doing.`,
  `2. **Per-venue character** — one tight paragraph each (MLSys, ISCA, MICRO, HPCA, ASPLOS): what that`,
  `   venue is really about, its dominant hardware targets and workloads, and 2-3 signature papers by id.`,
  `   Draw the real contrast: MLSys is systems-for-LLMs on GPUs; the architecture venues carry the work`,
  `   MLSys lacks — real silicon/ASIC/CIM, memory systems & coherence, interconnect/NoC, security/side-`,
  `   channels, reliability, near-data processing.`,
  `3. **Shared cross-venue themes** — 6-10 themes that recur ACROSS venues (e.g. LLM/attention accelerm,`,
  `   quantization/low-precision, memory & near-data, interconnect & communication, sparsity/MoE,`,
  `   compilation/programming models, security & reliability). For each: which venues carry it, the shared`,
  `   mechanism, and representative papers by id+venue.`,
  `4. **What differs by venue** — where the venues diverge (what ISCA/MICRO/HPCA do that MLSys never touches,`,
  `   and vice versa). This is the core payoff of going wide.`,
  `5. **Cross-cutting observations** — recurring baselines, the co-design reflex, tensions, and honest GAPS.`,
  `6. **Coverage & confidence** — be explicit and honest: 619 papers, 503 analyzed (120 full-text/high,`,
  `   383 abstract-only/low), 116 title-only NOT analyzed (esp. MICRO: 76 title-only because IEEE withholds`,
  `   abstracts and many papers are not on arXiv). State that abstract-only analyses are shallower, and that`,
  `   MICRO's picture in particular is under-sampled. Do not overclaim.`,
  ``,
  `Be concrete and technical; ground every theme in specific paper ids; no marketing language. Write only`,
  `the file, then return a 150-word executive summary.`,
].join('\n')

const out = await agent(prompt, { label: 'cross-synthesis', phase: 'Synthesize', model: 'opus' })
return { summary: out }
