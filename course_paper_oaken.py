"""Focused ISCA walkthrough of memory-efficient KV-cache representation and serving."""

PDF = 'https://jongse-park.github.io/files/paper/2025-isca-oaken.pdf'
DOI = 'https://doi.org/10.1145/3695053.3731019'

OAKEN = {
    'id': 'oaken-2025',
    'route': 'isca-2025',
    'title': 'Oaken: shrink the model’s working notes without losing rare values',
    'identity': 'Minsu Kim, Seongmin Hong, RyeoWook Ko, and colleagues · Oaken: Fast and Efficient LLM Serving with Online-Offline Hybrid KV Cache Quantization · ISCA 2025',
    'scope': 'A focused walkthrough of the KV-cache memory problem, outlier-aware quantization, compact storage, and the paper’s serving evaluation. The author-hosted final conference paper and its DOI metadata were inspected. Performance results come from the paper’s accelerator simulation and its reported GPU baselines; they have not been rerun. Hardware area results are synthesis results, not measurements of fabricated Oaken silicon. Numerical examples below are original teaching models, not Oaken measurements or an implementation.',
    'lessons': [('s2', 'Represent numbers with limited precision'), ('s3', 'Follow data through memory'), ('s6', 'Match a computation to its execution plan'), ('s10', 'Measure the complete result')],
    'blocks': [
        {
            'title': 'Why a conversation needs a growing store of values',
            'paragraphs': [
                'To produce the next word, a language model uses information computed for earlier words. It keeps these intermediate key and value vectors in memory; together they are called the key–value cache, or KV cache. A longer conversation and a larger batch of simultaneous requests require more cached values. Each request has its own context, so the service generally cannot reuse another request’s cache just because the calculations look similar.',
                'The cache creates two different limits. Its total size can prevent a device from keeping enough requests or long conversations in fast memory. The speed of reading it can also limit token generation, because each step must consult past context. A larger, slower memory can fit more cache but may deliver it more slowly. Compression helps only if it reduces transfers without adding so much conversion work or answer error that the full serving path gets worse.',
                'This is the paper’s starting point: do not optimize the arithmetic alone. Change the stored representation, then provide hardware that can create, move, and read that representation efficiently. Oaken pairs a quantization method with a memory-management design and evaluates both as a serving system.',
            ],
            'sources': [(PDF + '#page=1', 'Final ISCA paper, sections 1–2: KV-cache pressure and serving context')],
        },
        {
            'title': 'Use separate number ranges for values that behave differently',
            'paragraphs': [
                'Quantization replaces a fine-grained number format with a smaller set of representable values. It saves storage and transfer space, but nearby original values may become the same stored value. A single large outlier can stretch the range used for an entire group, leaving small but important values packed into too few available steps.',
                'Original teaching example: imagine a 4-bit format with 16 evenly spaced levels spanning 0 to 64. The spacing is about 64/15, or 4.27. Values 1 and 2 both round to the level at zero. If those ordinary values instead get a separate range from 0 to 8, the levels are about 8/15, or 0.53 apart; 1 and 2 can be represented more distinctly. This is not Oaken’s exact threshold selection or a paper measurement. It shows why allocating separate ranges can protect small values when rare large values would otherwise set the scale.',
                'Oaken profiles each model’s layers before serving to estimate four cutoffs: values are divided into a middle group, unusually large values, and unusually small values. The paper reports doing about 100 sample inferences for this offline profiling. During serving, newly produced values are grouped using those cutoffs and quantized with ranges calculated for the current token. The middle group uses 4 bits; the two outlier groups use 5 bits after a group-shift operation moves their ranges closer to zero. The paper’s rationale is that large values should not set the scale for ordinary values, and tiny values should not disappear simply because the main group’s range is wide.',
                'The benefit depends on the profiling remaining useful. The authors report similar value ranges across the tested input datasets, but profiling is model-specific and still adds preparation and stored threshold state. A new model needs its own thresholds. If a future workload creates value patterns unlike the tested ones, the same thresholds may no longer preserve the same accuracy.',
            ],
            'sources': [(PDF + '#page=5', 'Final ISCA paper, sections 4.1–4.3: value distributions, thresholds, and per-token quantization'), (PDF + '#page=7', 'Final ISCA paper, section 4.4: group shifting and 4-/5-bit groups')],
        },
        {
            'title': 'Make the compact representation efficient to store and fetch',
            'paragraphs': [
                'Keeping ordinary values in a dense array is convenient, but storing exceptional values separately needs their values and locations. The paper gives a conventional sparse outlier entry as 23 bits: 16 for the value, 6 for its location, and 1 to identify its group. Oaken shifts and compresses outliers, then places four bits of each 5-bit value into the empty 4-bit slot left behind in the dense array. The remaining location, group, and sign information is stored in an 8-bit aligned entry. The dense and sparse parts therefore share information rather than paying twice for an outlier’s position.',
                'That layout creates a new access problem: ordinary dense values and exceptional sparse values must be brought back together in the correct order. Oaken adds quantization and dequantization engines and a memory-management unit to its data-movement hardware. The paper’s design uses page-sized dense and sparse transfers to avoid fragmented, poorly ordered bursts. This is why a smaller representation is not automatically a faster one: the reader must know where every piece belongs and fetch it in a pattern the memory can serve.',
                'The memory choice makes the trade visible. The paper’s architecture table lists 256 GB and 1.1 TB/s for its LPDDR configuration, compared with 80 GB and 2.0 TB/s for HBM. More capacity can accommodate larger batches or contexts, while lower bandwidth can slow generation. The point is not that LPDDR is universally preferable; it is that Oaken tries to spend fewer transferred bits so a larger, slower memory can still serve the tested workload effectively.',
                'Original teaching arithmetic: for 1,000 outlier entries, 23-bit records use 23,000 bits; 8-bit records use 8,000 bits. The representation saves 15,000 bits of outlier records, before counting the dense array, tables, transfer behavior, or hardware. This local saving does not by itself predict total cache capacity or serving speed.',
            ],
            'sources': [(PDF + '#page=7', 'Final ISCA paper, section 4.5: fused dense/sparse encoding'), (PDF + '#page=8', 'Final ISCA paper, section 5: memory-management hardware'), (PDF + '#page=10', 'Final ISCA paper, table 1: HBM and LPDDR capacity/bandwidth configurations')],
        },
        {
            'title': 'Read the result with its baseline and evidence type attached',
            'paragraphs': [
                'The paper’s abstract reports up to 1.58× throughput improvement over an NVIDIA A100 at batch size 256, with an average 0.54% accuracy loss relative to the KV-cache quantization methods used for that comparison. In the evaluation discussion, the authors separately report Oaken-LPDDR averaging 1.79× over vLLM and 1.58× over QServe at batch size 256. Keep those comparison statements attached to their named comparison systems; “1.58× faster” alone is ambiguous.',
                'The accuracy table uses a different reference: it reports Oaken averaging 0.87% below the original FP16 baseline, 0.54% below KVQuant, and 0.32% below KIVI. Thus the abstract’s 0.54% should not be paraphrased as the loss from the original FP16 model. Nor does an average across its eight models and selected language tasks guarantee the same quality change for a different model or downstream task.',
                'The system-level evidence is also bounded. The authors evaluate Oaken in an extended LPU simulator, a software model of the proposed system, and compare GPU systems using reported A100 configurations. They use synthesis—a tool that estimates an implementation from a hardware description—to estimate chip area. This is not a measurement from fabricated Oaken silicon. Longer contexts and batch sizes make memory capacity more important, but the comparison remains tied to the evaluated models, traces, devices, simulator, and quality measures. A follow-up deployment test should use new models and conversation patterns, measure complete request delay and accepted output quality, and include the cost of per-model profiling and sparse reconstruction.',
            ],
            'sources': [(PDF + '#page=1', 'Final ISCA paper, abstract: batch-256 A100 claim and stated accuracy comparison'), (PDF + '#page=10', 'Final ISCA paper, sections 6.1–6.2: evaluation method and baselines'), (PDF + '#page=11', 'Final ISCA paper, section 6: accuracy comparisons')],
        },
    ],
    'exercise': {
        'question': 'Using the paper’s record sizes, what is the storage difference for 1,000 outlier entries if each is represented with 23 bits rather than 8 bits? What important costs does this arithmetic leave out? Then explain why this difference alone cannot establish a faster service.',
        'answer': 'The records use 23,000 bits versus 8,000 bits, saving 15,000 bits. This counts only outlier records; it omits the dense values, indices and tables beyond the stated entry format, and actual transfer or reconstruction time. A faster service also depends on whether these values are fetched efficiently, how much conversion work is added, the available memory bandwidth, and whether generated answers still meet the required quality. The arithmetic is an explanation of the bit counts reported in the paper, not a measured performance result.',
    },
}
