# ChipNeMo: Domain-Adapted LLMs For Chip Design

## Bibliographic Identity

- Title: ChipNeMo: Domain-Adapted LLMs for Chip Design
- Year: 2023
- Source: https://arxiv.org/abs/2311.00176
- Track: ai-for-eda
- Subtheme: domain-adapted language models for chip engineering

## First-Principles Reading

The object being controlled is language-heavy engineering work inside chip design: answering design questions, writing EDA scripts, retrieving relevant knowledge, and helping engineers triage problems.

The constraint is domain mismatch. General models can produce fluent text, but chip work depends on specialized vocabulary, tool conventions, design context, logs, constraints, and proprietary knowledge. A wrong answer can waste engineering time or suggest an unsafe design action.

The mathematical form is domain adaptation. The model distribution is changed through chip-domain tokenization, continued pretraining, supervised instruction tuning, retrieval adaptation, and task-specific evaluation.

The concrete method is to adapt language models to chip-design corpora and evaluate them on tasks closer to engineering work than generic chat. The paper is important because it frames LLM value as adaptation to a domain workflow, not as broad language ability.

The evidence artifact is task performance across chip-design assistant use cases, EDA script generation, retrieval-supported answering, and ablations showing how adaptation changes results.

The failure boundary is unchecked action. A chip-domain LLM can help write or retrieve, but its output becomes engineering evidence only after compilers, simulators, timing tools, DRC/LVS checks, or expert review test it.

## Concept Links

- `ai-for-eda-is-a-checked-design-loop`
- `verification-is-evidence-implementation-matches-intent`
- `design-space-search-is-trading-expensive-measurements`

## What The Paper Teaches

The deeper lesson is that an LLM for chip design should be judged by whether it enters a checked engineering loop. Domain adaptation helps only if the adapted output reduces real design uncertainty.

