"""Build the next replay queue without consuming held-out candidates."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
VALIDATED={
    ("OpenLane", "6042457d"),
    ("OpenROAD-flow-scripts", "c178fbb7"),
    ("OpenLane", "1c950442"),
    ("OpenROAD-flow-scripts", "304e5765"),
    ("OpenROAD-flow-scripts", "53d01015"),
    ("OpenLane", "9dbd8b5e"),
    ("OpenLane", "de7e2ca3"),
    ("OpenROAD-flow-scripts", "4b688827"),
    ("cross-sim", "adbf6800"),
    ("OpenLane", "54d5b5a3"),
    ("OpenLane", "09cfff0d"),
    ("OpenLane", "074a92b7"),
    ("OpenLane", "023f6673"),
    ("OpenLane", "1d46ea5f"), ("OpenLane", "24dcb51e"),
    ("OpenLane", "f507637d"), ("OpenLane", "6c80fdbc"),
    ("OpenLane", "b5b0bbdf"), ("OpenLane", "4eab9f70"),
    ("OpenLane", "0b94d33d"), ("OpenLane", "0e8827eb"),
    ("OpenLane", "5ba7fa07"), ("OpenLane", "4ced43c5"),
    ("OpenLane", "08587051"), ("OpenLane", "41ed0036"),
    ("OpenLane", "fe0ba006"), ("OpenROAD-flow-scripts", "bad83a4f1"),
    ("OpenLane", "0e33bf4c"), ("OpenLane", "c5763988"),
    ("OpenLane", "7ea7a2ae"), ("cross-sim", "d9548c0"),
    ("OpenLane", "cb59d1f8"), ("OpenLane", "0687a36b"),
    ("OpenLane", "f4f8dad8"), ("OpenLane", "18a1df43"),
    ("OpenLane", "281281cc"),
    ("OpenLane", "413d3010"),
    ("OpenLane", "e99deff7"),
    ("OpenLane", "4c1c6538"),
    ("OpenLane", "cb634fd5"),
    ("OpenLane", "48004937"),
    ("OpenLane", "d4b42bd1"),
    ("OpenLane", "a664c0e1"),
    ("OpenROAD-flow-scripts", "91844308"),
    ("OpenLane", "b43df386"),
    ("OpenLane", "c98a290f"),
    ("OpenLane", "5f20beb7"),
    ("OpenLane", "01e95109"),
    ("OpenLane", "11dcdbbc"),
    ("OpenLane", "14ef870b"),
}
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def matches_validated(key): return any(key[0] == repo and str(key[1]).startswith(commit) for repo, commit in VALIDATED)
def main():
    p=argparse.ArgumentParser(); p.add_argument("manifest",type=Path); p.add_argument("--output",type=Path,required=True); p.add_argument("--size",type=int,default=40); a=p.parse_args(); m=json.loads(a.manifest.read_text()); held={tuple(x) for x in m.get("heldout_keys",[])}; candidates=[]
    for item in m.get("candidates",[]):
        key=(item.get("repository"),item.get("commit"))
        if key not in held and not matches_validated(key): candidates.append(item)
    candidates=sorted(candidates,key=lambda x:(len(x.get("files",[])),x.get("repository",""),x.get("commit","")))[:a.size]
    body={"schema_version":"historical-replay-queue-v1","queue_size":len(candidates),"target_queue_size":a.size,"validated_excluded":len(VALIDATED),"heldout_excluded":len(held),"queue":[{"repository":x["repository"],"commit":x["commit"],"parent":x.get("parent"),"subject":x["subject"],"files":x["files"],"validation_status":"candidate_only"} for x in candidates],"claim_boundary":"ordered development queue only; entries require regression reconstruction and agent repair validation"}; body["queue_sha256"]=digest(body); a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(body,indent=2,sort_keys=True)+"\n"); print(json.dumps({"status":"passed" if len(candidates)==a.size else "blocked","queue_size":len(candidates),"queue":str(a.output)},sort_keys=True)); return 0 if len(candidates)==a.size else 1
if __name__=="__main__": raise SystemExit(main())
