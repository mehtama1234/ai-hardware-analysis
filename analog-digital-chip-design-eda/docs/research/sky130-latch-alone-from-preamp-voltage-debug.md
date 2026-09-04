# Sky130 Latch-Alone From Preamp Voltage Debug

This page is generated from the second isolated-latch debug-ladder step.

The preamp is replaced by ideal voltage sources equal to the measured preamp transient outputs. The sampled nodes are removed. This checks whether the latch core can resolve the preamp voltage before sampled-node kickback is reintroduced.

It is latch-alone debug evidence. It is not sampled-node kickback, not coupled preamp/latch loading, not SAR evidence, not layout, and not accepted post-layout converter evidence.
