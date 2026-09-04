# Sky130 Preamp OP Deck-Diff Diagnosis

- status: `current_preamp_op_rerun_confirms_known_good_shape_after_timeout_fix`
- prior known-good status: `known_good_reproduction_passed_for_known_and_measured_sense_inputs`
- prior known-good OP measured cases: `2`
- failed OP debug status: `preamp_op_latch_debug_failed`
- failed OP debug measured cases: `0`
- current known-good-shape rerun status: `known_good_shape_preamp_op_debug_passed_both_signs`
- current known-good-shape OP measured cases: `2`
- current known-good-shape timed-out cases: `0`
- accepted post-layout written: `False`

## First Principle

A timeout setting can create a false circuit failure. The older preamp OP report used a longer timeout. The first debug rerun used a shorter timeout and failed. After matching the timeout to the older authority script, the known-good-shape rerun measured both signs.

That means the preamp OP point is not the blocker. The next blocker is transient startup: the same known-good OP shape must be run as a transient with enough timeout and clear initial conditions before reconnecting the latch.

## Differences Checked

- known-good-shape rerun kept outp/outn node names
- known-good-shape rerun kept XINP/XINN instance names
- known-good-shape rerun kept wn parameter name
- known-good-shape rerun kept OP-only analysis
- known-good-shape rerun extended to both target-edge signs

## Next Debug Steps

- raise the preamp-alone transient debug timeout or shorten the transient deck before judging failure
- use the known-good OP node names and instance shape for the next transient debug
- measure transient startup from the known-good OP initial point
- only reconnect latch after preamp transient settling is measured

## Boundary

does not prove or disprove the physical preamp design; it proves the next debug target is the executable OP environment or deck setup
