# Statistical Timing Analysis: From Basic Principles To State Of The Art

## Bibliographic Identity

- Title: Statistical Timing Analysis: From Basic Principles to State of the Art
- Year: 2008
- Source: https://blaauw.engin.umich.edu/wp-content/uploads/sites/342/2017/11/331.pdf
- Track: physical-design-and-signoff
- Subtheme: variation-aware timing analysis

## First-Principles Reading

The object being controlled is delay uncertainty. Timing closure asks whether data arrives before the decision edge, but real delay changes with process, voltage, temperature, local variation, and correlations across the die.

The constraint is that a single deterministic delay can hide probability. Worst-case corners may be too pessimistic, while typical timing can miss rare slow paths. Variation turns timing into a distribution.

The mathematical form is random-variable propagation through a timing graph. Gate and wire delays have distributions. Path max operations, reconvergent paths, and correlation structure decide how uncertainty reaches the final slack estimate.

The concrete method is to survey statistical timing models and algorithms that estimate timing behavior under variation. The important move is not replacing STA; it is making STA aware that delay is not one fixed number.

The evidence artifact is the timing distribution, assumptions about variation and correlation, and comparisons among statistical timing approaches.

The failure boundary is silicon mismatch. SSTA is only as good as its variation model, correlation handling, and tail estimates. If the statistical assumptions are wrong, the yield and timing risk estimates are wrong.

## Concept Links

- `timing-closure-is-proof-data-arrives-before-decision`
- `yield-is-probability-over-manufacturing-variation`
- `verification-is-evidence-implementation-matches-intent`

## What The Paper Teaches

The deeper lesson is that timing closure and yield are linked. A path does not simply pass or fail in the abstract; it passes with probability across manufactured parts and operating conditions.

