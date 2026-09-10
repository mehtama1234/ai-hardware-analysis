#!/usr/bin/env python3
"""Verify pinned real text and tokenize nonoverlapping source ranges separately."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from transformers import AutoTokenizer

REVISION = '607a30d783dfa663caf39e06633721c8d4cfcd7e'
DATA_REVISION = '6f9487a6fe5b420b7ca9afb0d7c078e37c1d1b4e'
DATA_SHA = '86c4e6aa9db7c042ec79f339dcb96d42b0075e16b8fc2e86bf0ca57e2dc565ed'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=Path(__file__).parent / 'data')
    args = parser.parse_args()
    source = args.data_dir / 'tinyshakespeare.txt'
    if sha(source) != DATA_SHA:
        raise ValueError('pinned corpus checksum mismatch')
    text = source.read_bytes().decode('utf-8')
    tokenizer = AutoTokenizer.from_pretrained('openai-community/gpt2', revision=REVISION)
    boundaries = [0, len(text) * 90 // 100, len(text) * 95 // 100, len(text)]
    manifest = {'schema_version': 'training-data-v0.1', 'source_url':
        f'https://raw.githubusercontent.com/karpathy/char-rnn/{DATA_REVISION}/data/tinyshakespeare/input.txt',
        'source_sha256': DATA_SHA, 'source_characters': len(text),
        'tokenizer': 'openai-community/gpt2', 'tokenizer_revision': REVISION,
        'prepare_source_sha256': sha(__file__),
        'split_policy': 'contiguous 90/5/5 percent character ranges; tokenize each separately; no boundary-spanning examples',
        'limitations': 'Character boundaries may divide a scene or word; source overlap is prevented, semantic independence is not guaranteed.',
        'test_policy': 'test tokens excluded from training and checkpoint selection', 'splits': {}}
    for name, start, end in zip(('train', 'validation', 'test'), boundaries, boundaries[1:]):
        ids = np.asarray(tokenizer.encode(text[start:end], add_special_tokens=False, verbose=False), dtype=np.int64)
        path = args.data_dir / f'{name}.npy'
        np.save(path, ids, allow_pickle=False)
        manifest['splits'][name] = {'character_start': start, 'character_end': end,
            'text_sha256': hashlib.sha256(text[start:end].encode()).hexdigest(),
            'tokens': len(ids), 'file': path.name, 'sha256': sha(path)}
    (args.data_dir / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
