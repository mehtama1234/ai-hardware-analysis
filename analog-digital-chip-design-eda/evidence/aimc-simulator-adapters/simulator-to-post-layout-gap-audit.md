# Simulator To Post-Layout Gap Audit

- status: `simulator_evidence_present_post_layout_converter_evidence_missing`
- simulator payload count: `20`
- supporting simulator payload count: `13`
- post-layout converter ready payload count: `0`
- blocked post-layout payload count: `20`

## First Principle

A simulator run and a post-layout converter run answer different questions. The simulator run asks how much an analog matrix operation changes the output. The post-layout converter run asks what the physical converter costs after layout, extraction, and corner setup. A low residual can justify trying analog placement. It cannot by itself justify the converter energy, latency, noise, or area claim.

## Missing Physical Fields

- `extracted_netlist`
- `parasitic_format`
- `process_corner`
- `model_files`
- `adc_energy_per_conversion`
- `dac_energy_per_row_drive`
- `conversion_time_ns`
- `settling_time_ns`
- `output_noise_rms`
- `input_referred_noise`
- `adc_area_um2`
- `dac_area_um2`
- `replication_or_sharing_rule`
- `rerun_artifact`
- `same_run_id`

## Payload Boundary

### evidence/aimc-simulator-adapters/aihwkit-analog-error-simulation.json

- tool: `aihwkit optional adapter run`
- measurement level: `external_simulator_small_fixture`
- simulator claim support: `True`
- post-layout converter claim support: `False`
- residual: `0.05224148920879446` q8 `7`

### evidence/aimc-simulator-adapters/aihwkit-attention-block-analog-error-simulation.json

- tool: `aihwkit attention-block trained-weight adapter run`
- measurement level: `external_simulator_attention_block_trained_weight_replay`
- simulator claim support: `False`
- post-layout converter claim support: `False`
- residual: `0.9167446415863351` q8 `117`

### evidence/aimc-simulator-adapters/aihwkit-calibrated-attention-block-analog-error-simulation.json

- tool: `aihwkit calibrated attention-block adapter run`
- measurement level: `external_simulator_calibrated_attention_block_replay`
- simulator claim support: `False`
- post-layout converter claim support: `False`
- residual: `0.6099825005621208` q8 `78`

### evidence/aimc-simulator-adapters/aihwkit-calibrated-deep-transformer-mlp-stack-analog-error-simulation.json

- tool: `aihwkit calibrated deep transformer MLP stack adapter run`
- measurement level: `external_simulator_calibrated_deep_transformer_mlp_stack_replay`
- simulator claim support: `False`
- post-layout converter claim support: `False`
- residual: `0.8698838129192049` q8 `111`

### evidence/aimc-simulator-adapters/aihwkit-calibrated-transformer-mlp-block-analog-error-simulation.json

- tool: `aihwkit calibrated transformer MLP block adapter run`
- measurement level: `external_simulator_calibrated_transformer_mlp_block_replay`
- simulator claim support: `False`
- post-layout converter claim support: `False`
- residual: `0.6246638170974814` q8 `80`

### evidence/aimc-simulator-adapters/aihwkit-projection-stack-analog-error-simulation.json

- tool: `aihwkit projection-stack trained-weight adapter run`
- measurement level: `external_simulator_projection_stack_trained_weight_replay`
- simulator claim support: `False`
- post-layout converter claim support: `False`
- residual: `0.5551039438677029` q8 `71`

### evidence/aimc-simulator-adapters/aihwkit-tensor-shape-analog-error-simulation.json

- tool: `aihwkit tensor-shaped optional adapter run`
- measurement level: `external_simulator_backend_tensor_shape_replay`
- simulator claim support: `True`
- post-layout converter claim support: `False`
- residual: `0.0756692475974969` q8 `10`

### evidence/aimc-simulator-adapters/aihwkit-trained-weight-analog-error-simulation.json

- tool: `aihwkit trained-weight optional adapter run`
- measurement level: `external_simulator_backend_trained_weight_replay`
- simulator claim support: `False`
- post-layout converter claim support: `False`
- residual: `0.2845561545201431` q8 `36`

### evidence/aimc-simulator-adapters/aihwkit-transformer-mlp-block-analog-error-simulation.json

- tool: `aihwkit transformer MLP block trained-weight adapter run`
- measurement level: `external_simulator_transformer_mlp_block_trained_weight_replay`
- simulator claim support: `False`
- post-layout converter claim support: `False`
- residual: `0.6190536739521524` q8 `79`

### evidence/aimc-simulator-adapters/aihwkit-workload-analog-error-simulation.json

- tool: `aihwkit workload-shaped optional adapter run`
- measurement level: `external_simulator_backend_candidate_workload`
- simulator claim support: `True`
- post-layout converter claim support: `False`
- residual: `0.09000426441791687` q8 `12`

### evidence/aimc-simulator-adapters/crosssim-analog-error-simulation.json

- tool: `crosssim optional adapter run`
- measurement level: `external_simulator_small_fixture`
- simulator claim support: `True`
- post-layout converter claim support: `False`
- residual: `7.464046673886023e-08` q8 `0`

### evidence/aimc-simulator-adapters/crosssim-attention-block-analog-error-simulation.json

- tool: `crosssim attention-block trained-weight adapter run`
- measurement level: `external_simulator_attention_block_trained_weight_replay`
- simulator claim support: `True`
- post-layout converter claim support: `False`
- residual: `5.846699905128645e-08` q8 `0`

### evidence/aimc-simulator-adapters/crosssim-calibrated-attention-block-analog-error-simulation.json

- tool: `crosssim calibrated attention-block adapter run`
- measurement level: `external_simulator_calibrated_attention_block_replay`
- simulator claim support: `True`
- post-layout converter claim support: `False`
- residual: `4.177331466464009e-08` q8 `0`

### evidence/aimc-simulator-adapters/crosssim-calibrated-deep-transformer-mlp-stack-analog-error-simulation.json

- tool: `crosssim calibrated deep transformer MLP stack adapter run`
- measurement level: `external_simulator_calibrated_deep_transformer_mlp_stack_replay`
- simulator claim support: `True`
- post-layout converter claim support: `False`
- residual: `6.716349688914575e-08` q8 `0`

### evidence/aimc-simulator-adapters/crosssim-calibrated-transformer-mlp-block-analog-error-simulation.json

- tool: `crosssim calibrated transformer MLP block adapter run`
- measurement level: `external_simulator_calibrated_transformer_mlp_block_replay`
- simulator claim support: `True`
- post-layout converter claim support: `False`
- residual: `4.94497815376823e-08` q8 `0`

### evidence/aimc-simulator-adapters/crosssim-projection-stack-analog-error-simulation.json

- tool: `crosssim projection-stack trained-weight adapter run`
- measurement level: `external_simulator_projection_stack_trained_weight_replay`
- simulator claim support: `True`
- post-layout converter claim support: `False`
- residual: `5.0645552995255704e-08` q8 `0`

### evidence/aimc-simulator-adapters/crosssim-tensor-shape-analog-error-simulation.json

- tool: `crosssim tensor-shaped optional adapter run`
- measurement level: `external_simulator_backend_tensor_shape_replay`
- simulator claim support: `True`
- post-layout converter claim support: `False`
- residual: `4.3503356403413546e-08` q8 `0`

### evidence/aimc-simulator-adapters/crosssim-trained-weight-analog-error-simulation.json

- tool: `crosssim trained-weight optional adapter run`
- measurement level: `external_simulator_backend_trained_weight_replay`
- simulator claim support: `True`
- post-layout converter claim support: `False`
- residual: `7.50123133377775e-08` q8 `0`

### evidence/aimc-simulator-adapters/crosssim-transformer-mlp-block-analog-error-simulation.json

- tool: `crosssim transformer MLP block trained-weight adapter run`
- measurement level: `external_simulator_transformer_mlp_block_trained_weight_replay`
- simulator claim support: `True`
- post-layout converter claim support: `False`
- residual: `5.8187885598288214e-08` q8 `0`

### evidence/aimc-simulator-adapters/crosssim-workload-analog-error-simulation.json

- tool: `crosssim workload-shaped optional adapter run`
- measurement level: `external_simulator_backend_candidate_workload`
- simulator claim support: `True`
- post-layout converter claim support: `False`
- residual: `0.09000426441791687` q8 `12`

## Handoff Rule

use simulator residual evidence to choose which operators deserve layout work, then use the post-layout builder only after extracted converter artifacts and same-run numeric values exist

## Refused Claim

does not treat AIHWKIT or CrossSim output residuals as extracted layout, measured converter energy, measured latency, measured area, or accepted post-layout evidence
