"""DAC simulator walkthrough with original cost and state-transition examples."""
PAPER = 'https://arxiv.org/html/2508.02236v1'
DOI = 'https://doi.org/10.1109/DAC63849.2025.11133142'

GSIM = {
    'id': 'gsim-2025',
    'route': 'dac-2025',
    'title': 'GSIM: spend less work deciding what must be simulated',
    'identity': 'Lu Chen and colleagues · GSIM: Accelerating RTL Simulation for Large-Scale Designs · DAC 2025',
    'scope': 'Focused reading of manuscript sections II–IV. Author-reported results were not reproduced. The cost models and state examples below are original teaching scenarios.',
    'lessons': [('s6', 'Equivalent execution plans'), ('dependencies-and-pipelines', 'Dependencies'), ('s8', 'Correctness evidence'), ('physical-design', 'Models and measurements')],
    'blocks': [
        {
            'title': 'There are two machines in this experiment',
            'paragraphs': [
                'A software circuit simulator runs on a real computer and calculates what a described circuit would do. The described circuit has its own stored state, inputs, and clock steps. The computer running the simulator has a different instruction stream and elapsed runtime. Making that computer calculate the same circuit trace sooner improves simulation speed. It does not, by itself, change the circuit’s clock rate or how many circuit cycles a workload requires.',
                'Register-transfer-level, or RTL, descriptions specify stored values and the logic that updates them. A simulator must preserve the description’s relevant behavior while choosing how to calculate it. It may reuse an unchanged result, combine bookkeeping, or simplify an expression when justified. Skipping a required state change would instead simulate a different circuit.',
                'GSIM transforms FIRRTL—an internal hardware description—into C++ simulation code. It changes the simulator at three levels. First, it gives calculations that usually become active together one shared “needs work” check; that reduces checking but can make an unchanged calculation run unnecessarily. Second, it removes unused or duplicate calculations and chooses whether to keep a common result for later reuse or repeat the calculation at each consumer. Third, when a wide signal changes only in bits that a later calculation does not read, it can keep that later calculation inactive. These are separate ways to reduce host-computer work while preserving the modeled circuit behavior.',
            ],
            'sources': [(PAPER + '#S3', 'Author manuscript, section III'), ('https://talks-pubs.xiangshan.cc/publications/dac2025-GSIM.pdf', 'Author-hosted conference paper')],
        },
        {
            'title': 'Count the work of checking before celebrating skipped work',
            'paragraphs': [
                'Imagine one simulation step with 100 independent calculations. Evaluating one costs eight host-work units. Checking whether one needs evaluation costs one unit. Exactly ten need evaluation. Evaluating everything costs 800 units. Checking all 100 and evaluating only the ten active calculations costs 100 + 10×8 = 180. This invented model omits propagation, memory, and branch-prediction costs to isolate the trade.',
                'Now organize them into ten groups of ten. A group needs one check, and if any member is active, all ten members are evaluated. If the ten active calculations are all in one group, the cost is 10 + 10×8 = 90 units. If they are spread one per group, every group runs, costing 10 + 100×8 = 810. The number of truly active calculations is unchanged. Their placement within the groups changes how much unnecessary work is triggered.',
                'If all 100 calculations become active, individual checks cost 900 units while unconditional evaluation costs 800. Grouping costs 810. A scheme that is useful under sparse activity can lose when activity is dense. Before choosing a group size, ask which calculations tend to become active together and how that pattern changes across workloads. Fewer checks and fewer evaluations are competing objectives here.',
            ],
        },
        {
            'title': 'Preserve state changes, not just the final printed answer',
            'paragraphs': [
                'Take a two-register teaching circuit. Before a clock edge, q = 0 and r = 1. The next-state rule is q_next = r_old and r_next = q_old: swap the values at each edge. Correct next state is q = 1, r = 0. A simulator that updates q in place and then reads that new q while calculating r produces q = 1, r = 1. It has used the wrong version of state. Saving the old values or calculating both next values before committing either preserves the rule.',
                'After a second edge, the correct circuit returns to q = 0, r = 1. Checking only whether q eventually becomes zero could miss an incorrect intermediate trace or an error affecting r alone. Observed registers, outputs, exceptions, and timing boundaries must match the requested model. A successful application run is evidence for that run, but it does not test every possible state and input sequence.',
                'Tracking bits can avoid needless calculation only when dependencies justify it. In an invented sixteen-bit word assembled from independent eight-bit high and low fields, a consumer reading only the high field does not need reevaluation when only the low field changes. But for a sixteen-bit counter, incrementing hexadecimal 00FF yields 0100: carry changes the high field too. Treating the fields as independent would be wrong. A representation change must preserve the operation’s actual dependencies.',
            ],
        },
        {
            'title': 'Sharing a result is another cost trade',
            'paragraphs': [
                'Suppose an invented expression f(x) costs five units to calculate. Two consumers need it during one step. Calculating it separately in each consumer costs ten. Computing once and retaining the result costs five plus three units of bookkeeping, or eight. Sharing saves two units. With only one consumer, separate calculation costs five and the retained-result path costs eight. Creating a named intermediate result is not automatically cheaper.',
                'The shared result also needs a validity rule. If x changes, both consumers must receive a result based on the required version of x. If a consumer is inactive this step, it might not need any evaluation yet. The simple five-plus-three calculation assumes both consumers need the value now. Real scheduling and reuse information can change that premise.',
                'This connects to the MICRO cache walkthrough: retaining a value pays when it is reused while valid. It also connects to the MLSys compiler examples: combining operations may remove intermediate storage while repeating work or changing what can run independently. The right unit to count is the complete legal execution, including its bookkeeping.',
            ],
        },
        {
            'title': 'Measure the simulator at its actual boundary',
            'paragraphs': [
                'The paper compares against Verilator 5.026, ESSENT, and Arcilator on an i9-9900K host. In the selected designs, it reports that GSIM and Verilator successfully simulate XiangShan while ESSENT and Arcilator fail on some designs because of code-generation errors or wrong simulation results. It reports 7.34× faster XiangShan Linux-boot simulation than single-threaded Verilator. For sampled SPEC CPU2006 segments, the reported averages are 3.72× against one Verilator thread and 1.18× against eight. These are simulator-runtime comparisons, not chip-performance gains, and the correctness result is bounded to the tested designs and workloads.',
                'A baseline’s resources matter: comparing one thread with eight answers a different question from comparing two single-threaded programs. Also keep circuit version, input workload, starting state, observation requirements, and simulated duration aligned. A simulator that does less required work is not faster at the same task.',
                'Include preparation when that is part of the workflow. In an original example, the baseline takes 40 seconds to prepare a simulator and 80 seconds per run. A new approach takes 100 seconds to prepare and 20 seconds per run. One run ties at 120 seconds; two runs take 200 versus 140. If the circuit changes before each run and forces rebuilding, there is no preparation reuse. These invented numbers are not GSIM measurements.',
                'A faster simulator can make more testing affordable. It still cannot establish that untested cases are correct merely by completing the tested cases sooner. Nor does agreement at RTL establish a physical implementation’s wire delays, clock limit, or power consumption. Those require evidence at the corresponding implementation stage.',
            ],
            'sources': [(PAPER + '#S4', 'Author manuscript, section IV'), (DOI, 'Official DAC 2025 publication record: paper identity and venue')],
        },
    ],
    'exercise': {
        'question': 'Keep the 100-calculation model and ten groups of ten. Ten active calculations occupy three groups. What does grouping cost, compared with checking each calculation? What is the largest number of occupied groups for which grouping strictly wins? Separately, what state follows three clock edges in the swap circuit?',
        'answer': 'Three occupied groups cost 10 + 3×10×8 = 250 units, versus 180 for individual checks. For k occupied groups, grouping wins when 10 + 80k < 180, so at most two groups. Two cost 170; three cost 250. The correct swap states after edges one, two, and three are (1,0), (0,1), and (1,0). These results test the teaching models, not the GSIM implementation or the paper’s measured speedups.',
    },
}
