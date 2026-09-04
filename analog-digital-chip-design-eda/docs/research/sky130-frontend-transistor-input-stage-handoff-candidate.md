# Sky130 Frontend Transistor Input-Stage Handoff Candidate

This page replaces the active gain macro with a Sky130 transistor input stage.

The frontend is still the extracted ultra-sense capacitance network. The next block is no longer an ideal gain macro. It is a schematic-level Sky130 nfet differential input pair connected to the frontend sense nodes through finite gate paths.

This is the next proof rung. If it passes, the project has shown that the extracted frontend can drive real transistor input devices while preserving sign and creating enough output difference for the next latch test. It still does not prove latch behavior, SAR conversion, full energy, full noise, full area, or accepted post-layout converter evidence.
