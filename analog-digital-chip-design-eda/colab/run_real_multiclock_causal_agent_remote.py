"""Run the packaged real OpenLane causal-agent task on a Colab GPU."""
from __future__ import annotations
import hashlib,json,os,subprocess,tarfile
from pathlib import Path
CONTENT=Path("/content"); ARCHIVE=CONTENT/"real-causal-agent.tgz"; WORK=CONTENT/"real-causal-agent"; OUT=WORK/"artifacts"; SUMMARY=OUT/"real-causal-agent-colab-summary.json"
def write(path,payload):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
def main():
 with tarfile.open(ARCHIVE,"r:gz") as archive:archive.extractall(CONTENT,filter="data")
 cfg=json.loads((WORK/"config.json").read_text()); model_id=str(cfg["model_id"]); model_dir=WORK/"model"; model_dir.mkdir(exist_ok=True); env=os.environ.copy(); env.update({"OPENLANE_REPO_ROOT":str(WORK/"openlane"),"VERIFICATION_LLM_BATCH_COMMAND":"python3 analog-digital-chip-design-eda/scripts/hf_llm_batch_backend.py","VERIFICATION_HF_MODEL":str(model_dir),"VERIFICATION_HF_DEVICE":"cuda","VERIFICATION_HF_JSON_CONSTRAINED":"1","VERIFICATION_HF_MAX_NEW_TOKENS":"512"})
 steps=[]
 for command,timeout in [(["bash","-lc","nvidia-smi --query-gpu=name,memory.total --format=csv,noheader"],60),(["python3","-m","pip","install","-q","transformers==4.51.3","huggingface_hub","torch","lm-format-enforcer"],1800),(["python3","-c","from huggingface_hub import snapshot_download; import os; snapshot_download(os.environ['MODEL_ID'], local_dir=os.environ['MODEL_DIR'])"],3600)]:
  local=env|{"MODEL_ID":model_id,"MODEL_DIR":str(model_dir)}; result=subprocess.run(command,cwd=WORK,env=local,capture_output=True,text=True,timeout=timeout);steps.append({"command":command,"returncode":result.returncode,"status":"passed" if result.returncode==0 else "blocked","stdout_tail":result.stdout[-3000:],"stderr_tail":result.stderr[-3000:]});
  if result.returncode:break
 if all(x["status"]=="passed" for x in steps):
  result=subprocess.run(["python3","scripts/run_real_multiclock_agent_repair.py","--backend","local","--causal-report",str(WORK/"causal-report.json"),"--output",str(OUT/"repair")],cwd=WORK,env=env,capture_output=True,text=True,timeout=7200);steps.append({"command":["python3","scripts/run_real_multiclock_agent_repair.py"],"returncode":result.returncode,"status":"passed" if result.returncode==0 else "blocked","stdout_tail":result.stdout[-3000:],"stderr_tail":result.stderr[-3000:]})
 report=OUT/"repair/real-openlane-multiclock-agent-repair-report.json"
 if report.is_file() and all(x["status"]=="passed" for x in steps):
  check=subprocess.run(["python3","scripts/check_real_multiclock_causal_agent_repair.py",str(report)],cwd=WORK,capture_output=True,text=True);steps.append({"command":["python3","scripts/check_real_multiclock_causal_agent_repair.py",str(report)],"returncode":check.returncode,"status":"passed" if check.returncode==0 else "blocked","stdout_tail":check.stdout[-3000:],"stderr_tail":check.stderr[-3000:]})
 summary={"schema_version":"real-multiclock-causal-agent-colab-summary-v1","model_id":model_id,"steps":steps,"repair_report":str(report),"status":"passed" if report.is_file() and all(x["status"]=="passed" for x in steps) else "blocked","claim_boundary":"real Qwen Colab execution of one packaged OpenLane causal-agent repair; not broad model generalization or signoff"};summary["summary_sha256"]=hashlib.sha256(json.dumps(summary,sort_keys=True,separators=(",",":")).encode()).hexdigest();write(SUMMARY,summary);return 0 if summary["status"]=="passed" else 1
if __name__=="__main__":raise SystemExit(main())
