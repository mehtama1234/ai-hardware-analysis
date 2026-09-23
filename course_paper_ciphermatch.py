"""Focused ASPLOS walkthrough of encrypted matching and near-data processing."""

PDF = 'https://doi.org/10.1145/3676641.3716251'

CIPHERMATCH = {
    'id': 'ciphermatch-2025',
    'route': 'asplos-2025',
    'title': 'CIPHERMATCH: keep encrypted matching near the data',
    'identity': 'Mayank Kabra and colleagues · CIPHERMATCH: Accelerating Homomorphic Encryption-Based String Matching via Memory-Efficient Data Packing and In-Flash Processing · ASPLOS 2025',
    'scope': 'A focused walkthrough of encrypted-data representation, addition-only matching, in-flash processing, and the reported evaluation. The locally extracted full paper was inspected. Results are author-reported CPU and simulator results and have not been independently reproduced here. The arithmetic examples are original teaching models.',
    'lessons': [('s2', 'Representation'), ('s6', 'Execution plans'), ('s8', 'Privacy and correctness'), ('s10', 'Whole-system cost')],
    'blocks': [
        {
            'title': 'Privacy changes the cost of an ordinary search',
            'paragraphs': [
                'Homomorphic encryption lets a server compute on encrypted data without seeing the data itself. That promise does not make the computation free. Encryption can enlarge the stored representation, and the server must manipulate ciphertext rather than small plaintext values. In CIPHERMATCH, the paper identifies two linked costs: expensive homomorphic multiplication and rotation, and the movement of a much larger encrypted database between flash, memory, and the processor.',
                'This separates two goals that are easy to confuse. Confidentiality asks whether the server can read the input. Correctness asks whether the returned location really matches the query. Performance asks how much computation and movement are needed to preserve both. A faster method is useful only if it keeps the encrypted representation and the match rule valid.',
                'Original movement model: suppose a 32 GB plaintext database becomes 128 GB after encryption. If the processor can compute quickly but the storage path supplies only 8 GB/s, reading the full encrypted database takes at least 128/8 = 16 seconds before other work is counted. A design that saves arithmetic but repeatedly transfers that representation may still be dominated by movement. This is an original teaching model, not a CIPHERMATCH measurement.',
            ],
            'sources': [(PDF, 'CIPHERMATCH paper, abstract and introduction: ciphertext expansion, expensive operations, and data movement')],
        },
        {
            'title': 'Change the matching rule before changing the machine',
            'paragraphs': [
                'CIPHERMATCH first changes the representation and the algorithm. It packs groups of bits into plaintext coefficients before encryption. In the paper’s example, this lowers the encrypted-data expansion from a stated 64× lower bound for the prior packing approach to 4× for the proposed packing scheme. The central idea is not the particular numbers; it is that representation determines how much data every later level must store and move.',
                'It then reformulates exact matching so the server mainly needs homomorphic addition. A negated query is added to packed data; a match produces the encrypted pattern corresponding to all ones, and the result is checked against that encrypted match pattern. Replacing multiplication and rotation with addition is an algorithm change. It must be checked for every alignment and for the exact-match condition; it is not enough to label addition “cheaper.”',
                'Original small model: if one design performs 6 expensive operations at cost 10 each, its compute work is 60 units. A redesigned form performs 20 additions at cost 1 each plus 8 units of packing and checking, for 28 units. It wins in this model. If checking costs 40 instead, the redesigned form costs 60 and has no compute advantage. The number of operations, their costs, and the correctness work all belong in the comparison.',
            ],
            'sources': [(PDF, 'CIPHERMATCH paper, sections 4.2, 4.2.1, and 4.2.2: packing and addition-only matching')],
        },
        {
            'title': 'Move the remaining addition to where the data lives',
            'paragraphs': [
                'After making matching addition-heavy, CIPHERMATCH places that addition inside NAND flash. The design uses sensing and data latches for bitwise operations, arranges coefficient bits vertically so a carry can move from one bit position to the next, and builds a bit-serial adder from AND, OR, and XOR steps. Coefficient-wise additions can then use parallelism across bitlines, chips, and channels.',
                'This is near-data processing: the machine spends some hardware area and control complexity to avoid sending every encrypted value to a distant processor. The full path still includes flash reads, latch transfers, controller work, index generation, and SSD interfaces. Moving computation closer to storage removes one bottleneck; it does not erase the rest of the system.',
                'Original break-even model: a processor-based path spends 12 units reading and moving data plus 4 units computing. A flash-side path spends 5 units reading, 2 units moving a query, 6 units computing, and 3 units generating the index. The first path costs 16; the second costs 16, so moving the adder is not yet a win. The design must reduce the combined path, not only the named operation.',
            ],
            'sources': [(PDF, 'CIPHERMATCH paper, section 4.3: in-flash processing architecture, bit-serial addition, and system integration')],
        },
        {
            'title': 'Read the evaluation without widening its claim',
            'paragraphs': [
                'The paper evaluates two different boundaries. CM-SW is measured on a real six-core CPU system using Microsoft SEAL and compared with earlier Boolean and arithmetic approaches. CM-IFP is evaluated with an in-house simulator alongside modeled memory-centric and storage-centric alternatives. The workloads are exact DNA matching and encrypted database search; the paper varies query and database sizes, including a 32 GB DNA database that becomes 128 GB after the proposed encryption packing.',
                'The reported software speedup over the arithmetic approach is 20.7×–62.2× across the tested query sizes. The paper reports CM-IFP at 76.6×–216.0× over CM-SW in the query-size sweep and 250.1×–295.1× in the database-size sweep. It also estimates about 0.6% NAND die-area overhead. These numbers are tied to the paper’s parameters, simulator, baselines, workloads, and accounting choices; they are not a general speedup guarantee and not independent measurements.',
                'The evidence boundary matters especially for the hardware result: the software portion runs on a real CPU, while the proposed flash architecture is modeled. The approach is also aimed at exact encrypted string matching, not every encrypted computation. A fair follow-up would keep the match rule, database, query count, correctness check, and movement accounting fixed while changing only where the addition runs. This course has not performed that experiment.',
            ],
            'sources': [(PDF, 'CIPHERMATCH paper, sections 5 and 6: methodology, workloads, reported speedups, and area estimate')],
        },
    ],
    'exercise': {
        'question': 'A plaintext database is 32 GB and its encrypted form is 4× larger. A storage path moves 8 GB/s. A processor design adds 4 seconds of computation after the read. A near-data design reduces the transferred amount to 40 GB, but adds 2 seconds of in-storage work and 1 second of index generation. Which total time is lower in this original teaching model, and what evidence would still be needed before claiming a hardware win?',
        'answer': 'The processor design reads 128 GB in 16 seconds and then computes for 4, for 20 seconds. The near-data design moves 40 GB in 5 seconds, then spends 2 + 1 seconds, for 8 seconds, so it is lower by 12 seconds in this original teaching model. Before claiming a hardware win, measure or validate flash reads, latch operations, controller work, query transfer, correctness checks, energy, endurance, and the actual workload. These are not CIPHERMATCH measurements.',
    },
}
