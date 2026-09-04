# Analog Compute Is A Boundary Chain

The object is not a multiply. The object is a value that must survive a chain of physical translations. A digital model begins with stored numbers. An analog in-memory machine begins by turning some of those numbers into device states and voltages. It then lets physics produce a current, turns that current back into a number, corrects it, and passes it to the next model operation.

The chain is:

```text
weight code -> programmed device -> row voltage -> current sum -> sensed value -> ADC code -> corrected digital value
```

Every paper in the analog in-memory foundation-model set is really about one part of this chain.

The IBM analog-AI chip paper makes the device-to-chip chain visible. A phase-change memory cell can hold conductance, but a useful chip must coordinate many such cells across tiles. The evidence is not the equation `I = GV`. The evidence is that the measured chip still runs a neural task with useful accuracy and throughput after programming, readout, peripheral circuits, and communication are counted.

The Analog Foundation Models paper moves the boundary into training. It starts from the fact that pretrained language models were not trained to survive analog noise and low-precision input/output constraints. Its concrete move is to adapt the model so the hidden states tolerate the analog path. That means the model itself becomes part of the control loop around the hardware.

The transformer-adaptation paper makes the digital correction path explicit. Dense projections can be assigned to AIMC, while compact digital adapters repair some of the mismatch. The key idea is not that analog replaces digital. The key idea is that analog performs the large approximate operation and digital logic handles a smaller correction, provided the error has a shape the adapter can cover.

The analog-attention paper changes the object again. Attention is not only a fixed matrix. It uses token-dependent memory that is written during generation. That means the boundary is not just programming a weight once. The machine must write, retain, read, and compare changing state. This is why KV-cache behavior resists a simple static-crossbar story.

The compute-in-memory LLM survey provides the workload boundary. It reminds us that LLM inference has prefill, decode, projections, attention, cache movement, normalization, and sampling. These parts stress different machines. A design can win on dense projection and still lose when cache traffic or conversion dominates.

AIHWKit gives the simulation boundary. It lets us test model behavior under device-like noise before silicon is available. But simulation is not proof unless its errors are traceable to device and circuit assumptions. Otherwise it becomes an idealized model with analog vocabulary.

The constraint tying all of these papers together is preservation. The analog machine is useful only if the value that leaves the boundary is still close enough to the value the model needed. This is not one scalar error. It includes conductance error, row-voltage error, wire drop, ADC error, digital scaling error, and layer-level sensitivity.

The mathematical form is a perturbed layer:

```text
h_next = f(readout((G_target + delta_G) * DAC(h + delta_h)) + delta_adc + correction)
```

This expression is useful because it names where error enters. `delta_G` comes from programming, drift, and device variation. `delta_h` comes from input quantization and DAC behavior. `delta_adc` comes after summation. `correction` is digital evidence applied after measurement. The layer is not wrong merely because these errors exist. It is wrong when the errors move the model state outside the tolerance of the next operation.

The concrete design move is to assign each boundary a measurement. Conductance gets target-versus-measured programming error. Row inputs get DAC-bit and settling sweeps. Wires get voltage-drop sweeps. ADCs get bit-count and comparator-noise sweeps. Calibration gets before/after output error. Architecture gets tile count, partial-sum count, and memory traffic. Model adaptation gets benchmark loss or accuracy under the measured-like error.

The failure mode is a claim that begins and ends with "matrix multiplication in memory." That phrase hides almost everything that matters. It hides signed-weight representation. It hides DACs and ADCs. It hides tile scheduling. It hides cache movement. It hides the digital correction path. It hides whether the final logits changed.

The first-principles claim is narrower and more useful: analog compute can help when the chain has a measured advantage after every boundary is counted. The array must save enough weight movement and multiply energy to pay for conversion, correction, communication, and calibration. The model must tolerate the remaining error. The system must say which operations stay digital. Only then is the analog current sum part of a working foundation-model machine.
