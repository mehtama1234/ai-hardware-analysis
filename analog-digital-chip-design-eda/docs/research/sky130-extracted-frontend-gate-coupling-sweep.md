# Sky130 Extracted Frontend Gate Coupling Sweep

This page sweeps the weak gate-startup handoff that failed in one polarity.

The question is not whether the full converter works. It does not. The question is narrower: can any assisted sense-to-gate loading and prebias setting let the extracted frontend drive real Sky130 transistor gates in both directions with enough output margin?

If the answer is yes, the next step is to remove the assist. If the answer is no, the frontend needs a real circuit change before latch and SAR work can produce trustworthy evidence.
