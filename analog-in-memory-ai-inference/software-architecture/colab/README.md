# GPT-2/SAR qualification on Colab

This entry point runs the guarded workload handoff against the exact pinned
GPT-2 revision. It validates the SAR profile and dispatch policy first, then
can run the numerical projection evaluator on a Colab GPU.

In a fresh Colab GPU runtime:

```bash
!git clone https://github.com/mehtama1234/ai-hardware-analysis.git /content/ai-hardware-analysis
%cd /content/ai-hardware-analysis
!pip install -q torch transformers huggingface_hub
!python3 analog-in-memory-ai-inference/software-architecture/colab/run_profile_driven_gpt2_colab.py \
  --repo-root /content/ai-hardware-analysis \
  --output /content/gpt2-sar-t4 \
  --fetch-model --execute-model --device cuda
```

The receipt directory contains the model evaluation, operation trace, dispatch
simulation, and contract-check output. Verify the model result with:

```bash
!python3 analog-in-memory-ai-inference/software-architecture/scripts/check_gpt2_hybrid_evaluation.py \
  --package /content/gpt2-sar-t4/model-evaluation
```

The evaluator synchronizes CUDA around measured calls. `--device cuda` fails
closed when the runtime does not expose CUDA. The run remains a numerical
profile experiment: it does not claim analog hardware timing, energy, yield,
or speedup.

The frozen command and acceptance fields are also recorded in
[`t4-run-config.json`](t4-run-config.json).

The same flow is available as the importable notebook
[`gpt2_sar_t4_qualification.ipynb`](gpt2_sar_t4_qualification.ipynb).

After the T4 run, validate the receipt with:

```bash
!python3 analog-in-memory-ai-inference/software-architecture/scripts/check_profile_driven_colab_receipt.py \
  --require-cuda /content/gpt2-sar-t4/colab-receipt.json
```
