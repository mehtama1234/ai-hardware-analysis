"""Focused ASPLOS walkthrough of speculative encrypted data movement."""

PDF = 'https://arxiv.org/abs/2409.13702'

PIPE_LLM = {
    'id': 'pipellm-2025',
    'route': 'asplos-2025',
    'title': 'PipeLLM: overlap confidential transfer with useful GPU work',
    'identity': 'Yifan Tan, Cheng Tan, Zeyu Mi, and Haibo Chen · PipeLLM: Fast and Confidential Large Language Model Services with Speculative Pipelined Encryption · ASPLOS 2025',
    'scope': 'A focused walkthrough of confidential GPU transfer, ordered encryption state, speculative prediction, validation, recovery, and the reported H100 evaluation. The local author-hosted primary text was inspected. Results are author-reported and have not been independently reproduced here. The pipeline and break-even calculations are original teaching models.',
    'lessons': [('dependencies-and-pipelines', 'Dependencies'), ('s6', 'Execution plans'), ('s8', 'Privacy and correctness'), ('s10', 'Whole-system cost')],
    'blocks': [
        {
            'title': 'Confidentiality adds work to the transfer path',
            'paragraphs': [
                'A confidential GPU enclave protects data moving between the CPU side and the GPU. Large language model serving often moves model weights or KV-cache state because the GPU cannot hold everything at once. The data must be encrypted before it enters the protected transfer path and decrypted when it returns. If encryption waits in front of every transfer, the GPU can sit idle even when model computation is ready.',
                'PipeLLM’s first idea is to separate the encryption work from the request that is currently blocking the GPU. It predicts which block will be needed next, encrypts that block early, and overlaps encryption with computation and transfer. The prediction is not a security claim by itself: the system validates that the ciphertext still corresponds to the expected plaintext before exposing or sending it.',
                'Original pipeline model: a transfer needs 6 units of encryption and 4 units of GPU work. Sequential execution takes 10 units per block. With correct prediction and two-stage overlap, the first block takes 10 units and each later block takes max(6, 4) = 6, so four blocks take 10 + 3×6 = 28 rather than 40. The saving exists only if buffers, dependencies, and the next block are ready in time.',
            ],
            'sources': [(PDF, 'PipeLLM paper, sections 1–2: confidential GPU transfers, LLM memory pressure, and the pipeline motivation')],
        },
        {
            'title': 'Ordered encryption makes a wrong guess more expensive',
            'paragraphs': [
                'The encrypted transfer uses an initialization vector, or IV, that advances as data is encrypted. The IV is part of the ordered state shared by the CPU side and the GPU side. If PipeLLM encrypts the wrong block at the wrong point, it may not be enough to discard that one ciphertext: later ciphertexts may carry IVs that no longer match the receiver’s expected sequence.',
                'This is why speculative encryption is not ordinary read-ahead. A predictor must know both what data is likely to be requested and where it belongs in the encryption sequence. PipeLLM recognizes repeated, FIFO, and LIFO-like swapping patterns in LLM systems. Its validator uses protected memory permissions and checks that the predicted ciphertext still matches the address and length of the requested plaintext. A changed page triggers a fault rather than silently sending stale data.',
                'Original dependency model: three blocks are predicted with IVs 1, 2, and 3. If the application requests block 3 first while the receiver expects IV 1, sending it directly is invalid. If block 1 arrives next, the system can send it, then advance the IV with a one-byte no-op before sending block 3. The no-op preserves sequence but adds work; if the needed block is changed after prediction, validation must reject the stale ciphertext instead.',
            ],
            'sources': [(PDF, 'PipeLLM paper, sections 4.3 and 5.1–5.3: speculative IV ordering, prediction, validation, reordering, and NOP padding')],
        },
        {
            'title': 'Recovery is part of the fast path, not an afterthought',
            'paragraphs': [
                'PipeLLM uses different responses for different prediction errors. A block whose IV is ahead of the current state can sometimes wait while earlier requests are sent, and no-op padding can advance the sequence. An error that cannot be repaired causes the speculative pipeline to be relinquished and rebuilt. The system also makes decryption asynchronous for data that applications normally do not modify, while protecting the destination so an early access faults and falls back to synchronous decryption.',
                'This design illustrates a general rule for speculation: the expected saving must include detection, recovery, and the cost of a bad guess. A predictor that is accurate on ordinary LLM swapping patterns may not have the same behavior under irregular applications or adversarial access patterns. Preserving confidentiality and freshness is a hard boundary; a faster stale or incorrectly ordered ciphertext is not a valid result.',
                'Original break-even model: correct prediction saves 5 units per block. A wrong prediction costs 12 units to discard and rebuild. If 9 of 10 blocks are correct, the average saving is (9×5 − 12)/10 = 3.3 units per block. At 6 correct blocks out of 10, it becomes (6×5 − 4×12)/10 = −1.8, so speculation loses. The threshold depends on the actual recovery cost and overlap, not only the hit rate.',
            ],
            'sources': [(PDF, 'PipeLLM paper, sections 5.3–5.4: error handling, NOP padding, pipeline reset, and asynchronous decryption')],
        },
        {
            'title': 'Read security, throughput, and transfer capacity separately',
            'paragraphs': [
                'The paper evaluates a dual-Xeon server with one H100-SXM GPU over PCIe 5.0, using FlexGen, vLLM, and PEFT (parameter-efficient fine-tuning) workloads. It reports that confidential computing can cause large throughput or latency losses in the tested baselines, and that PipeLLM reduces the stated model-offloading overhead to below 19.6%. In its vLLM KV-cache study, it reports 5.2%–14.2% overhead after pipelining for the tested cases.',
                'The paper also reports that the confidential transfer path remains around 40 GB/s versus roughly 64 GB/s without confidentiality in the vLLM study, and that a zero-success prediction ablation produces an 8.3% performance drop. These results show why overlap can hide some encryption time without creating bandwidth. They are bounded to the H100 confidential-computing model, the chosen systems and models, and the paper’s access patterns.',
                'The paper does not characterize adversarial or highly variable swapping patterns well enough to claim universal predictor accuracy. This walkthrough has not reproduced the H100 experiments or established a general security proof. A fair follow-up must measure prediction success, stale-data detection, recovery frequency, encrypted and unencrypted bandwidth, end-to-end latency, and the same confidentiality boundary together.',
            ],
            'sources': [(PDF, 'PipeLLM paper, sections 7 and 8: H100 evaluation, prediction ablations, bandwidth, and limitations')],
        },
    ],
    'exercise': {
        'question': 'Four blocks each need 6 units of encryption and 4 units of GPU work. What is the sequential time? Under ideal two-stage overlap, what is the pipelined time? If one prediction error adds 12 units of recovery cost, what is the average time-saving contribution across the four blocks when the other three predictions are correct and each correct block saves 4 units?',
        'answer': 'Sequential time is 4×(6+4) = 40 units. Ideal overlap takes 6+4 + 3×max(6,4) = 28 units. Three correct predictions contribute 3×4 = 12 saved units, while one recovery costs 12 units, so their net contribution is 0 before other pipeline effects. The system still needs correctness, ordered-IV validation, bandwidth, and end-to-end timing checks. These are original teaching calculations, not PipeLLM measurements.',
    },
}
