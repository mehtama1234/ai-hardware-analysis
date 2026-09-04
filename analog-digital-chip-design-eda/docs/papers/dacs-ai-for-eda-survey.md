# Machine Learning For Electronic Design Automation: A Survey

## Bibliographic Identity

- Title: Machine Learning for Electronic Design Automation: A Survey
- Year: 2021
- Source: https://arxiv.org/abs/2102.03357
- Track: ai-for-eda
- Subtheme: EDA task taxonomy

## First-Principles Reading

The object being controlled is where learning belongs in the chip-design toolchain. EDA is not one task. It is a chain of representations and checks: specification, architecture, RTL, verification, synthesis, placement, routing, extraction, timing, power, and signoff. A survey matters when it separates these loops instead of treating “AI for chips” as one undivided promise.

The constraint is that each EDA stage has a different evidence standard. A model that predicts congestion is judged differently from a model that generates RTL, sizes an analog circuit, predicts timing, repairs design rules, or triages logs. Some tasks have strong automatic checkers. Some tasks depend on expensive simulation. Some tasks have sparse data because commercial designs and process details are private.

The mathematical form is task decomposition. Each learning use case can be read as:

```text
artifact + context -> prediction/action -> tool check -> design consequence
```

The artifact may be a graph, layout image, netlist, waveform, timing path, design rule violation, or text log. The important question is whether the prediction changes an engineering decision and whether that decision is checked.

The concrete method is taxonomy. The survey organizes machine-learning methods across the EDA hierarchy and names the kinds of models used for prediction, optimization, search, and classification. For this corpus, the useful move is not any single algorithm. It is the mapping from design stage to artifact type, data source, checker, and measured outcome.

The evidence artifact is the survey's classification of prior work, benchmark comparisons where available, and task-stage mapping. That evidence is weaker than a new tool result, but stronger than a vague claim because it shows which EDA loops have been attacked and what each loop tries to measure.

The failure boundary is survey abstraction. A taxonomy can clarify the field while hiding the hard part of deployment: proprietary data, PDK dependence, design-specific constraints, weak benchmarks, changing tool versions, and the cost of integrating a model into a real flow.

## Concept Links

- `ai-for-eda-is-a-checked-design-loop`
- `design-space-search-is-trading-expensive-measurements`
- `verification-is-evidence-implementation-matches-intent`
- `eda-is-constraint-solving`

## What The Paper Teaches

The deeper lesson is that AI for EDA must be read by loop, not by model family. The first question is not whether the method uses a neural network. The first question is what design artifact it acts on, what checker constrains it, and what engineering uncertainty it reduces.

