export const meta = {
  name: 'ai-hardware-analysis-haiku',
  description: 'Per-paper analysis with Haiku — for new venues (mostly abstract-only)',
  phases: [{ title: 'Extract' }],
}

// args: { venues: [["dac","2025",N], ...] }
const A = (() => {
  try { return typeof args === 'string' ? JSON.parse(args) : (args || {}) } catch { return {} }
})()
const VENUES = Array.isArray(A.venues) && A.venues.length
  ? A.venues
  : [[A.conf || 'dac', A.year || '2025', A.n_batches || 5]]

const ROOT = '/home/manishmehta/ui-projects/ai-hardware-analysis'
const BDIR = `${ROOT}/analysis/per-paper/batches`
const ODIR = `${ROOT}/analysis/per-paper`

const HW_TARGET = 'GPU, ASIC, FPGA, CIM (compute-in-memory), CPU, chiplet, photonic, analog, NPU, TPU, PIM (processing-in-memory), SoC, RISC-V, DPU, SmartNIC'
const TECH = 'dataflow, quantization, sparsity, memory-system, interconnect, compiler, circuit-design, packaging, power, scheduling, near-data-processing, approximation, pruning, kernel-fusion, parallelism, virtualization, security, cache, prefetching, reliability, coherence'
const WORK = 'LLM-inference, LLM-training, CNN, transformer, recommendation, GNN, diffusion, attention, MoE, graph-analytics, HPC, DLRM, RL, vision, speech, database, genomics, cryptography'

function prompt(conf, year, bs) {
  const inf = `${BDIR}/${conf}_${year}_batch_${bs}.jsonl`
  return [
    `You are a computer-architecture / AI-hardware analyst extracting structured records from top-venue papers.`,
    `Read ${inf} (JSONL; fields: id, title, venue, authors, abstract, text_path).`,
    ``,
    `For EACH paper:`,
    `- If text_path is non-null, READ that file (extracted full paper) and analyze from full text.`,
    `- Else analyze from title + abstract only.`,
    `- RESUMABLE: if ${ODIR}/<id>.json already exists, skip that paper (do not rewrite).`,
    ``,
    `Produce a JSON object with EXACTLY these fields:`,
    `  id, title: copied from input.  venue: copied from input.venue.`,
    `  problem: the specific problem addressed — 1-2 concrete technical sentences.`,
    `  motivation: why it matters / the bottleneck or trend driving it — 1 sentence.`,
    `  method: HOW the design works, in technical detail — 2-4 sentences. Name the actual mechanism.`,
    `  key_novelty: the single most novel idea — 1 sentence.`,
    `  contributions: array of 2-4 concrete contributions.`,
    `  hardware_target: array from {${HW_TARGET}}.`,
    `  technique_category: array from {${TECH}}.`,
    `  workloads: array from {${WORK}}.`,
    `  metrics: object with any of {speedup, energy_or_tops_w, area, ppa, accuracy, other} as short strings.`,
    `  baselines: array of systems/hardware compared against.`,
    `  limitations: 1 sentence (state "not discussed" if absent).`,
    `  tags: 3-6 lowercase tags.`,
    `  primary_theme: one short phrase naming the core theme.`,
    `  confidence: "high" if analyzed from full text, "low" if abstract-only. (Never a number.)`,
    ``,
    `Write ${ODIR}/<id>.json (the object) AND ${ODIR}/<id>.md (readable brief).`,
    `Return only the count of papers you wrote this run (excluding skips).`,
  ].join('\n')
}

const WAVE = A.wave || 8
const tasks = []
for (const [conf, year, n] of VENUES) {
  for (let i = 0; i < n; i++) tasks.push([conf, year, String(i).padStart(3, '0')])
}

// Run in waves to avoid rate limiting
const results = []
for (let i = 0; i < tasks.length; i += WAVE) {
  const wave = tasks.slice(i, i + WAVE)
  log(`Wave ${Math.floor(i/WAVE)+1}/${Math.ceil(tasks.length/WAVE)}: ${wave.map(t=>t[0]+'-'+t[2]).join(', ')}`)
  const waveRes = await parallel(wave.map(([conf, year, bs]) => () =>
    agent(prompt(conf, year, bs), { label: `haiku:${conf}-${bs}`, phase: 'Extract', model: 'haiku' })
  ))
  results.push(...waveRes)
}

return { venues: VENUES.map(v => v[0]), batches: tasks.length, completed: results.filter(Boolean).length }
