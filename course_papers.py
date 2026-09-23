"""Bounded paper walkthroughs with separately labeled original teaching examples."""
from course_paper_blitzscale import BLITZSCALE
from course_paper_cxl import CXL
from course_paper_banks import BANKS
from course_paper_fastserve import FASTSERVE
from course_paper_lut import LUT
from course_paper_correctbench import CORRECTBENCH
from course_paper_lego import LEGO
from course_paper_trrip import TRRIP
from course_paper_cuszhi import CUSZHI
from course_paper_gsim import GSIM
from course_paper_timefloats import TIMEFLOATS
from course_paper_convformer import CONVFORMER
from course_paper_rsizing import RSIZING
from course_paper_qserve import QSERVE
from course_paper_sola import SOLA
from course_paper_picsou import PICSOU
from course_paper_pmverify import PMVERIFY
from course_paper_exist import EXIST
from course_paper_afaas import AFAAS
from course_paper_emt import EMT
from course_paper_photon import PHOTON
from course_paper_past_future import PAST_FUTURE
from course_paper_dips import DIPS
from course_paper_oaken import OAKEN
from course_paper_pimba import PIMBA
from course_paper_milo import MILO
from course_paper_mirage import MIRAGE
from course_paper_tigon import TIGON
from course_paper_hydraserve import HYDRASERVE
from course_paper_dynamollm import DYNAMOLLM
from course_paper_vqllm import VQ_LLM
from course_paper_exion import EXION
from course_paper_iris import IRIS
from course_paper_chocoq import CHOCOQ
from course_paper_mve import MVE
from course_paper_teola import TEOLA
from course_paper_ciphermatch import CIPHERMATCH
from course_paper_vattention import VATTENTION
from course_paper_comet import COMET
from course_paper_micro_blossom import MICRO_BLOSSOM
from course_paper_pipellm import PIPE_LLM
from course_paper_partir import PARTIR
from course_paper_tapas import TAPAS
from course_paper_pccheck import PCCHECK
from course_paper_cascade import CASCADE
from course_paper_mint import MINT
from course_paper_powermove import POWERMOVE
from course_paper_pushtap import PUSHTAP
from course_paper_coserve import COSERVE
from course_paper_dvfs import FINE_DVFS
from course_paper_btrace import BTRACE
from course_paper_sat_sampling import SAT_SAMPLING
from course_paper_pulsebit import PULSE_BIT
from course_paper_daris import DARIS
from course_paper_camdn import CAMDN
from course_paper_tropical import TROPICAL
from course_paper_versaslot import VERSASLOT

FLASHINFER_PDF = 'https://proceedings.mlsys.org/paper_files/paper/2025/file/dbf02b21d77409a2db30e56866a8ab3a-Paper-Conference.pdf'

PAPERS = [{
    'id': 'flashinfer-2025',
    'route': 'mlsys-2025',
    'title': 'FlashInfer: divide uneven work without losing the meaning of the answer',
    'identity': 'Zihao Ye and colleagues · FlashInfer: Efficient and Customizable Attention Engine for LLM Inference Serving · MLSys 2025',
    'scope': 'A focused walkthrough of scheduling and partial-result combination, not a review of every feature. Sections 3.3–3.4 and 4–4.1 of the conference paper were inspected. Measurements are author-reported and have not been reproduced here. The arithmetic examples below are original teaching models, not measurements or a reimplementation.',
    'lessons': [('dependencies-and-pipelines', 'Dependencies'), ('s2', 'Rounding'), ('s6', 'Compilation'), ('queues-and-batching', 'Scheduling')],
    'blocks': [
        {
            'title': 'Start with a weighted answer',
            'paragraphs': [
                'Imagine calculating an answer from earlier values, where some values matter more than others. Multiply each value by its positive weight, add those products, and divide by the sum of the weights. This is a weighted average. Attention in a language model uses a related operation: a current query is compared with stored keys to determine weights for stored values. Keys help choose relevance; values supply the information being combined. The saved keys and values are called the key–value cache. Here we use scalar values to make the arithmetic visible; model values have many components.',
                'Requests with different amounts of saved context need different amounts of work. Giving each request one equally capable worker does not make their finishing times equal. More workers help only if the long calculation can be divided and its pieces can be combined into the required answer. That last condition is mathematical, not merely a scheduling preference.',
            ],
        },
        {
            'title': 'What the paper changes',
            'paragraphs': [
                'FlashInfer first reads the current sequence lengths on the CPU and makes an assignment table: which small piece of attention work each GPU worker should do, and which partial outputs must be joined. It sends that table to GPU memory, where long contexts can be split and their partial answers combined. The same table can be reused across layers with matching lengths.',
                'The paper also uses CUDA Graphs, a recorded GPU command sequence that expects the same launch shape and buffer locations each time it runs. FlashInfer keeps those outer details fixed while replacing the contents of the assignment table for each generation step. In other words, the recorded GPU loop stays the same, but it reads a new plan. The CPU planning step is not part of that recorded GPU sequence. These details come from sections 3.3–3.4.',
            ],
            'sources': [(FLASHINFER_PDF + '#page=7', 'Conference paper, sections 3.3–3.4, pages 7–8')],
        },
        {
            'title': 'Work through the scheduling tradeoff',
            'paragraphs': [
                'Use four identical workers and four independent jobs requiring 8, 2, 2, and 2 time units. Assume work time is proportional to job size, all jobs are ready initially, and workers do not interfere. One whole job per worker finishes after 8 units. Three workers finish at time 2 and wait while the long job continues. This is wasted available capacity, not a shortage of workers.',
                'Now suppose the long job can be split into four pieces of size 2. Together with the three short jobs, there are seven equal pieces. Assign two pieces each to three workers and one to the fourth. The longest worker assignment takes 4 units. If preparing the assignment costs 0.5 units before execution and combining the long job’s pieces costs 1 afterward, completion takes 0.5 + 4 + 1 = 5.5. The saving is 2.5, not 4: the new coordination costs belong in the total.',
                'The result depends on the workload. If all four original jobs take 2 units, one job per worker already finishes in 2. A variant that needlessly adds the same planning and combination costs takes 3.5. Likewise, splitting the uneven case loses if its added non-overlapped costs exceed the 4 units it saved in execution. These are predictions of the teaching model, not measured weaknesses of FlashInfer. Real decisions also depend on memory traffic, buffers, and how well a piece fills the device.',
            ],
        },
        {
            'title': 'Why partial averages cannot simply be averaged',
            'paragraphs': [
                'Take two pieces of one calculation. Piece A contains values 2 and 6 with weights 1 and 3. Its weighted sum is 20, its weight total is 4, and its average is 5. Piece B contains values 10 and 4 with weights 2 and 4. Its weighted sum is 36, its weight total is 6, and its average is 6. The full answer is (20 + 36)/(4 + 6) = 5.6. Averaging the two partial averages gives 5.5, which is wrong because the pieces carry different total weights.',
                'One sufficient summary for this small example is each piece’s weighted sum and weight total. Equivalently, keep its average and weight total, then compute (5 × 4 + 6 × 6)/(4 + 6). The scheduler needs space for whatever summary preserves the required combination; a partial answer alone may discard information. This toy formula is not a specification of FlashInfer’s numerical implementation. Attention implementations must additionally handle how weights are normalized and represented without overflow.',
                'Even a mathematically valid combination can change rounding when its order changes. The numerical-precision lesson explains why finite representations do not preserve every algebraic rearrangement exactly. Specify the allowed error or repeatability requirement, and check it after changing the partition. A faster assignment that violates the required answer is not a successful optimization.',
            ],
        },
        {
            'title': 'A fixed execution structure need not imply fixed work',
            'paragraphs': [
                'A useful way to understand the design is to distinguish instructions from the data those instructions read. Four workers can always run the same loop—read the next assignment, execute it, store its result—while the assignment table changes between rounds. The loop structure stays fixed; the work distribution does not. That distinction lets an implementation reuse some setup without pretending every request has the same length.',
                'This separation still has obligations. The table must describe the current round, its storage must remain valid while workers read it, and partial results must not overwrite one another. Reusing a plan across repeated operations helps only while the relevant shapes and dependencies match. In the toy cost model, spreading a 0.5-unit planning cost over ten matching operations costs 0.05 per operation; replanning for every operation costs 0.5 each. Neither calculation makes planning free.',
            ],
        },
        {
            'title': 'Read the evaluation at its actual boundary',
            'paragraphs': [
                'Section 4 evaluates FlashInfer v0.2. Section 4.1 compares the FlashInfer and Triton attention backends inside SGLang v0.3.4. It tests ShareGPT conversations and a synthetic workload whose sequence lengths range from 512 to 2,048 tokens. For each setup, the authors adjust how quickly requests arrive to keep the 99th-percentile time to the first output below 200 ms.',
                'Figure 7 reports median gaps between output tokens: for the 8-billion-parameter model, 21.7 to 13.5 ms on ShareGPT and 29.6 to 9.1 ms on the synthetic workload; for the 70-billion-parameter model, 48.3 to 24.0 ms and 30.7 to 21.8 ms. The figure uses one H100 GPU for the smaller model and four for the larger one. These are the paper’s measured results, not measurements made by this course.',
                'A smaller gap between output tokens means a response streams faster after it begins. It does not tell us how long the whole request takes or how many requests finish each second. The first-token delay is a separate measure. Because the authors tune request arrival to satisfy a first-token-delay target, read these numbers as results under that target-based procedure—not as a comparison at one fixed arrival rate. The paper’s result is limited to its models, software versions, request traces, hardware, and target; it does not promise the same gain on other systems.',
                'To test the scheduling explanation separately from the complete engine, hold the numerical operation, device, and traffic constant, then vary length imbalance and whether planning and combination costs are counted. To compare this mechanism with a reduced-precision proposal, additionally keep output acceptance fixed and measure conversion work. These are proposed follow-up comparisons, not experiments performed by this course and not evidence of a combined speedup.',
            ],
            'sources': [(FLASHINFER_PDF + '#page=8', 'Conference paper, section 4.1 and figure 7, page 8')],
        },
    ],
    'exercise': {
        'question': 'In the four-worker example, suppose planning costs 1 unit and combining partial results costs 3.5 units. Is splitting the 8-unit job worthwhile? Separately, if piece A has average 3 and weight total 2, while piece B has average 9 and weight total 8, what combined average is required?',
        'answer': 'Splitting takes 1 + 4 + 3.5 = 8.5 units, losing to the unsplit 8. The combined average is (3 × 2 + 9 × 8)/(2 + 8) = 7.8, not the unweighted average 6. Available parallel work and a valid mathematical combination are necessary, but added costs can still erase the saving.',
    },
}, BLITZSCALE, CXL, BANKS, FASTSERVE, LUT, CORRECTBENCH, LEGO, TRRIP, CUSZHI, GSIM, TIMEFLOATS, CONVFORMER, RSIZING, QSERVE, SOLA, PICSOU, PMVERIFY, EXIST, AFAAS, EMT, PHOTON, PAST_FUTURE, DIPS, OAKEN, PIMBA, MILO, MIRAGE, TIGON, HYDRASERVE, DYNAMOLLM, VQ_LLM, EXION, IRIS, CHOCOQ, MVE, TEOLA, CIPHERMATCH, VATTENTION, COMET, MICRO_BLOSSOM, PIPE_LLM, PARTIR, TAPAS, PCCHECK, CASCADE, MINT, POWERMOVE, PUSHTAP, COSERVE, FINE_DVFS, BTRACE, SAT_SAMPLING, PULSE_BIT, DARIS, CAMDN, TROPICAL, VERSASLOT]
