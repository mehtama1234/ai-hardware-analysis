#!/usr/bin/env python3
"""Compile and run the native CUDA paged-attention correctness kernel."""
from __future__ import annotations
import hashlib,json,shutil,subprocess,tempfile
from datetime import datetime,timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT_CANDIDATE=HERE.parents[2]
CURRICULUM=ROOT_CANDIDATE if (ROOT_CANDIDATE/"model-integration").is_dir() else ROOT_CANDIDATE/"gpu-mode-curriculum"
KERNEL=HERE/"paged_attention.cu"; RUNNER=HERE/"paged_attention_runner.cu"; OUT=CURRICULUM/"model-integration/reports/paged-attention-cuda.json"
def main():
    nvcc=shutil.which("nvcc"); report={"experiment":"paged_attention_cuda","generated_at":datetime.now(timezone.utc).isoformat(),"source_sha256":{n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in (("kernel",KERNEL),("runner",RUNNER),("launcher",Path(__file__)))},"gpu_execution_accepted":False,"measured":False}
    if not nvcc: report.update(status="unavailable",reason="nvcc not found on PATH",scope="native CUDA paged-attention source present; no compiler/runtime")
    else:
        with tempfile.TemporaryDirectory(prefix="paged-attention-cuda-") as build:
            binary=Path(build)/"paged_attention"; c=subprocess.run([nvcc,"-O3","-std=c++17",str(KERNEL),str(RUNNER),"-o",str(binary)],cwd=HERE,capture_output=True,text=True,timeout=180)
            if c.returncode: report.update(status="compile-failed",stderr_tail=c.stderr[-4000:])
            else:
                r=subprocess.run([str(binary)],cwd=HERE,capture_output=True,text=True,timeout=180);report.update(status="passed" if r.returncode==0 else "run-failed",measured=r.returncode==0,stdout=r.stdout[-4000:],stderr=r.stderr[-4000:])
                if r.returncode==0:
                    try: payload=json.loads(r.stdout.strip().splitlines()[-1]);report["native"]=payload;report["gpu_execution_accepted"]=payload.get("gpu_execution_accepted") is True and payload.get("max_abs_error",99)<2e-5
                    except (ValueError,IndexError): report["status"]="invalid-output"
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(report,indent=2,allow_nan=False)+"\n");print(json.dumps({"status":report["status"],"gpu_execution_accepted":report["gpu_execution_accepted"]},indent=2));return 0 if report["gpu_execution_accepted"] else (2 if report["status"]=="unavailable" else 1)
if __name__=="__main__":raise SystemExit(main())
