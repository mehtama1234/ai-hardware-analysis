# AI For EDA Is A Checked Design Loop

AI for EDA is useful when it changes a design loop that already has a checker. A model that writes plausible RTL, suggests placement, or explains timing logs is not enough. The value comes from coupling generation to evidence.

The object being controlled is engineering uncertainty. The designer needs to know whether the next action is likely to move the design toward a correct, timed, powered, manufacturable chip.

The constraint is that chip design has many local traps. A change can fix one failing path and break another. A generated assertion can miss the important state. A placement suggestion can reduce wire length while hurting congestion. A repaired design-rule violation can alter matching or parasitics.

The mathematical shape is search with checked feedback:

```text
candidate -> tool/checker -> error signal -> next candidate
```

The checker may be a compiler, simulator, formal tool, timing analyzer, DRC engine, LVS engine, SPICE run, or human review. Without a checker, the model's output is only a guess.

The concrete design move is to put the model inside a narrow loop. For RTL, the loop can be generate, compile, simulate, inspect failing trace, repair. For analog sizing, it can be choose parameters, run SPICE, compare metrics, propose the next point. For physical design, it can be inspect congestion or timing, propose a constrained edit, rerun the flow.

The measurement is improvement in checked artifacts: fewer compile errors, more passing assertions, better slack, fewer DRC violations, better sizing metrics, shorter debug time, or lower search cost for the same design target.

The failure mode is treating text as design evidence. Chip design does not reward fluent explanations unless the generated action survives the toolchain.

