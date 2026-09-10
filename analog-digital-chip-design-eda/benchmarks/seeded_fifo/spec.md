# Seeded FIFO benchmark

The FIFO accepts a write when `wr_en` is high and the FIFO is not full, and
accepts a read when `rd_en` is high and the FIFO is not empty. `count` reports
the number of stored entries and must never exceed `DEPTH`.

REQ-FIFO-RESET: count is zero while rst is asserted.
REQ-FIFO-BOUNDS: count never exceeds the FIFO depth.
REQ-FIFO-WRITE: a write increments count only when the FIFO is not full.

The RTL intentionally increments count on every write, including writes while
the FIFO is full. The testbench exposes the overflow defect.
