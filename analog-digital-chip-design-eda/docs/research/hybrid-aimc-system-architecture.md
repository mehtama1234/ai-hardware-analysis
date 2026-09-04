# Hybrid AIMC System Architecture

This page is the system view for the analog in-memory foundation-model work. It shows what the chip must contain if analog arrays are used as one part of a larger serving machine.

The object is a request phase: prefill, decode, or batched decode. The request carries tokens, active context, latency budget, error budget, and model state. The chip must decide whether this phase should use analog projection tiles or stay on the digital path.

## System Diagram

```text
                         request metadata
             phase, batch, context, latency, error budget
                                      |
                                      v
       +----------------------+  path/reason  +----------------------+
       | digital control      |-------------> | execution scheduler  |
       | plane                |               |                      |
       | - resident weights   |               | - issue tile work    |
       | - tile health        |               | - issue SRAM reads   |
       | - calibration age    |               | - issue fallback     |
       | - state-error limit  |               +----------+-----------+
       +----------+-----------+                          |
                  ^                                      |
                  | health/error                         |
                  |                                      v
       +----------+-----------+              +-----------+-----------+
       | calibration and      |              | activation SRAM       |
       | tile monitor         |              | and KV cache          |
       | - probe columns      |              | - prompt activations  |
       | - rank weak tiles    |              | - decode state        |
       | - update correction  |              | - token memory        |
       +----------+-----------+              +-----------+-----------+
                  |                                      |
                  | correction tables                    | activation codes
                  v                                      v
       +----------+-----------+              +-----------+-----------+
       | digital correction   |<-------------| DAC row drivers       |
       | and accumulation     | partial sums | - code to voltage     |
       | - scale              |              | - settle row input    |
       | - bias               |              +-----------+-----------+
       | - sparse residual    |                          |
       +----------+-----------+                          | row voltages
                  ^                                      v
                  | column codes             +-----------+-----------+
       +----------+-----------+              | conductance tiles     |
       | SAR ADC banks        |<-------------| - resident weights    |
       | - current to code    | column       | - current summation   |
       | - bit decisions      | currents     | - wire/drop/noise     |
       +----------------------+              +-----------------------+

       digital fallback path:

       activation SRAM and KV cache -> digital projection core
                                    -> normalization/softmax/sampling
                                    -> next model state
```

## What Each Block Owns

The control plane owns the decision. It does not compute the projection. It decides whether the analog path is allowed for this request phase.

The scheduler owns ordering. It sends activation blocks to DACs, chooses resident tiles, collects ADC reads, and reserves the fallback path when the control plane refuses analog.

The activation SRAM and KV cache own changing state. This is why decode can become digital-heavy even when projection math is cheap. The cache is not a fixed trained weight matrix.

The DAC row drivers own the input boundary. A digital activation code becomes a row voltage. Input error fans out through every programmed conductance on that row.

The conductance tiles own approximate dense weighted sums. They are good for resident fixed projections when reuse is high and tolerated error is known.

The SAR ADC banks own the output boundary. A current becomes a digital code through timed comparisons. More bits cost more decisions and only help if noise and settling allow them.

The digital accumulator and correction block owns partial sums, scale, bias, and residual repair. It turns measured analog behavior into a corrected model value.

The mixed-signal trust boundary owns the final accept-or-fallback decision for a measured tile result. The detailed interface is in `Mixed-Signal Trust Boundary Spec`: raw ADC code, zero code, gain, bias, residual, calibration age, tile enable, corrected value, valid bit, fallback bit, and reason code.

The calibration and tile monitor owns evidence about the physical array. It decides which columns, rows, converters, or tiles need measurement before they are trusted again.

## Request Flow

For prefill, the request has many prompt tokens. Projection weights are reused heavily. If weights are resident and tiles are healthy, the control plane can choose analog because the fixed boundary cost is amortized.

For single-token decode, the request has little dense work per step. If the active context is long, KV-cache movement can dominate. The control plane may choose digital even though the analog projection itself is cheap.

For batched decode, several requests share a decode step. Batch reuse can pay for DAC, ADC, scheduling, and correction overhead. The control plane can choose the batched analog path if tile health and error budget allow it.

For stale calibration or weak tiles, the request should fall back to digital. That is not a failure of the design. It is the design protecting the model state.

## Evidence Chain

The architecture is credible only if each block has a measurement:

- DAC: row-voltage error, gain error, offset error, settling time
- tile: conductance drift, wire drop, current-sum error, tile yield
- ADC: code error, comparator noise, conversion steps, energy per read
- accumulator: partial-sum correctness and overflow margin
- correction: residual state error after gain, bias, or sparse repair
- tile monitor: worst-column error and calibration work
- control plane: path decision and fallback reason
- scheduler: latency, queue delay, and utilization
- full request: energy per token, p95 latency, state error, output change

The important measurement is not only whether a tile computes a dot product. The important measurement is whether the request leaves the chip with the right next state at lower cost than the digital baseline.

## Operation Partition

The detailed operation-level split is in `Transformer Operation Partition For Hybrid AIMC`. That page turns the architecture into a checkable list: embedding lookup, projections, attention scores, masks, softmax, value mixing, normalization, residual addition, KV-cache movement, logits, sampling, adapters, calibration, and serving policy.

The main rule is simple. Analog is strongest when the object is a fixed trained dense matrix with enough reuse to pay for conversion and calibration. Digital is strongest when the object is an address, a rule, a comparison, a scale measurement, changing token memory, or a request decision. Hybrid work is useful only when it states exactly where the changing state lives and how the resulting error is measured after the next model boundary.

## What This Adds To The Project

The earlier pages explain the pieces: conductance stores a weight, crossbars sum current, DACs and ADCs set boundaries, attention is changing memory, calibration is a schedule, tile health decides where to spend measurement, and serving policy decides when to use the array.

This architecture page puts those pieces in one machine. It is the reference drawing for the next labs: RTL scheduler, mixed-signal boundary checks, SRAM/cache traffic model, and eventually an OpenLane/OpenROAD pass for the digital control block.
