"""Run a disposable runtime smoke test for a verification-pilot image."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import time
import urllib.error
import http.client
import urllib.request
import uuid


def run(image: str, *, port: int = 18080, timeout: float = 30.0, sandbox_probe: bool = False, security_opts: list[str] | None = None) -> list[str]:
    name = "verification-pilot-runtime-" + uuid.uuid4().hex[:10]
    errors: list[str] = []
    try:
        command = ["docker", "run", "-d", "--rm", "--name", name]
        for option in security_opts or []:
            command.extend(["--security-opt", option])
        command.extend(["-p", f"{port}:8080", "-e", "VERIFICATION_SERVICE_API_KEY=runtime-smoke-key", image])
        started = subprocess.run(
            command,
            check=False, capture_output=True, text=True,
        )
        if started.returncode:
            return [f"docker run failed: {started.stderr.strip()}"]
        for endpoint in ("healthz", "readyz"):
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                try:
                    with urllib.request.urlopen(f"http://127.0.0.1:{port}/{endpoint}", timeout=2) as response:
                        if response.status == 200:
                            break
                except (urllib.error.URLError, http.client.RemoteDisconnected, TimeoutError, ConnectionError):
                    time.sleep(0.5)
            else:
                errors.append(f"/{endpoint} did not return 200 before timeout")
        uid = subprocess.run(["docker", "exec", name, "id", "-u"], check=False, capture_output=True, text=True)
        if uid.returncode or uid.stdout.strip() != "10001":
            errors.append(f"container UID must be 10001 (observed {uid.stdout.strip() or uid.stderr.strip()})")
        if sandbox_probe:
            probe = subprocess.run(
                ["docker", "exec", name, "python3", "scripts/verify_execution_sandbox_runtime.py"],
                check=False, capture_output=True, text=True,
            )
            if probe.returncode:
                detail = (probe.stderr or probe.stdout).strip().replace("\n", " ")
                errors.append(f"execution sandbox probe failed inside image: {detail[:240] or 'no probe output'}")
    except FileNotFoundError:
        errors.append("docker executable is required")
    finally:
        subprocess.run(["docker", "stop", name], check=False, capture_output=True, text=True)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image")
    parser.add_argument("--port", type=int, default=18080)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--sandbox-probe", action="store_true")
    parser.add_argument("--security-opt", action="append", default=[], help="explicit Docker security-opt policy for the runtime smoke")
    parser.add_argument("--output", type=Path, help="write a bounded runtime evidence JSON")
    args = parser.parse_args()
    errors = run(args.image, port=args.port, timeout=args.timeout, sandbox_probe=args.sandbox_probe, security_opts=args.security_opt)
    inspect = subprocess.run(["docker", "image", "inspect", args.image, "--format", "{{.Id}}"], check=False, capture_output=True, text=True)
    evidence = {
        "schema_version": "verification-image-runtime-v1",
        "image": args.image,
        "image_id": inspect.stdout.strip() or None,
        "sandbox_probe_requested": args.sandbox_probe,
        "security_options": list(args.security_opt),
        "verified": not errors,
        "errors": errors,
        "claim_boundary": "Disposable container liveness, readiness, UID, and optional sandbox probe only; target-cluster policy, managed dependencies, HA, and customer production readiness require separate evidence.",
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"PASS: runtime smoke ({args.image})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
