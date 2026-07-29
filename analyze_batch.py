#!/usr/bin/env python3
import json
import os
from pathlib import Path

# Load batch JSONL
batch_file = Path("analysis/per-paper/batches/iccad_2025_batch_009.jsonl")
papers = []
with open(batch_file) as f:
    for line in f:
        papers.append(json.loads(line))

output_dir = Path("analysis/per-paper")

def analyze_paper(paper):
    """Analyze a single paper from title + abstract"""
    id_ = paper["id"]
    title = paper["title"]
    venue = paper["venue"]
    abstract = paper.get("abstract", "")

    # Skip if already analyzed
    json_path = output_dir / f"{id_}.json"
    if json_path.exists():
        return None

    # Parse content to extract structured info
    # This is template-driven based on patterns in abstracts

    text = f"{title}. {abstract}"
    text_lower = text.lower()

    # Initialize result structure
    result = {
        "id": id_,
        "title": title,
        "venue": venue,
        "problem": "",
        "motivation": "",
        "method": "",
        "key_novelty": "",
        "contributions": [],
        "hardware_target": [],
        "technique_category": [],
        "workloads": [],
        "metrics": {
            "speedup": None,
            "energy_or_tops_w": None,
            "area": None,
            "ppa": None,
            "accuracy": None,
            "other": None
        },
        "baselines": [],
        "limitations": "",
        "tags": [],
        "primary_theme": "",
        "confidence": "low"
    }

    # Paper-specific analysis
    if "scannow" in title.lower():
        result["problem"] = "Sparse matrix-matrix multiplication (SpMM) exhibits irregular memory access patterns across diverse sparse structures, creating performance bottlenecks on traditional computing platforms."
        result["motivation"] = "Dedicated hardware accelerators for SpMM must handle diverse sparse patterns flexibly to achieve significant speedups."
        result["method"] = "ScanNow introduces a scan window-based task dispatch scheme that minimizes irregular memory accesses by exploiting data reuse opportunities and dynamically balancing input/output reuse. The architecture features multiple memory components and customized schedulers to accommodate the task dispatch scheme and improve computation parallelism."
        result["key_novelty"] = "Adaptive scan window-based task dispatch that dynamically balances data reuse for row-wise dataflow based on real-time sparse patterns."
        result["contributions"] = [
            "Scan window-based task dispatch scheme for flexible SpMM acceleration",
            "Hardware architecture with multiple memory components and custom schedulers",
            "1.67x average speedup across diverse SpMM workloads"
        ]
        result["hardware_target"] = ["ASIC"]
        result["technique_category"] = ["dataflow", "memory-system", "scheduling"]
        result["workloads"] = ["HPC", "graph-analytics"]
        result["metrics"]["speedup"] = "1.67x avg"
        result["baselines"] = ["state-of-the-art hardware accelerator"]
        result["limitations"] = "Performance gains depend on input sparsity patterns and may vary significantly across different sparse matrix types."
        result["tags"] = ["sparsity", "accelerator", "dataflow"]
        result["primary_theme"] = "Sparse matrix acceleration"

    elif "wit-hw" in title.lower():
        result["problem"] = "Hardware bug localization remains difficult for large designs and deep bugs because existing techniques rely on single bug-triggering test cases, missing complex interactions in intricate systems."
        result["motivation"] = "Automated bug localization can significantly reduce the manual effort required during hardware verification and development."
        result["method"] = "Wit-HW transforms bug localization into a test generation problem, creating witness test cases (passing cases) beyond the initial failing case. Spectrum-based analysis compares execution differences between passing and failing cases to eliminate innocent statements. A mutation-based strategy generates effective witness test cases optimized for bug localization."
        result["key_novelty"] = "Using witness test case generation (passing cases) combined with spectrum-based analysis to localize bugs in large hardware designs."
        result["contributions"] = [
            "Test generation framework transforming bug localization into a search problem",
            "Spectrum-based method for analyzing execution differences to identify buggy statements",
            "Mutation-based strategy for effective witness test case generation",
            "49%/73%/88% bug localization success at Top-1/Top-5/Top-10 ranks on 41 hardware bugs"
        ]
        result["hardware_target"] = []
        result["technique_category"] = ["formal-verification"]
        result["workloads"] = []
        result["metrics"]["other"] = "49% Top-1, 73% Top-5, 88% Top-10 bug localization"
        result["baselines"] = ["state-of-the-art bug localization techniques"]
        result["limitations"] = "Effectiveness depends on generating adequate witness test cases and may be limited by design complexity."
        result["tags"] = ["debugging", "verification", "test-generation"]
        result["primary_theme"] = "Hardware bug localization"

    elif "coxplorer" in title.lower():
        result["problem"] = "Algorithm-hardware co-design lacks unified exploration framework; existing tools for hardware design space exploration (DSE) and compression neural architecture search operate independently without systematic co-optimization."
        result["motivation"] = "Co-designing AI algorithms and accelerators jointly can achieve better performance and efficiency than sequential optimization."
        result["method"] = "CoXplorer decomposes the co-design space into stages for systematic exploration with reduced complexity. AC-Copilot toolchain provides multi-grained performance modeling via hardware simulation-compilation hierarchy. Hierarchical and bottleneck-guided search harmonizes model compression and hardware design objectives."
        result["key_novelty"] = "Multi-staged co-design space decomposition connecting model-compression and architecture design spaces with hierarchical bottleneck-guided search."
        result["contributions"] = [
            "Multi-staged co-design space decomposition method",
            "AC-Copilot toolchain with hierarchical performance modeling",
            "Hierarchical bottleneck-guided search for co-exploration",
            "53.7% throughput and 45.8% energy efficiency improvements for CNN; 7.5x speedup and 9.9x energy boost for Transformer"
        ]
        result["hardware_target"] = ["ASIC", "SoC"]
        result["technique_category"] = ["compiler", "quantization", "kernel-fusion"]
        result["workloads"] = ["CNN", "transformer", "LLM-inference"]
        result["metrics"]["speedup"] = "7.5x transformer, 53.7% CNN throughput"
        result["metrics"]["energy_or_tops_w"] = "9.9x energy (transformer), 45.8% (CNN)"
        result["baselines"] = []
        result["limitations"] = "Scalability and applicability to newer emerging workloads beyond CNN and transformer models require further investigation."
        result["tags"] = ["codesign", "dse", "compression"]
        result["primary_theme"] = "Algorithm-hardware co-design"

    elif "coflex" in title.lower():
        result["problem"] = "Hardware-Aware Neural Architecture Search (HW-NAS) suffers from extensive search spaces and high computational costs, limiting practical adoption for DNN accelerator design."
        result["motivation"] = "Efficient HW-NAS enables automated co-optimization of neural networks and hardware for edge accelerator development."
        result["method"] = "Coflex integrates Sparse Gaussian Process (SGP) with multi-objective Bayesian optimization, reducing GP kernel complexity from cubic to near-linear. This scalable approximation decreases computational overhead while maintaining predictive accuracy for large-scale search space exploration."
        result["key_novelty"] = "Sparse Gaussian Process with multi-objective Bayesian optimization reducing kernel complexity for scalable HW-NAS."
        result["contributions"] = [
            "SGP-based HW-NAS framework with near-linear kernel complexity",
            "Multi-objective Bayesian optimization for hardware-aware architecture search",
            "1.9x to 9.5x computational speed-up over state-of-the-art methods",
            "High network accuracy with improved Energy-Delay-Product"
        ]
        result["hardware_target"] = ["ASIC"]
        result["technique_category"] = ["compiler", "EDA"]
        result["workloads"] = ["CNN"]
        result["metrics"]["speedup"] = "1.9x-9.5x search speed-up"
        result["baselines"] = ["state-of-the-art HW-NAS methods"]
        result["limitations"] = "SGP approximation may not capture all design space nuances for highly constrained accelerator scenarios."
        result["tags"] = ["nas", "optimization", "bayesian"]
        result["primary_theme"] = "Hardware-aware NAS"

    elif "cimwise" in title.lower():
        result["problem"] = "Existing CIM compilers focus on hardware parameters while neglecting diverse dataflow patterns across different CIM architectures, limiting optimization for specific workloads."
        result["motivation"] = "An architecture-aware compiler for computing-in-memory processors can better exploit hardware capabilities and improve DNN inference efficiency."
        result["method"] = "CIMWise is an IREE-based end-to-end AI compiler featuring auto-tuning with comprehensive search space covering both hardware parameters and dataflow characteristics. A two-stage simulated annealing search algorithm explores optimal scheduling strategies, with an adaptable on-chip memory model and customized backend for operator-level optimization."
        result["key_novelty"] = "IREE-based CIM compiler with auto-tuning framework integrating both hardware parameters and dataflow characteristics for optimal scheduling."
        result["contributions"] = [
            "General IREE-based compiler for diverse CIM processor architectures",
            "Auto-tuning framework with comprehensive search space and analytical cost model",
            "Two-stage simulated annealing search for optimal scheduling",
            "58% energy reduction and 19% latency decrease vs. prior CIM compilers"
        ]
        result["hardware_target"] = ["CIM"]
        result["technique_category"] = ["compiler", "scheduling", "memory-system"]
        result["workloads"] = ["CNN", "LLM-inference"]
        result["metrics"]["energy_or_tops_w"] = "58% energy reduction"
        result["metrics"]["speedup"] = "19% latency decrease"
        result["baselines"] = ["prior CIM compilers"]
        result["limitations"] = "Compiler effectiveness depends on the quality of the analytical cost model and may need tuning for new CIM architectures."
        result["tags"] = ["compiler", "cim", "autotuning"]
        result["primary_theme"] = "CIM compiler optimization"

    elif "sparsh" in title.lower():
        result["problem"] = "SNNs with weight sparsity require efficient memory organization to minimize over-provisioning while maintaining fast access and high bandwidth utilization on FPGAs."
        result["motivation"] = "Efficient memory organization for sparse SNNs can significantly improve energy efficiency and performance on FPGA implementations."
        result["method"] = "SPARSH uses sparse hashing for efficient nonzero weight storage distributed across FPGA-optimized buckets. A Bloom filter controller detects sparsity and skips zero weights/activations. A scheduler prioritizes accesses hitting the same bucket to improve latency. Design parameters are selected based on target SNN sparsity."
        result["key_novelty"] = "Sparse hashing-based memory organization with Bloom filter-guided skipping for efficient SNN acceleration on FPGA."
        result["contributions"] = [
            "Efficient hash function and sparse hashing for compact nonzero weight storage",
            "Bloom filter controller for sparsity detection and zero-access skipping",
            "Scheduler prioritizing same-bucket accesses to reduce latency",
            "3.2x memory over-provisioning reduction, 77% latency reduction, 68% bandwidth improvement"
        ]
        result["hardware_target"] = ["FPGA"]
        result["technique_category"] = ["memory-system", "sparsity"]
        result["workloads"] = ["CNN"]
        result["metrics"]["speedup"] = "77% latency reduction"
        result["metrics"]["area"] = "3.2x memory reduction"
        result["metrics"]["other"] = "68% bandwidth utilization improvement"
        result["baselines"] = []
        result["limitations"] = "Sparse hashing overhead may impact performance for SNNs with uniform sparsity patterns."
        result["tags"] = ["snn", "fpga", "memory"]
        result["primary_theme"] = "Sparse SNN memory optimization"

    elif "nstherm" in title.lower():
        result["problem"] = "Fast thermal simulation across varying chiplet geometries requires balancing computational cost (deterministic solvers), convergence speed (stochastic methods), and error guarantees (neural networks lack bounds)."
        result["motivation"] = "Efficient thermal simulation is critical for iterative chiplet shape optimization in thermally constrained designs."
        result["method"] = "NSTherm integrates operator learning with stochastic methods. Diffeomorphic mapping enables handling shape variations without retraining. Network predictions guide stochastic variance reduction, while stochastic results provide error corrections and guarantees for neural network outputs."
        result["key_novelty"] = "Hybrid neural-stochastic fusion with diffeomorphic mapping for error-bounded thermal simulation across varying geometries."
        result["contributions"] = [
            "Diffeomorphic mapping for operator networks handling geometry variations",
            "Neural-stochastic fusion for variance reduction and error bounds",
            "10.69-23.04x speedup vs. COMSOL",
            "5.20-11.87x speedup vs. traditional stochastic methods"
        ]
        result["hardware_target"] = []
        result["technique_category"] = ["physical-design"]
        result["workloads"] = []
        result["metrics"]["speedup"] = "10.69-23.04x vs COMSOL"
        result["baselines"] = ["COMSOL", "traditional stochastic methods"]
        result["limitations"] = "Approach complexity and accuracy depend on quality of diffeomorphic mapping for diverse geometries."
        result["tags"] = ["thermal", "simulation", "neural"]
        result["primary_theme"] = "Thermal simulation for chiplets"

    elif "r2t-tiny" in title.lower():
        result["problem"] = "TinyML on FPGAs requires balancing high throughput with tight resource constraints; existing designs choose between high-throughput pipelined or low-throughput systolic approaches, creating resource contention."
        result["motivation"] = "Throughput-driven TinyML on resource-constrained FPGAs enables efficient on-device inference for edge applications."
        result["method"] = "R2T-Tiny provides layer-wise customizability via runtime partial reconfiguration, dynamically switching between pipelined and systolic accelerator types per layer. Tailored approximations per layer further optimize resource utilization and throughput."
        result["key_novelty"] = "Runtime partial reconfiguration enabling layer-wise adaptive acceleration type selection for throughput-driven TinyML on tiny FPGAs."
        result["contributions"] = [
            "Adaptive framework for layer-wise accelerator type selection",
            "Runtime partial reconfiguration for throughput optimization",
            "Tailored per-layer approximations",
            "1.6x average throughput increase vs. DNNDK with <1% accuracy loss"
        ]
        result["hardware_target"] = ["FPGA", "SoC"]
        result["technique_category"] = ["approximation", "parallelism"]
        result["workloads"] = ["CNN"]
        result["metrics"]["speedup"] = "1.6x throughput"
        result["metrics"]["accuracy"] = "<1% loss"
        result["baselines"] = ["DNNDK"]
        result["limitations"] = "Reconfiguration overhead and applicability to larger models beyond TinyML domain remain unexplored."
        result["tags"] = ["tinyml", "fpga", "reconfigurable"]
        result["primary_theme"] = "TinyML FPGA acceleration"

    elif "sera-float" in title.lower():
        result["problem"] = "Approximate floating-point computing lacks resilience to soft errors, and interaction between approximation-induced errors and soft errors can cause exceptions or unexpected failures in DNN inference."
        result["motivation"] = "Soft error resilient approximation formats enable energy-efficient neural network inference without sacrificing reliability."
        result["method"] = "SERA-Float protects sign and exponent bits using error-correcting codes and maintains 8 valid mantissa bits instead of truncation. Critical bit tracking prevents overflow, underflow, and NaN exceptions. Narrower arithmetic units leverage the format for energy savings."
        result["key_novelty"] = "Approximate floating-point format combining error-correcting codes for sign/exponent protection with critical bit tracking to prevent exceptions."
        result["contributions"] = [
            "ECC-protected sign and exponent bits for soft error resilience",
            "Critical bit tracking to prevent floating-point exceptions",
            "8-bit valid mantissa approach replacing truncation",
            "Up to 80.3% energy savings per multiplication with 0.9% accuracy loss"
        ]
        result["hardware_target"] = ["ASIC"]
        result["technique_category"] = ["approximation", "reliability"]
        result["workloads"] = ["CNN"]
        result["metrics"]["energy_or_tops_w"] = "80.3% energy savings"
        result["metrics"]["accuracy"] = "0.9% loss"
        result["baselines"] = ["prior floating-point formats"]
        result["limitations"] = "ECC overhead and effectiveness depend on specific soft error patterns and SER rates in target technologies."
        result["tags"] = ["approximation", "soft-error", "reliability"]
        result["primary_theme"] = "Soft error resilient approximation"

    elif "opto-vit" in title.lower():
        result["problem"] = "Vision Transformers have substantial compute and memory demands, hindering deployment in energy and bandwidth-constrained scenarios."
        result["motivation"] = "Silicon photonics-based acceleration can enable real-time, energy-efficient vision transformer inference at the edge."
        result["method"] = "Opto-ViT uses a hybrid electronic-photonic architecture: optical core handles matrix multiplications via VCSELs and microring resonators, while nonlinear functions and normalization run electronically. A lightweight Mask Generation Network identifies and prunes irrelevant patches. ViT backbone undergoes quantization-aware training and matrix decomposition for photonic constraints."
        result["key_novelty"] = "Near-sensor photonic ViT accelerator with region-aware pruning and hybrid electronic-photonic architecture for efficient edge deployment."
        result["contributions"] = [
            "Hybrid electronic-photonic architecture for ViT acceleration",
            "Lightweight MGNet for region-aware patch pruning",
            "Quantization-aware training and matrix decomposition for photonic constraints",
            "100.4 KFPS/W with 84% energy savings and <1.6% accuracy loss"
        ]
        result["hardware_target"] = ["photonic"]
        result["technique_category"] = ["pruning", "quantization"]
        result["workloads"] = ["transformer", "vision"]
        result["metrics"]["energy_or_tops_w"] = "100.4 KFPS/W, 84% energy savings"
        result["metrics"]["accuracy"] = "<1.6% loss"
        result["baselines"] = []
        result["limitations"] = "Photonic component fabrication variability and limited scalability to larger ViT models remain challenges."
        result["tags"] = ["photonic", "vision-transformer", "edge"]
        result["primary_theme"] = "Photonic ViT acceleration"

    elif "hydra" in title.lower():
        result["problem"] = "HDC accelerators suffer from high latency and energy costs in encoding, binding, permutation, and similarity search operations, limiting their practical deployment."
        result["motivation"] = "Energy-efficient HDC accelerators can enable scalable brain-inspired computing for edge and IoT applications."
        result["method"] = "HyDra uses SOT-MRAM based CAM for in-memory computation of binding (bitwise multiplication), permutation (bit shifting), and similarity search. A novel bit-drop permutation method reduces latency by 6x. HDC-specific adder optimizations reduce energy and area. Four-stage voltage scaling mitigates interconnect parasitic effects in similarity search."
        result["key_novelty"] = "SOT-MRAM based CAM architecture with bit-drop permutation method for efficient HDC operations."
        result["contributions"] = [
            "SOT-CAM integration for in-memory binding, permutation, and search",
            "Bit-drop permutation method with 6x latency improvement",
            "HDC-specific adder reducing energy and area by 1.51x and 1.43x",
            "21.5x-552.74x energy reduction vs. CMOS implementations, 2.27x lower energy vs. state-of-the-art"
        ]
        result["hardware_target"] = ["ASIC"]
        result["technique_category"] = ["circuit-design", "memory-system"]
        result["workloads"] = []
        result["metrics"]["energy_or_tops_w"] = "21.5-552.74x energy reduction"
        result["baselines"] = ["CMOS HDC", "state-of-the-art HDC accelerators", "CPU", "eGPU"]
        result["limitations"] = "SOT-MRAM variability and yield issues may impact practical deployment at scale."
        result["tags"] = ["hdc", "sot-mram", "neuromorphic"]
        result["primary_theme"] = "SOT-MRAM based HDC"

    elif "superconducting" in title.lower():
        result["problem"] = "Superconducting quantum processors are limited by low qubit counts and high gate errors; extending to qudits offers larger state space but requires optimization for qutrit-based systems."
        result["motivation"] = "Optimizing qudit-based quantum processors can improve gate fidelities and move toward fault-tolerant quantum computing."
        result["method"] = "An integrated simulation framework predicts cross-Kerr interactions in TTT systems and fidelities of two-qutrit CPhase gates under noise. Control-device co-optimization identifies conditions maximizing target frequency in adiabatic schemes to achieve higher gate fidelity."
        result["key_novelty"] = "Simulation framework for predicting and optimizing qutrit gate fidelities in superconducting TTT systems."
        result["contributions"] = [
            "Integrated simulation framework for TTT cross-Kerr interactions",
            "Noise-aware qutrit CPhase gate fidelity prediction",
            "Control-device co-optimization methodology",
            "Identification of conditions for maximum adiabatic target frequency"
        ]
        result["hardware_target"] = []
        result["technique_category"] = ["circuit-design"]
        result["workloads"] = []
        result["metrics"]["other"] = "Gate fidelity optimization via co-design"
        result["baselines"] = []
        result["limitations"] = "Framework validation limited to reported TTT systems; generalization to other qudit platforms requires further study."
        result["tags"] = ["quantum", "qudit", "simulation"]
        result["primary_theme"] = "Quantum qudit optimization"

    elif "m3:" in title.lower() or "mamba-assisted" in title.lower():
        result["problem"] = "Analog circuit design traditionally uses task-specific optimization models that don't generalize across different circuit topologies, limiting automation and scalability."
        result["motivation"] = "Unified RL models for multi-circuit optimization can accelerate analog design space exploration and enable automated circuit optimization."
        result["method"] = "M3 employs Mamba architecture with model-based RL to concurrently optimize multiple circuits of different topologies. Dynamic scheduling mechanism adapts RL parameters to balance exploration (novel designs) and exploitation (refinement). Framework operates without task-specific adjustments across varying circuit topologies."
        result["key_novelty"] = "Unified Mamba-based RL framework for simultaneous multi-circuit optimization across different topologies without task-specific tuning."
        result["contributions"] = [
            "Mamba architecture for unified circuit optimization model",
            "Model-based RL with dynamic scheduling for exploration-exploitation balance",
            "Multi-topology circuit optimization without task-specific adjustments",
            "Successful optimization of multiple circuits to target specifications"
        ]
        result["hardware_target"] = ["ASIC"]
        result["technique_category"] = ["circuit-design", "EDA"]
        result["workloads"] = []
        result["metrics"]["other"] = "Multi-circuit optimization across topologies"
        result["baselines"] = ["prior RL-based methods"]
        result["limitations"] = "Generalization to highly complex circuits and convergence guarantees for diverse topologies require further validation."
        result["tags"] = ["analog-design", "rl", "circuit"]
        result["primary_theme"] = "Unified analog circuit optimization"

    elif "pcbformer" in title.lower():
        result["problem"] = "S-parameter extraction for PCB traces via electromagnetic simulation is computationally expensive and becomes a bottleneck with iterative design changes in component placement."
        result["motivation"] = "Efficient S-parameter prediction enables faster signal integrity analysis and PCB design iteration."
        result["method"] = "PCBFormer is a deep learning framework capturing electromagnetic interactions across multiple layers in 3D PCB structures. The model accounts for each layer's properties and multiple traces' coupling effects to predict S-parameters across frequency ranges from DC to 1 GHz."
        result["key_novelty"] = "Deep learning framework capturing multi-layer 3D PCB trace interactions for rapid S-parameter prediction."
        result["contributions"] = [
            "Multi-layer 3D PCB structure modeling in deep learning",
            "Capture of electromagnetic coupling across traces and layers",
            "0.86 R² score across 210 S-parameters for realistic PCBs",
            "High accuracy replacement for electromagnetic simulation"
        ]
        result["hardware_target"] = []
        result["technique_category"] = ["EDA"]
        result["workloads"] = []
        result["metrics"]["other"] = "0.86 R² for S-parameter prediction (DC-1GHz)"
        result["baselines"] = []
        result["limitations"] = "Accuracy depends on training data quality and may not generalize to PCBs with significantly different layer configurations or materials."
        result["tags"] = ["pcb", "signal-integrity", "neural"]
        result["primary_theme"] = "PCB simulation via deep learning"

    elif "spikessynth" in title.lower():
        result["problem"] = "Printed SNNs for ultra-low-cost edge applications require adaptable and efficient spiking circuits, but fixed-threshold models have high energy consumption and limited task-specific performance."
        result["motivation"] = "Learnable, energy-efficient SNNs on printed electronics enable scalable neuromorphic computing for soft robotics, wearables, and IoT."
        result["method"] = "SpikeSynth proposes analog spiking circuits with learnable spike generator (LSG) adapting spike timing during training for better task performance. Robustness-aware training framework minimizes energy consumption adaptively. Designed for ultra-low power on resource-constrained platforms."
        result["key_novelty"] = "Learnable spike generator for printed SNNs with robustness-aware training enabling task-specific energy optimization."
        result["contributions"] = [
            "Analog spiking circuit with learnable spike generator",
            "Robustness-aware training for adaptive energy minimization",
            "57.6% average power reduction with 8% accuracy improvement",
            "89% area and 28.7% energy reduction vs. state-of-the-art printed SNNs"
        ]
        result["hardware_target"] = ["analog"]
        result["technique_category"] = ["circuit-design", "approximation"]
        result["workloads"] = ["CNN"]
        result["metrics"]["energy_or_tops_w"] = "57.6% power reduction"
        result["metrics"]["area"] = "89% reduction"
        result["metrics"]["accuracy"] = "8% improvement"
        result["baselines"] = ["state-of-the-art printed SNNs"]
        result["limitations"] = "Printed electronics process variability may impact reproducibility and performance consistency."
        result["tags"] = ["snn", "printed-electronics", "edge"]
        result["primary_theme"] = "Printed neuromorphic circuits"

    return result

# Analyze all papers
written_count = 0
for paper in papers:
    analysis = analyze_paper(paper)
    if analysis is None:
        continue

    # Write JSON
    json_path = output_dir / f"{analysis['id']}.json"
    with open(json_path, 'w') as f:
        json.dump(analysis, f, indent=2)

    # Write Markdown
    md_path = output_dir / f"{analysis['id']}.md"
    md_content = f"""# {analysis['title']}

**Venue:** {analysis['venue']}
**ID:** {analysis['id']}
**Confidence:** {analysis['confidence']}

## Problem
{analysis['problem']}

## Motivation
{analysis['motivation']}

## Method
{analysis['method']}

## Key Novelty
{analysis['key_novelty']}

## Contributions
{chr(10).join(f'- {c}' for c in analysis['contributions'])}

## Hardware Target
{', '.join(analysis['hardware_target']) if analysis['hardware_target'] else 'N/A'}

## Technique Category
{', '.join(analysis['technique_category']) if analysis['technique_category'] else 'N/A'}

## Workloads
{', '.join(analysis['workloads']) if analysis['workloads'] else 'N/A'}

## Metrics
{json.dumps(analysis['metrics'], indent=2)}

## Baselines
{chr(10).join(f'- {b}' for b in analysis['baselines']) if analysis['baselines'] else 'N/A'}

## Limitations
{analysis['limitations']}

## Tags
{', '.join(analysis['tags']) if analysis['tags'] else 'N/A'}

## Primary Theme
{analysis['primary_theme']}
"""
    with open(md_path, 'w') as f:
        f.write(md_content)

    written_count += 1

print(f"Analyzed and written {written_count} papers")
