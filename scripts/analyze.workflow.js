export const meta = {
  name: 'ai-hardware-analysis',
  description: 'Per-paper analysis of AI-hardware/architecture/circuits papers (Sonnet, full-text where available)',
  phases: [{ title: 'Extract' }],
}

// args: { conf, year, n_batches }  (conf/year default to the mlsys-2025 pilot)
const A = (() => {
  try { return typeof args === 'string' ? JSON.parse(args) : (args || {}) } catch { return {} }
})()
const CONF = A.conf || 'mlsys'
const YEAR = A.year || '2025'
const N = A.n_batches || 5
const ROOT = '/home/manishmehta/ui-projects/ai-hardware-analysis'
const BDIR = `${ROOT}/analysis/per-paper/batches`
const ODIR = `${ROOT}/analysis/per-paper`

const HW_TARGET = 'GPU, ASIC, FPGA, CIM (compute-in-memory), CPU, chiplet, photonic, analog, NPU, TPU, PIM (processing-in-memory), SoC, RISC-V'
const TECH = 'dataflow, quantization, sparsity, memory-system, interconnect, compiler, circuit-design, packaging, power, scheduling, near-data-processing, approximation, pruning, kernel-fusion, parallelism, virtualization, security'
const WORK = 'LLM-inference, LLM-training, CNN, transformer, recommendation, GNN, diffusion, attention, MoE, graph-analytics, HPC, DLRM, RL, vision, speech, database'

function prompt(bs) {
  const inf = `${BDIR}/batch_${bs}.jsonl`
  return [
    `You are a computer-architecture / AI-hardware analyst extracting structured records from ${CONF.toUpperCase()} ${YEAR} papers.`,
    `Read ${inf} (JSONL; fields: id, title, venue, authors, abstract, text_path).`,
    ``,
    `For EACH paper:`,
    `- If text_path is non-null, READ that file (the extracted full paper) and analyze from the full text — this is a deep read.`,
    `- Else analyze from title + abstract only.`,
    `- RESUMABLE: if ${ODIR}/<id>.json already exists, skip that paper (do not rewrite).`,
    ``,
    `Produce a JSON object with EXACTLY these fields:`,
    `  id, title: copied from input.`,
    `  venue: "${CONF.toUpperCase()} ${YEAR}".`,
    `  problem: the specific problem addressed — 1-2 concrete technical sentences.`,
    `  motivation: why it matters / the trend or bottleneck driving it — 1 sentence.`,
    `  method: HOW the design works, in technical detail — 2-4 sentences. Name the actual mechanism`,
    `          (e.g. systolic dataflow, weight-stationary, W4A8 quantization, 2:4 sparsity, HBM/near-memory,`,
    `          NoC topology, chiplet/interposer, SRAM CIM macro, speculative decoding, kernel fusion, etc.).`,
    `  key_novelty: the single most novel idea — 1 sentence.`,
    `  contributions: array of 2-4 concrete contributions.`,
    `  hardware_target: array from {${HW_TARGET}} (or new term if none fit).`,
    `  technique_category: array from {${TECH}}.`,
    `  workloads: array from {${WORK}} — the AI/compute workloads targeted.`,
    `  metrics: object with any of {speedup, energy_or_tops_w, area, ppa, accuracy, other} as short strings`,
    `           quoting the paper's headline numbers vs baseline (e.g. speedup:"2.4x over A100"). Use null if not stated.`,
    `  baselines: array of systems/hardware compared against (e.g. ["A100","H100","prior ASIC X"]).`,
    `  limitations: 1 sentence on scope/limits (state "not discussed" if absent).`,
    `  tags: 3-6 lowercase tags (mechanisms/workloads/targets).`,
    `  primary_theme: one short phrase naming the paper's core theme (will be clustered later; be consistent).`,
    `  confidence: "high" if analyzed from full text, "low" if abstract-only, "none" if title-only.`,
    ``,
    `Write ${ODIR}/<id>.json (the object) AND ${ODIR}/<id>.md (a readable brief: title, one-line problem,`,
    `method, novelty, metrics, tags, confidence). Be concrete, technical, no marketing words.`,
    `Return only the count of papers you wrote this run (excluding skips).`,
  ].join('\n')
}

const idxs = Array.from({ length: N }, (_, i) => String(i).padStart(3, '0'))
const res = await parallel(
  idxs.map((bs) => () => agent(prompt(bs), { label: 'extract:' + bs, phase: 'Extract', model: 'sonnet' }))
)
return { conf: CONF, year: YEAR, batches: N, completed: res.filter(Boolean).length }
