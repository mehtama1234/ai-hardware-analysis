# Sky130 Corrected-Convention Capacitive Isolation Confirm

The direct latch connection moved the sampled nodes too much. The corrected latch output convention by itself did not solve that.

This page appends a narrower coupled ngspice result: tiny capacitive isolation between the sampled nodes and the latch input gates. It confirms whether the isolated input can read both signs while keeping sampled-node movement under the 12-bit half-LSB line.
