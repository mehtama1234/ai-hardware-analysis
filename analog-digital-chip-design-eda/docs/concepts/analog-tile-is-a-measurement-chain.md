# An Analog Tile Is A Measurement Chain

The simple story says an analog tile computes a matrix multiply.

That is true, but it is not the useful engineering statement.

The useful statement is this: an analog tile turns a trained dot product into a physical measurement chain. Each link in that chain can change the number. The digital side is responsible for deciding whether the final measured number is still allowed to become model state.

## The Object

The object is one projection output:

```text
y = w0 x0 + w1 x1 + w2 x2 + ...
```

In software, that is just arithmetic. In an analog tile, the same expression becomes a sequence of physical acts:

```text
activation code
-> row voltage
-> cell current
-> column current sum
-> ADC code
-> corrected digital value
-> accepted or refused model update
```

The tile is not only the crossbar. The tile is the whole chain from input code to accepted output.

This matters because the trained model does not consume current. It consumes numbers. The analog path is useful only if the measured current can be turned back into a number with small enough error for the layer that will use it next.

## The Constraint

The constraint is preservation across representation changes.

The same projection must survive several translations:

```text
number
-> voltage
-> current
-> code
-> corrected number
```

Each translation can preserve the broad computation while damaging the exact value. The array can still be physically working while the model update is no longer safe. That is why the measurement chain must expose the size and cause of the error, not only the final output.

## The First Boundary: Sign

A passive conductance is nonnegative. It can be larger or smaller, but it cannot be negative.

A trained weight can be negative.

So a signed weight needs a representation rule:

```text
w = w_positive - w_negative
```

The tile implements that with two ordinary conductance paths:

```text
I_positive = G_positive V
I_negative = G_negative V
I_signed = I_positive - I_negative
```

This is not a detail. It says the signed model value is already a difference between two measured physical quantities. If the positive and negative sides drift differently, the subtraction is wrong even when both sides are individually valid conductances.

## The Second Boundary: Row Voltage

The model thinks one activation value is broadcast to every cell in a row.

The circuit does not do that exactly. A row wire has resistance. As current leaves the row through earlier cells, the voltage farther down the row falls.

So the logical value:

```text
x_i
```

becomes a position-dependent physical value:

```text
V_i(position)
```

That changes the dot product before the ADC sees anything. The far cells multiply by a smaller voltage than the near cells. This is why the row-wire experiment matters: it measures how much of the error is caused by the path that carries the activation, not by the weight cell or the converter.

## The Third Boundary: The DAC

The DAC changes the input before multiplication.

That is different from rounding the output. If one activation is rounded by the DAC, every weight connected to that activation inherits the same input error.

The shape is:

```text
x_i -> quantized(x_i) -> V_i
```

The error is shared across columns. That can create correlated movement in the projection output. More DAC bits reduce the movement, but they cost area, energy, and time. The right question is not "how many bits are good?" The right question is "how few bits can this layer tolerate before the next model state changes too much?"

## The Fourth Boundary: Stored Conductance

The trained weight is a number in a file.

The stored analog weight is a conductance that was programmed into a cell:

```text
G_actual = G_target + programming_error + drift
```

That conductance must be measured again over time. Calibration is the act of asking what the cell has become, not the act of making the cell perfect.

This distinction is important. If the conductance moves slowly, the tile can still be useful with periodic calibration. If it moves unpredictably or differently across columns, the digital correction may not be enough. The governor should see that as residual error, stale calibration, or repeated fallback.

## The Fifth Boundary: The ADC

The ADC turns column current into a code:

```text
I_column -> adc_code
```

This is where information can disappear. Two different currents can map to the same code. A saturated current can hit the end of the ADC range. Comparator noise can move a decision across a threshold.

The output code is not model state yet.

It becomes a candidate value only after digital correction:

```text
centered = adc_code - zero_code
corrected = gain * centered + bias
```

Then the digital side must decide whether to accept it.

## The Governor View

The governor should not receive a vague claim that the tile computed.

It should receive evidence:

```text
residual_q8
drift_age
sensitivity_q8
saturation
tile_health_action
cumulative_error_q8
```

These fields answer different questions.

`residual_q8` says how far this measured value is from the ideal value under the current model of the tile.

`drift_age` says how old the calibration evidence is.

`sensitivity_q8` says how dangerous error is for this model path.

`cumulative_error_q8` says how much accepted analog error has already entered the current state.

The key point is that the governor is not judging analog compute in the abstract. It is judging one measured value at one moment.

## What The Nonideality Stack Shows

The current lab measures this chain in `analog-nonideality-stack.md`.

One projection starts with zero error in the ideal digital dot product. The signed-conductance stage still has almost zero error because it is only a representation change. Row drop adds the first physical loss. DAC quantization moves the input before multiplication. Programmed conductance and drift move the stored weights. ADC quantization turns the final current into a code.

The final value in the current operating point is:

```text
final_relative_residual: 0.09000
final_residual_q8: 12
```

That is not a universal accuracy claim. It is a measured statement about one chosen tile operating point:

```text
ADC: 6 bits
DAC: 4 bits
row segment case: 100 ohm
SPICE row-drop loss: 6.93 percent
converter energy: 3.22x
```

The result is useful because it gives the digital control plane something concrete to spend or refuse.

## The Concrete Design Move

Design the analog tile report as a ledger, not as a single output number.

For each operation, record:

```text
ideal value
signed-conductance value
row-drop value
DAC-damaged value
programmed-and-drifted value
ADC-read value
corrected value
accept or fallback decision
```

This makes the boundary visible. If the output is bad, the system can tell whether the cause was row wiring, converter precision, stored conductance drift, saturation, or model-path sensitivity.

That is the core rule:

```text
Analog compute is useful only when its measurement chain is visible enough for digital control.
```

Without that chain, the chip only has an analog answer. With that chain, the chip has a measured answer, a reason code, and a controlled way to decide whether the answer should matter.

## The Failure Mode

The failure mode is to report the crossbar current as if it were already the model value.

That skips the parts that can break the claim:

```text
signed representation mismatch
row-voltage loss
DAC rounding before multiplication
conductance programming error
drift since calibration
ADC rounding or saturation
model-path sensitivity
```

If those terms are hidden, the design cannot explain why one analog output should be accepted and another should be refused. The result may look like a working accelerator while the model is quietly receiving damaged state.

The stronger habit is to make each boundary measurable. Then a failed output is not just bad. It has a cause, a size, and a repair path.
