# One More Motivation to Use Evaluation Tools This Time for Hardware Multiplicative Masking of AES

**Venue:** DATE · **Subtheme:** Side-Channel Resistance Verification for Cryptographic Hardware

## What It Does

This work applies formal side-channel verification tools to evaluate prior hardware implementations of multiplicative masking for AES, a critical countermeasure against power analysis and differential fault attacks. Multiplicative masking—introduced by De Meyer et al. at CHES 2018—randomizes the AES S-box inputs and outputs using multiplicative constants in the underlying field to prevent attackers from correlating intermediate values with plaintext/ciphertext. The paper uses the PROLEAD evaluation tool under the glitch-and-transition-extended probing model to systematically search for information leakage in the first-order Kronecker delta function—a core component of the masking scheme that computes whether two values are equal without revealing the values themselves.

Through formal verification, the authors discover that the original Kronecker delta implementation permits information leakage under the transition-extended probing model: glitches and transition delays in the logic can expose the equality result or intermediate operands to a probing attacker. The paper proposes an improved randomness optimization—adjusting when random values are introduced and how intermediate computations are scheduled—to eliminate the identified leakage. The fix is then re-verified using PROLEAD to confirm closure of the vulnerability.

## The Key Result

The paper demonstrates critical vulnerability in the prior state-of-the-art multiplicative masking design and validates an effective fix. While exact quantitative metrics (e.g., simulation time, area overhead of the fix) are not detailed, the formal verification methodology proves that the improved randomness optimization eliminates detectable leakage under the glitch-and-transition-extended probing model, achieving first-order security against a broader threat model than the original design.

## Why This Approach

AES is the de facto encryption standard for critical infrastructure, finance, and national security. Side-channel attacks—exploiting power consumption, electromagnetic emissions, and timing—have broken AES implementations in the field; hardware masking is the standard mitigation. However, prior masking designs often have subtle bugs in helper functions (like equality testing) that are difficult to find through manual code review or simulation. Formal verification tools like PROLEAD enable exhaustive search over all possible input/state combinations and probing locations, finding vulnerabilities that human review misses. This work underscores that even SOTA designs require tool-assisted verification and that the evaluation model (glitch-and-transition extensions) matters critically—the original design may have passed simpler probing models but fails under more realistic hardware fault models.

## What It Leaves Open

- The paper does not discuss the area, power, or latency overhead of the improved randomness optimization, making it unclear whether the fix is practical for resource-constrained embedded systems.
- No comparison of the proposed fix against other Kronecker delta implementations or alternative masking schemes (Boolean masking, threshold implementations).
- Evaluation limited to first-order masking; higher-order masking (d-order, for d > 1) and its security guarantees are not addressed.
- The glitch-and-transition-extended probing model is formal but represents a specific threat model; real-world side-channel attacks (power analysis, EM side channels) may have different vulnerability profiles.
- No discussion of randomness quality requirements or entropy costs for the improved optimization.
