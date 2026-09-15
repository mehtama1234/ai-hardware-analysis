#!/usr/bin/env python3
"""One-shot Hugging Face backend using the shared typed JSONL contract."""
from __future__ import annotations
import runpy
from pathlib import Path


# Reuse the resident worker's typed prompts, request-bound fields, and
# provenance metadata.  The worker exits naturally at stdin EOF after one
# request, so one-shot callers retain their existing process boundary.
runpy.run_path(str(Path(__file__).with_name("hf_llm_batch_backend.py")), run_name="__main__")
