# Seeded handshake benchmark

`ready` must be low during reset and may become high after reset is released.

REQ-HS-RESET: ready is zero while rst is asserted.

The RTL intentionally drives ready high regardless of reset.
