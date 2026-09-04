# Sky130 Frontend Sense To Transistor OP Handoff

This page checks a narrower handoff after the full extracted-frontend plus real-transistor transient timed out.

It takes the measured sense voltages from the extracted frontend and feeds them as DC inputs into the real Sky130 transistor input pair. This does not prove the full transient handoff. It asks whether the transistor pair has enough steady-state gain and output margin at the voltage the frontend actually produced.
