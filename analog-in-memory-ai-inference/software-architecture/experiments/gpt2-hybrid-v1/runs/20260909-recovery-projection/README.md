# GPT-2 hybrid projection evaluation

Real GPT-2 sensitivity to one provisional tiled projection. CPU emulation time is not hybrid hardware latency. No silicon, energy advantage, or full-task acceptance claim.

| Variant | NLL increase (nats/token) | Argmax agreement | Exact generations | Exploratory screen |
| --- | ---: | ---: | ---: | --- |
| ideal_tiled_control | -0.000001 | 1.0000 | 4/4 | True |
| dac10_weight8_adc8 | 0.025967 | 0.8254 | 3/4 | False |
| dac10_weight8_adc12 | 0.004654 | 1.0000 | 4/4 | True |
| dac10_weight8_adc12_noise001 | 0.028013 | 0.9683 | 3/4 | False |

Digital fallback and ideal tiled controls passed.

Physical converter accepted: False; extracted netlist hash matches: True.

Hardware benefit remains unproven. Conversion counts are explicit; matched physical costs are missing.
