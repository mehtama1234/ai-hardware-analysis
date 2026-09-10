"""Validate a fixed-shape StaticCache CUDA Graph probe report."""
import argparse
import json
from pathlib import Path


def validate(report, model_id, revision):
    errors = []
    def check(ok, msg):
        if not ok:
            errors.append(msg)
    check(report.get('status') == 'passed' and report.get('evidence_kind') == 'measured_gpu', 'GPU pass missing')
    check(report.get('model_id') == model_id and report.get('model_revision') == revision, 'model identity')
    protocol = report.get('protocol', {})
    check(protocol.get('fixed_shapes') is True and protocol.get('cache') == 'StaticCache', 'fixed StaticCache protocol')
    check(protocol.get('batch_size', 0) >= 1 and protocol.get('steps', 0) >= 2, 'probe dimensions')
    checks = report.get('checks', {})
    check(checks.get('token_parity') is True and checks.get('slot_reuse_parity') is True and
          checks.get('shape_stable') is True and checks.get('graph_replayed') is True, 'capture checks')
    check(report.get('tokens', {}).get('eager') == report.get('tokens', {}).get('graph'), 'token arrays')
    check(report.get('runtime', {}).get('device', '').startswith('Tesla T4'), 'T4 device')
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('report', type=Path)
    parser.add_argument('--model-id', default='EleutherAI/pythia-70m')
    parser.add_argument('--model-revision', required=True)
    args = parser.parse_args()
    try:
        errors = validate(json.loads(args.report.read_text()), args.model_id, args.model_revision)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        errors = [f'malformed report: {exc}']
    result = {'status': 'failed' if errors else 'passed', 'errors': errors}
    args.report.with_suffix('.verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
