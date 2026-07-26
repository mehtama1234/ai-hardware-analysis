export const meta = {
  name: 'ai-hardware-synthesis',
  description: 'Cross-corpus theme synthesis over per-paper analyses (Opus)',
  phases: [{ title: 'Synthesize' }],
}

const A = (() => {
  try { return typeof args === 'string' ? JSON.parse(args) : (args || {}) } catch { return {} }
})()
const CONF = A.conf || 'mlsys'
const YEAR = A.year || '2025'
const ROOT = '/home/manishmehta/ui-projects/ai-hardware-analysis'
const PDIR = `${ROOT}/analysis/per-paper`
const SDIR = `${ROOT}/analysis/syntheses`

const prompt = [
  `You are a senior computer-architecture / AI-hardware analyst synthesizing themes across the`,
  `${CONF.toUpperCase()} ${YEAR} corpus.`,
  ``,
  `Inputs:`,
  `- ${SDIR}/${CONF}-${YEAR}-digest.md  — deterministic roll-up (normalized hardware/workload counts;`,
  `  RAW technique_category, primary_theme, and tags that you must semantically CLUSTER — they are too granular).`,
  `- ${PDIR}/${CONF}-${YEAR}-*.json     — the per-paper records (read them; each has problem, method,`,
  `  key_novelty, hardware_target, technique_category, workloads, metrics, primary_theme, confidence).`,
  ``,
  `Task: write ${SDIR}/${CONF}-${YEAR}-themes.md — a cross-corpus theme taxonomy. Requirements:`,
  `1. Identify 6-12 THEMES by clustering the granular primary_theme/tags/technique_category into coherent groups`,
  `   (e.g. "attention-kernel & KV-cache optimization", "quantization & low-precision", "parallelism & scheduling",`,
  `   "sparsity/MoE routing", "memory & near-data", "compiler/codegen", "interconnect/communication overlap").`,
  `2. For EACH theme: a 2-3 sentence description of the shared problem and the recurring MECHANISM(s); the list of`,
  `   member papers by id + short title; and the headline metric pattern (typical speedup/energy claims + baselines).`,
  `3. A "Workloads & targets" section: what hardware targets and AI workloads dominate this venue, from the counts.`,
  `4. A "Cross-cutting observations" section: what the field is collectively pushing on, recurring baselines`,
  `   (e.g. A100/H100/vLLM), tensions/trade-offs, and visible GAPS (what is NOT being worked on).`,
  `5. An honest "Coverage & confidence" line: n papers, full-text vs abstract-only split (from confidence fields).`,
  ``,
  `Be concrete and technical; ground every theme in specific papers; no marketing language. Write only the file,`,
  `then return a one-paragraph summary of the top 3 themes.`,
].join('\n')

const out = await agent(prompt, { label: 'synthesize', phase: 'Synthesize', model: 'opus' })
return { conf: CONF, year: YEAR, summary: out }
