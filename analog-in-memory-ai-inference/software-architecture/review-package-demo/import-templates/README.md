# Import Templates

These files are example shapes for evidence that a real backend adapter or lab import should provide.

They are not proof. They show what the product should collect before it changes a claim from missing, estimated, or simulated into measured evidence.

Use these templates to wire the next implementation pass:

- `compiler-placement.template.json`: compiler mapping, tiling, bit-slicing, memory placement, and unsupported operators
- `analog-error-simulation.template.json`: analog noise, drift, voltage, temperature, and calibration assumptions
- `board-runtime-trace.template.json`: board load, run status, latency, jitter, firmware, fallback, and failure data
- `power-thermal-report.template.json`: power rail, energy, peak power, temperature, equipment, and sampling data
- `calibration-trace.template.json`: correction profile, weak tiles, monitor readings, pass/fail, and fallback behavior
- `weight-update-report.template.json`: write scope, write energy, write latency, retention, rollback, and post-update accuracy
- `sensor-path-report.template.json`: sensor capture, preprocessing, buffering, synchronization, latency, and input energy
- `task-accuracy-report.template.json`: baseline metric, candidate metric, tolerance, dataset, sample count, and pass/fail

Every filled import should keep raw logs separately and attach a normalized JSON record that the backend can validate.
