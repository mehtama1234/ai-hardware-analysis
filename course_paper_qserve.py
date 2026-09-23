"""Focused MLSys walkthrough; simplified arithmetic is not a QServe benchmark."""

PDF = 'https://proceedings.mlsys.org/paper_files/paper/2025/file/fbe2b2f74a2ece8070d8fb073717bda6-Paper-Conference.pdf'

QSERVE = {
    'id': 'qserve-2025',
    'route': 'mlsys-2025',
    'title': 'QServe: when smaller numbers make the whole serving path faster',
    'identity': 'Yujun Lin, Haotian Tang, Shang Yang, and colleagues · QServe: W4A8KV4 Quantization and System Co-design for Efficient LLM Serving · MLSys 2025',
    'scope': 'A focused walkthrough of the paper’s quantization and execution co-design, its serving-throughput comparison, and the distinction between storage savings and useful work. The paper reports author-run experiments; this course does not reproduce them. Arithmetic examples are invented teaching models unless explicitly attributed.',
    'lessons': [('s2', 'Representation and rounding'), ('s3', 'Movement costs'), ('s6', 'Hardware execution'), ('s10', 'Complete serving path')],
    'blocks': [
        {
            'title': 'A number format changes both storage and work',
            'paragraphs': [
                'A model stores many numerical values. Quantization represents them with fewer bits, which can reduce the bytes that must fit in memory or move to the processor. But the processor must still interpret those compact values and calculate with them. If unpacking, rescaling, or converting them takes too much time, a smaller representation can make the complete operation slower.',
                'The names distinguish different jobs that numbers do. Weights are values learned during training and used in later calculations. Activations are intermediate results produced while processing an input. Attention keeps intermediate arrays called keys and values so it can reuse information from earlier text while processing later text. Their lifetimes differ: the same trained weights can serve many requests, while a request builds its own stored attention history.',
                'QServe names its format W4A8KV4: weights use 4-bit values, activations use 8-bit values, and the stored attention keys and values use 4-bit values. “Four bits” describes representation size; it does not mean the entire calculation happens as one four-bit operation. The supported hardware operations and the conversions between representations determine the execution path.',
                'To see the accounting, use an invented serial model. A conventional representation costs 80 time units to move and 20 to compute: 100 total. A compact representation halves movement to 40, but takes 65 extra units to unpack and convert, plus the same 20 units to compute: 125 total. Fewer bytes helped the storage side and lost on elapsed time. These units are deliberately simple; they are not GPU measurements or QServe’s measured overhead.',
            ],
        },
        {
            'title': 'The paper targets conversion on the critical path',
            'paragraphs': [
                'The paper identifies a concrete reason earlier low-bit approaches can lose at larger serving batches: conversion work may run on general-purpose GPU cores inside the repeated matrix calculation, rather than disappearing into the faster specialized matrix units. Its introduction reports 20–90% runtime overhead for dequantizing weights or partial sums in the approaches it studies. A fast multiply does not help if every iteration waits for a slower conversion.',
                'The paper names its 4–8–4 conversion method QoQ. First, it converts weights to eight-bit integers with one scale for each output channel: the weights used to calculate one output component share that scale. It then packs smaller groups of those eight-bit values into four-bit codes for storage. When a matrix calculation needs them, its kernel rebuilds the codes as eight-bit integers and sends those integers to Tensor Cores: GPU units designed to multiply blocks of numbers quickly. The first conversion deliberately keeps the eight-bit values inside a safe range, so rebuilding them does not overflow the eight-bit calculation.',
                'Section 3.1 shows why that range matters. In the paper’s example, a weight value of 120 receives the four-bit code 15, with a scale of 16 and an offset of 7. Rebuilding it gives (15 − 7) × 16 = 128, above the signed eight-bit maximum of 127. The original value fitted; the reconstructed approximation does not. The paper restricts the first conversion to −119 through 119 to leave room for this reconstruction error. Keeping the intermediate calculation in range is a separate requirement from keeping the model’s answers accurate.',
                'Its SmoothAttention step moves a separate scaling adjustment from stored attention keys to queries, which are not stored in the four-bit cache. QServe also changes the order in which weights are stored and how they are unpacked. These are linked choices: format, numerical range, memory layout, and supported instructions must fit together.',
                'This is the broader design lesson: do not ask only “How many bits did we remove?” Ask where those bits are decoded, which unit performs that work, whether it lies on the result’s dependent path, and whether saved memory traffic outweighs the added work. A conversion overlapped with other work may have a different cost from one that every iteration must await.',
            ],
            'sources': [(PDF + '#page=1', 'Conference paper, introduction: conversion overhead'),
                        (PDF + '#page=5', 'Conference paper, sections 3.1–3.2 and Figure 6: protective range and SmoothAttention'),
                        (PDF + '#page=7', 'Conference paper, section 4.2: weight order and fast reconstruction')],
        },
        {
            'title': 'Check numerical quality separately from speed',
            'paragraphs': [
                'A compact representation approximates the original values. Therefore, faster execution is useful only if the resulting model still meets the application’s answer-quality requirement. “Accuracy” is not one universal number: next-token prediction, a set of question-answering tasks, and a production application can respond differently to the same numerical change.',
                'QServe evaluates numerical behavior separately from throughput, including perplexity and zero-shot task results in the paper’s stated configurations. Perplexity measures how well a language model predicts the next text item on a dataset; lower is better on that score. Read those tables for the specific models, tasks, sequence lengths, and calibration settings they cover. They are evidence about those tests, not a proof that every task, prompt, or downstream use is unaffected. A deployment needs an acceptance test for its own outputs as well as a serving-speed measurement.',
                'A useful invented acceptance rule is: a candidate must keep every required test within its allowed quality loss, then compete on time or cost among candidates that pass. A candidate that is fastest but fails the rule is not a faster solution to the same task; it has changed the task’s requirements.',
            ],
            'sources': [(PDF + '#page=8', 'Conference paper, numerical-quality evaluation')],
        },
        {
            'title': 'Read the throughput result with its comparison boundary',
            'paragraphs': [
                'The authors report maximum achievable serving-throughput improvements over TensorRT-LLM: 1.2× for Llama-3-8B on A100, 1.4× for Llama-3-8B on L40S, 2.4× for Qwen1.5-72B on A100, and 3.5× for Qwen1.5-72B on L40S. These ratios compare the paper’s QServe system with the best-performing TensorRT-LLM configuration across the precision configurations the authors tested. The paper also reports that QServe on L40S can exceed TensorRT-LLM on A100 for some of its evaluated models.',
                'Those numbers are throughput results, not a promise that each request has lower delay or that every model can move to a cheaper GPU. They depend on the named models, devices, software, serving setup, quality results, and throughput procedure. Before using them to estimate a service, match request lengths, batch and arrival patterns, response-time limits, and the quality test. Then measure the complete deployed path, including loading, conversion, queueing, and output delivery where relevant.',
                'A clean follow-up comparison would hold the model, inputs, output-quality rule, GPU, software, and offered workload fixed while separately measuring bytes moved, conversion time, matrix time, end-to-end throughput, and request-delay percentiles. That would help explain which cost changed. It is a proposed experiment, not one performed by this course.',
            ],
            'sources': [(PDF + '#page=1', 'Conference paper, abstract and headline result'), (PDF + '#page=16', 'Conference paper, Table 5 throughput configurations')],
        },
    ],
    'exercise': {
        'question': 'In the invented serial model, the original path costs 80 movement units plus 20 compute units. A compact path costs 40 movement units, 20 compute units, and 30 conversion units. Which is faster, and by what fraction? If conversion can overlap completely with movement but not computation, what is the compact-path time under that new assumption? What evidence would still be needed before claiming an application-level win?',
        'answer': 'The original costs 100 time units. The compact path costs 40 + 20 + 30 = 90, reducing time by 10%. Its speedup is 100/90, about 1.11×. If conversion overlaps movement completely, its time is max(40, 30) + 20 = 60: a 40% time reduction and a speedup of 100/60, about 1.67×. That overlap is an added assumption, not a free consequence of using compact values. A real claim still needs measured device timings, numerical-quality acceptance, the target model and workload, request-delay behavior, and the complete serving configuration. None of these toy ratios predicts QServe’s performance.',
    },
}
