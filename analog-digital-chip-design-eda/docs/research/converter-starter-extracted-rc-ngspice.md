# Converter Starter Extracted RC Ngspice

This page records the first ngspice transient run that uses the extracted starter macro capacitance network from Magic.

The generated evidence below is stronger than a hand estimate because SPICE solves voltage over time through the extracted capacitances and named driver/load resistors. It is still not a converter proof. The extracted starter macro does not contain transistor DAC switches, a SAR comparator, a reference ladder, mismatch, noise, or supply-current integration.

