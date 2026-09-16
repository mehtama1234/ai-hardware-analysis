"""Catalog and compile real multi-module RTL targets from local EDA repos."""
from __future__ import annotations
import argparse, hashlib, json, re, subprocess, tempfile
from pathlib import Path

TARGETS = [
    ("OpenLane", "/home/mehtama1/eda-tools/OpenLane/designs/aimc_error_budget_governor_physical", "aimc_error_budget_governor_physical"),
    ("OpenLane", "/home/mehtama1/eda-tools/OpenLane/designs/aimc_micro_tile_controller", "aimc_micro_tile_controller"),
    ("OpenLane", "/home/mehtama1/eda-tools/OpenLane/designs/aimc_multi_clock_control_subsystem", "aimc_multi_clock_control_subsystem"),
    ("OpenLane", "/home/mehtama1/eda-tools/OpenLane/designs/aimc_operation_partition_output_registered", "aimc_operation_partition_output_registered"),
    ("OpenLane", "/home/mehtama1/eda-tools/OpenLane/designs/aimc_operation_partition_physical", "aimc_operation_partition_physical"),
    ("OpenLane", "/home/mehtama1/eda-tools/OpenLane/designs/aimc_scheduler_governor_physical", "aimc_scheduler_governor_physical"),
    ("OpenLane", "/home/mehtama1/eda-tools/OpenLane/designs/aimc_scheduler_governor_pipelined", "aimc_scheduler_governor_pipelined"),
    ("OpenLane", "/home/mehtama1/eda-tools/OpenLane/designs/aimc_tile_service_scheduler_physical", "aimc_tile_service_scheduler_physical"),
    ("OpenLane", "/home/mehtama1/eda-tools/OpenLane/designs/peripheral", "peripheral"),
    ("OpenLane", "/home/mehtama1/eda-tools/OpenLane/designs/spm", "spm"),
    ("OpenROAD-flow-scripts", "/home/mehtama1/eda-tools/OpenROAD-flow-scripts/flow/designs/src/aes", "aes_cipher_top"),
    ("OpenROAD-flow-scripts", "/home/mehtama1/eda-tools/OpenROAD-flow-scripts/flow/designs/src/fifo", "fifo"),
    ("OpenROAD-flow-scripts", "/home/mehtama1/eda-tools/OpenROAD-flow-scripts/flow/designs/src/chameleon/acc", "AHB_SPM"),
    ("OpenROAD-flow-scripts", "/home/mehtama1/eda-tools/OpenROAD-flow-scripts/flow/designs/src/uart", "uart"),
    ("OpenROAD-flow-scripts", "/home/mehtama1/eda-tools/OpenROAD-flow-scripts/flow/designs/ihp-sg13g2/i2c-gpio-expander", "I2cGpioExpanderTop"),
]
MODULE_RE = re.compile(r"\bmodule\s+([A-Za-z_][A-Za-z0-9_]*)")
INSTANCE_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s+(?:#\s*\([^;]*?\)\s*)?([A-Za-z_][A-Za-z0-9_]*)\s*\(", re.S)
PORT_RE = re.compile(r"\b(?:input|output|inout)\b[^;]*?\b([A-Za-z_][A-Za-z0-9_]*)\b")
EXTRA_FILES = {"i2c-gpio-expander": [Path("/home/mehtama1/eda-tools/OpenROAD-flow-scripts/flow/platforms/ihp-sg13g2/verilog/sg13g2_io.v")]}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def digest(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--output",type=Path,required=True); args=parser.parse_args(); args.output=args.output.resolve(); args.output.mkdir(parents=True,exist_ok=True)
    designs=[]; errors=[]
    for repository, root_text, top in TARGETS:
        root=Path(root_text); files=(sorted(root.glob("src/*.sv"))+sorted(root.glob("src/*.v"))) if (root/"src").is_dir() else sorted(root.glob("*.v"))+sorted(root.glob("*.sv"))
        if not files: errors.append(f"{root}: no RTL files"); continue
        modules=[]; text_by_file={}
        for path in files:
            text=path.read_text(encoding="utf-8", errors="replace"); text_by_file[path]=text; modules += [{"name":m,"file":str(path),"sha256":sha(path)} for m in MODULE_RE.findall(text)]
        names={x["name"] for x in modules}; edges=[]
        for parent_text in text_by_file.values():
            for candidate, instance in INSTANCE_RE.findall(parent_text):
                if candidate in names and candidate != instance: edges.append({"module":candidate,"instance":instance})
        compile_dir=Path(tempfile.mkdtemp(prefix="real-multimodule-compile-", dir="/tmp")); binary=compile_dir/"design.vvp"
        compile_files = files + EXTRA_FILES.get(root.name, [])
        completed=subprocess.run(["iverilog","-g2012","-I",str(root),"-s",top,"-o",str(binary),*[str(x) for x in compile_files]],capture_output=True,text=True,timeout=120,check=False)
        (args.output/f"{len(designs):02d}-{root.name}-compile.stdout.log").write_text(completed.stdout); (args.output/f"{len(designs):02d}-{root.name}-compile.stderr.log").write_text(completed.stderr)
        designs.append({"repository":repository,"root":str(root),"top":top,"rtl_file_count":len(files),"rtl_files":[{"path":str(x),"sha256":sha(x)} for x in files],"module_count":len(modules),"modules":modules,"hierarchy_edges":sorted(set((x["module"],x["instance"]) for x in edges)),"clock_signals":sorted(set(re.findall(r"\b(?:posedge|negedge)\s+([A-Za-z_][A-Za-z0-9_]*)", "\n".join(text_by_file.values())))),"reset_signals":sorted(set(re.findall(r"\b(?:rst|reset)[A-Za-z0-9_]*\b", "\n".join(text_by_file.values()), re.I))),"compile_status":"passed" if completed.returncode==0 else "blocked","compile_returncode":completed.returncode})
    report={"schema_version":"real-multimodule-rtl-catalog-v1","target_count":len(designs),"minimum_target_count":10,"designs":designs,"errors":errors,"status":"passed" if len(designs)>=10 and not errors and all(x["module_count"]>=2 for x in designs) else "blocked","claim_boundary":"real multi-module RTL source trees cataloged and compile-checked where supported; no functional correctness, failure localization, or physical signoff claim"}
    report["report_sha256"]=digest(report); path=args.output/"real-multimodule-rtl-catalog.json"; path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n"); print(json.dumps({"status":report["status"],"targets":report["target_count"],"compiled":sum(x["compile_status"]=="passed" for x in designs),"report":str(path)},sort_keys=True)); return 0 if report["status"]=="passed" else 1
if __name__=="__main__": raise SystemExit(main())
