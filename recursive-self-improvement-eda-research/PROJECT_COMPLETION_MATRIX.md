# Recursive hardware-free converter project matrix

| Requirement | Evidence | Current state |
|---|---|---|
| Transistor models execute reproducibly | `transistor-probe.json` | Passed with repaired Sky130 compatibility bundle |
| Multi-bit transistor topology | `transistor-3bit-readout-pvt.json` | 3 bits, TT/SS/FF, all logic contracts pass |
| Converter code transfer | `transistor-3bit-dac-pvt.json` | 8 codes, monotonic and settled at all corners |
| PVT robustness | DAC and current-mode PVT artifacts | TT/SS/FF measurements recorded |
| Calibration path | `transistor-dac-calibration.json` | LUT generated; true INL gate fails |
| Recursive cost decision | `transistor-policy-bridge.json` | Fail-closed when INL exceeds 0.5 LSB |
| Held-out workload application | `transistor-policy-workload-application.json` | 36 cases, currently all digital fallback |
| Mutation memory | `transistor-dac-inl-work-order.json` | R-2R, thermometer, degeneration, and cascode outcomes retained |
| Circuit improvement search | sizing/current-mode/cascode search artifacts | Current-mode improves INL to 2.94 LSB |
| Differential correction linearization | Gate-bias, cascode, passive/active feedback, group-bias reports, width/finger refinements, and PVT provenance | Finger refinement reaches the current simulator best of 0.7394457 LSB; it remains above the 0.5 LSB gate and is not runtime-promotion evidence |
| Recursive search-method comparison | `recursive_search_experiment.json` plus three hash-bound round reports and ledgers | Learned, heuristic, and random compared over 3 adaptive rounds; all 18 candidates safe, 0 meet the 0.5 LSB promotion gate |
| Hardware-free claim boundary | final manifest and research status | No silicon, board, yield, or production claim |

The project is end-to-end and fail-closed, but not complete as an analog
replacement: the strict INL gate, common-unit runtime-cost evidence, and
physical-board validation remain unsatisfied. The next authorized action is
synchronized digital/hybrid cost import; a new circuit mutation must remain
bounded and hash-bound, then cross the 0.5 LSB gate before any analog runtime
promotion.

The separate recursive converter-search pilot is complete as an experiment,
not as an analog replacement: learned search had the lowest mean safe INL in
three rounds against the heuristic and in two rounds against random search,
but every measured candidate remains above the promotion threshold. The
runtime stays fail-closed; independent adaptive trajectories and physical
board evidence remain open requirements.

Current-mode branch evidence is also available: binary-weighted NMOS current sinks
with a diode-connected PMOS load are monotonic and settled across PVT, with
 measured INL improving to 2.94 LSB with 1u/5u/100u NMOS widths, a 100u load, and 1.0V input drive. This is the strongest
measured direction, but it remains below the analog promotion threshold.

| Input-drive robustness | `current-mode-drive-margin-sweep.json` plus standalone verifier | 1.0/1.2/1.5 V high drive passes TT/SS/FF monotonicity and settling; INL remains above promotion gate |
