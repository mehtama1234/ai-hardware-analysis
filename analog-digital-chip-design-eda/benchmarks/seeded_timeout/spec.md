# Seeded timeout benchmark

After a request starts, `timed_out` asserts on the second following clock
edge if no completion is observed.

REQ-TIMEOUT-BOUNDARY: the timeout is high at the second post-start edge.

The RTL intentionally asserts one cycle late.
