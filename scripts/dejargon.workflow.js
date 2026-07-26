export const meta = {
  name: 'ai-hardware-dejargon',
  description: 'Rewrite every theme section into genuinely plain language (Sonnet, per theme)',
  phases: [{ title: 'Rewrite' }],
}

const ROOT = '/home/manishmehta/ui-projects/ai-hardware-analysis'
const SECT = `${ROOT}/analysis/themes/sections`
const KEYS = ['T1_attention','T2_quantization','T3_memory','T4_interconnect','T5_sparsity',
  'T6_compiler','T7_security','T8_reliability','T9_specialized','T0_other']

function prompt(key) {
  const f = `${SECT}/${key}.json`
  return [
    `Read ${f} (a JSON explainer section: problem_plain, why_plain, approach_plain, groups[{heading,explain,papers[{id,name,gloss}]}], connect).`,
    `REWRITE it IN PLACE (same file, same JSON shape, same paper ids and order) so a smart adult who knows NOTHING about computer chips understands every line.`,
    ``,
    `A reader is assumed to already know ONLY these ten plain ideas (defined elsewhere on the page): math-vs-memory,`,
    `the model's running notes, reading-vs-writing an answer, smaller numbers (rounding), skipping unimportant numbers,`,
    `a model made of specialists, a flexible chip vs a hard-wired chip, doing math inside the memory, chips talking to`,
    `each other, and bandwidth (how fast data moves). You MAY use those.`,
    ``,
    `BANNED — never use these without replacing them with plain words: kernel, GEMM, GEMV, softmax, tensor core, SM,`,
    `warp, CUDA, systolic, dataflow array, KV cache (say "the model's running notes"), MoE (say "a model of specialists"),`,
    `quantize/quantization (say "use smaller/rounded numbers"), sparsity/sparse (say "skipping unimportant numbers"),`,
    `DRAM/SRAM/HBM/GDDR6 (say "memory chips"/"fast on-chip memory"), CXL (say "a fast link to extra memory"),`,
    `PIM/CIM/NMP (say "doing math inside the memory"), NoC/interconnect/all-reduce/all-to-all/collective (say`,
    `"the wiring/messages between chips"), RoPE, TLB, MMIO, MSHR, BTB, prefetch (say "fetching data early"),`,
    `RTL/HLS (say "a chip blueprint"), chiplet/interposer/hybrid-bonding (say "stacking chips together"),`,
    `transformer (say "the model"), embedding, LUT (say "a lookup table"), FlashAttention/vLLM/A100/H100`,
    `(say "the standard GPU software"/"a top data-center GPU"), INT4/INT8/FP8/W4A8/MXFP (say "4-bit"/"8-bit numbers").`,
    ``,
    `RULES:`,
    `- Every gloss: 10-22 plain words. Say what the paper actually DOES and WHY, in words a curious outsider gets.`,
    `  Keep the striking headline number if there is one (e.g. "2.3x faster", "half the energy").`,
    `- If a paper truly needs a rare idea, explain it in 3-5 words inline, don't just name it.`,
    `- Keep the structure and every id. Do not drop or merge papers.`,
    `- The problem_plain / approach_plain / explain fields must also be jargon-free and genuinely explanatory.`,
    ``,
    `After writing, return the count of glosses rewritten.`,
  ].join('\n')
}

const res = await parallel(
  KEYS.map(k => () => agent(prompt(k), { label: `dejargon:${k}`, phase: 'Rewrite', model: 'sonnet' }))
)
return { rewritten: res.filter(Boolean).length }
