# SAR ADCs Turn Current Into A Timed Digital Decision

The object is a digital code that stands for an analog value. In analog in-memory compute, a column current is not useful to the rest of a foundation-model accelerator until it becomes a number. A successive-approximation ADC does this by making a sequence of comparisons. It does not discover all bits at once. It asks one yes/no question per bit.

The constraint is that every bit costs time and precision. A 6-bit conversion needs enough settling and comparison accuracy to distinguish 64 levels. An 8-bit conversion needs 256 levels. The analog circuit must be quieter, more stable, and more carefully settled as the number of levels grows. This is why "just use more ADC bits" is not a free fix for analog compute error.

The mathematical shape is interval narrowing. Start with a voltage or current range. Try the middle. If the measured signal is above the trial level, keep that bit. If it is below, clear that bit. Repeat with the next smaller step:

```text
range -> compare MSB -> compare next bit -> ... -> final code
```

For a current-sensing crossbar, the current may first be integrated onto a capacitor or converted into a voltage. The SAR logic then searches for the digital code whose reconstructed analog value is closest to that sensed value.

The concrete design move is to put a time budget beside the precision budget. If every column needs an ADC conversion, and every conversion needs one comparison per bit, then a tile with many columns may need many comparators, slower conversion, multiplexing, or lower resolution. Each choice changes area, energy, and throughput. A foundation-model accelerator cannot treat ADC precision as a software setting. It is a circuit and schedule decision.

The measurement is conversion error versus bit count and comparator noise. A useful experiment should sweep the number of bits and show two limits. First, quantization error falls as bit count rises. Second, comparator noise and analog settling eventually stop the improvement. After that point, adding bits creates codes that look more precise than the signal actually is.

The failure mode is to use high ADC precision to repair every analog imperfection. If the crossbar output is noisy, drifting, or wire-corrupted, more ADC bits may only digitize the wrong value more carefully. The right boundary is measured: enough bits to preserve the useful signal, not so many bits that conversion becomes the accelerator.
