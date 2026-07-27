export const meta = {
  name: 'ai-hardware-theme-intros',
  description: 'Rich first-principles problem+approaches essay per theme (Opus)',
  phases: [{ title: 'Intros' }],
}

const ROOT = '/home/manishmehta/ui-projects/ai-hardware-analysis'
const BDIR = `${ROOT}/analysis/themes/buckets`
const ODIR = `${ROOT}/analysis/themes/deep`

const THEMES = [
  ['T1_attention', 'Serving language models fast — attention and the model\'s running notes'],
  ['T2_quantization', 'Using smaller numbers'],
  ['T3_memory', 'The memory wall — moving the math to the data'],
  ['T4_interconnect', 'When chips must talk to chips'],
  ['T5_sparsity', 'Skipping the work that does not matter'],
  ['T6_compiler', 'Describing hardware so a machine can build it'],
  ['T7_security', 'Trusting the machine — attacks and defenses'],
  ['T8_reliability', 'Being sure it is actually correct'],
  ['T9_specialized', 'Beyond the GPU — new chips and new domains'],
  ['T0_other', 'Everything else that keeps it running'],
]

function prompt(key, label) {
  const inf = `${BDIR}/${key}.jsonl`
  const out = `${ODIR}/${key}_intro.json`
  return [
    `You are writing the opening of a deep, first-principles explainer chapter titled "${label}", for a smart`,
    `person who knows NOTHING about computer chips. Read EVERY paper in ${inf} (JSONL: id, t=title, v=venue,`,
    `c=confidence, pb=problem, me=method, nv=novelty, hw, wl, mx=metrics) to ground yourself in what this theme covers.`,
    ``,
    `Then WRITE ${out}:`,
    `{`,
    `  "problem_in_depth": "4-7 rich paragraphs. Explain, from PHYSICAL FIRST PRINCIPLES, what problem this whole`,
    `     theme is about and WHY it exists — the way a great teacher would, building it up from nothing. No cliche,`,
    `     no jargon (translate any unavoidable term). Connect it to the one root problem: computers are limited by`,
    `     moving data around, not by doing arithmetic. Make the reader FEEL why this is hard and why it matters.",`,
    `  "approaches": [`,
    `     { "title": "plain name of a distinct approach the field uses",`,
    `       "prose": "2-4 paragraphs explaining this approach from first principles: the core idea, why it works,`,
    `                 what it trades off. Name the mechanism in plain words. Reference a few papers by id as examples." }`,
    `     // 4-7 approaches, ordered from most fundamental/common to more specialized`,
    `  ],`,
    `  "where_it_stands": "1-2 paragraphs: what's solved, what's still open, and the honest gaps in this theme."`,
    `}`,
    ``,
    `VOICE: plain English, first principles, concrete, no marketing, no cliche. Translate EVERY acronym`,
    `(GPU = a flexible chip; a model's 'running notes' not 'KV cache'; 'smaller numbers' not 'quantization'; etc.).`,
    `This is the conceptual heart of the chapter — write it so a curious outsider genuinely understands the field.`,
    `After writing, return the number of approaches you wrote.`,
  ].join('\n')
}

const res = await parallel(
  THEMES.map(([k, l]) => () => agent(prompt(k, l), { label: `intro:${k}`, phase: 'Intros', model: 'opus' }))
)
return { intros: THEMES.length, completed: res.filter(Boolean).length }
