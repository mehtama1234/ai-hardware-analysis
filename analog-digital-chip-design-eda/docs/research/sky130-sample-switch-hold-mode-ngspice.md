# Sky130 Sample Switch Hold Mode Ngspice

This page records a Sky130 MOS sample-switch hold-mode run.

The on-state sample-switch page asks whether the sample node can follow the input while the switch is on. This page asks the next question: after the switch turns off, how much does the held voltage move?

That matters because an ADC does not only need a voltage to arrive. It needs the voltage to stay stable while the decision is made. This is still not a full ADC proof. It only measures one starter switch-and-capacitor hold path with Sky130 transistor models.

