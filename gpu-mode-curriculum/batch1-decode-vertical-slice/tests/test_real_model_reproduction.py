import hashlib
import io
import json
import sys
import tarfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import replay_real_model_bundle as replay


def test_dependency_check_traverses_required_dependencies_and_rejects_drift(monkeypatch):
    versions = {'torch': '1', 'transformers': '2', 'ninja': '3', 'dependency': '4'}
    monkeypatch.setattr(replay.importlib.metadata, 'version', lambda name: versions[name])
    monkeypatch.setattr(replay.importlib.metadata, 'requires', lambda name: ['dependency>=1', 'extra-package; extra == "unused"'] if name == 'torch' else [])
    recorded = '\n'.join(f'{name}=={version}' for name, version in versions.items())
    checked, errors = replay.dependency_check(recorded)
    assert not errors and set(checked) == set(versions)
    versions['dependency'] = '5'
    assert replay.dependency_check(recorded)[1]


def test_reproduction_requires_matching_bundle_manifest_and_sources(tmp_path):
    source = b'print("fixture")\n'
    requirements = b'torch==1\n'
    hashes = {'runner.py': hashlib.sha256(source).hexdigest()}
    manifest = json.dumps({'source_hashes': hashes, 'requirements_sha256': hashlib.sha256(requirements).hexdigest()}).encode()
    bundle = tmp_path / 'source.tar.gz'
    with tarfile.open(bundle, 'w:gz') as archive:
        for name, data in [('runner.py', source), ('requirements.recorded.txt', requirements), ('source-manifest.json', manifest)]:
            member = tarfile.TarInfo(name)
            member.size = len(data)
            archive.addfile(member, io.BytesIO(data))
    report = {'source_hashes': hashes, 'reproduction_bundle': {'sha256': hashlib.sha256(bundle.read_bytes()).hexdigest()}}
    dest = tmp_path / 'extracted'
    dest.mkdir()
    assert replay.extract_verified(bundle, report, dest) == requirements.decode()
    report['source_hashes'] = {'runner.py': '0' * 64}
    with pytest.raises(ValueError, match='manifest'):
        replay.extract_verified(bundle, report, dest)
    report['reproduction_bundle']['sha256'] = '0' * 64
    with pytest.raises(ValueError, match='bundle checksum'):
        replay.extract_verified(bundle, report, dest)
