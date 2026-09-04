# Sky130 Transistor DAC PVT Calibration Policy

This page turns the measured transistor-switched capacitor DAC results into a controller decision. It asks a narrow question: can calibration make the DAC accurate enough for the analog SAR at each tested operating point?

The current answer is no. The policy is deliberately conservative: an operating point may use analog SAR service only when the required calibration codes are measured, the measured transfer is within the half-LSB limit, and an endpoint gain/offset correction also leaves the midscale check within the half-LSB limit.

The generated evidence report is appended below.
