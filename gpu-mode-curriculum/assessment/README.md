# GPUMODE Assessment Bank

This layer turns the 118-lesson GPUMODE curriculum, external CUDA/Triton/ROCm/JAX/Hugging Face tutorial sources, and implemented lab evidence into a practical exam.

Run:

```bash
python3 scripts/build_assessment.py
python3 scripts/verify_assessment.py
```

Outputs:

- `assessment/question-bank.json`: concept checks, practical tasks, source lessons, tutorial links, and grading checks.
- `assessment/reports/assessment-report.md`: concise generated assessment summary.
