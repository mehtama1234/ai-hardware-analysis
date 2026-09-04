# Lab: Counter In Verilog

This lab uses a small counter to show the digital state problem: a register samples a value at a clock edge and preserves it until the next allowed decision.

## Object

The object being controlled is the stored count state.

## Constraint

The next count value must be computed and stable before the receiving flip-flops sample it. Reset must also put the state into a known value.

## Concrete Design Move

The always block describes a timed state update. On reset, the state becomes zero. Otherwise, each rising clock edge stores `count + 1`.

## Measurement

With `iverilog` installed:

```bash
iverilog -o counter_tb counter.v counter_tb.v
vvp counter_tb
gtkwave counter.vcd
```

Useful questions:

- Does reset force the count to zero?
- Does the count change only on clock edges?
- What state follows `1111` for a 4-bit counter?
- What timing evidence would be needed after synthesis?

## Failure Mode

The RTL can describe the intended sequence while the physical chip still fails if timing, reset, clocking, or synthesis semantics are wrong.

