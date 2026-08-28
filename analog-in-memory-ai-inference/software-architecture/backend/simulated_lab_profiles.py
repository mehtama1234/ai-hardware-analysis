from copy import deepcopy


SIMULATED_LAB_PROFILE_SCHEMA_VERSION = "simulated-lab-profile-v0.1"


SIMULATED_LAB_PROFILES = {
    "wearable": {
        "scenario_id": "wearable-camera-audio-v0",
        "label": "Wearable always-on inference",
        "target_device": "small battery device with a tight skin-temperature limit",
        "workload_shape": "short repeated inference bursts with long idle periods",
        "analog_array": {
            "mac_array": "64x64 equivalent",
            "weight_precision_bits": 4,
            "activation_precision_bits": 8,
            "adc_bits": 6,
            "dac_bits": 6,
        },
        "memory": {
            "local_sram_kb": 512,
            "external_dram": "not assumed",
            "host_interface": "low-power serial or shared memory",
        },
        "environment": {
            "temperature_c": [25, 42],
            "voltage_v": [0.85, 0.95],
            "thermal_limit_c": 45,
        },
        "energy_model": {
            "analog_mac_pj": 0.15,
            "adc_conversion_pj": 6.0,
            "dac_conversion_pj": 2.0,
            "sram_access_pj": 0.08,
            "dram_access_pj": 8.0,
            "host_overhead_uj": 3.5,
            "idle_power_mw": 3.0,
        },
        "runtime": {
            "target_latency_ms": 10,
            "duty_cycle": "bursty",
            "replay_count": 128,
        },
        "accuracy": {
            "metric": "classification_accuracy",
            "tolerance": 0.01,
            "synthetic_record_count": 128,
        },
    },
    "camera": {
        "scenario_id": "smart-camera-v0",
        "label": "Smart camera edge vision",
        "target_device": "mains or large-battery camera with limited passive cooling",
        "workload_shape": "regular frame-by-frame inference with image preprocessing",
        "analog_array": {
            "mac_array": "128x128 equivalent",
            "weight_precision_bits": 4,
            "activation_precision_bits": 8,
            "adc_bits": 7,
            "dac_bits": 6,
        },
        "memory": {
            "local_sram_kb": 2048,
            "external_dram": "possible but counted as expensive traffic",
            "host_interface": "camera pipeline plus local accelerator runtime",
        },
        "environment": {
            "temperature_c": [0, 60],
            "voltage_v": [0.82, 0.98],
            "thermal_limit_c": 75,
        },
        "energy_model": {
            "analog_mac_pj": 0.18,
            "adc_conversion_pj": 7.5,
            "dac_conversion_pj": 2.4,
            "sram_access_pj": 0.1,
            "dram_access_pj": 12.0,
            "host_overhead_uj": 12.0,
            "idle_power_mw": 20.0,
        },
        "runtime": {
            "target_latency_ms": 33,
            "duty_cycle": "steady frame loop",
            "replay_count": 300,
        },
        "accuracy": {
            "metric": "top1_accuracy_or_map",
            "tolerance": 0.015,
            "synthetic_record_count": 300,
        },
    },
    "robotics": {
        "scenario_id": "mobile-robot-perception-v0",
        "label": "Mobile robot perception",
        "target_device": "battery robot with real-time control and safety margins",
        "workload_shape": "continuous sensor inference with strict tail latency",
        "analog_array": {
            "mac_array": "128x128 equivalent",
            "weight_precision_bits": 4,
            "activation_precision_bits": 8,
            "adc_bits": 7,
            "dac_bits": 7,
        },
        "memory": {
            "local_sram_kb": 4096,
            "external_dram": "available but should be minimized",
            "host_interface": "robot middleware and real-time runtime",
        },
        "environment": {
            "temperature_c": [-10, 70],
            "voltage_v": [0.8, 1.0],
            "thermal_limit_c": 85,
        },
        "energy_model": {
            "analog_mac_pj": 0.22,
            "adc_conversion_pj": 8.0,
            "dac_conversion_pj": 3.0,
            "sram_access_pj": 0.12,
            "dram_access_pj": 14.0,
            "host_overhead_uj": 20.0,
            "idle_power_mw": 35.0,
        },
        "runtime": {
            "target_latency_ms": 20,
            "duty_cycle": "continuous with deadline checks",
            "replay_count": 500,
        },
        "accuracy": {
            "metric": "task_success_or_detection_metric",
            "tolerance": 0.02,
            "synthetic_record_count": 500,
        },
    },
    "industrial": {
        "scenario_id": "industrial-sensor-v0",
        "label": "Industrial sensor anomaly detection",
        "target_device": "sealed sensor node with long service life",
        "workload_shape": "periodic sensor-window inference under wide environment range",
        "analog_array": {
            "mac_array": "64x64 equivalent",
            "weight_precision_bits": 4,
            "activation_precision_bits": 8,
            "adc_bits": 6,
            "dac_bits": 6,
        },
        "memory": {
            "local_sram_kb": 1024,
            "external_dram": "not assumed",
            "host_interface": "microcontroller plus sensor front end",
        },
        "environment": {
            "temperature_c": [-20, 85],
            "voltage_v": [0.78, 1.02],
            "thermal_limit_c": 95,
        },
        "energy_model": {
            "analog_mac_pj": 0.2,
            "adc_conversion_pj": 7.0,
            "dac_conversion_pj": 2.5,
            "sram_access_pj": 0.1,
            "dram_access_pj": 10.0,
            "host_overhead_uj": 8.0,
            "idle_power_mw": 8.0,
        },
        "runtime": {
            "target_latency_ms": 50,
            "duty_cycle": "periodic sensor windows",
            "replay_count": 256,
        },
        "accuracy": {
            "metric": "anomaly_f1_or_recall",
            "tolerance": 0.02,
            "synthetic_record_count": 256,
        },
    },
    "edge_llm": {
        "scenario_id": "edge-llm-small-v0",
        "label": "Small edge language model",
        "target_device": "power-limited edge module running repeated token steps",
        "workload_shape": "memory-heavy token generation with repeated matrix multiplies",
        "analog_array": {
            "mac_array": "128x128 equivalent",
            "weight_precision_bits": 4,
            "activation_precision_bits": 8,
            "adc_bits": 7,
            "dac_bits": 7,
        },
        "memory": {
            "local_sram_kb": 8192,
            "external_dram": "likely required and counted as a major cost",
            "host_interface": "token runtime with digital attention and control path",
        },
        "environment": {
            "temperature_c": [0, 70],
            "voltage_v": [0.82, 1.0],
            "thermal_limit_c": 85,
        },
        "energy_model": {
            "analog_mac_pj": 0.24,
            "adc_conversion_pj": 9.0,
            "dac_conversion_pj": 3.5,
            "sram_access_pj": 0.14,
            "dram_access_pj": 18.0,
            "host_overhead_uj": 35.0,
            "idle_power_mw": 45.0,
        },
        "runtime": {
            "target_latency_ms": 100,
            "duty_cycle": "repeated token loop",
            "replay_count": 128,
        },
        "accuracy": {
            "metric": "perplexity_or_task_score",
            "tolerance": 0.03,
            "synthetic_record_count": 128,
        },
    },
}


def simulated_lab_profile(target_profile, modality=None, runtime_mode=None):
    profile_key = target_profile if target_profile in SIMULATED_LAB_PROFILES else "wearable"
    profile = deepcopy(SIMULATED_LAB_PROFILES[profile_key])
    profile["schema_version"] = SIMULATED_LAB_PROFILE_SCHEMA_VERSION
    profile["target_profile"] = target_profile
    profile["selected_profile_key"] = profile_key
    profile["modality"] = modality
    profile["runtime_mode"] = runtime_mode
    profile["not_measured_hardware"] = True
    profile["plain_reading"] = (
        "This is a scenario-based local lab profile. It makes the simulator use explicit assumptions "
        "about precision, conversion cost, memory traffic, voltage, temperature, duty cycle, and host overhead. "
        "It is useful for workflow testing and interview reasoning, but it is not measured silicon or board data."
    )
    return profile


def simulated_lab_metadata(target_profile, modality=None, runtime_mode=None):
    profile = simulated_lab_profile(target_profile, modality=modality, runtime_mode=runtime_mode)
    return {
        "schema_version": SIMULATED_LAB_PROFILE_SCHEMA_VERSION,
        "scenario_id": profile["scenario_id"],
        "label": profile["label"],
        "target_profile": target_profile,
        "modality": modality,
        "runtime_mode": runtime_mode,
        "not_measured_hardware": True,
        "plain_reading": profile["plain_reading"],
        "profile": profile,
    }
