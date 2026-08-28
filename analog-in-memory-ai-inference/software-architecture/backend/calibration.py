CALIBRATION_PROFILES = {
    "sim-wearable-v0": {
        "profile_id": "sim-wearable-v0",
        "label": "Simulated wearable profile",
        "status": "Mock profile",
        "board": "simulated-wearable",
        "temperature": "0C to 70C",
        "voltage": "0.72V to 0.88V",
        "weak_rows": "not measured",
        "accuracy_impact": "estimated only",
        "provenance": "estimated",
        "confidence": "low",
        "correction_factors": {
            "gain": 1.0,
            "offset": 0.0,
            "adc_reference": "nominal",
        },
        "notes": "Default simulated profile for early wearable analysis.",
    },
    "proto-audio-0237": {
        "profile_id": "proto-audio-0237",
        "label": "Prototype audio board 0237",
        "status": "Valid lab profile",
        "board": "AS-EDGE-0237",
        "temperature": "0C to 70C",
        "voltage": "0.72V to 0.88V",
        "weak_rows": "12 masked",
        "accuracy_impact": "-0.3% estimated",
        "provenance": "prototype_board",
        "confidence": "medium",
        "correction_factors": {
            "gain": 0.992,
            "offset": 0.018,
            "adc_reference": "rev-b-shared-ref",
        },
        "notes": "Representative prototype profile for always-on audio workloads.",
    },
    "proto-camera-011": {
        "profile_id": "proto-camera-011",
        "label": "Prototype camera board 011",
        "status": "Valid lab profile",
        "board": "AS-EDGE-CAM-011",
        "temperature": "-10C to 80C",
        "voltage": "0.76V to 0.90V",
        "weak_rows": "19 masked",
        "accuracy_impact": "-0.2% estimated",
        "provenance": "prototype_board",
        "confidence": "medium",
        "correction_factors": {
            "gain": 1.006,
            "offset": -0.011,
            "adc_reference": "rev-b-shared-ref",
        },
        "notes": "Representative prototype profile for image classification and camera workloads.",
    },
    "proto-robot-004": {
        "profile_id": "proto-robot-004",
        "label": "Prototype robotics board 004",
        "status": "Needs wider sweep",
        "board": "AS-EDGE-ROB-004",
        "temperature": "-20C to 60C tested",
        "voltage": "0.74V to 0.88V",
        "weak_rows": "31 masked",
        "accuracy_impact": "-1.1% estimated",
        "provenance": "prototype_board",
        "confidence": "low",
        "correction_factors": {
            "gain": 0.981,
            "offset": 0.027,
            "adc_reference": "rev-a-local-ref",
        },
        "notes": "Prototype profile with limited operating sweep for robotics-style burst workloads.",
    },
}


def list_calibration_profiles():
    return {
        key: {
            "profile_id": value["profile_id"],
            "label": value["label"],
            "status": value["status"],
            "board": value["board"],
            "provenance": value["provenance"],
            "confidence": value["confidence"],
        }
        for key, value in CALIBRATION_PROFILES.items()
    }


def get_calibration_profile(profile_id):
    return CALIBRATION_PROFILES.get(profile_id) or CALIBRATION_PROFILES["sim-wearable-v0"]

