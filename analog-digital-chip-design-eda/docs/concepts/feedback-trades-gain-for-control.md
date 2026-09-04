# Feedback Trades Gain For Control

Feedback sends part of a circuit's output back to its input. The point is to make the circuit less dependent on the raw behavior of its devices.

The object being controlled is error between the desired output and the actual output. A feedback loop measures that error indirectly and drives the circuit so the error becomes smaller.

The constraint is delay. Feedback can correct only after the circuit senses a difference, amplifies it, and sends a correction through the loop. If the correction arrives with too much phase lag at a frequency where loop gain is still high, the loop can ring or oscillate.

The mathematical shape is closed-loop gain:

```text
closed_loop_response = forward_gain / (1 + loop_gain)
```

When loop gain is large and stable, the response is set more by the feedback network than by the uncertain forward amplifier. This is the trade: open-loop gain is spent to get accuracy, linearity, bandwidth control, or lower sensitivity.

The concrete design move is to choose what is fed back, how much is fed back, and where the dominant pole sits. Designers compensate amplifiers, choose feedback resistors or capacitors, set bias currents, and place poles and zeros so the loop corrects errors without creating a larger time-domain error.

The measurement is loop gain, phase margin, gain margin, settling time, overshoot, distortion, output impedance, and closed-loop accuracy. A feedback circuit must be checked in frequency and time because stability and settling are the same physical problem seen from two views.

The failure mode is assuming feedback is automatically good. Feedback can hide device error, but it can also amplify noise, reduce headroom, oscillate, recover slowly from saturation, or become unstable under load.

