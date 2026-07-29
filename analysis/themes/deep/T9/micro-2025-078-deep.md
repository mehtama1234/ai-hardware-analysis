# Accurate Leakage Speculation for Quantum Error Correction

**Venue:** MICRO · **Subtheme:** Quantum Error Detection

## What It Does

GLADIATOR frames leakage detection in quantum error correction (QEC) as a graph-labeling problem. Physical qubits in superconducting systems can leak into higher energy levels (e.g., |2⟩ state for transmon qubits), causing erroneous error syndromes and leading to undetected logical errors. GLADIATOR detects leakage by analyzing syndrome patterns: offline, it constructs a code-specific syndrome classifier trained on simulated data with and without leakage events. Online, as new syndromes arrive, GLADIATOR assigns each syndrome to a probability distribution over leakage/no-leakage labels via a learned probabilistic model. The key innovation: decoupling leakage detection from the decoder, so detection runs in parallel with classical error correction without sequential feedback.

Architecture: syndrome extraction → probabilistic labeling (via offline-trained classifier) → leakage flag + decoder output. Detection cost: O(d²) for surface code distance d (scanning syndrome patterns), vs. O(d³) for the decoder itself.

## The Key Result

GLADIATOR detects 94% of leakage events (sensitivity) while maintaining 99.2% specificity (no false positives) on surface code simulations at physical error rate p=0.1%. Compared to Union-Find decoder alone, adding GLADIATOR leakage detection reduces logical error rate by 3.2x at distance d=7 and 8.7x at d=13. Latency overhead: <50 ns per syndrome (negligible compared to MWPM decoder's 0.8 us).

## Why This Approach

Standard QEC decoders (MWPM, Union-Find) assume bit-flip and phase-flip errors only; leakage events manifest as anomalous syndrome patterns that decoders misinterpret. Leakage is particularly dangerous because it's "silent"—the qubit leaves the computational subspace without raising a syndrome flag. Prior work used expensive full-waveform analysis or real-time discrimination; GLADIATOR's graph-labeling formulation enables offline training on simulated syndromes, then fast online inference. This is critical for fault-tolerant systems where leakage events occur 1–10% of the time.

## What It Leaves Open

- Generalization to other qubit types (trapped ion, photonic) requires retraining classifiers; cross-platform robustness unclear
- Scaling to larger codes (d > 13): syndrome graph complexity grows; inference time scaling and memory footprint not fully characterized
- Distinguishing leakage from other error types (decay, collective dephasing) requires more complex labeling; current model assumes binary leakage/no-leakage
- Integration with real QEC controllers: feedback latency between detector and decoder not modeled; causal consistency under pipelined detection unclear
- Adaptive thresholds for changing environmental noise: fixed classifier may degrade over time; online re-training mechanisms not proposed

