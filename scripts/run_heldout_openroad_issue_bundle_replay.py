#!/usr/bin/env python3
"""Replay the held-out OpenROAD issue-runner self-containment fix."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


UPSTREAM = Path("/home/mehtama1/eda-tools/OpenROAD-flow-scripts")
COMMIT = "7b6f366962eb093f7f76c136892a2950b9caebdb"
PARENT = "d90873f47b79f343c6be15210ce398e1383c08e"
SOURCE = "flow/util/makeIssue.sh"


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def show(revision: str) -> bytes:
    return subprocess.run(["git", "-C", str(UPSTREAM), "show", f"{revision}:{SOURCE}"], capture_output=True, check=True).stdout


def generated_runner(source: bytes, root: Path) -> Path:
    text = source.decode()
    matches = re.findall(r"else\ncat > \$\{RUN_ME_SCRIPT\} <<EOF\n(.*?)\nEOF", text, re.S)
    if not matches:
        raise RuntimeError("could not extract OpenROAD runner template")
    template = matches[-1]
    original = root / "original-workspace"
    extracted = root / "extracted-bundle"
    original.mkdir(parents=True)
    extracted.mkdir(parents=True)
    vars_file = original / "vars-demo.sh"
    vars_file.write_text("export TEST_BUNDLE_VALUE=portable\n", encoding="utf-8")
    script_text = template.replace("${VARS_BASENAME}", str(original / "vars-demo")).replace("${SCRIPTS_DIR}", str(original / "scripts")).replace("${ISSUE_TARGET}", "demo")
    # makeIssue.sh writes an unquoted heredoc: escaped dollars survive into
    # the generated runner as literal shell syntax, while $(basename ...) is
    # evaluated during generation.
    script_text = script_text.replace("\\$", "$")
    script_text = script_text.replace(f"$(basename {original / 'vars-demo'})", "vars-demo")
    script = original / "run-me-demo.sh"
    script.write_text("#!/usr/bin/env bash\nset -e\n" + script_text, encoding="utf-8")
    script.chmod(0o755)
    extracted_script = extracted / script.name
    extracted_vars = extracted / vars_file.name
    extracted_script.write_text(script.read_text(encoding="utf-8"), encoding="utf-8")
    extracted_vars.write_text(vars_file.read_text(encoding="utf-8"), encoding="utf-8")
    extracted_script.chmod(0o755)
    bin_dir = extracted / "bin"
    bin_dir.mkdir()
    fake_tool = bin_dir / "openroad"
    fake_tool.write_text("#!/usr/bin/env bash\nprintf '%s\\n' \"$TEST_BUNDLE_VALUE\"\n", encoding="utf-8")
    fake_tool.chmod(0o755)
    shutil.rmtree(original)
    completed = subprocess.run([str(extracted_script)], cwd=extracted, env={"PATH": f"{bin_dir}:/usr/bin:/bin"}, capture_output=True, text=True, check=False)
    return {"returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr, "runner_text": script_text}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    parent_source = show(f"{COMMIT}^")
    fixed_source = show(COMMIT)
    (output / "parent-makeIssue.sh").write_bytes(parent_source)
    (output / "fixed-makeIssue.sh").write_bytes(fixed_source)
    with tempfile.TemporaryDirectory(prefix="heldout-openroad-issue-bundle-") as td:
        parent = generated_runner(parent_source, Path(td) / "parent")
        fixed = generated_runner(fixed_source, Path(td) / "fixed")
    report = {
        "schema_version": "heldout-openroad-issue-bundle-replay-v1",
        "repository": "OpenROAD-flow-scripts",
        "commit": COMMIT,
        "parent": PARENT,
        "subject": "fix: make issue tarballs self-contained when WORK_HOME differs",
        "source": SOURCE,
        "source_snapshots": {
            "parent": {"path": "parent-makeIssue.sh", "sha256": hashlib.sha256(parent_source).hexdigest(), "size_bytes": len(parent_source)},
            "fixed": {"path": "fixed-makeIssue.sh", "sha256": hashlib.sha256(fixed_source).hexdigest(), "size_bytes": len(fixed_source)},
        },
        "contract": {"extracted_runner_must_work_without_original_workspace": True, "package_installation_performed": False},
        "parent_result": parent,
        "fixed_result": fixed,
        "status": "passed" if parent["returncode"] != 0 and fixed["returncode"] == 0 and fixed["stdout"].strip() == "portable" else "blocked",
        "claim_boundary": "generated OpenROAD issue-runner self-containment contract replayed in a disposable extraction directory; no full tarball flow, no tool signoff, no agent repair, and no model-generalization claim",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    report["report_sha256"] = digest(report)
    (output / "replay-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "output": str(output)}, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
