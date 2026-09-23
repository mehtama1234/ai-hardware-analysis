"""Focused ASPLOS walkthrough of mixed-precision quantization and GPU kernels."""

PDF = 'https://arxiv.org/abs/2410.12168'

COMET = {
    'id': 'comet-2025',
    'route': 'asplos-2025',
    'title': 'COMET: keep rare difficult values precise and the common case small',
    'identity': 'Lian Liu and colleagues · COMET: Towards Practical W4A4KV4 LLMs Serving · ASPLOS 2025',
    'scope': 'A focused walkthrough of activation outliers, mixed-precision quantization, data layout and conversion, GPU scheduling, and the reported serving evaluation. The local primary source text was inspected. Results are author-reported A100 measurements and have not been independently reproduced here. The error and work calculations are original teaching models.',
    'lessons': [('s2', 'Representation'), ('s6', 'Compilation'), ('s8', 'Accuracy and correctness'), ('s10', 'Whole-system cost')],
    'blocks': [
        {
            'title': 'A smaller representation is useful only if the answer survives',
            'paragraphs': [
                'Quantization stores numbers with fewer bits. That can reduce memory traffic and let a processor perform more operations per cycle, but it changes the numbers used by the model. The risk is not evenly distributed: most activation values may fit a narrow range, while a small number of outliers carry an unusually large value. Rounding every value to 4 bits can therefore save space and damage the output at the same time.',
                'COMET’s FMPQ method keeps most activation values at 4 bits and retains selected outliers at 8 bits. This is a mixed-precision representation: the system spends more bits where the error would matter most instead of giving every value the same precision. The acceptance condition remains application-level accuracy, not merely a lower byte count or a faster integer instruction.',
                'Original error model: suppose the exact output is the sum of 100 ordinary terms and 2 sensitive terms. If ordinary quantization contributes at most 0.01 error each, their worst-case sum is 1.0. If the two sensitive terms would contribute 0.5 each when quantized, protecting them at higher precision removes that additional 1.0. The numbers are invented to show why frequency and impact are different; they are not COMET measurements or an accuracy bound.',
            ],
            'sources': [(PDF, 'COMET paper, abstract and sections 3.1–3.2: W4A4KV4 motivation, activation outliers, and FMPQ')],
        },
        {
            'title': 'Mixed precision creates a data-layout problem',
            'paragraphs': [
                'A 4-bit value and an 8-bit value cannot be loaded, unpacked, and multiplied in exactly the same way. A straightforward implementation may spend so much time identifying formats, converting values, and moving scattered fields that it gives back the gain from using fewer bits. The algorithm therefore determines a kernel problem: where should the 4-bit and 8-bit pieces sit so loads and conversion can be regular?',
                'COMET’s W4Ax kernel uses a mixed-precision layout for W4A4 and W4A8 matrix multiplication. It overlaps data loading and conversion with computation, and it uses fast conversion paths rather than treating conversion as free. The layout is part of the algorithm–hardware contract: changing the format changes the instructions, buffers, synchronization, and amount of useful work per load.',
                'Original traffic model: a kernel needs to process 80 common values and 20 protected values. If the common values use 4 bits and protected values use 8 bits, the payload is 80×4 + 20×8 = 480 bits, or 60 bytes. A uniform 8-bit format needs 100 bytes, saving 40 bytes before metadata and alignment. If format metadata and conversion add 20 bytes of equivalent traffic, the net saving is only 20 bytes. The kernel must be judged on the complete path, not the nominal bit width.',
            ],
            'sources': [(PDF, 'COMET paper, section 4: W4Ax layout, conversion, software pipelining, and mixed-precision execution')],
        },
        {
            'title': 'Unequal work must be scheduled, not merely compressed',
            'paragraphs': [
                'The protected values create unequal work. Some tiles can use the fast W4A4 tensor-core path; others need W4A8 work and additional conversion. If GPU streaming multiprocessors receive very different mixtures, one processor can finish early while another remains on the critical path. COMET therefore adds fine-grained scheduling to balance mixed-precision tiles and overlaps the stages that can safely proceed together.',
                'This exposes a general rule: reducing the average cost of an item does not guarantee balanced execution. A scheduler needs the location and format of each tile, the resources required by each instruction type, and the dependencies between loading, conversion, multiplication, and reduction. More overlap also needs buffers and synchronization; a race or stale converted value would be a correctness failure, not an acceptable performance tradeoff.',
                'Original schedule model: four workers receive tiles costing 4, 4, 4, and 12 units. The batch finishes in 12 units. If the last tile can be split into three independent 4-unit tiles, the twelve units can be spread across the workers and the compute phase can finish in 8 units. If splitting adds 5 units of conversion and synchronization on the critical path, the new time is 13 and the change loses. Balance is valuable only after its coordination cost is counted.',
            ],
            'sources': [(PDF, 'COMET paper, sections 4.2–4.4: simultaneous W4A4/W4A8 execution, overlap, and SM scheduling')],
        },
        {
            'title': 'Separate kernel speed, serving throughput, and model quality',
            'paragraphs': [
                'COMET reports a kernel-level speedup of 2.88× over cuBLAS and an end-to-end throughput improvement of 2.02× over TensorRT-LLM for the stated LLaMA-family experiments on one A100-80G-SXM4. These are different comparisons: the first isolates a kernel against a library baseline, while the second includes the framework and serving path. A kernel ratio cannot be copied directly into a service ratio because loading, scheduling, KV-cache handling, and other operators remain.',
                'The paper evaluates W4A4 and W4A8 behavior, model accuracy, and KV-cache quantization under its chosen models, batch sizes, and GPU. Its claim of negligible accuracy loss belongs to those tested tasks and settings. It does not establish that every model has harmless outliers, that every long-context workload behaves the same way, or that an A100 result transfers unchanged to another GPU generation.',
                'The right follow-up keeps three ledgers separate: accepted model quality, time or tokens per second at the agreed service boundary, and energy or memory traffic if those matter. This course has not rerun COMET, inspected every reported accuracy table, or measured its kernels. The teaching examples are not COMET measurements.',
            ],
            'sources': [(PDF, 'COMET paper, abstract and evaluation sections: kernel, end-to-end, accuracy, and A100 evidence boundaries')],
        },
    ],
    'exercise': {
        'question': 'A mixed-precision kernel processes 80 values at 4 bits and 20 values at 8 bits. A uniform 8-bit kernel processes all 100 at 8 bits. How many payload bytes does each move? If mixed-precision metadata and conversion add 20 bytes, what is the net payload saving? What separate result must be checked before accepting the optimization?',
        'answer': 'The mixed payload is (80×4 + 20×8)/8 = 60 bytes. The uniform payload is 100×8/8 = 100 bytes. After 20 bytes of metadata and conversion, the mixed path has an 80-byte modeled cost, saving 20 bytes. The model’s accepted output quality must still be checked, along with total latency and any service-level requirement. These are original teaching calculations, not COMET measurements.',
    },
}
