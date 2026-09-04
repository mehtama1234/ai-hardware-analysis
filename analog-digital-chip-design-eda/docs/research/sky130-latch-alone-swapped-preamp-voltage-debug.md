# Sky130 Latch-Alone Swapped Preamp Voltage Debug

This page is generated from the latch-alone polarity debug step.

The prior latch-alone run resolved strongly but with the wrong sign. This runner swaps the measured preamp voltages before driving the latch input gates. It checks whether the latch-alone failure was a polarity-map issue instead of a weak latch issue.

It is latch-alone debug evidence. It is not sampled-node kickback, not coupled preamp/latch loading, not SAR evidence, not layout, and not accepted post-layout converter evidence.
