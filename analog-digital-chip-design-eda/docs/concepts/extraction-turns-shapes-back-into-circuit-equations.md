# Extraction Turns Shapes Back Into Circuit Equations

Extraction reads the drawn layout and turns it back into electrical quantities. It is the step where geometry becomes circuit behavior again.

The object being controlled is the gap between intended circuit and physical circuit. The schematic or netlist contains idealized devices and connections. The layout contains wires, vias, spacing, coupling, resistance, and capacitance.

The constraint is that every physical shape has electrical side effects. A long wire has resistance and capacitance. Nearby wires couple. Vias add resistance. Diffusion and well regions add parasitic devices. These effects can be small individually and large together.

The mathematical shape is an expanded circuit model:

```text
drawn_layout -> devices + R + C + coupling + parasitic elements
```

After extraction, timing and analog behavior are no longer based on guessed load. They are based on what was actually drawn.

The concrete design move is to use extracted parasitics to repair the design. Designers resize cells, add buffers, change routes, shield nets, widen wires, move blocks, improve matching, or revise compensation after seeing the extracted behavior.

The measurement is post-layout simulation, post-route timing, parasitic reports, crosstalk reports, resistance/capacitance totals, and differences between pre-layout and post-layout behavior. For analog circuits, post-layout simulation can change gain, phase margin, noise, offset, and settling.

Extraction also changes accountability. Before extraction, a failure can be blamed on estimates. After extraction, the drawn geometry has made a more specific claim: these wires, vias, spacings, and devices create this electrical circuit. That is why signoff uses extracted views.

The failure mode is trusting pre-layout results after physical design. The circuit that gets manufactured is the extracted circuit, not the clean schematic. Extraction is how the design admits what the layout actually built.
