# First Real Converter Frontend To Input-Stage Proxy

This page connects two pieces of evidence that were previously separate.

The extracted ultra frontend produces a small but correctly signed sense-node voltage. The Sky130 comparator input-stage proxy can turn a tiny input difference into a larger output difference. This run feeds the measured frontend sense difference into the active input-stage proxy.

The first-principles question is simple: after the passive physical frontend weakens the sampled signal, can an active Sky130 transistor stage make the signal larger while keeping the sign correct? If the active-stage deck cannot solve promptly, that is also useful evidence: the next step is to make this handoff measurable before claiming gain.

This is not accepted post-layout converter evidence. It is a bridge from extracted passive sensing to active transistor gain. The frontend and active input stage still need to become one extracted layout object with latch timing, kickback, offset, noise, SAR control, energy integration, DRC/LVS area, and one strict payload.
