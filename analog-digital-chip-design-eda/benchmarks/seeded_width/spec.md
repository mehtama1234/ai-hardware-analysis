# Seeded width adapter benchmark

After reset, the adapter exposes the low nibble of the input byte.

REQ-WIDTH-LOW-NIBBLE: data `8'hA5` produces `low=4'h5`.

The RTL intentionally exposes the high nibble.
