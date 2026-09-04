# Sky130 Frontend Preamp Interface Redesign Target

- status: `frontend_to_preamp_interface_needs_more_voltage_before_latch_work`
- attached best setting: `known_input_stage_bias`
- output margin target V: `5.000000000e-04`
- attached minimum sense diff V: `6.398769586e-06`
- attached minimum output diff V: `5.650000000e-05`
- standalone measured sense diff V: `6.700000000e-05`
- required sense diff at current gain V: `6.106194690e-05`
- current sample-to-sense transfer ratio: `0.041830`
- required sample-to-sense transfer ratio at current gain: `0.399174`
- required transfer improvement x: `9.543`
- standalone-to-attached sense loss x: `10.471`
- accepted post-layout written: `False`

## First Principle

A preamp cannot amplify voltage that never reaches its input. The standalone preamp passes because the input source directly supplies about the needed sense voltage. When the extracted frontend is attached, the preamp input sees only a much smaller voltage.

That means the next design target is not more output gain by itself. The interface must first preserve more of the sampled voltage at the preamp gate. After that, the same preamp gain can produce a useful output margin.

## Design Target

The current attached interface gives a sample-to-sense transfer ratio of `0.041830`. At the measured attached preamp gain, the interface needs about `0.399174`. That is a `9.543x` transfer improvement.

## Next Experiments

- reduce preamp input loading seen by sense_p and sense_n
- increase sample-to-sense coupling while keeping both signs correct
- add an isolation interface whose input capacitance is smaller than the direct preamp gate load
- rerun the attached preamp margin check before any latch test

## Refused Claim

does not prove a redesigned frontend, latch resolution, SAR conversion, extracted-layout signoff, or accepted converter evidence
