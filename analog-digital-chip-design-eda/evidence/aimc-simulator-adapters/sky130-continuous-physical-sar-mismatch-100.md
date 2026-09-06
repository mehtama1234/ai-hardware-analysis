# Sky130 Continuous Physical SAR Mismatch Sweep

- status: `continuous_sar_mismatch_stress_measured_not_foundry_yield_proof`
- trials: `97/100`
- seed: `130`
- capacitor mismatch model: independent Gaussian perturbations around base scales `[1.0, 0.75, 1.0, 1.0]`, sigma `1.0%`
- full five-conversion code-map passes: `95/100`
- legal bottom-plate passes: `97/100`

## Purpose

Each trial runs the same continuous four-bit, five-conversion physical SAR transient used by the nominal candidate. Only the four binary DAC capacitor scales are perturbed. The seed and sigma are recorded so the exact trial population can be replayed.

## Trial Summary

| trial | scales | status | code map | map pass | bottom legal |
| ---: | --- | --- | --- | --- | --- |
| 0 | 0.99207, 0.74926, 0.99897, 0.98215 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 1 | 0.99873, 0.74874, 1.00057, 1.00907 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 2 | 1.01449, 0.74837, 0.98535, 0.99732 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 3 | 1.01196, 0.75700, 0.99609, 0.99437 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 4 | 0.99346, 0.75601, 1.00927, 0.99738 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 5 | 1.01807, 0.75237, 1.00600, 0.99313 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 6 | 0.99576, 0.72931, 0.98842, 1.00916 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 7 | 0.98795, 0.74722, 0.98126, 0.99546 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 8 | 1.02029, 0.74170, 1.01349, 1.01429 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 9 | 1.00433, 0.75289, 1.00249, 1.00344 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 10 | 0.99566, 0.75130, 0.98063, 1.00811 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 11 | 0.99654, 0.75161, 1.00055, 0.98785 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 12 | 1.00365, 0.75625, 0.99948, 1.01283 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 13 | 1.00567, 0.74775, 0.99270, 1.00304 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 14 | 0.98581, 0.73849, 1.00112, 1.00535 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 15 | 0.99311, 0.75789, 0.98692, 1.00430 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 16 | 1.00155, 0.75906, 1.00820, 1.01044 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 17 | 0.99417, 0.76293, 0.99670, 0.99996 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 18 | 0.99357, 0.74549, 0.99576, 1.00098 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 19 | 0.99604, 0.74483, 1.01045, 1.00347 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 20 | 1.00561, 0.75736, 1.00302, 1.00635 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 21 | 1.00415, 0.75355, 1.00380, 0.99548 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 22 | 0.99143, 0.75743, 1.00295, 1.00538 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 23 | 0.99688, 0.76535, 1.01023, 0.98982 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 24 | 1.00622, 0.75212, 0.99867, 0.99195 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 25 | 1.00662, 0.75432, 1.00545, 0.99673 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 26 | 1.00126, 0.74798, 0.98931, 0.98707 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 27 | 1.01073, 0.75136, 1.01989, 0.98898 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 28 | 0.99413, 0.74749, 0.99409, 1.00542 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 29 | 0.99535, 0.74617, 0.99942, 0.98512 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 30 | 0.99093, 0.75248, 1.00353, 0.99416 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 31 | 0.99674, 0.74929, 1.01099, 1.00305 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 32 | 1.00097, 0.75593, 0.99897, 1.00519 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 33 | 0.99210, 0.75205, 1.01579, 0.98903 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 34 | 0.99455, 0.75072, 1.00858, 0.99724 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 35 | 1.01589, 0.75081, 1.00943, 1.02156 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 36 | 0.99884, 0.75093, 0.99942, 0.99066 | continuous_physical_sar_candidate_measured_not_accepted | 7, 10, 10, 13, 14 | False | True |
| 37 | 1.00254, 0.75217, 0.99596, 0.99852 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 38 | 1.00282, 0.75585, 0.98961, 0.99992 | continuous_physical_sar_failed | not measured | False | False |
| 39 | 0.99274, 0.73589, 1.00668, 0.99472 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 40 | 0.99959, 0.73506, 0.98735, 1.00354 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 41 | 0.99535, 0.74200, 0.97280, 0.99295 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 42 | 0.99771, 0.75146, 0.99677, 1.00487 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 43 | 0.99552, 0.74234, 0.98321, 0.99619 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 44 | 1.00014, 0.74515, 1.02254, 0.98037 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 45 | 1.00171, 0.75353, 1.00366, 1.01363 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 46 | 0.98249, 0.76175, 0.99182, 1.00033 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 47 | 1.00563, 0.75860, 1.00965, 1.00834 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 48 | 0.99799, 0.76156, 0.98926, 1.00051 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 49 | 0.99915, 0.74763, 0.99136, 1.00395 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 50 | 1.00833, 0.74366, 0.99148, 1.01040 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 51 | 1.00231, 0.76218, 1.01182, 0.99566 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 52 | 1.00423, 0.74769, 1.00963, 0.98376 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 53 | 0.98653, 0.76360, 0.98550, 0.99222 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 54 | 1.00394, 0.74577, 1.00149, 1.01914 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 55 | 0.99346, 0.75066, 1.00501, 0.99167 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 56 | 0.99894, 0.76069, 1.00594, 1.01204 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 57 | 0.98796, 0.74747, 0.98735, 0.99937 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 58 | 0.99733, 0.75439, 0.99792, 1.00595 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 59 | 1.00695, 0.75625, 1.01227, 1.00201 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 60 | 1.01943, 0.74835, 0.98440, 1.00389 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 61 | 1.00729, 0.72833, 0.98077, 0.98453 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 62 | 1.00846, 0.75699, 1.01537, 1.00500 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 63 | 0.98836, 0.74114, 1.00050, 1.00544 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 64 | 1.01837, 0.74963, 0.98973, 0.99866 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 65 | 0.99963, 0.74271, 0.99844, 0.99998 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 66 | 0.98967, 0.76072, 1.00625, 1.01122 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 67 | 0.99272, 0.75211, 0.98964, 1.00486 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 68 | 1.01664, 0.75044, 1.00259, 1.00704 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 69 | 0.99135, 0.74671, 1.01269, 0.99854 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 70 | 1.01356, 0.74057, 1.00276, 0.99597 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 71 | 0.99829, 0.74394, 0.99557, 0.98682 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 72 | 1.00278, 0.75825, 0.99945, 1.02108 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 73 | 0.99578, 0.74880, 1.00332, 0.98854 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 74 | 0.99242, 0.74551, 0.99408, 1.00282 | continuous_physical_sar_failed | not measured | False | False |
| 75 | 0.99272, 0.74602, 1.00526, 1.00365 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 76 | 1.01003, 0.75772, 0.99605, 1.00267 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 77 | 0.99282, 0.76088, 0.99664, 1.00285 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 78 | 0.99747, 0.74179, 1.00305, 0.99695 | continuous_physical_sar_failed | not measured | False | False |
| 79 | 1.00228, 0.73486, 0.99757, 0.99932 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 80 | 0.99356, 0.75261, 1.00466, 1.00366 | continuous_physical_sar_candidate_measured_not_accepted | 7, 10, 10, 13, 14 | False | True |
| 81 | 1.00258, 0.75698, 1.00268, 1.01643 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 82 | 1.00512, 0.74176, 0.99014, 1.01166 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 83 | 1.00292, 0.75459, 0.99324, 0.98372 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 84 | 0.98392, 0.74530, 1.00794, 0.99733 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 85 | 1.00065, 0.75613, 1.00653, 1.00108 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 86 | 1.00559, 0.75384, 0.98968, 1.00772 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 87 | 0.99336, 0.74514, 0.99262, 0.99394 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 88 | 1.01466, 0.73984, 1.01591, 1.01180 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 89 | 1.00616, 0.75156, 0.99463, 0.99856 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 90 | 0.99589, 0.73439, 0.98903, 1.00990 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 91 | 1.00353, 0.75286, 0.99912, 0.99443 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 92 | 0.99154, 0.76327, 1.01039, 1.00045 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 93 | 0.98431, 0.75358, 1.00218, 1.00223 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 94 | 0.99783, 0.76428, 0.99655, 0.99299 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 95 | 0.99859, 0.74280, 1.00711, 1.00029 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 96 | 0.99929, 0.74758, 1.00748, 1.01703 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 97 | 0.99771, 0.74505, 1.01738, 1.00853 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 98 | 1.00301, 0.74385, 0.99215, 0.99778 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |
| 99 | 1.00051, 0.73628, 0.99382, 1.00526 | continuous_physical_sar_nominal_map_passed | 0, 2, 4, 6, 7 | True | True |

## Interpretation

A full-map pass means all five representative conversions produced their expected retained code and the reported bottom-plate values stayed within the declared supply range. This is stronger than an isolated DAC mismatch sweep because the perturbed values pass through the actual decision-dependent continuous controller.

## Claim Boundary

This is a reproducible capacitor-variation stress model, not foundry Monte Carlo. It does not prove random device mismatch, comparator offset/noise yield, extracted-layout behavior, DRC/LVS signoff, board behavior, or silicon acceptance.
