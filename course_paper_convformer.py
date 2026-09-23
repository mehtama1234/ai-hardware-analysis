"""ISSCC chip walkthrough with explicit algorithm and measurement boundaries."""
PAPER = 'https://arxiv.org/pdf/2512.17555v1'
DOI = 'https://doi.org/10.1109/ISSCC49661.2025.10904499'

CONVFORMER = {
    'id': 'convformer-2025',
    'route': 'isscc-2025',
    'title': 'ConvFormer accelerator: reduce the work without hiding the changed answer',
    'identity': 'Pingcheng Dong, Yonghao Tan, and colleagues · ConvFormer accelerator · ISSCC 2025, paper 23.2',
    'scope': 'Focused reading of the three-page conference digest deposited as arXiv:2512.17555v1. Author-reported results were not reproduced. Numerical examples are original teaching models.',
    'lessons': [('s2', 'Numerical meaning'), ('s3', 'Live storage'), ('s6', 'Execution plans'), ('physical-design', 'Measurement boundaries')],
    'blocks': [
        {
            'title': 'Different stages can need different kinds of help',
            'paragraphs': [
                'Semantic segmentation assigns categories to image locations. A model first constructs useful features, then uses them to produce the location-level answers. One stage may wait for data while another spends most of its time calculating. Improving the first stage’s transfer path does not automatically reduce the second stage’s arithmetic.',
                'The paper makes three separate changes. It uses two different ways to decide which image locations should influence one another, keeps selected lookup data and learned convolution coefficients long enough to use them again, and removes selected groups of intermediate values with a learned mask. The choice of attention pattern and the mask are learned from data.',
                'In ordinary softmax attention, a query gives every possible match a score, converts scores with an exponential function, and normalizes them into weights. The paper’s linear-attention path uses a different calculation that can be arranged with a smaller temporary result. That is a changed model calculation, not merely an exact reordering of ordinary softmax attention. A query says what a location seeks, keys describe possible matches, and values supply information to combine. The following matrix examples isolate storage and arithmetic choices; they do not implement the trained model or establish equal segmentation quality.',
            ],
            'sources': [(PAPER + '#page=1', 'Conference digest, mechanisms and figures 23.2.1–23.2.5')],
        },
        {
            'title': 'Reassociation saves an intermediate only when the operation permits it',
            'paragraphs': [
                'First set aside attention’s nonlinear normalization and consider plain matrix multiplication in exact arithmetic. Let Q contain values 1 and 2 in a column, K contain 1 and 3, and V contain 2 and 4. Q times K-transpose produces rows [1,3] and [2,6]. Multiplying those rows by V gives 14 and 28. Alternatively, K-transpose times V gives the scalar fourteen; multiplying Q by it again gives 14 and 28. The answers agree while the temporary result has one entry rather than four. This equality follows from the rules of ordinary matrix multiplication, not from an assumption that any attention calculation can be rearranged this way.',
                'For N image locations and C values per location, with Q, K, and V each N by C, the first order creates an N-by-N temporary array and the second a C-by-C array. With N = 1,024 and C = 16, those have 1,048,576 and 256 entries. At two bytes per entry, that is 2 MiB versus 512 bytes if each array is fully kept. Processing small blocks can avoid holding the whole large array at once; these sizes are not a universal storage minimum for attention. They also exclude inputs, outputs, and other working storage. Ordinary dense multiplication counts are 2N²C versus 2NC² in this simplified equal-width case.',
                'Now restore an operation that cannot move through a product in the same way. For the first query, ordinary softmax turns scores [1,3] into positive weights proportional to exp(1) and exp(3), then makes them sum to one. The weighted value is about 3.762, not fourteen. Even normalizing the raw scores directly gives (1×2 + 3×4)/(1+3) = 3.5, also a different answer. Smaller storage follows from a changed formulation only after the required output behavior has been tested.',
            ],
        },
        {
            'title': 'Keep reusable data until all of its consumers are ready',
            'paragraphs': [
                'Use an invented 128 KiB buffer. Attention key/value data occupies 96 KiB, convolution weights another 96 KiB, and all required retained outputs and control state 16 KiB. Everything together needs 208 KiB and cannot fit. Either working set plus the retained state needs 112 KiB and fits. This makes execution order important.',
                'Suppose four tiles each need an attention phase followed by a convolution phase. Alternating phases tile by tile loads 96 KiB of key/value data and 96 KiB of weights four times, totaling 768 KiB of transfers. Doing all four attention phases first, retaining their required outputs within the stipulated 16 KiB, then doing all four convolution phases loads each large working set once: 192 KiB. The saving depends on those outputs fitting and the dependency order allowing the two phases.',
                'A neighboring tile can prevent early execution. Suppose a three-position convolution needs values [4,5,6] with weights [1,1,1]. Its answer is fifteen. If the last value is not ready, replacing it with zero gives nine, not an equivalent result. A schedule must wait, retain boundary data, recompute it legally, or adopt an explicitly evaluated approximation. Fusing stages does not cancel a neighbor dependency.',
            ],
        },
        {
            'title': 'Expand and prune only if the retained work and quality justify it',
            'paragraphs': [
                'In an original factorization example, input [1,2] multiplies a matrix with rows [1,0,1] and [0,1,1], producing intermediate [1,2,3]. A second matrix with rows [1,0], [0,1], and [1,1] produces output [4,5]. Dropping the third intermediate produces [1,2], changing both outputs by three. An intermediate that can be omitted mechanically is not necessarily unimportant to the answer.',
                'Count the dense work as well. A direct 64-input, 64-output matrix product needs 4,096 multiplications per input vector. Factoring through 128 intermediate channels needs 64×128 + 128×64 = 16,384 if all channels are computed. If only sixteen channels are retained, and the implementation can skip both their generation and use for all discarded channels, it needs 64×16 + 16×64 = 2,048. The expansion alone increases work; the usable pruning creates the saving.',
                'That count excludes mask decoding, indexing, movement, and output accumulation. It also assumes the trained factorization and mask preserve the required quality. Sparse values scattered in inconvenient positions can cost more to locate and move than a regular kept block. The representation of sparsity must match what the hardware can actually skip.',
            ],
        },
        {
            'title': 'Read silicon measurements without extending their boundary',
            'paragraphs': [
                'The digest reports a fabricated 28 nm chip and tests SegFormer-B0, PVTv1-Ti, and PVTv2-B0 on Cityscapes. Its prior-accelerator system-energy comparison assumes those designs operate at their reported peak efficiencies. That assumption is part of the comparison, not a measurement of every competing system under identical conditions.',
                'A peak ratio also needs a clear operation count. In an invented example, a dense formulation requires one hundred arithmetic operations, pruning executes forty, and the measured energy is twenty picojoules. Counting executed operations gives two operations per picojoule; counting the equivalent dense work gives five. Neither calculation changes the energy. A comparison must state which numerator it uses and hold the quality requirement fixed.',
                'To assess a complete application, include the relevant input preparation, memory interfaces, model execution, and accepted output. A per-token result needs the token count and model shape before conversion to per-image energy. A measured chip establishes more than a circuit estimate about that chip’s tested operation, but does not establish all workloads, operating points, or future software configurations.',
                'This connects to the SC compression walkthrough: reducing an intermediate representation and changing the accepted numerical answer are separate decisions. It also connects to the DAC simulator lesson: accelerating one implementation stage does not prove a different stage’s performance or correctness.',
            ],
            'sources': [(PAPER + '#page=1', 'Conference digest, measurement discussion; figures 23.2.6–23.2.7 on following pages'), (DOI, 'Official ISSCC 2025 publication record: paper identity and venue')],
        },
    ],
    'exercise': {
        'question': 'For the 64-input, 64-output factorization, what is the largest whole number of retained intermediate channels that strictly reduces multiplication count below 4,096? If mask and movement work costs the equivalent of 512 extra multiplications per vector, what is the new threshold? Does either threshold guarantee acceptable predictions?',
        'answer': 'With k retained channels the multiplication count is 128k. Strictly less than 4,096 requires k < 32, so at most 31. Adding the stipulated 512-unit overhead requires 128k + 512 < 4,096, or k < 28, so at most 27. These are cost thresholds under the toy model, not accuracy guarantees. The first numerical example shows that removing a channel can change the answer substantially; quality needs separate evaluation of the trained model and mask.',
    },
}
