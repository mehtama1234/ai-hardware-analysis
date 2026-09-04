# Sky130 Transistor Handoff Decomposition

This page separates the current transistor handoff failure into smaller facts.

The goal is simple: avoid guessing. If the frontend alone fails, fix the frontend. If the transistor input pair alone fails, fix the input pair. If both pass separately but fail together, debug the combined handoff.

The current evidence points to the third case.
