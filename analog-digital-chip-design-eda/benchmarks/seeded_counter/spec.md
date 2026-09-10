# Seeded counter benchmark

`counter_q` resets to zero on `rst`, increments by one on each rising clock edge
when `enable` is high, and holds its previous value when `enable` is low.

REQ-COUNTER-RESET: counter_q is zero while rst is asserted.
REQ-COUNTER-ENABLE: counter_q increments only on a rising edge with enable high.
REQ-COUNTER-HOLD: counter_q holds its previous value when enable is low and rst is released.

The RTL intentionally contains one seeded defect: it increments whenever reset is
released, regardless of `enable`. The testbench assertion exposes that defect.
