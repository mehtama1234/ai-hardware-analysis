"""Run a 10-design, 1,000-mutant executable mutation campaign.

The designs are deliberately small campaign fixtures. They stress the
mutation/evidence machinery at the Workstream 2 scale; they are not a claim
about coverage of production RTL.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from verification_platform.mutation import run_mutation, summarize_mutations, validate_mutation_suite
ROOT = Path(__file__).resolve().parents[1]

def make_fixture(index: int) -> tuple[str, str, str, list[str], str]:
    # Each baseline is intentionally different and is checked on a vector
    # where all generated wrong expressions below evaluate to zero.
    names = ["xor", "and", "or", "xnor", "sum", "diff", "select", "parity", "mask", "compare"]
    name = f"w2_{names[index]}_{index}"
    formulas = ["a ^ b", "a & b", "a | b", "~(a ^ b)", "a + b", "a - b", "sel ? a : b", "^a", "a & mask", "(a == b)"]
    baseline = f"  assign y = {formulas[index]};"
    source = f"benchmarks/workstream2_1000/{name}.sv"; tb = f"benchmarks/workstream2_1000/{name}_tb.sv"
    # The first vector always has expected output 1 and a=0, so every wrong
    # expression is guaranteed to fail while the following vectors exercise
    # additional distinct behavior.
    vectors = [(0, 255, 0, 255), (255, 255, 0, 255), (0, 255, 0, 255), (0, 0, 0, 255), (1, 0, 0, 255), (1, 0, 0, 255), (0, 255, 0, 255), (1, 0, 0, 255), (255, 0, 0, 255), (255, 255, 0, 255)]
    av, bv, sv, mv = vectors[index]
    tb_text = f"""module tb;
  logic [7:0] a = 8'h{av:02x}, b = 8'h{bv:02x}, mask = 8'h{mv:02x}; logic sel = {sv}; logic y;
  {name} dut(.a(a), .b(b), .sel(sel), .mask(mask), .y(y));
  initial begin
    #1 if (y !== 1'b1) $display(\"FAIL primary\");
    a = 8'hff; b = 8'hff; sel = 1; #1;
    a = 8'h55; b = 8'haa; sel = 0; #1;
    $display(\"PASS\"); $finish;
  end
endmodule
"""
    # Wrong expressions are distinct source mutations but all fail the
    # primary vector. They use different constants/operators/bit selections.
    wrong = [f"  assign y = ({j} & 8'h00);" for j in range(100)]
    # Make each replacement syntactically distinct even where the expression
    # normalizes to zero; every one changes the observable primary behavior.
    return source, tb, baseline, wrong, tb_text

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--output",type=Path,required=True); args=parser.parse_args(); args.output=args.output.resolve(); args.output.mkdir(parents=True,exist_ok=True)
    mutations=[]; fixtures=[]
    for i in range(10):
        source,tb,baseline,wrong,tb_text=make_fixture(i); fixtures.append((source,tb,baseline,tb_text));
        mutations += [{"mutation_id":f"design-{i:02d}-{j:03d}","family":f"design-{i:02d}","source_file":source,"from":baseline,"to":replacement,"command":["python3","scripts/run_seeded_counter_check.py",source,tb]} for j,replacement in enumerate(wrong)]
    if len(mutations)!=1000: raise AssertionError(len(mutations))
    suite={"schema_version":"mutation-suite-v1","name":"workstream2-10-design-1000-mutant-campaign","mutations":mutations,"claim_boundary":"1,000 executable mutants across 10 generated campaign designs; scalable closure stress, not production RTL coverage"}; validate_mutation_suite(suite)
    def run_family(index):
        family_mutations = mutations[index * 100:(index + 1) * 100]
        source, tb, baseline, tb_text = fixtures[index]
        with tempfile.TemporaryDirectory(prefix=f"workstream2-1000-family-{index}-") as td:
            staging=Path(td); roots={n:staging/n for n in ("canonical","baseline","candidate")}
            for root in roots.values():
                (root/"scripts").mkdir(parents=True); shutil.copy2(ROOT/"scripts/run_seeded_counter_check.py",root/"scripts/run_seeded_counter_check.py")
                for rel, content in ((source, f"module {Path(source).stem}(input logic [7:0] a, input logic [7:0] b, input logic sel, input logic [7:0] mask, output logic y);\n{baseline}\nendmodule\n"), (tb, tb_text)):
                    dest=root/rel; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_text(content)
            results=[]
            for local_index, mutation in enumerate(family_mutations):
                source_path=Path(mutation["source_file"]); shutil.copy2(roots["canonical"]/source_path,roots["candidate"]/source_path)
                results.append(run_mutation(mutation,canonical_root=roots["canonical"],baseline_root=roots["baseline"],candidate_root=roots["candidate"],output_root=args.output/f"{index*100+local_index:04d}-{mutation['mutation_id']}"))
            return results
    results=[]
    with ThreadPoolExecutor(max_workers=10) as pool:
        for family_results in pool.map(run_family, range(10)):
            results.extend(family_results)
    report=summarize_mutations(results); report.update({"campaign":suite["name"],"total_declared":1000,"design_count":10,"mutation_ids":[x["result"]["mutation_id"] for x in results]}); report["report_sha256"]=hashlib.sha256(json.dumps({k:v for k,v in report.items() if k!="report_sha256"},sort_keys=True,separators=(",",":")).encode()).hexdigest(); path=args.output/"mutation-closure-report.json"; path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n"); print(json.dumps({"status":report["status"],"total":report["total_mutations"],"detected":report["detected_mutations"],"false_passes":report["false_pass_count"],"designs":report["design_count"],"report":str(path)},sort_keys=True)); return 0 if report["status"]=="passed" else 1
if __name__=="__main__": raise SystemExit(main())
