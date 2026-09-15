#!/usr/bin/env python3
"""Bind a qualified numerical range profile to a blocked hardware review plan."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1]
SOFTWARE=ROOT.parent/"analog-in-memory-ai-inference/software-architecture"
sys.path.insert(0,str(SOFTWARE/"scripts"))
from check_gpt2_adc_holdout import check
from calibrated_adc_controller_contract import pack_ranges,unpack_ranges,make_program,replay
from compile_hybrid_transformer_execution_package import main as compile_package,align,OPCODES,validate_range_lowering
from run_target_bytecode_reference import main as execute_reference


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path,value):
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+"\n")


def run(args):
    check(args.quality)
    quality=json.loads((args.quality/"result.json").read_text())
    plan=json.loads((args.quality/"frozen_plan/plan.json").read_text())
    selected=plan["selected_variant"]
    if not quality["variants"][selected]["screen_pass"]:
        raise ValueError("Selected profile failed its quality screen")
    contract=plan["selected_contract"]
    args.output=args.output.resolve()
    if not args.output.is_relative_to(ROOT):
        raise ValueError("Compiler review artifacts must reside in the EDA project")
    args.output.mkdir(parents=True,exist_ok=False)
    snapshots=args.output/"source_snapshot";snapshots.mkdir()
    for name in [Path(__file__).name,"calibrated_adc_controller_contract.py",
                 "compile_hybrid_transformer_execution_package.py","run_target_bytecode_reference.py"]:
        shutil.copy2(Path(__file__).with_name(name),snapshots/name)
    shutil.copy2(SOFTWARE/"scripts/check_gpt2_adc_holdout.py",snapshots/"check_gpt2_adc_holdout.py")
    table=pack_ranges(contract)
    (args.output/"range_descriptors.bin").write_bytes(table)
    descriptors=unpack_ranges(table)
    program=make_program(descriptors)
    observed=replay(program,descriptors)
    write(args.output/"range_descriptors.json",descriptors)
    write(args.output/"controller_review_program.json",program)
    write(args.output/"controller_reference_replay.json",observed)
    range_requirement={"schema_version":"calibrated_adc_range_requirement.v1",
                       "selected_contract_sha256":digest(args.quality/"frozen_plan/plan.json"),
                       "descriptor_table_sha256":digest(args.output/"range_descriptors.bin"),
                       "units":"dimensionless model partial-sum units; not volts or register codes",
                       "ranges":contract["adc_range"]["ranges"]}
    operator={"operator_id":"transformer.h.0.mlp.c_fc","placement":"digital_support",
              "weight_shape_in_out":[768,3072],"activation_shape":[1,768],"output_shape":[1,3072],
              "adc_range_contract":range_requirement}
    analog=dict(operator,placement="analog_memory")
    try: validate_range_lowering(analog)
    except ValueError as error: refusal=str(error)
    else: raise RuntimeError("Compiler accepted unsupported range programming")
    execution_plan=args.output/"execution_plan.json"
    write(execution_plan,{"operator_placements":[operator]})
    source=args.output/"compiler_source.json"
    write(source,{"target_package_id":"gpt2_calibrated_range_digital_fallback",
                  "physical_gate_status":"unqualified_calibrated_range_hardware",
                  "models":[{"model_id":"gpt2_calibrated_adc12","source_plan":str(execution_plan.relative_to(ROOT)),
                              "operator_count":1,"converter_plan":{"simulator_dac_bits":10,"simulator_adc_bits":12}}]})
    compile_package(source,args.output)
    execute_reference(args.output)
    compiled=json.loads((args.output/"compiled_target_execution_package.json").read_text())
    commands=json.loads((args.output/"runtime_commands.json").read_text())["commands"]
    if [c["command"] for c in commands]!=["RUN_DIGITAL_SUPPORT"]:
        raise RuntimeError("Expected digital-only lowering")
    used=compiled["sram_memory_maps"][0]["sram_bytes_used"]
    descriptor_offset=align(used)
    if descriptor_offset+len(table)>65536:
        raise ValueError("Candidate range table exceeds SRAM budget")
    report={"schema_version":"calibrated_adc_controller_contract.v1",
            "status":"range_requirements_bound_review_protocol_checked_physical_lowering_blocked",
            "quality_source":{"path":str((args.quality/"result.json").resolve()),"sha256":digest(args.quality/"result.json")},
            "range_source":{"path":str((args.quality/"frozen_plan/plan.json").resolve()),"sha256":digest(args.quality/"frozen_plan/plan.json")},
            "range_table":{"records":len(descriptors),"record_bytes":16,"bytes":len(table),
                           "encoding":"little-endian uint16 tile,row,column; uint8 ADC bits,reserved; float64 model bound",
                           "claim":"review data format, not hardware register encoding"},
            "resource_assumptions":{"resident_logical_tiles":144,"shared_adc_banks":8,"lanes_per_bank":16,
                                    "waves_per_vector":18,"adc_rounds_per_wave":8},
            "per_vector_review_counts":observed,
            "sram":{"compiler_digital_arena_bytes":used,"candidate_descriptor_offset":descriptor_offset,
                    "candidate_combined_bytes":descriptor_offset+len(table),
                    "status":"descriptor storage is proposed; digital fallback does not load it"},
            "physical_mapping":{"assumption":"linear differential array: I_diff = alpha_tile * beta_DAC * model_partial",
                                "required_transimpedance_equation":"R_tile = V_ADC_full_scale / (alpha_tile * beta_DAC * selected_bound)",
                                "alpha_tile_siemens_per_weight_unit":None,"beta_DAC_volts_per_activation_unit":None,
                                "V_ADC_full_scale":None,"R_tile_ohms":None,
                                "alternative":"fixed gain with per-tile ADC reference; neither implementation selected or qualified"},
            "compiler":{"available_opcodes":OPCODES,"analog_refusal":refusal,
                        "emitted_commands":[c["command"] for c in commands],
                        "missing_operations":["configure ADC range/reference","wait for range settling acknowledgement"]},
            "unresolved_costs":["range configuration transfers","range switching and settling","sample/hold and mux timing",
                                "absolute physical noise across ranges","gain/reference area and energy"],
            "analog_authorized":False,"physical_io_performed":False,
            "claim_boundary":"Model-bound descriptors and software ordering checks only. No implemented range circuit, physical timing, firmware execution or analog inference."}
    write(args.output/"range_controller_contract.json",report)
    write(args.output/"manifest.json",{str(p.relative_to(args.output)):digest(p) for p in args.output.rglob('*') if p.is_file()})
    print(json.dumps({"output":str(args.output),"tiles":len(descriptors),"descriptor_bytes":len(table),"review_events":len(program),"compiler_route":"digital_fallback"}))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quality",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    run(parser.parse_args())
