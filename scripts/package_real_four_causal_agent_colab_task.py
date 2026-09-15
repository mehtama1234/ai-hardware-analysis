"""Package the four real causal-agent repair tasks for Colab GPU execution."""
from __future__ import annotations
import argparse,json,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OPENLANE=Path("/home/mehtama1/eda-tools/OpenLane")
TASKS={"peripheral":Path("designs/peripheral/src"),"operation":Path("designs/aimc_operation_partition_physical/src"),"error_budget":Path("designs/aimc_error_budget_governor_physical/src"),"multiclock":Path("designs/aimc_multi_clock_control_subsystem/src")}
def main():
 p=argparse.ArgumentParser();p.add_argument("--peripheral-causal-report",type=Path,required=True);p.add_argument("--operation-causal-report",type=Path,required=True);p.add_argument("--error-budget-causal-report",type=Path,required=True);p.add_argument("--multiclock-causal-report",type=Path,required=True);p.add_argument("--output",type=Path,required=True);p.add_argument("--model-id",default="Qwen/Qwen2.5-0.5B-Instruct");a=p.parse_args();a.output=a.output.resolve();a.output.parent.mkdir(parents=True,exist_ok=True);reports={"peripheral":a.peripheral_causal_report,"operation":a.operation_causal_report,"error_budget":a.error_budget_causal_report,"multiclock":a.multiclock_causal_report}
 if any(not x.is_file() for x in reports.values()):raise SystemExit("all four causal reports are required")
 with tarfile.open(a.output,"w:gz") as archive:
  def add(path,arc):archive.add(path,arcname=Path("real-four-causal-agent")/arc)
  for path in sorted((ROOT/"analog-digital-chip-design-eda/verification_platform").glob("*.py")):add(path,Path("analog-digital-chip-design-eda/verification_platform")/path.name)
  for path in sorted((ROOT/"scripts").glob("*.py")):add(path,Path("scripts")/path.name)
  for path in sorted((ROOT/"analog-digital-chip-design-eda/scripts").glob("*.py")):add(path,Path("analog-digital-chip-design-eda/scripts")/path.name)
  add(ROOT/"analog-digital-chip-design-eda/colab/run_real_four_causal_agent_remote.py",Path("colab/run_real_four_causal_agent_remote.py"))
  add(ROOT/"analog-digital-chip-design-eda/benchmarks/register_peripheral/tb.sv",Path("analog-digital-chip-design-eda/benchmarks/register_peripheral/tb.sv"))
  for key,rel in TASKS.items():
   for path in sorted((OPENLANE/rel).glob("*.v"))+sorted((OPENLANE/rel).glob("*.sv")):add(path,Path("openlane")/rel/path.name)
  for key,path in reports.items():add(path,Path("causal")/(key+".json"))
  config={"model_id":a.model_id,"reports":{key:"causal/"+key+".json" for key in reports},"tasks":["peripheral","operation","error_budget","multiclock"]};temp=ROOT/"/tmp/real-four-causal-colab-config.json";temp.write_text(json.dumps(config,sort_keys=True)+"\n");add(temp,Path("config.json"))
 print(json.dumps({"status":"passed","archive":str(a.output),"tasks":list(reports)},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
