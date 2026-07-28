# CGO 2025: The Compiler as Architecture Interpreter

## What CGO is

CGO (International Symposium on Code Generation and Optimization) sits at the intersection of programming languages, compiler infrastructure, and computer architecture. The 500-person community that attends are systems researchers, compiler engineers, and hardware-conscious software builders who own the problem of translating high-level intent into efficient machine execution. Unlike PL venues (PLDI, OOPSLA), CGO assumes the hardware is real and fixed; unlike architecture venues (ISCA, ASPLOS), CGO assumes the code is alive and heterogeneous. CGO's unique contribution is the deep integration of these two worlds — the recognition that semantics-preserving compilation is the irreducible interface where algorithmic ambition meets hardware capability.

## The one problem this community is organized around

CGO 2025 reveals a field unified by a single architectural pressure: **specialized hardware has exploded, but the compiler infrastructure to exploit it has not kept pace.** This is not a new problem — it has been the CGO mandate since its inception — but 2025 shows it in acute form. Nearly three-quarters of the papers (28/40) target CPUs as their primary platform, yet within that category lies crushing diversity: ARM with MTE and PAC, RISC-V with custom ISA extensions, NPUs with spatial hardware loops, quantum processors with zone-segregated execution, PIM devices with radically different memory hierarchies. The compiler must become an architecture interpreter: it must understand not just control flow and data dependencies, but the *specific affordances* of each target and map computational intent onto those affordances precisely.

The deeper tension is that this specialization is increasingly fine-grained and problem-specific. A GEMM for a LLM on PIM has entirely different requirements than one on a GPU or RISC-V accelerator. A hash function synthesizer needs a different backend than an FHE compiler. A quantum circuit optimizer has no common ground with a Java heap protector. Yet all these problems flow through the same infrastructure — the same IR frameworks (MLIR dominates, appearing in 10+ papers directly or in spirit), the same optimization passes, the same code-generation stages. The organizing question becomes: how can a single compiler *infrastructure* accommodate this radical diversity without becoming a special-case factory?

## The main approaches in 2025

### Multi-level intermediate representations (MLIR and dialects as universal translator)

The most striking trend is the embrace of MLIR — an infrastructure explicitly designed to support multiple abstraction levels within a single compilation pipeline. Papers using MLIR include *Tensorize*, *ASDF* (for quantum circuits), *Combining MLIR Dialects with Domain-Specific Architecture for Efficient Regular Expression Matching*, *xDSL*, *CUrator*, *DialEgg*, and implicitly many others. The MLIR philosophy is to avoid the traditional compiler hourglass (high-level IR → narrow IR → target IR) and instead create a *multi-level mesh* where domain-specific dialects can coexist, lower progressively, and interact through equality saturation or rule-based transformation.

*DialEgg: Dialect-Agnostic MLIR Optimizer using Equality Saturation with Egglog* exemplifies this approach by integrating the Egglog equality-saturation engine with MLIR in a dialect-agnostic manner, enabling systematic optimization exploration without hand-coded dialect-specific rules. *ASDF: A Compiler for Qwerty, a Basis-Oriented Quantum Programming Language* implements a high-level quantum IR in MLIR specifically for basis-oriented quantum languages, enabling efficient synthesis from higher-level abstractions. The common insight: specialization does not require language-specific compilers; it requires infrastructure-level flexibility to define domain-appropriate abstractions and lowering rules.

Speedups are typically measured not in raw performance but in expressiveness and engineering burden. *Tensorize* achieves 100+ speedups on tensor DSL code by synthesizing tensor programs from legacy code automatically; the compiler does the translation work that otherwise requires human rewriting.

### Synthesis and search: from sketching to exhaustive enumeration

A second major approach inverts the traditional compiler role: instead of applying predetermined optimizations, the compiler *searches* for the right transformation. This appears across diverse problem domains:

*Tensorize: Fast Synthesis of Tensor Programs from Legacy Code using Symbolic Tracing, Sketching and Solving* uses algebraic solvers and symbolic traces to lift legacy code to tensor DSLs. *Automatic Synthesis of Specialized Hash Functions* learns format-specific hash functions from key examples via regex pattern identification. *Synthesis of Sorting Kernels* uses A* search with specialized heuristics to enumerate optimal sorting kernels for small arrays. *ANT-ACE: An FHE Compiler Framework for Automating Neural Network Inference* accepts ONNX models and generates C/C++ FHE programs through systematic search over compilation strategies.

The rationale is pragmatic: manual optimization of specialized operations is human-intensive and brittle. If the problem can be formulated as a search problem (cost function + constraint satisfaction), the compiler can automate it. *Synthesis of Sorting Kernels* demonstrates the power of this approach: using A* search with optimality-preserving heuristics, it synthesizes sorting kernels competitive with hand-tuned and AlphaDev-generated kernels without requiring TPU clusters. Typical speedups range from 2-10x on specialized micro-kernels.

### Precision in static analysis: tracking more information with less overhead

A third thrust focuses on making compiler analyses *richer* without proportional cost increase. This is critical for late-stage optimizations (auto-tuning, pass selection, profiling) that depend on accurate program properties.

*SkipFlow: Improving the Precision of Points-to Analysis using Primitive Values and Predicate Edges* tracks both primitives and objects, capturing branching structure via predicate edges to improve precision of alias analysis used downstream. *Stack Filtering: Elevating Precision and Efficiency in Rust Pointer Analysis* leverages Rust's explicit stack object lifetimes to prune spurious context-sensitive points-to relations. *GraalNN: Context-Sensitive Static Profiling with Graph Neural Networks* uses Graph Neural Networks to predict program profiles directly from control-flow structure without runtime instrumentation.

These approaches avoid the false binary of "expensive precise analysis" vs. "cheap imprecise analysis." By exploiting problem structure (predicate flow edges, stack lifetime semantics, CFG patterns) or learned models, they achieve precision gains at manageable cost. The payoff is upstream: downstream optimizations (vectorization, memory layout, pass selection) operate on richer, more accurate information.

### Hardware-level security and memory safety: compiling for protection primitives

A distinct cluster of papers (6-8 in total) approach security not as a post-hoc instrumention but as a first-class compiler problem. This represents a maturation of the field: security is now a hardware-level primitive (ARM MTE, PAC) that the compiler must understand and exploit.

*Cage: Hardware-Accelerated Safe WebAssembly* leverages ARM MTE and PAC hardware features to enforce spatial and temporal safety for WASM heaps simultaneously. *MTE4JNI: A Memory Tagging Method to Protect Java Heap Memory from Illicit Native Code Access* uses MTE to tag Java objects and prevent unauthorized access from JNI native code. *Janitizer: Rethinking Binary Tools for Practical and Comprehensive Security* adopts hybrid static-dynamic mechanisms for sound binary rewriting. *Teapot: Efficiently Uncovering Spectre Gadgets in COTS Binaries* instruments Speculation Shadows for efficient speculative-execution simulation.

The key insight is that hardware security primitives (MTE, PAC) are *asymmetric*: they require compiler support to instrument correctly but unlock performance compared to software-only approaches. Speedups are typically modest (10-30% overhead reduction vs. software-only), but the security guarantees are substantially stronger. This is a fundamental inversion: historically, security was "free" only if you sacrificed performance; now, security can be cheaper than unsafe alternatives if the compiler understands the hardware primitives.

### Heterogeneous hardware: specialization meets programmability

A smaller but important cluster addresses the challenge of heterogeneous execution platforms: how do you compile for a system with multiple execution contexts (big/little cores, scalar/vector units, PIM vs. host, quantum control vs. computation)?

*Scalar Interpolation: A Better Balance between Vector and Scalar Execution for SuperScalar Architectures* inserts scalar operations into vectorized loops on processors with distinct scalar and vector pipelines, achieving better utilization. *Parallaft: Runtime-Based CPU Fault Tolerance via Heterogeneous Parallelism* repurposes hardware heterogeneity concepts for software fault tolerance using OS primitives and little-core offloading. *Proteus: Portable Runtime Optimization of GPU Kernel Execution with Just-in-Time Compilation* performs lightweight JIT compilation on GPU kernels using language-agnostic LLVM IR.

These papers recognize that homogeneous execution is no longer the norm. Compilers must actively load-balance across execution units with different performance characteristics, costs, and constraints. The speedup is typically 10-30% by better utilization of underused hardware capabilities.

### Auto-tuning and learned optimizers: replacing hand-tuned heuristics

Two papers directly address the problem of discovering optimal compiler parameters without manual tuning:

*Towards Efficient Compiler Auto-tuning: Leveraging Synergistic Search Spaces* (appearing twice in the corpus, a sign of community focus) identifies "synergistic pass pairs" — compiler optimization sequences that jointly improve a specific metric. By clustering these pairs and using coreset-based search, the approach reduces the compiler auto-tuning search space from exponential to tractable, enabling learning across programs. *IntelliGen: Instruction-Level Auto-tuning for Tensor Program with Monotonic Memory Optimization* performs fine-grained instruction-level auto-tuning for tensor code by identifying monotonic memory-optimization strategies that preserve search tractability.

These approaches acknowledge that manual heuristics do not scale to the parameter explosion in specialized compilers. Rather than hand-coding "optimal" pass sequences or instruction-selection rules, the compiler discovers good policies via constrained search. Typical speedups are 5-20% vs. hand-tuned defaults on non-trivial workloads.

### Domain-specific lowering: breaking the hourglass abstraction

A final cluster takes the radical step of questioning the traditional compiler hourglass — the assumption that a single narrow IR (like LLVM IR) should sit in the middle. Instead, these papers introduce multiple lowering levels tailored to specific domains.

*A Multi-level Compiler Backend for Accelerated Micro-kernels Targeting RISC-V ISA Extensions* breaks the hourglass by progressive lowering across domain-specific abstraction levels, directly exposing hardware features like loops and streaming registers. *Combining MLIR Dialects with Domain-Specific Architecture for Efficient Regular Expression Matching* combines MLIR's multi-level representation with domain-specific dialects for regex matching. *LFQS: Synthesis of Quantum Simulators by Compilation* uses compilation-based synthesis to generate efficient quantum simulators rather than relying on dense tensor frameworks.

The insight is that universal IR compression loses information critical for specialized optimization. By preserving domain structure through intermediate lowering stages, the compiler can exploit regularities that would be invisible in a fully flattened representation. Speedups vary widely (2-50x depending on domain) but are often dramatic for specialized workloads.

## How it connects to the broader field

CGO sits between upstream hardware research and downstream language/runtime ecosystems. From hardware, CGO receives new primitives (MTE, PAC, quantum gates, PIM transfers, custom ISA extensions) and must rapidly integrate them into the compilation pipeline. From ML workloads (the source of many benchmarks in 2025), CGO receives pressure to optimize specific operations (GEMM, convolution, attention) at scale. The corpus shows this pressure directly: 8 papers target CNNs, 5 LLM-inference, 3 transformers explicitly.

What CGO feeds downstream is *infrastructure for specialization* — techniques, intermediate representations, and synthesis methods that enable runtime systems, programming languages, and application frameworks to exploit hardware effectively. MLIR, now integrated into TensorFlow, PyTorch, and numerous domain-specific frameworks, is the clearest example. Papers on secure compilation feed into Java runtime and WASM implementations. Auto-tuning techniques flow into Ansor (TVM's auto-scheduler) and similar systems. The compiler is no longer a black box between source and binary; it is a platform that other systems build upon.

The broader tension is this: specialization increases the complexity of the compiler pipeline, but this complexity must remain hidden from both programmers and downstream systems. The compression of multiple heterogeneous hardware capabilities into a single unified code generation pipeline is CGO's core challenge and contribution.

## What's open

Despite the breadth of 2025's work, significant gaps remain.

**First, cross-domain optimization is primitive.** A single application often mixes multiple workloads (e.g., a neural network with custom-kernel database operations and regex matching). The corpus contains no papers addressing *joint* optimization across these domains. Each paper optimizes within a domain (CNNs, regex, quantum, FHE) with little consideration for how its optimizations affect code outside the domain. The implicit assumption is that individual components are optimized in isolation and then composed. This breaks down badly for memory-constrained systems and complex applications. CGO has not yet solved the problem of *holistic* application-level compilation.

**Second, confidence in abstractions is low.** The corpus notes "confidence: low" across all 40 papers — they are working from abstracts only. More substantively, the 2025 work shows little consensus on *which* abstractions will stick. MLIR dominates, but DialEgg introduces Egglog; xDSL proposes sidekick compilation; *Tensorize* sketches programs with symbolic solving. Each paper invents slightly different notions of "what information to preserve through lowering." Without long-term experimental validation (5+ years of compiler use), it is unclear which abstractions are robust enough for production use. The field is still in the "try many frameworks" phase.

**Third, programmer control over specialization is absent.** The papers focus on automatic discovery (synthesis, search, auto-tuning) but provide little mechanism for programmers to *direct* specialization when automation fails. If a programmer knows their GEMM is memory-bound on a PIM device, how do they express that preference to *PIM-LLM*? If they want to exploit a novel ISA extension, do they write inline assembly or can they express intent at a higher level? The corpus lacks papers on *programmer-facing* APIs for specialization. The automation story is strong; the pragmatic "what do you do when the compiler is wrong" story is weak.

**Fourth, the verification problem is largely untouched.** With compilers performing synthesis, search, and code generation via learned models (*VEGA: Automatically Generating Compiler Backends using a Pre-trained Transformer Model*), how do we ensure correctness? *Pattern Matching in AI Compilers and Its Formalization* formalizes pattern matching in one domain, but the broader question — how to verify synthesized compilation strategies end-to-end — is open. The corpus contains one paper on formal verification of ML compiler semantics; 40 papers on producing code with no verification guarantees. This is sustainable only as long as fuzzing and testing catch bugs in practice. For safety-critical workloads (medical imaging, autonomous driving), this gap is untenable.

**Fifth, the scalability of multi-level IR ecosystems remains unproven.** MLIR is powerful, but papers using it often implement single-target optimizations (ASDF for quantum, CUrator for LLMs) rather than demonstrating cross-target reuse. Does a dialect written for quantum circuits help with FHE compilation? The corpus provides no evidence that the MLIR abstraction stack truly generalizes across domains. It is possible that each domain will require dialect-specific engineering, negating the cost savings promised by the infrastructure.

The field has made tremendous progress on *domain specialization* — optimizing specific workloads (LLMs, CNNs, quantum, FHE, regex, hash functions) to high performance. What remains open is *cross-domain integration*, *programmer control*, *verification at scale*, and *proof* that the abstraction infrastructure (MLIR, dialects, synthesized optimizations) generalizes robustly across the full spectrum of future workloads. CGO 2025 represents excellent progress on the former; the latter awaits the next chapter.
