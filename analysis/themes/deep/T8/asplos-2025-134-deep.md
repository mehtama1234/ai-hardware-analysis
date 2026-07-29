# Formalising CXL Cache Coherence

**Venue:** ASPLOS · **Subtheme:** Formal Verification of Coherence Protocols

## What It Does

The paper formalizes the CXL.cache inter-device cache coherence protocol as a state-transition system in the Isabelle proof assistant, modeling 20 system components (device caches, host memory cache, message channels, buffers, transaction counters, and program threads) with 68 transition rules that encode all legal message flows. The model traces how cache blocks flow between device caches, host caches, and memory across PCIe interconnects as multiple agents (CPUs, GPUs, accelerators) perform coherent reads and writes. Crucially, the formalization captures the protocol's ordering constraints: when a device may send a snoop request, when replies must arrive before stores commit, and how message direction (forward vs. response) affects coherence safety.

The verification methodology chains two proof strategies: first, scenario verification using litmus tests from the CXL specification itself (message-sequence charts) to show the model faithfully reproduces expected behavior and to identify which protocol restrictions are truly necessary (e.g., proving that relaxing "Snoop-pushes-GO" constraints causes coherence violations). Second, automated proof of the Single-Writer-Multiple-Reader (SWMR) property via a 796-conjunct inductive invariant, machine-checked by Isabelle with 53,332 auto-generated lemmas (~211k lines of proof), using a custom super_sketch proof automation tool to manage the proof scale.

## The Key Result

The mechanized proof produced 53,332 Isabelle lemmas and ~211k lines of verified proof code, building a 796-conjunct inductive invariant that provably implies SWMR holds under all 68 transition rules. The formal analysis identified and proposed fixes for five defects in the CXL.cache prose specification: one inconsistency (contradictory message-ordering requirements), one redundancy (overly restrictive snoop requirements), one inefficiency (unnecessary reply serialization), and two ambiguities (vague conditions for cacheline invalidation). Four of these fixes were accepted by the CXL consortium and incorporated into the CXL 3.x standard before wide vendor deployment. Build time: 3–5 hours on Intel Core i9-14900HX.

## Why This Approach

CXL is the first industry standard for device-to-device cache coherence (PCIe-based, supporting CPUs/GPUs/ASICs), destined to underpin cloud datacenters at scale. Prose specifications, however clear, contain ambiguities that lead to incompatible implementations or subtle coherence bugs that only manifest at scale. Formal verification via machine-checked proof is the only approach that guarantees no hidden violations: informal reasoning, code reviews, and simulation testing (the traditional alternatives) cannot rule out corner cases in complex concurrent protocols. Isabelle mechanized verification was chosen because it scales to large state spaces (our 20-component model with explicit message channels and buffers) and produces a trustworthy artifact (the proof itself is machine-checkable and reusable as protocol evolution continues).

## What It Leaves Open

- The formal model is restricted to **two interacting devices**: coherence violations requiring three or more device interactions (e.g., cycles in multi-device request chains) are not covered, though the authors argue such scenarios are unlikely given the protocol's forward-only snoop flow.
- **Timing and liveness properties are not proven**: SWMR only guarantees safety (no two writers); it does not prove that coherent reads always complete or that stalled devices eventually receive snoop responses.
- **Model does not include performance-critical optimizations** such as speculative snoops or early snoop responses; their interaction with SWMR remains unverified.
- **Protocol evolution burden**: each change to CXL.cache (new message types, new constraints) requires re-proving the inductive invariant, which is labor-intensive despite automation.
- **The super_sketch proof automation is specialized to Isabelle**: portability to other proof assistants or integration into continuous integration pipelines for protocol maintenance is unclear.
