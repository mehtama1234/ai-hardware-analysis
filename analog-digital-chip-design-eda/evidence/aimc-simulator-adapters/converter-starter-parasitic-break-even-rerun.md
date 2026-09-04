# Converter Starter Parasitic Break-Even Rerun

- status: `starter_parasitic_break_even_rerun_complete_not_accepted_evidence`
- base energy unit J: `1.000000e-12`
- starter total pin charge energy J: `3.225791e-14`
- starter total pin charge energy in base units: `3.225791e-02`
- starter max settle 0.1 percent s: `9.559010e-11`
- passing scenario count: `2` of `4`
- first passing scenario: `sixty_four_row_tile_shared_over_16_outputs`
- replacement decision: `keep_digital_fallback_until_real_converter_post_layout_measurement`
- candidate post-layout written: `False`
- accepted post-layout written: `False`

## First Principle

A parasitic load changes the break-even question only through the extra charge that must be moved and the extra time needed to settle that charge. If the load is tiny next to the converter energy model, it should not change the scenario decision. If it is large, it can erase the energy margin that made analog look useful.

This rerun keeps that accounting honest. It adds only the extracted starter capacitance energy. It does not pretend that capacitance is the full converter, because a converter also needs transistor switching, references, comparator decisions, mismatch, and supply-current integration.

## Scenario Table

| scenario | sharing | base analog/output | added parasitic/output | adjusted analog/output | digital/output | adjusted margin | beats digital |
|---|---:|---:|---:|---:|---:|---:|---|
| four-row_fixture_no_sharing | 1 | `206.622222` | `3.225791e-02` | `206.654480` | `4.000000` | `-202.654480` | `False` |
| sixty_four_row_tile_no_sharing | 1 | `212.622222` | `3.225791e-02` | `212.654480` | `64.000000` | `-148.654480` | `False` |
| sixty_four_row_tile_shared_over_16_outputs | 16 | `19.288889` | `2.016119e-03` | `19.290905` | `64.000000` | `44.709095` | `True` |
| two_fifty_six_row_tile_shared_over_64_outputs | 64 | `28.822222` | `5.040298e-04` | `28.822726` | `256.000000` | `227.177274` | `True` |

## Refused Claim

does not replace real ADC/DAC energy, transistor settling, noise, supply-current integration, physical area signoff, or accepted post-layout evidence
