# Register peripheral workbench

The bus wrapper accepts a write when `valid && write` is asserted. Address zero
updates `control`; writes to other addresses are ignored. Reset clears control
and the wrapper keeps `ready` low while reset is asserted.

REQ-CSR-RESET: control is zero while rst is asserted.
REQ-CSR-ADDRESS: a write to a nonzero address does not change control.
REQ-CSR-WRITE: a write to address zero stores wdata in control.
REQ-CSR-READY: ready is zero while rst is asserted.

The register implementation intentionally ignores the address on writes. The
hierarchical testbench exposes the defect through the bus wrapper.
