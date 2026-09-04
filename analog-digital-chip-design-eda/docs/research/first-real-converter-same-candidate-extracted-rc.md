# First Real Converter Same-Candidate Extracted RC

This page records the first ngspice run that instantiates the assembled `aimc_readout_candidate_001` extracted netlist as one object.

The point is narrow but important. The previous loop tied energy, latency, noise, area, and break-even numbers to the same candidate name. This run asks a stricter physical question: can the named candidate netlist itself be included in a transient deck, driven at its row, sense, clock, supply, reference, and output pins, and measured as one circuit object?

It still does not prove the converter. The extracted netlist is a starter capacitance object. It does not contain transistor-level row-DAC switching, mux switching, sample-and-hold behavior, comparator resolution, SAR timing, code error, or signed-off physical area.

The useful result is the next honest rung in the ladder: one assembled candidate can be simulated as a physical RC object. The remaining work is to replace the starter capacitance object with active extracted converter circuitry and then fill the strict same-run payload from that one run.
