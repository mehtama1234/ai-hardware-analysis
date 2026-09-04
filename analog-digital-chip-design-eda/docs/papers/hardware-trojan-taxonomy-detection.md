# A Survey Of Hardware Trojan Taxonomy And Detection

## Bibliographic Identity

- Title: A Survey of Hardware Trojan Taxonomy and Detection
- Year: 2010
- Source: https://www.computer.org/csdl/magazine/dt/2010/01/mdt2010010010/13rRUzpzeJ5
- Track: manufacturing-packaging-and-yield
- Subtheme: hardware security and malicious modification detection

## First-Principles Reading

The object being controlled is trust in the implemented hardware. A chip can match its expected function under normal tests while containing malicious logic that activates only under rare conditions.

The constraint is hidden alteration. A hardware Trojan can be inserted during design, IP integration, fabrication, or test. It may be small, dormant, and hard to activate accidentally. Process variation can also mask side-channel evidence.

The mathematical form is taxonomy over threat dimensions: insertion stage, physical form, activation trigger, payload action, and observable effect. Detection then becomes a question of which evidence can expose which class of alteration.

The concrete method is to classify hardware Trojans and survey detection techniques, including logic testing and side-channel analysis. The paper gives the field a vocabulary for matching threat models to evidence.

The evidence artifact is the taxonomy itself plus the comparison of detection approaches and their limits. For this corpus, it connects verification, manufacturing variation, and security into one trust problem.

The failure boundary is incomplete activation or observation. A detector can miss a Trojan if the trigger is rare, the payload is subtle, side-channel noise is high, or the assumed threat model is too narrow.

## Concept Links

- `verification-is-evidence-implementation-matches-intent`
- `yield-is-probability-over-manufacturing-variation`
- `noise-is-uncertainty-at-the-signal-boundary`

## What The Paper Teaches

The deeper lesson is that manufactured correctness is not only about defects. It is also about adversarial changes that are designed to survive ordinary evidence.

