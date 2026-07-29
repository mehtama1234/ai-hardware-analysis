# SMaCk: Efficient Instruction Cache Attacks via Self-Modifying Code Conflicts

**Venue:** ASPLOS · **Subtheme:** Instruction Cache Side-Channel Attacks

## What It Does

SMaCk exploits the x86 processor's self-modifying code (SMC) detection mechanism—a security feature designed to maintain coherence when instructions in the L1i cache are overwritten—as a high-fidelity timing side channel. When an instruction executes a write (MOV, LOCK+INC, CLFLUSH, CLFLUSHOPT, PREFETCH, CLWB) to a cache line already resident in the L1i cache, the processor serializes all SMT sibling threads and flushes the entire pipeline, inducing an observable delay of 235–425 cycles. This is 100–350x larger than conventional L1i cache hit/miss differences (1–2 cycles). SMaCk constructs Prime+iProbe and Flush+iReload covert channels: the attacker primes L1i cache sets with nop-filled instructions, then probes using SMC-triggering writes. Evictions caused by the victim's instruction cache activity result in cache misses, which are detected via slow probe latencies. The authors reverse-engineer which x86 instructions trigger machine clears using hardware performance counters (MACHINE_CLEARS.SMC, CYCLE_ACTIVITY.STALLS_TOTAL) and validate SMC behavior across Intel Skylake through Raptor Lake and AMD Ryzen architectures.

For attacks, the receiver primes L1i sets with NOP instructions on both SMT threads, then the attacker issues SMC-creating instructions while timing the victim's code execution. Variations include using selective flush instructions (clflush/clflushopt) to target specific cache lines and prefetch instructions (PREFETCHNTA, PREFETCHT2) to observe which cache lines the victim loads. The attack operates entirely unprivileged and can leak cryptographic operations, control flow, and speculative execution paths.

## The Key Result

On RSA decryption (2048-bit Libgcrypt), SMaCk recovers 70% of key bits from just 10 side-channel traces using Prime+iFlush, outperforming the Mastik L1i toolkit (which requires many more traces). For OpenSSL SRP server authentication, a single trace leaks 65–90% of session key bits via instruction cache activity patterns, compared to 22–48% for Mastik. Flush+iReload achieves up to 670 Kbit/s covert channel bandwidth with <1% error rate. ISpectre (a Spectre-v1 variant using L1i encoding) demonstrates up to 4105 B/s data exfiltration on AMD Ryzen 5. Performance counter-based detection (machine_clears.smc counter monitoring) achieves 99.36% F-score distinguishing attack from benign code.

## Why This Approach

Conventional L1i cache side-channel attacks suffer from extremely low signal-to-noise: a cache hit vs. miss is only 1–2 cycles, making cryptographic leakage unreliable and requiring dozens to thousands of traces. SMC pipeline flushes provide a 100–350x amplification of timing differences, enabling single-trace or few-trace attacks that were previously infeasible. The x86 SMC mechanism is ubiquitous—present across all modern Intel and AMD processors—and unavoidable for security reasons. SMaCk's contribution is recognizing that this security feature, designed to prevent instruction cache coherence violations, creates a larger side channel than the cache itself. Prior work focused on data caches (Spectre, Meltdown) or TLBs; exploiting instruction cache coherence is novel and affects all SMT-capable systems with self-modifying code detection.

## What It Leaves Open

- Attack requires SMT (Hyper-Threading) to be enabled; systems with SMT disabled, or single-threaded systems, are resistant.
- Effectiveness varies significantly across microarchitectures: AMD EPYC 7232P resists flush-based SMC conflicts, suggesting vendor-specific implementations may differ in vulnerability.
- For SRP key extraction, approximately 45% of key bits per single trace remain unrecoverable due to ambiguity in sliding-window decoding—multiple traces or additional side channels are needed for high-confidence key recovery.
- No evaluation of SMC behavior on newer architectures (Intel Meteor Lake, Arrow Lake; AMD Zen 5) or on systems with future microcode patches that may reduce SMC pipeline flush penalties.
- Defense via performance counter monitoring (99.36% F-score) is reactive; proactive defenses (e.g., randomizing SMC latency, removing SMC detection) are not evaluated.
