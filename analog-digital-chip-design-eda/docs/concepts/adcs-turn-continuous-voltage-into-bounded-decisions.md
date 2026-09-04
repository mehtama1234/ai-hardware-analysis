# ADCs Turn Continuous Voltage Into Bounded Decisions

An analog-to-digital converter turns a continuous input voltage into a digital code. It is a controlled decision process, not a magic boundary between analog and digital worlds.

The object being controlled is quantized representation. The converter must decide which finite code best represents an input that could lie anywhere in a continuous range.

The constraint is that finite codes create finite bins. If an ADC has `N` bits, it has `2^N` output codes. The input range is divided into intervals, and every value inside an interval maps to the same code.

The mathematical shape is quantization:

```text
code = round(input_voltage / step_size)
step_size = full_scale_range / 2^N
```

That step size creates quantization error. Real ADCs add more error through thermal noise, comparator offset, reference noise, aperture jitter, capacitor mismatch, finite amplifier settling, and nonlinear decision thresholds.

The concrete design move is architecture selection. A flash ADC spends many comparators for speed. A SAR ADC uses a binary search with a DAC and comparator. A pipeline ADC splits conversion across stages. A sigma-delta ADC oversamples and shapes noise. Each architecture chooses a different trade among speed, resolution, power, area, latency, and calibration.

The measurement is effective number of bits, signal-to-noise-and-distortion ratio, integral nonlinearity, differential nonlinearity, missing codes, sampling rate, latency, power, and input bandwidth.

The failure mode is thinking an ADC simply records the truth. It records a bounded decision under noise, timing error, reference quality, and circuit mismatch. The code is useful only when those error sources are small enough for the system's purpose.

