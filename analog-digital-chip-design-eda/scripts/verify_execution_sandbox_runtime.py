#!/usr/bin/env python3
"""Probe the Linux namespace capabilities required by isolated execution."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys


def probe(*, unshare_binary: str | None = None) -> dict[str, object]:
    binary = unshare_binary or shutil.which("unshare")
    result: dict[str, object] = {
        "schema_version": "verification-execution-sandbox-runtime-v1",
        "backend": "linux-unshare",
        "required_namespaces": ["user", "pid", "mount", "network"],
        "executable": binary or "",
        "verified": False,
    }
    if not binary:
        result["error"] = "unshare executable is unavailable"
        return result
    code = (
        "import json, os; "
        "print(json.dumps({'pid': os.getpid(), 'uid': os.getuid(), "
        "'user_ns': os.stat('/proc/self/ns/user').st_ino, "
        "'pid_ns': os.stat('/proc/self/ns/pid').st_ino, "
        "'mount_ns': os.stat('/proc/self/ns/mnt').st_ino, "
        "'net_ns': os.stat('/proc/self/ns/net').st_ino, "
        "'routes': open('/proc/net/route', encoding='utf-8').read().strip()}))"
    )
    command = [binary, "--user", "--map-root-user", "--mount", "--pid", "--fork", "--net", "--mount-proc", "--", sys.executable, "-c", code]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=10, check=False)
    except (OSError, subprocess.TimeoutExpired) as error:
        result["error"] = f"{type(error).__name__}: {error}"
        return result
    result["exit_code"] = completed.returncode
    if completed.stderr:
        result["stderr"] = completed.stderr[-500:]
    try:
        child = json.loads(completed.stdout)
    except json.JSONDecodeError:
        result["error"] = "namespace probe did not return JSON"
        return result
    result["child"] = child
    result["verified"] = (
        completed.returncode == 0
        and child.get("pid") == 1
        and child.get("uid") == 0
        and all(isinstance(child.get(name), int) and child[name] > 0 for name in ("user_ns", "pid_ns", "mount_ns", "net_ns"))
        and child.get("routes", "") == ""
    )
    if not result["verified"]:
        result["error"] = "namespace or deny-by-default network invariant failed"
    result["claim_boundary"] = "Runtime capability probe only; cluster security policy, read-only mounts, quotas, and customer egress rules still require deployment validation."
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = probe()
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    print(payload, end="")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    return 0 if result["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
