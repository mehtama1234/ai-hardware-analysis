"""Independently validate the packaged real-model Colab summary."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("summary",type=Path); args=parser.parse_args(); summary=json.loads(args.summary.read_text()); expected=summary.pop("summary_sha256")
    steps=summary.get("steps",[]); checks={"summary_hash":expected==hashlib.sha256(json.dumps(summary,sort_keys=True,separators=(",",":")).encode()).hexdigest(),"status":summary.get("status")=="passed","model":bool(summary.get("model_id")),"steps":bool(steps) and all(item.get("status")=="passed" and item.get("returncode")==0 for item in steps),"repair_report":Path(summary.get("repair_report","")).is_file(),"independent_checker":any("check_real_multiclock_causal_agent_repair.py" in " ".join(item.get("command",[])) and item.get("status")=="passed" for item in steps)}
    ok=all(checks.values()); print(json.dumps({"status":"passed" if ok else "failed","checks":checks},sort_keys=True)); return 0 if ok else 1
if __name__=="__main__":raise SystemExit(main())
