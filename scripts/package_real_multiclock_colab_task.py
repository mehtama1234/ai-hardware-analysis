"""Package the real OpenLane CDC task and causal evidence for Colab."""
from __future__ import annotations
import argparse, json, shutil, tarfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; OPENLANE=Path("/home/mehtama1/eda-tools/OpenLane"); DESIGN=Path("designs/aimc_multi_clock_control_subsystem/src")
def main():
 p=argparse.ArgumentParser();p.add_argument("--causal-report",type=Path,required=True);p.add_argument("--output",type=Path,required=True);p.add_argument("--model-id",default="Qwen/Qwen2.5-0.5B-Instruct");a=p.parse_args();a.output=a.output.resolve();a.output.parent.mkdir(parents=True,exist_ok=True)
 if not a.causal_report.is_file():raise SystemExit("causal report is required")
 source_root=OPENLANE/DESIGN
 with tarfile.open(a.output,"w:gz") as archive:
  for path in sorted((ROOT/"analog-digital-chip-design-eda/verification_platform").glob("*.py")):archive.add(path,arcname=Path("real-causal-agent/analog-digital-chip-design-eda/verification_platform")/path.name)
  for path in sorted((ROOT/"scripts").glob("*.py")):archive.add(path,arcname=Path("real-causal-agent/scripts")/path.name)
  for path in sorted((ROOT/"analog-digital-chip-design-eda/scripts").glob("*.py")):archive.add(path,arcname=Path("real-causal-agent/analog-digital-chip-design-eda/scripts")/path.name)
  for name in ("run_real_multiclock_causal_agent_remote.py","check_real_multiclock_causal_agent_remote.py"):
   path=ROOT/"analog-digital-chip-design-eda/colab"/name; archive.add(path,arcname=Path("real-causal-agent/colab")/name)
  for path in sorted(source_root.glob("*.v")):archive.add(path,arcname=Path("real-causal-agent/openlane")/DESIGN/path.name)
  archive.add(a.causal_report,arcname="real-causal-agent/causal-report.json")
  config={"model_id":a.model_id,"causal_report":"causal-report.json"}; info=ROOT/"/tmp/real-causal-colab-config.json"; info.write_text(json.dumps(config)+"\n"); archive.add(info,arcname="real-causal-agent/config.json")
 print(json.dumps({"status":"passed","archive":str(a.output),"causal_report":str(a.causal_report)},sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
