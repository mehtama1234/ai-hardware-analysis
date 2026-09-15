"""Independently validate the four-task Colab archive manifest."""
from __future__ import annotations
import argparse,hashlib,json,tarfile
from pathlib import Path
REQUIRED={
 "real-four-causal-agent/config.json",
 "real-four-causal-agent/colab/run_real_four_causal_agent_remote.py",
 "real-four-causal-agent/analog-digital-chip-design-eda/verification_platform/causal.py",
 "real-four-causal-agent/analog-digital-chip-design-eda/scripts/hf_llm_batch_backend.py",
 "real-four-causal-agent/analog-digital-chip-design-eda/benchmarks/register_peripheral/tb.sv",
 "real-four-causal-agent/causal/peripheral.json",
 "real-four-causal-agent/causal/operation.json",
 "real-four-causal-agent/causal/error_budget.json",
 "real-four-causal-agent/causal/multiclock.json",
}
def main():
 p=argparse.ArgumentParser();p.add_argument("archive",type=Path);a=p.parse_args();errors=[]
 try:
  with tarfile.open(a.archive,"r:gz") as t:
   names=set(t.getnames());missing=sorted(REQUIRED-names);errors.extend("missing archive entry: "+x for x in missing)
   try:cfg=json.load(t.extractfile("real-four-causal-agent/config.json"))
   except Exception as exc:cfg={};errors.append(f"invalid config: {exc}")
   if cfg.get("tasks")!= ["peripheral","operation","error_budget","multiclock"]:errors.append("task order/config mismatch")
   if set((cfg.get("reports") or {}))!=set(cfg.get("tasks") or []):errors.append("causal report map mismatch")
 except (OSError,tarfile.TarError) as exc:errors.append(f"archive unreadable: {exc}")
 raw=a.archive.read_bytes() if a.archive.is_file() else b"";result={"schema_version":"real-four-causal-agent-colab-package-check-v1","archive":str(a.archive.resolve()),"archive_sha256":hashlib.sha256(raw).hexdigest(),"status":"passed" if not errors else "blocked","errors":sorted(errors)};result["check_sha256"]=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(",",":")).encode()).hexdigest();print(json.dumps(result,sort_keys=True));return 0 if not errors else 1
if __name__=="__main__":raise SystemExit(main())
