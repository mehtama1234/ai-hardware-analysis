# Transformer Tile Scheduling

Analog in-memory compute becomes useful only after a tensor can be scheduled through tiles without spending more on movement and conversion than it saves on multiplication.

The object is a projection:

```text
y = Wx
```

For a transformer, the most important projections are Q/K/V, attention output, MLP up, and MLP down. These are attractive because the weights are large and reused many times. The constraint is that one crossbar tile is much smaller than a full model matrix. A large projection must be cut across row tiles and column tiles.

For a `4096 -> 16384` MLP-up projection with `128 x 128` tiles:

```text
row tiles = 4096 / 128 = 32
column tiles = 16384 / 128 = 128
total tiles = 4096
```

Each output block needs partial sums from 32 row tiles. That means the analog array does not remove accumulation. It moves part of multiplication into the conductance array and leaves a digital accumulation problem behind.

## What Must Be Scheduled

The scheduler must decide:

- which activation block feeds which tile
- when DACs convert that activation block into row voltages
- when ADCs read column currents
- where partial sums wait
- when digital accumulation and correction run
- when the final output returns to the model stream

This is why the architecture is hybrid by nature. The analog tile is not the whole machine. It is a dense-projection unit inside a digital schedule.

## KV Cache Boundary

The KV cache is different from a stored weight matrix. It grows with generated tokens. It is read according to sequence position and attention pattern. It is not a fixed conductance array that can simply sit in place across many requests.

For long-context inference, the KV cache can become the dominant memory object. Analog projection may reduce weight movement while the KV cache still forces large digital memory traffic. Any claim about foundation-model acceleration must say whether it helps prefill, decode, or both.

## Tile Size Trade

Larger tiles reduce the number of partial sums and boundary crossings. They also increase analog error sources: longer wires, larger current range, slower settling, and harder calibration. Smaller tiles are easier to control but require more digital accumulation and more scheduling overhead.

The design move is not "make the tile as large as possible." The design move is to find the largest tile whose physical errors can still be measured, corrected, and tolerated by the model layer.
