"""Run a deterministic 100-mutant, multi-family RTL verification campaign."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from verification_platform.mutation import run_mutation, summarize_mutations, validate_mutation_suite


ROOT = Path(__file__).resolve().parents[1]


def _variants(source: str, testbench: str, family: str, before: str, replacements: list[str]) -> list[dict[str, object]]:
    return [{
        "mutation_id": f"{family}-{index:02d}",
        "family": family,
        "source_file": source,
        "from": before,
        "to": replacement,
        "command": ["python3", "scripts/run_seeded_counter_check.py", source, testbench],
    } for index, replacement in enumerate(replacements, 1)]


def build_campaign() -> dict[str, object]:
    """Build 12 behavior-changing variants for each of eight seeded families."""
    mutations: list[dict[str, object]] = []
    mutations += _variants("benchmarks/seeded_arbiter/arbiter.sv", "benchmarks/repository_scale/parameterized_mutation_tb/arbiter.sv", "arbiter", "assign grant = rst ? 2'b00 : (req[0] ? 2'b01 : (req[1] ? 2'b10 : 2'b00));", [
        "assign grant = rst ? 2'b01 : (req[0] ? 2'b01 : (req[1] ? 2'b10 : 2'b00));",
        "assign grant = rst ? 2'b10 : (req[0] ? 2'b01 : (req[1] ? 2'b10 : 2'b00));",
        "assign grant = rst ? 2'b11 : (req[0] ? 2'b01 : (req[1] ? 2'b10 : 2'b00));",
        "assign grant = rst ? 2'b00 : (req[0] ? 2'b00 : (req[1] ? 2'b10 : 2'b00));",
        "assign grant = rst ? 2'b00 : (req[0] ? 2'b10 : (req[1] ? 2'b10 : 2'b00));",
        "assign grant = rst ? 2'b00 : (req[0] ? 2'b11 : (req[1] ? 2'b10 : 2'b00));",
        "assign grant = rst ? 2'b00 : (req[0] ? 2'b01 : (req[1] ? 2'b00 : 2'b00));",
        "assign grant = rst ? 2'b00 : (req[0] ? 2'b01 : (req[1] ? 2'b01 : 2'b00));",
        "assign grant = rst ? 2'b00 : (req[0] ? 2'b01 : (req[1] ? 2'b11 : 2'b00));",
        "assign grant = rst ? 2'b00 : (req[0] ? 2'b01 : 2'b10);",
        "assign grant = rst ? 2'b00 : (req[0] ? 2'b01 : 2'b01);",
        "assign grant = rst ? 2'b00 : 2'b01;",
    ])
    mutations += _variants("benchmarks/seeded_decoder/decoder.sv", "benchmarks/repository_scale/parameterized_mutation_tb/decoder.sv", "decoder", "        2'd2: decode = 4'b0100;\n        2'd3: decode = 4'b1000;", [
        f"        2'd2: decode = 4'b{value:04b};\n        2'd3: decode = 4'b1000;" for value in [0, 1, 2, 3, 8, 15]
    ] + [
        "        2'd1: decode = 4'b0010;\n        2'd3: decode = 4'b1000;",
        "        2'd2: decode = 4'b1000;\n        2'd3: decode = 4'b1000;",
        "        2'd2: decode = 4'b0100;\n        2'd3: decode = 4'b0000;",
        "        2'd2: decode = 4'b0100;\n        2'd3: decode = 4'b0001;",
        "        2'd2: decode = 4'b0100;\n        default: decode = 4'b0000;",
        "        2'd2: decode = 4'b0000;\n        2'd3: decode = 4'b1000;",
    ])
    mutations += _variants("benchmarks/seeded_fifo/fifo.sv", "benchmarks/repository_scale/parameterized_mutation_tb/fifo.sv", "fifo", "        2'b10: count <= (count < DEPTH) ? count + 3'd1 : count;", [
        "        2'b10: count <= count + 3'd1;",
        "        2'b10: count <= (count <= DEPTH) ? count + 3'd1 : count;",
        "        2'b10: count <= (count < 1) ? count + 3'd1 : count;",
        "        2'b10: count <= (count < DEPTH) ? count + 3'd2 : count;",
        "        2'b10: count <= (count < DEPTH) ? count - 3'd1 : count;",
        "        2'b10: count <= 3'd0;",
        "        2'b10: count <= 3'd1;",
        "        2'b10: count <= (count == DEPTH) ? count + 3'd1 : count;",
        "        2'b10: count <= (count < DEPTH + 1) ? count + 3'd1 : count;",
        "        2'b10: count <= (count < DEPTH) ? count : count;",
        "        2'b10: count <= (count < DEPTH + 1) ? count + 3'd1 : count;",
        "        2'b10: count <= (count <= 3'd0) ? count + 3'd1 : count;",
    ])
    mutations += _variants("benchmarks/seeded_handshake/handshake.sv", "benchmarks/repository_scale/parameterized_mutation_tb/handshake.sv", "handshake", "  assign ready = rst ? 1'b0 : 1'b1;", [
        "  assign ready = 1'b1;", "  assign ready = rst ? 1'b1 : 1'b1;", "  assign ready = rst ? 1'b0 : 1'b0;",
        "  assign ready = rst ? 1'b1 : 1'b0;", "  assign ready = rst;", "  assign ready = !(!rst);",
        "  assign ready = 1'b0;", "  assign ready = rst ? 1'bx : 1'b1;", "  assign ready = rst ? 1'bz : 1'b1;",
        "  assign ready = rst || 1'b1;", "  assign ready = rst && 1'b1;", "  assign ready = (rst == 1'b1);",
    ])
    mutations += _variants("benchmarks/seeded_parity/parity.sv", "benchmarks/repository_scale/parameterized_mutation_tb/parity.sv", "parity", "  assign even = rst ? 1'b0 : ~^data;", [
        "  assign even = rst ? 1'b0 : ^data;", "  assign even = rst ? 1'b1 : ~^data;", "  assign even = rst ? 1'b0 : ~data[0];",
        "  assign even = rst ? 1'b0 : data[2];", "  assign even = rst ? 1'b0 : (data[1] & data[2]);", "  assign even = rst ? 1'b0 : data[3];",
        "  assign even = rst ? 1'b0 : (data[0] & data[1]);", "  assign even = rst ? 1'b0 : (data[0] | data[1]);",
        "  assign even = rst ? 1'b0 : 1'b0;", "  assign even = rst ? 1'b0 : 1'b1;", "  assign even = rst ? 1'b0 : (data == 4'b0010);",
        "  assign even = rst ? 1'b0 : (data != 4'b0011);",
    ])
    mutations += _variants("benchmarks/seeded_regblock/regblock.sv", "benchmarks/repository_scale/parameterized_mutation_tb/regblock.sv", "regblock", "      if (addr == 2'd0) reg0 <= wdata;", [
        "      if (addr == 2'd1) reg0 <= wdata;", "      if (addr == 2'd2) reg0 <= wdata;", "      if (addr != 2'd0) reg0 <= wdata;",
        "      if (addr == 2'd0) reg0 <= 8'hFF;", "      if (addr == 2'd0) reg0 <= 8'h01;", "      if (addr == 2'd0) reg0 <= 8'h00;",
        "      if (addr == 2'd0) reg0 <= ~wdata;", "      if (addr == 2'd0) reg0 <= wdata + 8'd1;", "      if (addr == 2'd0) reg0 <= wdata - 8'd1;",
        "      if (addr[0]) reg0 <= wdata;", "      if (!addr[1]) reg0 <= wdata;", "      if (wr_en) reg0 <= wdata;",
    ])
    mutations += _variants("benchmarks/seeded_signed/signed_add.sv", "benchmarks/repository_scale/parameterized_mutation_tb/signed.sv", "signed", "  assign sum = rst ? 6'sd0 : {{2{a[3]}},a} + {{2{b[3]}},b};", [
        "  assign sum = rst ? 6'sd0 : {2'b00,a} + {2'b00,b};", "  assign sum = rst ? 6'sd0 : {{2{a[3]}},a} + {2'b00,b};",
        "  assign sum = rst ? 6'sd0 : {2'b00,a} + {{2{b[3]}},b};", "  assign sum = rst ? 6'sd0 : a - b;",
        "  assign sum = rst ? 6'sd0 : {{2{a[3]}},a} - {{2{b[3]}},b};", "  assign sum = rst ? 6'sd0 : {{2{a[3]}},a} + {{2{b[3]}},a};",
        "  assign sum = rst ? 6'sd0 : {{2{b[3]}},b} + {{2{b[3]}},b};", "  assign sum = rst ? 6'sd0 : -({{2{a[3]}},a} + {{2{b[3]}},b});",
        "  assign sum = rst ? 6'sd0 : {{2{a[3]}},a} + 6'sd0;", "  assign sum = rst ? 6'sd0 : {{2{b[3]}},b} + 6'sd0;",
        "  assign sum = rst ? 6'sd0 : 6'sd0;", "  assign sum = rst ? 6'sd0 : 6'sd1;",
    ])
    mutations += _variants("benchmarks/seeded_width/width_adapter.sv", "benchmarks/repository_scale/parameterized_mutation_tb/width.sv", "width", "  assign low = rst ? 4'b0000 : data[3:0];", [
        "  assign low = rst ? 4'b0000 : data[7:4];", "  assign low = rst ? 4'b0000 : data[4:1];", "  assign low = rst ? 4'b0000 : data[6:3];",
        "  assign low = rst ? 4'b0000 : data[3:1];", "  assign low = rst ? 4'b0000 : {data[2:0],1'b0};", "  assign low = rst ? 4'b0000 : 4'h0;",
        "  assign low = rst ? 4'b0000 : 4'h1;", "  assign low = rst ? 4'b0000 : 4'hA;", "  assign low = rst ? 4'b0000 : ~data[3:0];",
        "  assign low = rst ? 4'b0000 : data[3:0] + 4'd1;", "  assign low = rst ? 4'b0000 : data[3:0] - 4'd1;", "  assign low = rst ? 4'b0000 : data[0] ? 4'h1 : 4'h0;",
    ])
    if len(mutations) != 96:
        raise AssertionError(f"expected 96 generated mutations, got {len(mutations)}")
    # Add four cross-family variants to reach the declared 100-mutant target.
    mutations += _variants("benchmarks/seeded_arbiter/arbiter.sv", "benchmarks/repository_scale/parameterized_mutation_tb/arbiter.sv", "arbiter-extra", "assign grant = rst ? 2'b00 : (req[0] ? 2'b01 : (req[1] ? 2'b10 : 2'b00));", [
        "assign grant = rst ? 2'b00 : (req[0] ? 2'b10 : (req[1] ? 2'b01 : 2'b00));",
        "assign grant = rst ? 2'b00 : (req[0] ? 2'b11 : (req[1] ? 2'b11 : 2'b00));",
        "assign grant = rst ? 2'b00 : (req[0] ? 2'b00 : (req[1] ? 2'b00 : 2'b00));",
        "assign grant = rst ? 2'b00 : (req[0] ? 2'b01 : (req[1] ? 2'b01 : 2'b00));",
    ])
    return {"schema_version": "mutation-suite-v1", "name": "seeded-parameterized-100-mutant-campaign", "mutations": mutations, "claim_boundary": "100 declared deterministic same-command mutants across eight seeded RTL families; not exhaustive verification"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/repository-scale-m2/parameterized-100")
    args = parser.parse_args()
    suite = build_campaign()
    validate_mutation_suite(suite)
    with tempfile.TemporaryDirectory(prefix="parameterized-mutation-campaign-") as directory:
        staging = Path(directory)
        roots = {name: staging / name for name in ("canonical", "baseline", "candidate")}
        needed = {str(item["source_file"]) for item in suite["mutations"]} | {str(item["command"][-1]) for item in suite["mutations"]}
        for root in roots.values():
            (root / "scripts").mkdir(parents=True)
            shutil.copy2(ROOT / "scripts/run_seeded_counter_check.py", root / "scripts/run_seeded_counter_check.py")
            for relative in needed:
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / relative, destination)
            from scripts.run_seeded_multi_mutation_demo import FILES
            for relative, (buggy, good) in FILES.items():
                source = root / relative
                text = source.read_text(encoding="utf-8")
                if text.count(buggy) != 1:
                    raise RuntimeError(f"could not normalize seeded source: {relative}")
                source.write_text(text.replace(buggy, good), encoding="utf-8")
        results = []
        for index, mutation in enumerate(suite["mutations"]):
            source = Path(str(mutation["source_file"]))
            shutil.copy2(roots["canonical"] / source, roots["candidate"] / source)
            results.append(run_mutation(mutation, canonical_root=roots["canonical"], baseline_root=roots["baseline"], candidate_root=roots["candidate"], output_root=args.output / f"{index:03d}-{mutation['mutation_id']}"))
    report = summarize_mutations(results)
    report.update({"campaign": suite["name"], "total_declared": len(suite["mutations"]), "mutation_ids": [item["result"]["mutation_id"] for item in results]})
    report["report_sha256"] = hashlib.sha256(json.dumps({key: value for key, value in report.items() if key != "report_sha256"}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "mutation-closure-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "total": report["total_mutations"], "detected": report["detected_mutations"], "mutation_score": report["mutation_score"], "false_passes": report["false_pass_count"], "report": str(args.output / "mutation-closure-report.json")}, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
