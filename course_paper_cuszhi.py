"""SC compression walkthrough with bounded source claims and original examples."""
PAPER = 'https://arxiv.org/html/2507.11165v1'

CUSZHI = {
    'id': 'cuszhi-2025',
    'route': 'sc-2025',
    'title': 'cuSZ-Hi: decide what may change before making the data smaller',
    'identity': 'Shixun Wu, Jinwen Pan, and colleagues · cuSZ-Hi · SC 2025',
    'scope': 'Focused reading of manuscript sections 3–5 and 6.1–6.2.4. Teaching examples are original, not implementations. Author-reported experiments were not reproduced.',
    'lessons': [('s2', 'Numerical error'), ('s3', 'Movement costs'), ('dependencies-and-pipelines', 'Dependencies'), ('scientific-workflow', 'Accepted scientific results')],
    'blocks': [
        {
            'title': 'Separate changing values from encoding them',
            'paragraphs': [
                'Lossless compression must recover the original information exactly. Lossy compression permits specified differences. The decision question is not whether an image looks similar or whether a file is smaller, but which differences the application accepts and how the compressor controls them. Here we will use an absolute per-value error bound: every reconstructed value must differ from its original by at most a stated amount.',
                'cuSZ-Hi predicts each value from nearby values, rounds the remaining prediction error into an integer code, and then losslessly encodes those codes. After the same error-bounded conversion, it can select a compression-ratio mode (CR) whose lossless pipeline aims for fewer output bytes, or a throughput mode (TP) whose pipeline aims to encode and decode more quickly. The choice changes the final-byte representation, not the permitted numerical difference set by the earlier conversion. The paper’s error rule bounds the largest reconstruction error for one value. The lossless stage preserves the already-quantized codes; it does not restore discarded numerical detail.',
                'Keep three objects distinct: the original numerical array, the integer codes chosen to represent it approximately, and the compressed bytes that represent those codes exactly. A change to the first conversion can change numerical error. A reversible change to the last representation can change size or decoding work without adding numerical error.',
            ],
            'sources': [(PAPER + '#S4', 'Author manuscript, sections 3–5'), ('https://doi.org/10.1145/3712285.3759798', 'SC conference publication')],
        },
        {
            'title': 'Reconstruct five values by hand',
            'paragraphs': [
                'Use an original five-value array: 0, 1.08, 2.04, 2.97, 4. Store the endpoints exactly. Predict the middle value from their average, giving 2. For each prediction, round its error to the nearest multiple of 0.2 and store the corresponding integer. The middle error is 0.04, so its code is zero and its reconstruction is 2. Now predict the two remaining positions from the reconstructed neighbors: 1 and 3. Their errors are 0.08 and −0.03; both also receive code zero. The reconstructed array is 0, 1, 2, 3, 4.',
                'The largest error is 0.08, within an allowed 0.1. More generally, rounding a residual to the nearest point on a grid spaced by 0.2 leaves at most 0.1 between it and the selected point. This argument assumes exact arithmetic, a defined tie rule, and codes with enough range. An implementation must also handle finite arithmetic, exceptional values, and codes outside its chosen range. This small model does not verify cuSZ-Hi’s implementation.',
                'The predictor must use information the decoder can reproduce. Suppose a different, sequential predictor uses the previous value. Its first value 1.09 has reconstructed as 1.0. To encode the next value 1.18, using the original previous value gives residual 0.09, which rounds to zero. But the decoder predicts from 1.0 and reconstructs 1.0, making error 0.18: outside the bound. Using the reconstructed previous value gives residual 0.18, code one, and reconstruction 1.2, with error 0.02. Agreement about prediction inputs is part of the error argument.',
            ],
        },
        {
            'title': 'The order of codes changes what an encoder can exploit',
            'paragraphs': [
                'Consider only an invented integer-encoding stage, with eight one-byte codes. The sequence 0,0,0,0,1,1,1,1 can be stored as two value/count pairs: value zero repeated four times, then value one repeated four times. If each value and count occupies one byte, that uses four bytes instead of eight. The alternating sequence 0,1,0,1,0,1,0,1 needs eight such pairs, or sixteen bytes. The two sequences contain exactly the same frequencies; their neighboring relationships differ.',
                'A known reversible rearrangement can expose repeated neighbors. For the alternating sequence, take positions 0,2,4,6 first and 1,3,5,7 second. The reordered codes become four zeros followed by four ones. The decoder can place them back using the agreed position rule. This does not change the reconstructed numerical values. Arbitrarily sorting codes would not have that property unless the original order could also be recovered.',
                'Count the description needed to reverse the operation. If selecting this mode and recording the length costs two bytes in the toy format, the total is six, not four. If it costs five, the total is nine and exceeds the original eight. These are sizes of the integer stage only: anchors, numerical parameters, exceptional values, and other headers would belong in a complete compressed-file comparison.',
            ],
        },
        {
            'title': 'Translate the bound into the calculation that matters',
            'paragraphs': [
                'A per-value guarantee is not automatically a guarantee about every calculation on those values. Use two samples, 1.00 and 1.01, spaced 0.01 units apart. Their slope, computed as difference divided by spacing, is one. A reconstruction of 1.10 and 0.91 changes each sample by exactly 0.1, meeting that per-value bound. Its slope is −19. A visually small or individually permitted change can therefore reverse this derived result.',
                'Let each sample change by at most e and let their positive spacing be h. The difference can change by at most 2e because the two errors may point in opposite directions. Dividing by h gives a worst-case slope error of 2e/h. With e = 0.1 and h = 0.01, the bound is twenty, attained by the example. Smaller spacing can amplify the same value error. This is a bound for this two-point calculation, not a guarantee for an entire scientific solver.',
                'Before choosing the compressor tolerance, identify the downstream requirements: an average, a derivative, an extreme value, or a threshold decision can react differently. The scientific-workflow lesson asks the same question about a solver: which accepted output is required, and what evidence connects the intermediate accuracy condition to that output?',
            ],
        },
        {
            'title': 'Choose a mode using the complete transfer path',
            'paragraphs': [
                'Use an invented 1 GiB snapshot, equal to 1,024 MiB, and assume both candidate modes meet the same numerical acceptance rule. Fast mode takes 0.3 seconds to compress, produces 128 MiB including metadata, and takes 0.2 seconds to decompress. Compact mode takes 0.9 seconds to compress, produces 64 MiB, and takes 0.4 seconds to decompress. Assume all three stages run sequentially and there are no other differences.',
                'On a 256 MiB/s connection, uncompressed transfer takes four seconds. Fast mode takes 0.3 + 0.5 + 0.2 = one second. Compact mode takes 0.9 + 0.25 + 0.4 = 1.55 seconds. The smaller file loses to the faster mode. On a 32 MiB/s connection, fast mode takes 4.5 seconds and compact mode 3.3. Changing the connection changes the preferred trade, even though neither compressor changed.',
                'If GPU compression competes with the simulation producing the data, account for the simulation time it displaces. If processing and transfer overlap, derive their actual schedule rather than adding times from a sequential model. Also include device-to-host copies, storage, and validation when those fall inside the chosen workflow boundary.',
                'The paper evaluates six scientific datasets on A100 and RTX 6000 Ada GPUs. It compares compressed size, reconstruction quality, and compression/decompression rates. Its speed assessment measures GPU kernel throughput; this is not a measurement of an entire simulation, transfer, storage, and analysis workflow.',
            ],
            'sources': [(PAPER + '#S6', 'Author manuscript, section 6')],
        },
    ],
    'exercise': {
        'question': 'For the two-point slope with spacing 0.01, what per-value error bound suffices to keep slope error at most 0.5 under exact arithmetic? Separately, at what connection rate do the two invented compression modes tie, and on which side does compact mode win?',
        'answer': 'Require 2e/0.01 ≤ 0.5, giving e ≤ 0.0025. This is sufficient for the stated slope calculation, not every later analysis. For connection rate B in MiB/s, fast mode takes 0.5 + 128/B seconds and compact mode 1.3 + 64/B. They tie when 64/B = 0.8, so B = 80 MiB/s, with each taking 2.1 seconds. Compact wins below 80; fast wins above it. The timing comparison remains valid only when both outputs meet the same acceptance rule and the stated costs and sequential schedule apply.',
    },
}
