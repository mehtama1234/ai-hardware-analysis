# Sky130 Dynamic Offset-Cancelled Latch

- status: `dynamic_offset_cancelled_latch_passed_ready_for_coupled_preamp`
- calibration zero-input differential V: `0.006333299999999986`
- passing cases: `2` of `2`

The source is held at its measured zero-input output during calibration, then steps to the measured target output. Series capacitors transfer the change to an isolated regenerative latch.

This is a dynamic charge-transfer proof; it does not yet connect the transistor preamp directly or prove statistical analog performance.
