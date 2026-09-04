# Noise Is Uncertainty At The Signal Boundary

Noise is unwanted uncertainty added to the signal. It matters because every circuit eventually has to decide whether a voltage or current means one state rather than another.

The object being controlled is the separation between useful signal and unwanted variation. A circuit is usable when the signal movement is large enough compared with the random movement that rides on top of it.

The constraint is that devices and resistors generate noise because charge is carried by discrete particles and because thermal energy keeps disturbing those particles. A larger resistor, a smaller current, a narrower bandwidth, or a smaller device can all change the noise seen by the next stage.

The mathematical shape is often a ratio:

```text
SNR = useful_signal_power / noise_power
```

For many circuits, noise accumulates over bandwidth. If the circuit accepts more frequency content, it also accepts more noise power. This is why filtering and bandwidth are part of noise design, not separate cleanup steps.

The concrete design move is to decide where uncertainty is allowed to enter and where it must be reduced. A designer can increase signal swing, add gain before a noisy stage, reduce bandwidth, enlarge devices, increase bias current, filter the input, or change the architecture so a sensitive node sees less noise.

The measurement is input-referred noise, output noise, integrated noise over bandwidth, SNR, jitter, bit error rate, or effective number of bits. The right measurement depends on the decision the circuit must support.

The failure mode is measuring only the average behavior. A circuit can have the right gain and the right bandwidth while still failing because the signal and noise overlap too often at the decision boundary.

