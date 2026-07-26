export const meta = {
  name: 'ai-hardware-analysis',
  description: 'Per-paper analysis of AI-hardware/architecture/circuits papers (Sonnet, full-text where available, abstract-only otherwise)',
  phases: [{ title: 'Extract' }],
}

// args: { venues: [["isca","2025",8], ["micro","2025",4], ...] }  each = [conf, year, n_batches]
// back-compat: { conf, year, n_batches } for a single venue.
const A = (() => {
  try { return typeof args === 'string' ? JSON.parse(args) : (args || {}) } catch { return {} }
})()
const VENUES = Array.isArray(A.venues) && A.venues.length
  ? A.venues
  : [[A.conf || 'mlsys', A.year || '2025', A.n_batches || 5]]

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
    `- If text_path is non-null, READ that file (extracted full paper) and analyze from full text (deep read).`,
    `- Else analyze from title + abstract only.`,
    `- RESUMABLE: if ${ODIR}/<id>.json already exists, skip that paper (do not rewrite).`,
    ``,
    `Produce a JSON object with EXACTLY these fields:`,
    `  id, title: copied from input.  venue: copied from input.venue.`,
    `  problem: the specific problem addressed — 1-2 concrete technical sentences.`,
    `  motivation: why it matters / the bottleneck or trend driving it — 1 sentence.`,
    `  method: HOW the design works, in technical detail — 2-4 sentences. Name the actual mechanism`,
    `          (systolic/weight-stationary dataflow, W4A8 quantization, 2:4 sparsity, HBM/near-memory, NoC`,
    `          topology, chiplet/interposer, SRAM/ReRAM CIM macro, cache/coherence protocol, prefetcher,`,
    `          speculative decoding, kernel fusion, compiler pass, etc.).`,
    `  key_novelty: the single most novel idea — 1 sentence.`,
    `  contributions: array of 2-4 concrete contributions.`,
    `  hardware_target: array from {${HW_TARGET}} (map specific chips to the family, e.g. "A100"->"GPU").`,
    `  technique_category: array from {${TECH}} (prefer these exact terms; add a new one only if none fit).`,
    `  workloads: array from {${WORK}}.`,
    `  metrics: object with any of {speedup, energy_or_tops_w, area, ppa, accuracy, other} as short strings`,
    `           quoting headline numbers vs baseline (e.g. speedup:"2.4x over A100"). null if not stated.`,
    `  baselines: array of systems/hardware compared against.`,
    `  limitations: 1 sentence (state "not discussed" if absent).`,
    `  tags: 3-6 lowercase tags.`,
    `  primary_theme: one short phrase naming the core theme (consistent, clusterable).`,
    `  confidence: "high" if analyzed from full text, "low" if abstract-only. (Never a number.)`,
    ``,
    `Write ${ODIR}/<id>.json (the object) AND ${ODIR}/<id>.md (readable brief). Concrete, technical, no marketing.`,
    `Return only the count of papers you wrote this run (excluding skips).`,
  ].join('\n')
}

// build a flat list of batch descriptors across all venues
const tasks = []
for (const [conf, year, n] of VENUES) {
  for (let i = 0; i < n; i++) tasks.push([conf, year, String(i).padStart(3, '0')])
}

const res = await parallel(
  tasks.map(([conf, year, bs]) => () =>
    agent(prompt(conf, year, bs), { label: `extract:${conf}-${bs}`, phase: 'Extract', model: 'sonnet' }))
)
return { venues: VENUES.map(v => v[0]), batches: tasks.length, completed: res.filter(Boolean).length }
