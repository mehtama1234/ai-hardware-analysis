# Need for zkSpeed: Accelerating HyperPlonk for Zero-Knowledge Proofs

**Venue:** ISCA · **Subtheme:** Cryptographic Acceleration (zkSNARK)

## What It Does

zkSpeed is a modular ASIC for accelerating HyperPlonk zero-knowledge proofs. The bottleneck in zkSNARK proving is the SumCheck protocol: the prover computes multivariate polynomial evaluations over a polynomial-sized domain. HyperPlonk uses three SumCheck variants (ZeroCheck, PolyCheck, VirtualPolyCheck), each performing 50–70% of total proving time. zkSpeed instantiates eight dedicated hardware units: a unified SumCheck processing element (handling all three variants via polynomial evaluation primitives), a multipoint evaluation unit (FFT-based), a polynomial commitment engine (Pedersen hashing), field arithmetic units (addition, multiplication in large prime fields), and a ring buffer for polynomial intermediate caching.

Data path: input polynomial coefficients → multipoint evaluation (FFT) → field arithmetic (mod p operations) → SumCheck reduction → output challenges. The unified SumCheck unit processes 64-bit field elements at 1 GHz, reducing proving time from CPU hours to seconds.

## The Key Result

zkSpeed achieves 14.5x speedup over CPU-optimized provers (libstark, gnark-go) for a 2²⁰-constraint circuit on HyperPlonk. For a 2³⁰-constraint proof (e.g., zkML use cases), zkSpeed generates proofs in 45 seconds, compared to 12+ hours on optimized CPUs. Memory bandwidth usage drops 3.2x because polynomial coefficients stream through the dataflow without reloading. Energy efficiency: 8.2 TOPS/W (throughput / power) vs. 0.3 TOPS/W on CPU.

## Why This Approach

HyperPlonk and similar IOP-based zkSNARKs are CPU-bound on polynomial arithmetic: evaluating p(x) at many points requires 10⁹+ modular multiplications, all serialized through CPU ALUs. A CPU can do ~1 GHz × 1 multiply/cycle = ~1 billion ops/sec; proving a 2³⁰-constraint circuit needs ~10¹² operations, forcing multi-hour latencies. zkSpeed's unified SumCheck unit parallelizes polynomial evaluation across eight pipelined stages, enabling sub-second proving. This is important because zero-knowledge proofs are entering production (privacy chains, zkML, compliance audits), making proving latency a business constraint.

## What It Leaves Open

- Single-proof throughput optimized; batch verification and incremental proving not addressed
- Polynomial representation fixed to coefficient form; Lagrange basis or other encodings not supported
- Scaling to larger proof systems (2⁴⁰+ constraints) requires more dataflow stages; area and power scaling not modeled
- Integration with software stacks (Circom, Cairo) requires host-ASIC communication protocols and memory management
- Generalization to other SNARKs (Groth16, Marlin, Spartan) requires custom unit re-design; unclear if modular architecture generalizes
