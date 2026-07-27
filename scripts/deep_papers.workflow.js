export const meta = {
  name: 'ai-hardware-deep-papers',
  description: 'Per-paper deep writeups: "what it does" + "the method, in detail" (Sonnet)',
  phases: [{ title: 'Full-text methods' }, { title: 'Abstract summaries' }],
}

const A = (() => { try { return typeof args === 'string' ? JSON.parse(args) : (args || {}) } catch { return {} } })()
const NFT = A.ft || 24, NAB = A.ab || 24
const ROOT = '/home/manishmehta/ui-projects/ai-hardware-analysis'
const BDIR = `${ROOT}/analysis/themes/deep/batches`
const ODIR = `${ROOT}/analysis/themes/deep/papers`

const PLAIN = [
  `PLAIN-LANGUAGE RULES (a smart adult who knows nothing about chips must follow every line):`,
  `- Explain the idea from first principles. Translate EVERY acronym and insider term the first time.`,
  `- Banned unless explained inline in plain words: kernel(GPU program), GEMM(big matrix multiply), softmax,`,
  `  tensor core(the GPU's math units), KV cache(the model's running notes), MoE(a model of specialists),`,
  `  quantize(use smaller/rounded numbers), sparsity(skipping unimportant numbers), DRAM/SRAM/HBM(memory chips),`,
  `  CXL(a fast link to extra memory), PIM/CIM/NMP(doing math inside the memory), NoC/all-reduce/all-to-all`,
  `  (messages between chips), RowHammer(an attack that flips bits in memory), TEE(a walled-off secure area),`,
  `  systolic/dataflow array(a grid of tiny multipliers), bit-serial(one bit at a time), RTL(a chip blueprint).`,
  `- Concrete and specific. Name the real mechanism, but in words a curious outsider understands.`,
].join('\n')

function ftPrompt(bs) {
  const inf = `${BDIR}/ft_${bs}.jsonl`
  return [
    `You are writing deep, plain-language explanations of AI-hardware papers for a smart non-specialist.`,
    `Read ${inf} (JSONL: id, title, venue, theme, abstract, problem, method, tp=path to the full paper text).`,
    `For EACH paper: READ the full text at tp, then WRITE ${ODIR}/<id>.json:`,
    `{`,
    `  "id": "<id>", "confidence": "high",`,
    `  "what_it_does": "2-3 plain sentences: the problem this paper solves and what its answer is, big-picture.",`,
    `  "method_in_detail": "150-260 words, PLAIN. Explain HOW the design actually works, step by step, from the`,
    `     full text: what goes in, the core mechanism and why it helps, the single key design choice that makes`,
    `     it work, and the headline result vs what it's compared against. Use short paragraphs or labeled points`,
    `     (e.g. 'The idea.', 'How it works.', 'The catch.', 'The result.'). This is the centerpiece — make it genuinely explain."`,
    `}`,
    `RESUMABLE: skip any paper whose ${ODIR}/<id>.json already exists.`,
    PLAIN,
    `After writing, return the count written.`,
  ].join('\n')
}

function abPrompt(bs) {
  const inf = `${BDIR}/ab_${bs}.jsonl`
  return [
    `You are writing plain-language summaries of AI-hardware papers for a smart non-specialist.`,
    `Read ${inf} (JSONL: id, title, venue, theme, problem, method — these came from the ABSTRACT only; there is no full text).`,
    `For EACH paper WRITE ${ODIR}/<id>.json:`,
    `{`,
    `  "id": "<id>", "confidence": "low",`,
    `  "what_it_does": "3-5 plain sentences from the abstract: the problem, the approach in plain words, and what's new.`,
    `     Be appropriately hedged — this is from the abstract, not the full paper.",`,
    `  "method_in_detail": "" (leave empty — we did not read the full text)`,
    `}`,
    `RESUMABLE: skip any paper whose ${ODIR}/<id>.json already exists.`,
    PLAIN,
    `After writing, return the count written.`,
  ].join('\n')
}

const ftTasks = Array.from({ length: NFT }, (_, i) => String(i).padStart(3, '0')).map(bs => () =>
  agent(ftPrompt(bs), { label: `ft:${bs}`, phase: 'Full-text methods', model: 'sonnet' }))
const abTasks = Array.from({ length: NAB }, (_, i) => String(i).padStart(3, '0')).map(bs => () =>
  agent(abPrompt(bs), { label: `ab:${bs}`, phase: 'Abstract summaries', model: 'sonnet' }))

const res = await parallel([...ftTasks, ...abTasks])
return { fullText: NFT, abstract: NAB, completed: res.filter(Boolean).length }
