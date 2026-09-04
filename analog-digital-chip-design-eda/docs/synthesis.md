# First-Principles Synthesis: From Charge To Manufactured Logic

Chip design is one chain of preservation. The designer starts with a desired behavior and must preserve it while translating through physics, circuits, logic, geometry, manufacturing, and test.

The first object is charge. Current moves charge. Voltage is the state created by where charge sits. Capacitance decides how much charge is needed to move a node. Resistance and device strength decide how quickly it can move. This is why speed, power, and noise are connected before any digital abstraction appears.

Analog design lives close to this physical layer. It controls continuous quantities: voltage, current, gain, bandwidth, noise, phase, and offset. A transistor is useful because voltage at one terminal controls current through another path. Transconductance measures that local control. Feedback spends raw gain to make the circuit less dependent on uncertain device behavior. Stability asks whether correction shrinks error over time. Bandwidth asks how fast the circuit can move stored charge without losing control.

Digital design is built by making voltage behave like a symbol. A gate receives a messy physical voltage and restores it into a valid low or high range. A flip-flop turns that restored signal into timed state. The clock does not make logic correct by itself. It creates deadlines. Timing closure proves that each value arrives before the receiving memory element makes its decision and not so early that it corrupts the old one.

Power is the cost of this movement. Dynamic power comes from charging and discharging capacitance. Leakage comes from devices that never turn off perfectly. Delivery loss comes from pushing current through real power networks. Area is the physical budget where all these devices, wires, memories, margins, and test structures must fit.

EDA is the set of translations that tries to keep the intended behavior true while the representation changes. RTL becomes gates. Gates become placed cells. Placed cells become routed wires. Routed wires become an extracted circuit with resistance, capacitance, coupling, and parasitic devices. Verification gathers evidence that each translation preserved the right claim.

The central failure is false preservation. A design can be correct as an equation and fail as a circuit. It can be correct as RTL and fail after placement. It can route cleanly and fail timing. It can pass typical simulation and fail across process variation. It can work once and fail yield because too few manufactured copies meet the requirements.

The first-principles map is therefore:

```text
charge -> voltage/current -> analog control -> digital symbol -> timed state
      -> physical geometry -> extracted circuit -> verified manufactured chip
```

Each arrow is a claim. Each claim needs a measurement. A serious chip-design workflow asks what object is being preserved, what constraint threatens it, what design move changes it, and what evidence proves it survived the next translation.

