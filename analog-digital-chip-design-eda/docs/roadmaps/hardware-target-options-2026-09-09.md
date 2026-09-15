# Hardware target options after the simulation closeout

The software and circuit-linked numerical evidence is complete enough to choose
a physical execution route. Local inspection found no positively identified
analog-compute board, FPGA target or power instrument. This is limited local
visibility, not proof that remote or disconnected hardware does not exist.

## Route A: existing analog-memory board

This is the shortest route to a measured end-to-end result. The board must
expose array programming, signed input drive, converter output, reset/clock and
accessible power rails. Its array dimensions and converter must support either
the frozen 128×128 tile contract or a documented remapping. The board identity,
firmware/API, timing, usable precision, programming repeatability and power
measurement points must be recorded before adapting the compiler.

This route can prove real analog execution and measured task quality, latency
and energy. A board with only a digital controller or external ADC cannot prove
analog in-memory compute.

## Route B: fabricate the selected custom macro

The current physical candidate is not ready for fabrication: the extracted
converter fails the electrical margin gate, complete converter LVS is missing,
and repeated schematic diagnostics show history-dependent polarity. The next
macro revision must first resolve reset/history behavior, implement drain
isolation and controlled capacitance balance in layout, then pass extraction,
DRC/LVS and the full converter matrix. Fabrication also needs a foundry/MPW,
package, probe/board plan and an explicit cost/timeline decision.

This route can prove the custom converter claim, but it is the longest and most
expensive route. No fabrication authorization is implied by this document.

## Route C: simulation-only continuation

If no physical target is available, continue with extracted-SPICE and RTL
co-simulation. Complete the converter matrix, propagate measured circuit error
and timing distributions into the GPT-2 tile model, and report a simulated
latency/energy estimate with every assumption exposed. This can produce a
strong feasibility or no-benefit result, but it cannot claim hardware execution
or measured efficiency.

## Minimum information to resume Route A or B

1. Target identity and availability: array technology, dimensions, weight
   programming, input/output interfaces and documentation.
2. Control boundary: FPGA/MCU/host interface, clocks, reset, DMA/SRAM and
   converter handshake signals.
3. Measurement boundary: rails to measure, current/voltage bandwidth, scope or
   DAQ synchronization, warmup and repetition procedure.
4. Mapping: how the physical array realizes signed weights, DAC inputs, ADC
   references and the 144 logical tiles in the frozen GPT-2 contract.
5. Acceptance: allowed task degradation, latency percentile, energy boundary,
   fallback policy and uncertainty requirement.

Until those fields are supplied by an actual target, Route C is the only
authorized execution route. The digital-only decision remains valid and the
full hardware-backed goal remains open.
