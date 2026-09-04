# Verification Is Evidence That Implementation Matches Intent

Verification is the evidence that the implemented design matches the intended design under the conditions that matter. It is not the same as running a few examples.

The object being controlled is uncertainty about correctness. A chip has too many states, paths, interactions, and physical cases to trust informal inspection.

The constraint is state explosion. Digital designs can have enormous numbers of possible states. Analog and mixed-signal designs add continuous values, noise, corners, and layout parasitics. Manufacturing adds variation. Software-driven chips add long sequences of interaction.

The mathematical shape depends on the claim. Simulation samples behaviors. Formal verification proves properties over a state space. Equivalence checking proves two representations preserve function. Static timing proves timing inequalities. DRC and LVS prove physical rule and connectivity claims.

The concrete design move is to choose the right evidence for the claim. A testbench checks scenarios. Assertions check invariants. Formal tools prove bounded or unbounded properties. Coverage measures what has been exercised. Equivalence checking protects synthesis. Signoff checks protect manufacturability and timing.

The measurement is coverage, failing traces, assertion results, proof status, equivalence status, timing slack, DRC/LVS violations, silicon bring-up results, and escaped bug rate. A good verification plan names what is being claimed and what evidence would falsify it.

The failure mode is confusing activity with evidence. Many simulations can miss the important state. A passing unit test can coexist with a broken clock-domain crossing, reset sequence, analog corner, or physical rule violation. Verification is only strong when the evidence matches the claim.

