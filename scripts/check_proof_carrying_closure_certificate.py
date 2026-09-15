"""Independently check a proof-carrying closure certificate and its evidence."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
REQUIRED={"simulation","mutation","formal","coverage","security","assertion_integrity"}
def digest(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
def main():
    parser=argparse.ArgumentParser(); parser.add_argument("certificate",type=Path); args=parser.parse_args(); cert=json.loads(args.certificate.read_text(encoding="utf-8")); errors=[]
    if cert.get("schema_version")!="proof-carrying-closure-certificate-v1": errors.append("schema mismatch")
    if cert.get("status")!="passed": errors.append("certificate is not passed")
    if set(cert.get("required_roles",[]))!=REQUIRED or set(cert.get("evidence",{}))!=REQUIRED: errors.append("required evidence roles are incomplete")
    aggregate=Path(cert.get("aggregate_report",""))
    if not aggregate.is_file() or hashlib.sha256(aggregate.read_bytes()).hexdigest()!=cert.get("aggregate_sha256"): errors.append("aggregate digest mismatch")
    for role, item in cert.get("evidence",{}).items():
        path=Path(item.get("path",""))
        if not path.is_file(): errors.append(f"missing evidence: {role}"); continue
        if hashlib.sha256(path.read_bytes()).hexdigest()!=item.get("sha256"): errors.append(f"evidence digest mismatch: {role}")
    unsigned=dict(cert); actual=unsigned.pop("certificate_sha256",None)
    if actual!=digest(unsigned): errors.append("certificate digest mismatch")
    result={"schema_version":"proof-carrying-closure-certificate-check-v1","status":"passed" if not errors else "blocked","errors":sorted(set(errors)),"certificate":str(args.certificate)}; result["check_sha256"]=digest(result); print(json.dumps(result,sort_keys=True)); return 0 if not errors else 1
if __name__=="__main__": raise SystemExit(main())
