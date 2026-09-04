# VerilogEval: Evaluating Large Language Models For Verilog Code Generation

## Bibliographic Identity

- Title: VerilogEval: Evaluating Large Language Models for Verilog Code Generation
- Year: 2023
- Source: https://arxiv.org/abs/2309.07544
- Track: digital-design-and-architecture
- Subtheme: LLM evaluation for RTL generation

## First-Principles Reading

The object being controlled is functional correctness of generated hardware code. Verilog text is not useful because it looks like RTL. It is useful only if it compiles and behaves like the intended circuit.

The constraint is executable ambiguity. A language model can produce code that appears reasonable but has syntax errors, wrong sensitivity, wrong state update, wrong reset behavior, width mistakes, latch inference, or incomplete case behavior.

The mathematical form is benchmarked program synthesis with simulation as the checker:

```text
prompt -> generated Verilog -> compile/simulate -> compare with expected behavior
```

This makes the claim testable. The model is not rewarded for sounding correct; it is measured by whether generated code passes functional checks.

The concrete method is a Verilog generation benchmark built from HDLBits-style problems, with automated evaluation through hardware simulation and comparison against golden behavior.

The evidence artifact is pass rate, compile error rate, simulation behavior, task difficulty, and fine-tuning comparisons. This evidence is stronger than examples because it uses repeatable tests across many tasks.

The failure boundary is chip correctness. Passing VerilogEval does not prove timing closure, clock-domain safety, reset architecture, synthesis quality, physical implementation, power, or verification coverage for a real chip.

## Concept Links

- `digital-logic-turns-voltage-into-symbols`
- `verification-is-evidence-implementation-matches-intent`
- `ai-for-eda-is-a-checked-design-loop`

## What The Paper Teaches

The deeper lesson is that code generation for hardware must be tied to execution. The minimum standard for a generated RTL fragment is not fluency; it is behavior under a checker.

