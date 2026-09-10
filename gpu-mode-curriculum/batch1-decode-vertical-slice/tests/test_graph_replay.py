import hashlib
import io
import json
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from replay_graph_decode import extract


class BundleIntegrityTest(unittest.TestCase):
    def test_source_archive_and_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = b'# captured source\n'
            requirements = b'torch==0.test\n'
            hashes = {'graph_decode.py': hashlib.sha256(source).hexdigest()}
            payload = {'graph_decode.py': source, 'requirements.recorded.txt': requirements,
                'source-manifest.json': json.dumps({'source_hashes': hashes,
                    'requirements_sha256': hashlib.sha256(requirements).hexdigest()}).encode()}
            for kind in ('valid', 'source_changed', 'dependencies_changed', 'symlink', 'extra_member'):
                with self.subTest(kind=kind):
                    members = dict(payload)
                    if kind == 'source_changed':
                        members['graph_decode.py'] += b'# modified\n'
                    if kind == 'dependencies_changed':
                        members['requirements.recorded.txt'] += b'extra==1\n'
                    if kind == 'extra_member':
                        members['../escape'] = b'bad'
                    bundle = root / f'{kind}.tar.gz'
                    with tarfile.open(bundle, 'w:gz') as archive:
                        for name, content in members.items():
                            item = tarfile.TarInfo(name)
                            if kind == 'symlink' and name == 'graph_decode.py':
                                item.type = tarfile.SYMTYPE
                                item.linkname = '/tmp/unrelated'
                                archive.addfile(item)
                            else:
                                item.size = len(content)
                                archive.addfile(item, io.BytesIO(content))
                    report = {'source_hashes': hashes, 'reproduction_bundle': {
                        'sha256': hashlib.sha256(bundle.read_bytes()).hexdigest()}}
                    dest = root / kind
                    dest.mkdir()
                    if kind == 'valid':
                        extract(bundle, report, dest)
                        self.assertEqual((dest / 'graph_decode.py').read_bytes(), source)
                        report['reproduction_bundle']['sha256'] = '0' * 64
                        with self.assertRaisesRegex(ValueError, 'checksum'):
                            extract(bundle, report, dest)
                    else:
                        with self.assertRaises(ValueError):
                            extract(bundle, report, dest)


if __name__ == '__main__':
    unittest.main()
