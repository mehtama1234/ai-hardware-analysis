#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-frontend-preamp-interface-redesign-target.json"
OUT_MD = EVIDENCE / "sky130-frontend-preamp-interface-redesign-target.md"

GAIN_SWEEP = EVIDENCE / "sky130-extracted-frontend-preamp-gain-sweep.json"
MEASURED_PREAMP = EVIDENCE / "sky130-measured-sense-differential-preamp.json"
FRONTEND = EVIDENCE / "sky130-ultra-sense-frontend-candidate.json"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_report() -> dict[str, Any]:
    sweep = load(GAIN_SWEEP)
    measured_preamp = load(MEASURED_PREAMP)
    frontend = load(FRONTEND)
    best = sweep["best_setting"]
    output_margin_target_v = float(sweep["output_margin_target_v"])
    attached_sense_v = float(best["minimum_sample_to_sense_transfer_ratio"]) * 0.00015297058540778352
    attached_output_v = float(best["minimum_abs_preamp_output_diff_v"])
    attached_gain = float(best["minimum_sense_to_preamp_gain_v_per_v"])
    required_sense_v_at_current_gain = output_margin_target_v / attached_gain
    standalone_sense_v = min(abs(float(row["sense_diff_v"])) for row in measured_preamp["rows"] if row.get("measured"))
    required_transfer_ratio = required_sense_v_at_current_gain / 0.00015297058540778352
    current_transfer_ratio = float(best["minimum_sample_to_sense_transfer_ratio"])
    return {
        "result_type": "sky130_frontend_preamp_interface_redesign_target",
        "status": "frontend_to_preamp_interface_needs_more_voltage_before_latch_work",
        "source_gain_sweep": rel(GAIN_SWEEP),
        "source_measured_preamp": rel(MEASURED_PREAMP),
        "source_frontend": rel(FRONTEND),
        "output_margin_target_v": output_margin_target_v,
        "attached_best_setting": best["name"],
        "attached_minimum_sense_diff_v": attached_sense_v,
        "attached_minimum_output_diff_v": attached_output_v,
        "attached_minimum_sense_to_preamp_gain_v_per_v": attached_gain,
        "standalone_measured_sense_diff_v": standalone_sense_v,
        "required_sense_diff_v_at_current_gain": required_sense_v_at_current_gain,
        "current_sample_to_sense_transfer_ratio": current_transfer_ratio,
        "required_sample_to_sense_transfer_ratio_at_current_gain": required_transfer_ratio,
        "required_transfer_improvement_x": required_transfer_ratio / current_transfer_ratio if current_transfer_ratio else None,
        "standalone_to_attached_sense_loss_x": standalone_sense_v / attached_sense_v if attached_sense_v else None,
        "frontend_nominal_transfer_ratio": frontend["minimum_sample_to_sense_transfer_ratio"],
        "accepted_post_layout_written": False,
        "strict_payload_ready": False,
        "design_rule": "preserve frontend voltage first; gain only helps after enough voltage reaches the preamp gate",
        "next_experiments": [
            "reduce preamp input loading seen by sense_p and sense_n",
            "increase sample-to-sense coupling while keeping both signs correct",
            "add an isolation interface whose input capacitance is smaller than the direct preamp gate load",
            "rerun the attached preamp margin check before any latch test",
        ],
        "claim_boundary": {
            "allowed": "turns measured attached-preamp failure into a numeric frontend-to-preamp interface target",
            "not_allowed": "does not prove a redesigned frontend, latch resolution, SAR conversion, extracted-layout signoff, or accepted converter evidence",
        },
    }


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Frontend Preamp Interface Redesign Target",
        "",
        f"- status: `{report['status']}`",
        f"- attached best setting: `{report['attached_best_setting']}`",
        f"- output margin target V: `{report['output_margin_target_v']:.9e}`",
        f"- attached minimum sense diff V: `{report['attached_minimum_sense_diff_v']:.9e}`",
        f"- attached minimum output diff V: `{report['attached_minimum_output_diff_v']:.9e}`",
        f"- standalone measured sense diff V: `{report['standalone_measured_sense_diff_v']:.9e}`",
        f"- required sense diff at current gain V: `{report['required_sense_diff_v_at_current_gain']:.9e}`",
        f"- current sample-to-sense transfer ratio: `{report['current_sample_to_sense_transfer_ratio']:.6f}`",
        f"- required sample-to-sense transfer ratio at current gain: `{report['required_sample_to_sense_transfer_ratio_at_current_gain']:.6f}`",
        f"- required transfer improvement x: `{report['required_transfer_improvement_x']:.3f}`",
        f"- standalone-to-attached sense loss x: `{report['standalone_to_attached_sense_loss_x']:.3f}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "A preamp cannot amplify voltage that never reaches its input. The standalone preamp passes because the input source directly supplies about the needed sense voltage. When the extracted frontend is attached, the preamp input sees only a much smaller voltage.",
        "",
        "That means the next design target is not more output gain by itself. The interface must first preserve more of the sampled voltage at the preamp gate. After that, the same preamp gain can produce a useful output margin.",
        "",
        "## Design Target",
        "",
        f"The current attached interface gives a sample-to-sense transfer ratio of `{report['current_sample_to_sense_transfer_ratio']:.6f}`. At the measured attached preamp gain, the interface needs about `{report['required_sample_to_sense_transfer_ratio_at_current_gain']:.6f}`. That is a `{report['required_transfer_improvement_x']:.3f}x` transfer improvement.",
        "",
        "## Next Experiments",
        "",
    ]
    lines.extend(f"- {item}" for item in report["next_experiments"])
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print("sky130_frontend_preamp_interface_redesign_target")
    print(f"status,{report['status']}")
    print(f"required_transfer_improvement_x,{report['required_transfer_improvement_x']:.3f}")
    print(f"standalone_to_attached_sense_loss_x,{report['standalone_to_attached_sense_loss_x']:.3f}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
