export const meta = {
  name: 'ai-hardware-theme-writeups',
  description: 'First-principles plain-language writeup of each theme + its papers (Sonnet, per theme)',
  phases: [{ title: 'Write' }],
}

const ROOT = '/home/manishmehta/ui-projects/ai-hardware-analysis'
const BDIR = `${ROOT}/analysis/themes/buckets`
const ODIR = `${ROOT}/analysis/themes/sections`

const THEMES = [
  ['T1_attention', 'LLM serving, attention & KV-cache'],
  ['T2_quantization', 'Using smaller numbers (quantization)'],
  ['T3_memory', 'The memory wall: near-data & in-memory compute'],
  ['T4_interconnect', 'Chips talking to chips (interconnect & communication)'],
  ['T5_sparsity', 'Skipping the work that does not matter (sparsity & MoE)'],
  ['T6_compiler', 'Describing hardware so a machine can build it (compilers & generators)'],
  ['T7_security', 'Trusting the machine (security & side-channels)'],
  ['T8_reliability', 'Being sure it is correct (reliability & verification)'],
  ['T9_specialized', 'Beyond the GPU (specialized silicon & new domains)'],
  ['T0_other', 'Everything else (systems & infrastructure)'],
]

function prompt(key, label) {
  const inf = `${BDIR}/${key}.jsonl`
  const out = `${ODIR}/${key}.json`
  return [
    `You are writing ONE section of a first-principles explainer of AI-hardware research for a smart NON-specialist.`,
    `Theme: "${label}".`,
    `Read EVERY paper in ${inf} (JSONL; fields id, t=title, v=venue, c=confidence, pb=problem, me=method,`,
    `nv=novelty, hw=hardware, wl=workloads, mx=metrics).`,
    ``,
    `Then WRITE a JSON object to ${out} with EXACTLY this shape:`,
    `{`,
    `  "problem_plain": "2-4 sentences: the specific sub-problem in plain first-principles words. NO jargon.",`,
    `  "why_plain": "1-2 sentences: the physical or economic reason this problem exists.",`,
    `  "approach_plain": "2-3 sentences: the shared approach across these papers, plain words.",`,
    `  "groups": [`,
    `    { "heading": "plain-language name of a sub-approach (no jargon)",`,
    `      "explain": "2-3 plain sentences explaining this sub-approach from first principles",`,
    `      "papers": [ { "id": "<paper id>", "name": "<system name or ''>", "gloss": "plain 8-18 words: what THIS paper does + headline number if striking; translate every acronym" } ] } `,
    `  ],`,
    `  "connect": "1-2 sentences tying this theme back to the ONE root problem: AI is bottlenecked by moving data, not by arithmetic."`,
    `}`,
    ``,
    `RULES:`,
    `- NO jargon, NO cliche, NO marketing. Explain any unavoidable term (e.g. "KV cache" = the model's running notes on the conversation) in plain words the first time it appears.`,
    `- Connect the dots: the reader should grasp WHY the problem exists physically, then the APPROACHES, then see the papers as instances.`,
    `- COVER ALL PAPERS in the file — every id gets exactly one gloss, filed under the best-fitting group. Use 2-7 groups.`,
    `- Full-text papers (c:"high") get the richest glosses; abstract-only (c:"low") get shorter, suitably hedged glosses.`,
    `- Write for reading. Be concrete and specific; name real mechanisms but in plain words.`,
    ``,
    `After writing the file, return only the count of papers you covered.`,
  ].join('\n')
}

const res = await parallel(
  THEMES.map(([key, label]) => () =>
    agent(prompt(key, label), { label: `write:${key}`, phase: 'Write', model: 'sonnet' }))
)
return { sections: THEMES.length, completed: res.filter(Boolean).length }
