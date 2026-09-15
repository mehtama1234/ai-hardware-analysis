#!/usr/bin/env python3
"""Independently check durable historical breadth and split evidence."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

def sha256(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def digest(value: object) -> str: return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("receipt",type=Path); args=parser.parse_args(); receipt_path=args.receipt.resolve(); errors=[]
    try: receipt=json.loads(receipt_path.read_text(encoding="utf-8")); candidate=json.loads((receipt_path.parent/"historical-fix-candidate-manifest.json").read_text()); queue=json.loads((receipt_path.parent/"historical-replay-queue.json").read_text())
    except (OSError,json.JSONDecodeError) as exc: print(json.dumps({"status":"blocked","errors":[str(exc)]})); return 1
    unsigned={k:v for k,v in receipt.items() if k!="receipt_sha256"}
    if receipt.get("schema_version")!="historical-breadth-evidence-v1" or receipt.get("receipt_sha256")!=digest(unsigned): errors.append("receipt schema or digest mismatch")
    candidates=candidate.get("candidates",[]); development={tuple(x) for x in candidate.get("development_keys",[])}; heldout={tuple(x) for x in candidate.get("heldout_keys",[])}; queue_items=queue.get("queue",[])
    repos={x.get("repository") for x in candidates}; queue_keys={(x.get("repository"),x.get("commit")) for x in queue_items}
    if candidate.get("candidate_count")!=len(candidates) or len(candidates)<50 or len(repos)<3: errors.append("candidate breadth is below 50 items across three repositories")
    if candidate.get("development_count")!=len(development) or candidate.get("heldout_count")!=len(heldout) or len(heldout)<15: errors.append("development/held-out split counts are incomplete")
    if development & heldout or not queue_keys.issubset(development): errors.append("development/held-out/queue split leaks or is inconsistent")
    if candidate.get("validated_replay_count",0)<50 or queue.get("queue_size")!=len(queue_items) or queue.get("target_queue_size")!=len(queue_items): errors.append("validated replay or queue breadth is incomplete")
    if any(x.get("validation_status")!="candidate_only" for x in queue_items): errors.append("queue contains an unclassified entry")
    for name,item in receipt.get("artifacts",{}).items():
        path=receipt_path.parent/item.get("path","")
        if not path.is_file() or sha256(path)!=item.get("sha256"): errors.append(f"artifact digest mismatch: {name}")
    if receipt.get("status")!="passed": errors.append("receipt is not passed")
    result={"schema_version":"historical-breadth-evidence-check-v1","status":"passed" if not errors else "blocked","receipt":str(receipt_path),"metrics":receipt.get("metrics",{}),"errors":sorted(set(errors))}; result["check_sha256"]=digest(result); print(json.dumps(result,sort_keys=True)); return 0 if not errors else 1
if __name__ == "__main__": raise SystemExit(main())
