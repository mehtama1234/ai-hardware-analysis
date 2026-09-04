# Stability Means Disturbances Shrink Over Time

Stability means a disturbance gets smaller instead of larger as time passes. In circuits, it is the difference between correction and self-amplifying error.

The object being controlled is the time evolution of an error. A stable circuit can be bumped away from its operating point and return. An unstable circuit turns the bump into ringing, oscillation, latch-up, or an invalid state.

The constraint is stored energy. Capacitors and inductors remember past voltage or current. That memory creates poles. Multiple energy-storage points can make the output correction arrive late relative to the input error.

The mathematical shape is the location of poles or the loop response around unity gain. In simple terms:

```text
error_next should be smaller than error_now
```

For linearized systems, poles in the stable region mean natural responses decay. In feedback systems, enough phase margin means the correction still points mostly in the direction that reduces error.

The concrete design move is compensation. Designers move poles, add zeros, reduce bandwidth, isolate capacitive loads, add resistance, change device sizes, or split gain across stages. The goal is not maximum speed by itself; the goal is useful speed with controlled error.

The measurement is phase margin, gain margin, damping, settling time, overshoot, ringing, startup behavior, and transient recovery. A circuit can look stable under one load and fail under another because the load changes the poles.

The failure mode is checking only final DC values. A circuit can have a correct operating point and still be unusable because it takes too long to settle, rings through a forbidden voltage range, or oscillates when connected to the real load.

