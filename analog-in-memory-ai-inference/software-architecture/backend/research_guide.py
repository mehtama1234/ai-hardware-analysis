RESEARCH_GUIDE_SCHEMA_VERSION = "research-guide-v0.1"


PAPER_NOTES = [
    {
        "id": "isca-2025-098",
        "title": "Hybrid SLC-MLC RRAM Mixed-Signal PIM for Transformers",
        "access": "full text",
        "theme": "hybrid precision and protected weights",
        "first_principle": "Not every weight needs the same numeric care. Dense lower-precision analog storage can help for tolerant weights, while sensitive weights need a safer path.",
        "interview_angle": "The mature answer is not 'make everything analog.' It is 'put each weight and operator where its error tolerance allows it.'",
        "do_not_overclaim": "Do not treat one transformer PIM result as proof that every transformer layer should be analog.",
    },
    {
        "id": "date-2025-193",
        "title": "Fully Differential Analog In-Memory MAC in MRAM",
        "access": "abstract only",
        "theme": "analog MAC and calibration",
        "first_principle": "Weak physical signals need circuit techniques and calibration before they can act like useful compute results.",
        "interview_angle": "Ask how process and voltage variation are calibrated and how much calibration costs in time, energy, and software complexity.",
        "do_not_overclaim": "Do not treat abstract-only TOPS/W numbers as a complete system result.",
    },
    {
        "id": "isscc-2025-089",
        "title": "16nm Multi-Mode Gain-Cell CIM Macro for Edge AI",
        "access": "abstract only",
        "theme": "multi-format compute-in-memory macro",
        "first_principle": "Different edge models need different number formats, so fixed precision can limit usefulness.",
        "interview_angle": "A useful edge accelerator should explain which precisions it supports and how the compiler chooses between them.",
        "do_not_overclaim": "Do not compare macro efficiency directly with completed product efficiency.",
    },
    {
        "id": "isscc-2025-100",
        "title": "MRAM In-Memory Microprocessor for End-to-End DNN Inference",
        "access": "abstract only",
        "theme": "beyond a single macro",
        "first_principle": "A product needs control, storage, execution, and runtime behavior, not only an isolated compute cell.",
        "interview_angle": "Ask what part of the end-to-end inference path is on chip and what still depends on a host or external memory.",
        "do_not_overclaim": "Do not assume end-to-end in a paper means production-ready customer software.",
    },
    {
        "id": "dac-2025-376",
        "title": "YOCO: Hybrid In-Memory Computing for Large-Scale AI",
        "access": "abstract only",
        "theme": "hybrid memory and attention path",
        "first_principle": "Large AI workloads are often limited by memory movement, but attention and irregular paths still need special handling.",
        "interview_angle": "Use this to discuss hybrid systems: analog where it saves movement, digital or specialized paths where precision/control matters.",
        "do_not_overclaim": "Do not assume the same design applies unchanged to tiny wearables and large transformer workloads.",
    },
    {
        "id": "dac-2025-380",
        "title": "Analog Accumulator and In-Memory ADC With Shared References",
        "access": "abstract only",
        "theme": "ADC and accumulation cost",
        "first_principle": "Analog compute eventually has to become digital again. Conversion can dominate if it happens too often or costs too much.",
        "interview_angle": "Ask how many ADC/DAC events happen per inference and whether they are counted in the efficiency claim.",
        "do_not_overclaim": "Do not quote compute-array efficiency without asking about conversion overhead.",
    },
    {
        "id": "dac-2024-370",
        "title": "Hybrid Analog-Digital IMC for Lossless Neural Network Inference",
        "access": "medium confidence",
        "theme": "route sensitive work digitally",
        "first_principle": "If an operation is sensitive to analog error, moving it through digital logic can protect correctness while analog handles tolerant work.",
        "interview_angle": "This is the clean architecture idea: choose the analog/digital boundary by value sensitivity and proof target.",
        "do_not_overclaim": "Do not say hybrid routing is free; boundary crossings and scheduling still cost energy and complexity.",
    },
    {
        "id": "iccad-2025-056",
        "title": "How Non-Ideal Analog PIM Errors Impact NN Accuracy",
        "access": "abstract only",
        "theme": "accuracy impact of analog non-idealities",
        "first_principle": "Hardware error is only useful to model if it can be connected to task accuracy quickly enough for design exploration.",
        "interview_angle": "Ask how the company predicts accuracy under variation before expensive silicon or board measurements.",
        "do_not_overclaim": "Do not assume a fast error model replaces measured silicon validation.",
    },
    {
        "id": "dac-2025-130",
        "title": "HH-PIM for Edge AI Devices",
        "access": "abstract only",
        "theme": "heterogeneous memory-side cores",
        "first_principle": "Different parts of a workload may belong on different memory-side or compute-side resources.",
        "interview_angle": "Ask how the runtime moves work to the resource that fits current latency, energy, and precision needs.",
        "do_not_overclaim": "Do not treat one PIM core as a universal edge AI solution.",
    },
    {
        "id": "dac-2025-127",
        "title": "PIMPAL: In-DRAM Lookup for Edge LLM Inference",
        "access": "abstract only",
        "theme": "memory-heavy edge LLM inference",
        "first_principle": "For LLMs, avoiding movement can matter as much as raw multiply-add speed.",
        "interview_angle": "Use this as a contrast: not all in-memory acceleration is analog, but the system goal can still be reducing movement.",
        "do_not_overclaim": "Do not mix lookup-table PIM results with analog MAC claims.",
    },
    {
        "id": "fccm-2025-053",
        "title": "LLM-IMC: Automating Analog IMC Design",
        "access": "abstract only",
        "theme": "AI-assisted hardware design",
        "first_principle": "Analog IMC design is hard because circuit choices affect system behavior. Automation can help explore designs, but validation still needs simulation and silicon.",
        "interview_angle": "AI can help design AI hardware, but circuit simulation, measurement, and product proof remain the gate.",
        "do_not_overclaim": "Do not say generated circuits are validated until simulation and measured hardware agree.",
    },
]


def build_research_guide(package_report=None):
    summary = (package_report or {}).get("summary", {})
    lessons = [
        "Hybrid is the recurring theme: analog where error is tolerable, digital where precision or control matters.",
        "ADC/DAC and memory movement must be counted because they can erase core-level gains.",
        "Calibration and variation are not side details; they decide whether analog math remains useful.",
        "Transformer and edge workloads need different boundaries, precisions, and software support.",
        "Prototype or macro results are important, but production needs yield, repeatability, packaging, drift, runtime, and customer integration proof.",
    ]
    questions = [
        "Which papers are closest to the company architecture: RRAM, MRAM, gain-cell SRAM/CIM, or another analog core?",
        "What is the first workload where the analog boundary is clean enough to win?",
        "Which weights or layers are protected, and which are allowed to use lower precision?",
        "How are ADC/DAC, memory movement, host control, and idle power counted?",
        "How does the software stack expose calibration, profiling, and debugging to customers?",
    ]
    return {
        "result_type": "research_guide",
        "schema_version": RESEARCH_GUIDE_SCHEMA_VERSION,
        "provenance": "curated from the paper list captured in this workspace discussion",
        "confidence": "medium for themes, low for abstract-only implementation details",
        "package_id": (package_report or {}).get("package_id"),
        "summary": {
            "target_profile": summary.get("target_profile"),
            "modality": summary.get("modality"),
            "paper_count": len(PAPER_NOTES),
            "plain_reading": "Use these papers to discuss the design space, not as proof of this package's measured performance.",
        },
        "papers": PAPER_NOTES,
        "cross_paper_lessons": lessons,
        "questions_to_ask": questions,
        "do_not_overclaim": [
            "Do not cite abstract-only records as if you have verified full methods and assumptions.",
            "Do not compare reported TOPS/W numbers unless counted scope, precision, workload, and accuracy targets match.",
            "Do not present research prototypes as product readiness.",
        ],
    }
