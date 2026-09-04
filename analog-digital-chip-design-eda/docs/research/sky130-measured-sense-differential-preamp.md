# Sky130 Measured Sense Differential Preamp

This page removes the extracted frontend and tests the differential preamp with measured frontend sense voltages.

The question is narrow: can the preamp bias resolve the tiny sense voltage when that voltage is supplied directly?

If this passes, the preamp idea is locally valid and the next failure is frontend loading. If this fails, the preamp itself needs bias tuning before it is reconnected to the extracted frontend.
