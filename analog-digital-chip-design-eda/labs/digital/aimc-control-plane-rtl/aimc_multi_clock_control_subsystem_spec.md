# AIMC multi-clock control subsystem contract

This is the first requirement contract for the canonical digital block used by
the local RTL-to-GDS/STA handoff. It is intentionally small and explicit. It
does not claim to be a complete product specification for the analog tile.

## Requirements

### REQ-CDC-001: maintenance budget crossing

The asynchronous maintenance budget input shall be sampled in the maintenance
clock domain and synchronized into the core clock domain with a two-stage
register synchronizer. The synchronized value is exposed as
`maintenance_budget_core`.

### REQ-CTRL-001: core input registration

The control-plane inputs used by the micro-tile controller shall be registered
on `core_clk` and reset to known values when active-low `rst_n` is asserted.

### REQ-GOV-001: bounded scheduler decision

For a valid analog candidate with an enabled, healthy requested tile and
acceptable error conditions, the scheduler shall produce the analog decision
and selected tile according to the governor policy.

### REQ-READOUT-001: accepted execution result

When a valid sample is accepted by the controller, the execution path shall
report the accepted analog path and expose the corrected result and accounting
counters.

### REQ-RESET-001: deterministic reset

After reset, the synchronized maintenance budget, controller state, scheduler
decision, selected tile, corrected result, and accounting outputs shall be
deterministic before a new valid request is accepted.

## Verification boundary

The current smoke test directly exercises the CDC synchronization and a
nominal analog-acceptance path. The remaining requirements need broader
directed tests and assertions before they can be called fully covered. This
contract therefore records intent and traceability; it does not convert a
single passing simulation into complete verification closure.

