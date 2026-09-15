"""Independently validate the development replay queue."""
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
 p=argparse.ArgumentParser(); p.add_argument("queue",type=Path); a=p.parse_args(); q=json.loads(a.queue.read_text()); errors=[]; items=q.get("queue",[]); keys={(x.get("repository"),x.get("commit")) for x in items}
 if q.get("schema_version")!="historical-replay-queue-v1" or len(items)!=q.get("target_queue_size"): errors.append("queue schema or size mismatch")
 if any(matches_validated(key) for key in keys): errors.append("validated commit appears in queue")
 if any(x.get("validation_status")!="candidate_only" for x in items): errors.append("queue entry promoted without validation")
 u=dict(q); recorded=u.pop("queue_sha256",None)
 if recorded!=digest(u): errors.append("queue digest mismatch")
 out={"schema_version":"historical-replay-queue-check-v1","status":"passed" if not errors else "blocked","errors":errors,"queue":str(a.queue)}; out["check_sha256"]=digest(out); print(json.dumps(out,sort_keys=True)); return 0 if not errors else 1
if __name__=="__main__": raise SystemExit(main())
