# Choco-Q: Commute Hamiltonian-based QAOA for Constrained Binary Optimization

**Venue:** HPCA · **Subtheme:** Performance Scheduling & Autotuning

## What It Does

Choco-Q encodes constraints by selecting a driver Hamiltonian that commutes with the constraint operator (the commute Hamiltonian), exploiting the Heisenberg picture to guarantee that constraint expectation values remain invariant during quantum evolution, achieving 100% in-constraints rate. Three optimization passes reduce circuit complexity for NISQ deployment: (1) Hamiltonian serialization decomposes the global commute Hamiltonian into independent local sub-Hamiltonians (proven via Lemma 1 to preserve constraint satisfaction), reducing circuit depth from ~4000 to ~24; (2) equivalent decomposition converts each local commute Hamiltonian into control-phase gates and CX gates with linear O(n) time complexity and O(n) circuit depth (Lemma 2), replacing exponential Trotter-Suzuki decomposition; (3) variable elimination reduces the constraint matrix dimension by removing variables with the most non-zero solution entries, shrinking qubit count and circuit depth at the cost of additional classical measurements. Evaluation is conducted on IBMQ Fez (159-qubit Heron r2), Sherbrooke, and Osaka (127-qubit Eagle r3) platforms, plus a classical GPU simulator (A100).

Using the commute Hamiltonian as the QAOA driver Hamiltonian provides a universal hard-constraint encoding for arbitrary linear constraints, paired with a linear-complexity exact decomposition that makes it deployable on current NISQ hardware.

## The Key Result

- **Speedup:** 4.69x end-to-end over cyclic Hamiltonian-based QAOA on real IBMQ hardware
- **Accuracy:** 235x improvement in success rate; 100% in-constraints rate; 658x improvement in approximation ratio gap vs. cyclic Hamiltonian
- **Other:** 10^6x decomposition time reduction; circuit depth reduction from ~10^4 to ~100; 2.65x in-constraints rate improvement on IBMQ

## Why This Approach

First QAOA framework achieving 100% in-constraints rate for arbitrary linear equality constraints via commute Hamiltonian encoding. Hamiltonian serialization technique that decomposes the global commute Hamiltonian into local sub-Hamiltonians with provably preserved constraint satisfaction, reducing circuit depth from thousands to tens. Exact linear-complexity decomposition of local commute Hamiltonians into control-phase and CX gates, eliminating exponential Trotter approximation overhead (10^6x decomposition time reduction). Variable elimination technique for further circuit depth reduction on NISQ devices; overall 235x algorithmic improvement in success rate and 4.69x end-to-end speedup over cyclic Hamiltonian-based QAOA

This work addresses the fundamental problem: Existing QAOA approaches for constrained binary optimization based on penalty terms or cyclic Hamiltonian simulation fail to encode arbitrary linear constraints, yielding near-zero success rates (as l...

## What It Leaves Open

- Circuit depth still grows linearly with problem size and number of constraints, limiting scalability to problems well within current NISQ qubit counts (tested up to 28 variables).
