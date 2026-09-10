# Seeded register block benchmark

Writes to address zero update `reg0`; writes to other addresses are ignored.
Reads return the addressed register value. Reset clears `reg0`.

REQ-REG-RESET: reg0 is zero while rst is asserted.
REQ-REG-ADDRESS: a write to a nonzero address does not change reg0.
REQ-REG-WRITE: a write to address zero stores wdata in reg0.

The RTL intentionally ignores the address and writes every transaction to
reg0. The testbench exposes the address decode defect.
