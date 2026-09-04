# Sky130 Transistor Handoff Replacement Work Order

This page defines the next physical replacement after the active-macro handoff passes.

The active-macro deck proves that the extracted frontend signal can flow into a gain stage in one same-deck run. The macro is still ideal. It does not load the frontend like real transistor gates, does not need bias current, and does not prove transistor operating point.

The next task is to replace that macro with a Sky130 transistor input stage while keeping the same four frontend cases and the same acceptance tests.
