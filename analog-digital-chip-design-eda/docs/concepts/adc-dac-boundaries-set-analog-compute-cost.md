# ADCs And DACs Set The Cost Of Analog Compute

The object is the boundary between numbers and physical signals. A transformer stores activations and weights as digital values. A crossbar consumes row voltages and produces column currents. A DAC turns an input number into a voltage. An ADC turns an output current or voltage back into a number. Analog compute can reduce the cost of multiplication, but it cannot remove the cost of entering and leaving the analog domain.

The constraint is precision. Every extra conversion bit asks the circuit to distinguish smaller differences. That usually costs area, time, and energy. If the ADC has too few bits, many different column currents collapse to the same code. If the DAC has too few bits, the input vector is already damaged before the crossbar computes. If the converters are too accurate, their cost can dominate the array and erase the advantage of analog multiplication.

The mathematical shape is quantization:

```text
x_digital -> DAC -> x_voltage = scale * quantize(x_digital)
I_column = G_actual * x_voltage
I_column -> ADC -> y_digital = quantize(I_column)
```

The useful question is not whether the crossbar can multiply. The useful question is how many bits the model needs at each boundary. A projection layer may tolerate lower precision if later normalization, residual paths, or fine-tuning absorb the error. A logits layer may be more sensitive because small changes can alter the next-token distribution. Precision is therefore not a generic hardware number. It is a property of a layer inside a model.

The concrete design move is mixed precision. Use low-bit DACs for inputs when activation quantization is tolerable. Use enough ADC bits to preserve the partial-sum range. Accumulate across tiles digitally with more precision. Keep fragile operations such as normalization, softmax, sampling, and control flow digital. Calibrate column gains so the ADC code maps back to the intended numerical scale.

The measurement is an energy-error curve. For each ADC bit count and DAC bit count, measure layer-output error and estimated conversion cost. Then compare against a digital baseline. A serious experiment should show the point where increasing converter precision stops improving model behavior enough to justify its cost. It should also show the point where reducing precision breaks the computation.

The failure mode is saying "analog is efficient" while hiding conversion. If every token requires many high-resolution conversions, the accelerator may spend more energy proving analog outputs than it saves by producing them. If conversion latency is longer than digital matrix multiply latency for the chosen batch and sequence length, the array is not the bottleneck solution. The boundary is where analog compute becomes a system, and that boundary must be measured before claiming an advantage.
