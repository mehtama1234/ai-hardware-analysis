# Sky130 Transistor Handoff Decomposition

- status: `combined_real_transistor_handoff_is_current_blocker`
- strict payload ready: `False`
- accepted post-layout written: `False`

## What The Split Shows

| check | passed |
|---|---|
| `extracted_frontend_sign_and_transfer_passes` | `True` |
| `standalone_sky130_input_stage_polarity_passes` | `True` |
| `combined_active_macro_handoff_passes` | `True` |
| `frontend_sense_to_transistor_op_measured_cases_have_margin` | `True` |
| `frontend_sense_to_transistor_short_transient_passes` | `True` |
| `frontend_sense_to_transistor_ramp_startup_passes` | `True` |
| `extracted_frontend_to_transistor_assisted_gate_startup_runs` | `True` |
| `extracted_frontend_to_transistor_assisted_gate_startup_passes` | `False` |
| `extracted_frontend_gate_coupling_sweep_finds_passing_setting` | `False` |
| `extracted_frontend_source_follower_handoff_passes` | `False` |
| `extracted_frontend_differential_preamp_runs` | `True` |
| `extracted_frontend_differential_preamp_passes` | `False` |
| `measured_sense_differential_preamp_runs` | `True` |
| `measured_sense_differential_preamp_passes` | `True` |
| `measured_sense_preamp_bias_sweep_finds_passing_setting` | `True` |
| `measured_sense_preamp_op_map_finds_valid_bias_point` | `True` |
| `preamp_known_good_sanity_gap_resolved` | `True` |
| `preamp_known_good_reproduction_passes` | `True` |
| `extracted_frontend_preamp_gain_sweep_finds_passing_setting` | `False` |
| `frontend_preamp_capacitance_budget_ready` | `True` |
| `combined_real_transistor_handoff_runs_to_completion` | `False` |

## Key Numbers

| number | value |
|---|---:|
| `frontend_minimum_transfer_ratio` | `0.43790849673094956` |
| `frontend_remaining_transfer_improvement_x` | `2.283582089557853` |
| `standalone_input_stage_gain_v_per_v` | `9.201769060684017` |
| `active_macro_minimum_output_diff_v` | `0.0006205999999999712` |
| `op_handoff_measured_case_count` | `2` |
| `op_handoff_minimum_abs_output_diff_v` | `0.0006166000000000782` |
| `op_handoff_minimum_gain_v_per_v` | `9.20298507465314` |
| `short_transient_minimum_abs_output_diff_v` | `0.0006299999999999084` |
| `short_transient_minimum_output_retention_ratio` | `1.021732079143413` |
| `ramp_startup_minimum_abs_output_diff_v` | `0.0006264000000000269` |
| `ramp_startup_minimum_gain_v_per_v` | `9.349253731369194` |
| `assisted_gate_startup_measured_case_count` | `2` |
| `assisted_gate_startup_sign_pass_count` | `1` |
| `assisted_gate_startup_output_margin_pass_count` | `1` |
| `assisted_gate_startup_minimum_abs_output_diff_v` | `0.00011700000000014477` |
| `assisted_gate_startup_minimum_sense_to_gate_transfer_ratio` | `0.012257100149496825` |
| `gate_coupling_sweep_setting_count` | `4` |
| `gate_coupling_sweep_passing_setting_count` | `0` |
| `gate_coupling_sweep_timed_out_case_count` | `8` |
| `source_follower_measured_case_count` | `2` |
| `source_follower_sign_pass_count` | `0` |
| `source_follower_minimum_sample_to_sense_transfer_ratio` | `0.062091503267962` |
| `source_follower_minimum_sense_to_buffer_transfer_ratio` | `4.000000000067677e-06` |
| `differential_preamp_measured_case_count` | `2` |
| `differential_preamp_timed_out_case_count` | `0` |
| `differential_preamp_sign_pass_count` | `2` |
| `differential_preamp_output_margin_pass_count` | `0` |
| `differential_preamp_minimum_abs_output_diff_v` | `5.650000000001487e-05` |
| `measured_sense_preamp_measured_case_count` | `2` |
| `measured_sense_preamp_timed_out_case_count` | `0` |
| `preamp_bias_sweep_setting_count` | `4` |
| `preamp_bias_sweep_passing_setting_count` | `1` |
| `preamp_bias_sweep_timed_out_case_count` | `0` |
| `preamp_op_map_setting_count` | `1` |
| `preamp_op_map_passing_setting_count` | `1` |
| `preamp_op_map_timed_out_case_count` | `0` |
| `known_good_input_stage_measured_case_count` | `6` |
| `known_good_input_stage_polarity_pass_count` | `6` |
| `sanity_gap_preamp_op_timed_out_case_count` | `0` |
| `known_good_reproduction_op_measured_case_count` | `2` |
| `known_good_reproduction_polarity_pass_count` | `2` |
| `preamp_gain_sweep_setting_count` | `4` |
| `preamp_gain_sweep_passing_setting_count` | `0` |
| `preamp_gain_sweep_best_minimum_abs_output_diff_v` | `5.650000000001487e-05` |
| `cap_budget_total_cap_reduction_needed_x_if_useful_fixed` | `1.6430867963410842` |
| `cap_budget_useful_coupling_increase_needed_x_if_total_fixed` | `1.6430867963410845` |
| `real_transistor_measured_case_count` | `0` |
| `real_transistor_timed_out_case_count` | `4` |

## First Principle

A circuit proof should fail at the smallest named object we can isolate. Here the frontend alone preserves sign, the standalone Sky130 input pair resolves tiny inputs, the active-macro handoff carries the signal forward, and direct gate ramp startup works. The assisted gate-startup run completes, but one polarity fails sign and margin once the extracted frontend is loaded by the gate connection. A targeted passive coupling sweep finds no passing assisted setting. A bare source follower runs, but it destroys the tiny differential signal instead of preserving it. A direct extracted-frontend differential-preamp transient times out. The same preamp bias also times out when driven by measured sense-voltage sources. A small measured-source transient bias sweep still finds no passing setting. The first measured-source OP map also times out. The sanity-gap report shows that this conflicts with older known-good input-stage evidence, so the primitive must be reproduced exactly.

That means the next work is not another broad AIMC page. It is a one-stage sanity deck for the preamp primitive itself. We need the smallest transistor pair to settle before adding measured inputs, transient startup, or extracted frontend loading.

## Next Debug Probes

- run measured-sense preamp transient startup from the now-passing OP bias
- measure whether both input signs preserve output sign, output margin, startup time, and rail headroom
- only after the one-stage OP deck settles, reintroduce measured sense-voltage polarity and transient startup
- then reconnect the passing preamp to the extracted frontend and check whether loading still collapses the sense signal
- only after both polarities preserve sign and margin, remove the gate startup assist and rerun the full free handoff

## Blockers

- The failed object is the combined extracted-frontend plus real-transistor transient handoff, not the frontend alone, not the standalone input pair, and not the active-macro signal path.
- The current handoff produces timeout evidence, so sign, margin, loading, and output-gain claims are unmeasured for the real transistor combined deck.
- The assisted gate-startup deck now runs to completion, but one polarity fails sign and output margin, so the loaded extracted frontend is not yet a reliable source for the real input pair.
- A targeted passive gate-coupling sweep found no setting that preserves both polarities, so the next design move should be a buffer or active preamp, not more passive resistance tuning.
- A simple Sky130 source follower also fails: it loads the sense node down to about 9.5 microvolts and passes almost no differential signal to the readout pair.
- A direct extracted-frontend differential-preamp transient now runs and preserves sign, but the output difference is below the decision margin, so extracted frontend loading or transfer loss is still the blocker.
- The corrected measured-source DC preamp OP map now finds a valid bias point, so the remaining preamp question is transient startup and then extracted-frontend loading.
- The known-good reproduction now passes at the old target input and the smaller measured frontend input, so the remaining preamp OP-map failure is not the basic Sky130 differential pair.
- The extracted-frontend preamp gain sweep finds no margin-passing simple gain setting, so the next physical change must preserve more frontend voltage before amplification or add a different isolation interface.
- The capacitance budget turns that into layout terms: reduce wasted sense-node capacitance or increase useful sample-to-sense coupling by about 1.64x before trying another latch handoff.

## Refused Claim

does not prove transistor handoff, latch behavior, SAR conversion, accepted post-layout evidence, or replacement economics
