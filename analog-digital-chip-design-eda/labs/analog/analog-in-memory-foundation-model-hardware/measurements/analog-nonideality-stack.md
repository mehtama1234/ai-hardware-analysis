# Analog Nonideality Stack

This report follows one small foundation-model projection through the analog tile boundary. The point is not to show that analog compute is accurate in general. The point is to show where the number changes before the digital governor is allowed to trust it.

The operating point is loaded from `tile-operating-point.csv`: ADC 6, DAC 4, the 100 ohm SPICE row-drop case, and a converter energy cost of 3.22x. The row-drop loss is loaded from the SPICE row-wire measurement instead of being invented inside this script.

## Stage Table

| stage | out0 | out1 | out2 | out3 | residual | relative | q8 | first principle |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| ideal_digital_dot | 0.61000 | -0.45000 | -0.23500 | 0.50500 | 0.00000 | 0.00000 | 0 | A model projection starts as a dot product: each output is a sum of weight times activation. |
| differential_signed_conductance | 0.61000 | -0.45000 | -0.23500 | 0.50500 | 0.00000 | 0.00000 | 0 | A passive cell cannot store a negative conductance, so sign is represented by two nonnegative paths and a subtraction. |
| spice_row_drop_applied | 0.59775 | -0.44133 | -0.22564 | 0.49021 | 0.01153 | 0.02450 | 3 | A row activation is not one voltage everywhere; farther cells see less voltage after current has left through earlier cells. |
| dac_quantized_rows | 0.54178 | -0.41896 | -0.24286 | 0.43993 | 0.04978 | 0.10584 | 14 | The DAC damages the input before multiplication, so one rounded activation perturbs every output column that uses it. |
| programmed_and_drifted_cells | 0.54427 | -0.42371 | -0.24557 | 0.44896 | 0.04545 | 0.09664 | 12 | The stored conductance is a measured physical state, not the exact trained weight; mismatch and drift move the dot product. |
| adc_quantized_column_readout | 0.57143 | -0.44444 | -0.19048 | 0.44444 | 0.04233 | 0.09000 | 12 | The ADC turns current into a code; nearby currents can become the same code and small analog differences can disappear. |

## Governor Input

```text
adc_bits: 6
dac_bits: 4
row_drop_case_ohm: 100
spice_row_drop_loss_pct: 6.93
converter_energy_relative: 3.22
latency_comparisons: 24
final_relative_residual: 0.09000
final_residual_q8: 12
```

## First-Principles Reading

The ideal dot product is the mathematical object the model was trained to use. The analog tile does not directly produce that object. It produces a current made from conductances, voltages, wires, device state, and a readout circuit.

The signed-conductance stage has almost no residual because it is still only a representation change. It says that negative weights require two physical paths and a subtraction. That matters because later mismatch can hit the positive and negative paths differently.

The row-drop stage is the first physical loss. The same input activation is no longer the same voltage at every cell. Cells near the driver and cells farther down the row are multiplying by different voltages, so the dot product is bent before any ADC decision is made.

The DAC stage changes the input before the array. This is different from output rounding. If an activation is rounded before multiplication, all weights connected to that activation inherit the same input error.

The programmed-and-drifted stage changes the stored weight. A trained parameter is a number in software; a cell conductance is a physical state that was programmed, measured, and then allowed to age. This is why calibration is not a footnote. It is the act of remeasuring what the weights have become.

The ADC stage is the trust boundary. Current becomes a code, and the code becomes model state only if the residual is still inside budget. The governor should not ask whether the crossbar multiplied. It should ask whether this measured value is allowed to enter the next transformer layer.
