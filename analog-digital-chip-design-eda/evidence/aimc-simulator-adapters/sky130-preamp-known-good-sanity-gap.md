# Sky130 Preamp Known-Good Sanity Gap

- status: `known_good_input_stage_and_measured_sense_preamp_op_now_pass`
- known-good measured cases: `6`
- known-good polarity passes: `6`
- known-good target-edge gain V/V: `9.201769`
- measured-sense OP measured cases: `2`
- measured-sense OP timed-out cases: `0`
- same nominal bias as known-good: `True`
- accepted post-layout written: `False`

## First Principle

When a larger circuit fails, the next useful test is the smallest circuit that should have worked. The known comparator input-stage evidence says the Sky130 differential pair can settle and preserve sign. The corrected preamp OP map now says the same bias also settles at the smaller measured frontend voltage.

That means the failed evidence moved. The DC bias point is no longer the blocker. The next question is whether the same preamp reaches and holds the right decision during transient startup, and after that whether the extracted frontend can drive it without losing the signal.

## Diagnosis

- The existing comparator input-stage evidence proves that a simple Sky130 nfet differential pair can settle and preserve polarity at about 0.153 mV differential input.
- The measured-sense preamp OP map uses the same nominal load, tail current, input width, and common-mode idea, and now settles when it is allowed the same long solve window as the known-good deck.
- The earlier timeout was a runner limit, not evidence that the DC preamp bias point was invalid.
- Because the known primitive and measured-sense OP map both pass, the next step is transient startup and then extracted frontend loading.

## Next Runner

- name: `sky130_measured_sense_preamp_transient_startup`
- start from the passing measured-sense OP bias
- drive both measured sense-voltage polarities in transient
- measure output sign, output margin, startup time, and rail headroom
- only after transient startup passes should the extracted frontend be reattached

## Refused Claim

does not prove a new circuit run, preamp acceptance, extracted frontend loading, latch behavior, SAR conversion, or accepted converter evidence
