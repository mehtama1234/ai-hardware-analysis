# Sky130 Bottom-Plate Cell

This page publishes the isolated one-bit bottom-plate transistor-cell experiment. The generated measurements are appended below. A timeout is recorded as a circuit or simulation failure, not treated as a missing pass.

The fixture was rerun with explicit top and bottom leakage paths, Gear
integration, tighter voltage/charge tolerances, and deterministic non-`uic`
startup. It still timed out in all `4/4` cases. The failure therefore persists
after a solver-initialization check and remains a cell/control-topology issue,
not evidence of a working bottom-plate switch.
