#!/usr/bin/env python3
"""Bounded solver-sensitivity diagnostic for the unresolved 1 pF bank case."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import time


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_variant(source, output, label, option, timeout):
    text = source.read_text()
    marker = '.options reltol=1e-5 abstol=1e-14 vntol=1e-9'
    assert marker in text
    deck = text.replace(marker, marker + ' ' + option, 1)
    directory = output / label
    directory.mkdir()
    path = directory / 'deck.spice'; path.write_text(deck)
    start = time.monotonic()
    try:
        proc = subprocess.run(['ngspice', '-b', str(path.resolve())], cwd=directory,
                              capture_output=True, text=True, timeout=timeout)
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        proc = None; timed_out = True
        (directory / 'stdout.log').write_bytes(exc.stdout or b'')
        (directory / 'stderr.log').write_bytes(exc.stderr or b'')
    if proc is not None:
        (directory / 'stdout.log').write_text(proc.stdout)
        (directory / 'stderr.log').write_text(proc.stderr)
    return dict(label=label, option=option, timeout_seconds=timeout,
                elapsed_seconds=time.monotonic()-start, timed_out=timed_out,
                returncode=None if proc is None else proc.returncode,
                waveform_present=(directory / 'waveform.txt').is_file(),
                deck_sha256=digest(path), stdout_sha256=digest(directory / 'stdout.log'),
                stderr_sha256=digest(directory / 'stderr.log'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--timeout', type=float, default=120)
    args = parser.parse_args()
    if not 1 <= args.timeout <= 300: raise ValueError('timeout must be between 1 and 300 seconds')
    args.output.mkdir(parents=True, exist_ok=False)
    source_hash = digest(args.source)
    variants = [run_variant(args.source, args.output, 'gear', '.options method=gear maxord=2', args.timeout),
                run_variant(args.source, args.output, 'gear-maxstep-100p', '.options method=gear maxord=2\n.tran 100p 5.42u 0 100p', args.timeout)]
    report = dict(schema_version='reference_sequence_solver_diagnostic.v1', source=str(args.source.resolve()),
                  source_sha256=source_hash, circuit_or_measurement_protocol_changed=False,
                  variants=variants, physical_profile_qualified=False, analog_authorized=False,
                  interpretation='A completed waveform under altered solver controls diagnoses numerical stiffness only; it does not replace the declared 50 ps protocol.')
    import json
    (args.output / 'result.json').write_text(json.dumps(report, indent=2)+'\n')
    (args.output / 'manifest.json').write_text(json.dumps({str(p.relative_to(args.output)):digest(p) for p in args.output.rglob('*') if p.is_file()}, indent=2)+'\n')
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__': main()
