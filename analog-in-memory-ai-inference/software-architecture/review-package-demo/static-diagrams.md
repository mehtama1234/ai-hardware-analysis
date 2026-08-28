# Static Diagrams

This file gives simple diagrams for the review package.

They are intentionally plain. Their job is to make the roadmap easier to explain when the interactive HTML page is not open.

## Diagram 1: Full Product Flow

```text
User brings one workload
  |
  v
Model intake
  - model file
  - input shape
  - output target
  - accuracy target
  - power and timing target
  |
  v
Analog and digital fit
  - analog candidates
  - digital-required regions
  - unsupported regions
  - rewrite options
  |
  v
Evidence runs or imports
  - analog accuracy simulation
  - crossbar layout check
  - compiler mapping
  - full-system runtime estimate
  - board runtime trace
  - power and temperature traces
  - task accuracy result
  |
  v
Normalized package
  - one artifact per step
  - proof level
  - supported claims
  - blocked claims
  - missing evidence
  |
  v
Final answer
  - fit, partial fit, no fit, or unknown
  - what is proven
  - what is not proven
  - what must be built or measured next
```

What this diagram teaches:

The product is not one simulator and not one chip demo. It is a workflow that turns a workload into evidence and a claim boundary.

## Diagram 2: Analog And Digital Split

```text
Modern physical AI workload
  |
  +--> Stable matrix-heavy layers
  |      |
  |      v
  |   Analog array candidate
  |      - repeated weights
  |      - matrix multiply
  |      - possible energy benefit
  |
  +--> Dynamic attention and normalization
  |      |
  |      v
  |   Digital logic
  |      - changing token interactions
  |      - Softmax
  |      - LayerNorm
  |      - exact control
  |
  +--> Sensor, action, and safety boundary
         |
         v
      Digital or dedicated sensor/control path
         - timing
         - buffering
         - safety checks
         - fallback behavior
```

What this diagram teaches:

The safe claim is not "the full modern model is analog." The safe claim is that selected stable matrix-heavy regions may fit analog compute if the rest of the system is handled and measured.

## Diagram 3: Proof Ladder

```text
Weakest proof
  |
  v
Source context
  - explains why the topic matters
  - does not prove our chip
  |
  v
Local estimate
  - supports planning
  - not measured proof
  |
  v
Simulator output
  - supports risk discussion
  - not board proof
  |
  v
Compiler mapping
  - shows model-to-chip plan
  - not proof the board ran
  |
  v
System simulation
  - shows possible host and memory bottlenecks
  - not measured hardware
  |
  v
Board runtime
  - proves the package ran or failed on one board setup
  - not power or task proof
  |
  v
Power and thermal measurement
  - proves energy and heat for the same setup
  - not task proof
  |
  v
Task accuracy result
  - proves the tested task result
  - not long-term reliability
  |
  v
Repeated reliability and update evidence
  - supports stronger product claims under tested conditions
Strongest proof
```

What this diagram teaches:

Lower proof cannot silently become higher proof. The final answer must say which level each claim uses.

## Diagram 4: Silicon To Board Proof

```text
Chip feature exists
  |
  v
Board exposes the feature
  |
  v
Runtime can command it
  |
  v
Calibration checks the chip
  |
  v
Board runs the package
  |
  v
Lab measures power and temperature
  |
  v
Task result is checked
  |
  v
Final claim is allowed or blocked
```

What this diagram teaches:

A board response is not enough. A product claim needs synchronized runtime, calibration, power, temperature, task, and failure evidence for the same package and setup.

## Diagram 5: Claim Gate

```text
Proposed claim
  |
  v
Does an artifact support it?
  |
  +-- no --> Mark blocked
  |
  +-- yes
       |
       v
Does the proof level match the claim?
       |
       +-- no --> Downgrade or block
       |
       +-- yes
            |
            v
Does the package id and setup match?
            |
            +-- no --> Reject as mismatched evidence
            |
            +-- yes
                 |
                 v
              Allow narrow claim
```

What this diagram teaches:

The claim engine should be conservative. It should allow narrow claims tied to evidence, not broad claims that the artifacts do not support.

## Diagram 6: What The Company Must Own

```text
Reusable outside tools
  |
  +--> AIHWKIT-style analog behavior tests
  +--> CrossSim-style layout risk tests
  +--> analog-mlir compiler ideas
  +--> SST/Golem or ALPINE-style system simulation
  +--> lab instruments and board links
  |
  v
Company-owned product layer
  |
  +--> chip target
  +--> tile and bit-slicing rules
  +--> ADC and DAC scheduling
  +--> calibration profile format
  +--> runtime package format
  +--> board command protocol
  +--> evidence schema
  +--> final claim engine
```

What this diagram teaches:

Outside tools reduce work, but they do not replace the company-specific compiler, runtime, board, calibration, evidence, and claim layers.
