"""Run mutation closure across the seeded RTL design and bug-variant matrix."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from verification_platform.mutation import run_mutation, summarize_mutations, validate_mutation_suite


ROOT = Path(__file__).resolve().parents[1]
SUITE_PATH = ROOT / "benchmarks/repository_scale/seeded_multi_mutation_suite.json"
FILES = {
    "benchmarks/seeded_arbiter/arbiter.sv": ("assign grant = rst ? 2'b00 : (req[0] ? 2'b01 : 2'b00);", "assign grant = rst ? 2'b00 : (req[0] ? 2'b01 : (req[1] ? 2'b10 : 2'b00));"),
    "benchmarks/seeded_decoder/decoder.sv": ("        2'd3: decode = 4'b1000;", "        2'd2: decode = 4'b0100;\n        2'd3: decode = 4'b1000;"),
    "benchmarks/seeded_fifo/fifo.sv": ("        2'b10: count <= count + 3'd1;", "        2'b10: count <= (count < DEPTH) ? count + 3'd1 : count;"),
    "benchmarks/seeded_handshake/handshake.sv": ("  assign ready = 1'b1; // SEEDED_BUG: ready must be low during reset", "  assign ready = rst ? 1'b0 : 1'b1;"),
    "benchmarks/seeded_parity/parity.sv": ("  assign even = rst ? 1'b0 : ^data;", "  assign even = rst ? 1'b0 : ~^data;"),
    "benchmarks/seeded_regblock/regblock.sv": ("      if (addr == 2'd0) reg0 <= wdata;\n      else reg0 <= wdata; // SEEDED_BUG: nonzero addresses must be ignored", "      if (addr == 2'd0) reg0 <= wdata;"),
    "benchmarks/seeded_signed/signed_add.sv": ("  assign sum = rst ? 6'sd0 : {2'b00,a} + {2'b00,b};", "  assign sum = rst ? 6'sd0 : {{2{a[3]}},a} + {{2{b[3]}},b};"),
    "benchmarks/seeded_width/width_adapter.sv": ("  assign low = rst ? 4'b0000 : data[7:4];", "  assign low = rst ? 4'b0000 : data[3:0];")
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/repository-scale-m2/multi-design")
    args = parser.parse_args()
    suite = json.loads(SUITE_PATH.read_text(encoding="utf-8"))
    validate_mutation_suite(suite)
    with tempfile.TemporaryDirectory(prefix="multi-mutation-demo-") as directory:
        staging = Path(directory)
        roots = {name: staging / name for name in ("canonical", "baseline", "candidate")}
        needed = {item["source_file"] for item in suite["mutations"]} | {item["command"][-1] for item in suite["mutations"]}
        for root in roots.values():
            (root / "scripts").mkdir(parents=True)
            shutil.copy2(ROOT / "scripts/run_seeded_counter_check.py", root / "scripts/run_seeded_counter_check.py")
            for relative in needed:
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / relative, destination)
            for relative, (buggy, good) in FILES.items():
                source = root / relative
                text = source.read_text(encoding="utf-8")
                if text.count(buggy) != 1:
                    raise RuntimeError(f"could not normalize seeded source: {relative}")
                source.write_text(text.replace(buggy, good), encoding="utf-8")
        results = []
        for index, mutation in enumerate(suite["mutations"]):
            # Each mutation gets a fresh candidate copy; multiple variants may
            # target the same source file and must not compound edits.
            source = Path(mutation["source_file"])
            shutil.copy2(roots["canonical"] / source, roots["candidate"] / source)
            results.append(run_mutation(mutation, canonical_root=roots["canonical"], baseline_root=roots["baseline"], candidate_root=roots["candidate"], output_root=args.output / f"{index:02d}-{mutation['mutation_id']}"))
    report = summarize_mutations(results)
    report["mutation_ids"] = [item["result"]["mutation_id"] for item in results]
    (args.output / "mutation-closure-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "total": report["total_mutations"], "detected": report["detected_mutations"], "mutation_score": report["mutation_score"], "false_passes": report["false_pass_count"], "report": str(args.output / "mutation-closure-report.json")}, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
