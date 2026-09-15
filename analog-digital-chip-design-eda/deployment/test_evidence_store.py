from pathlib import Path

import pytest

from deployment.evidence_store import EvidenceIntegrityError, EvidenceObject, FilesystemEvidenceStore, InvalidEvidenceKey, S3EvidenceStore, validate_evidence_key


def test_filesystem_store_is_idempotent_and_hashes_content(tmp_path: Path):
    store = FilesystemEvidenceStore(tmp_path / "objects")
    first = store.put("job-1/runs/latest/report.json", b'{"status":"passed"}')
    with pytest.raises(EvidenceIntegrityError):
        store.put("job-1/runs/latest/report.json", b"different")
    second = store.put("job-1/runs/latest/report.json", b'{"status":"passed"}')
    assert second == first
    assert store.exists("job-1/runs/latest/report.json")
    loaded = store.get("job-1/runs/latest/report.json")
    assert loaded == first
    assert loaded.sha256 == first.sha256


def test_filesystem_store_rejects_overwrite_and_symlink_targets(tmp_path: Path):
    store = FilesystemEvidenceStore(tmp_path / "objects")
    store.put("job-1/report.json", b"stable")
    with pytest.raises(EvidenceIntegrityError):
        store.put("job-1/report.json", b"changed", overwrite=True)
    outside = tmp_path / "outside"
    outside.write_bytes(b"outside")
    link = tmp_path / "objects" / "job-1" / "link.json"
    link.symlink_to(outside)
    with pytest.raises((EvidenceIntegrityError, InvalidEvidenceKey)):
        store.put("job-1/link.json", b"attempt")


@pytest.mark.parametrize("key", ["", "/tmp/evidence", "../escape", "job/../../escape", "job\\escape", "job//report"])
def test_store_rejects_path_like_keys(tmp_path: Path, key: str):
    store = FilesystemEvidenceStore(tmp_path / "objects")
    with pytest.raises(InvalidEvidenceKey):
        store.put(key, b"evidence")


def test_key_normalization_is_logical_and_platform_independent():
    assert validate_evidence_key("job-1/runs/latest/report.json") == "job-1/runs/latest/report.json"


class _Body:
    def __init__(self, value): self.value = value
    def read(self): return self.value


class _FakeS3:
    def __init__(self): self.objects = {}
    def put_object(self, **kwargs):
        key = (kwargs["Bucket"], kwargs["Key"])
        if kwargs.get("IfNoneMatch") == "*" and key in self.objects: raise RuntimeError("PreconditionFailed")
        self.objects[key] = bytes(kwargs["Body"])
    def get_object(self, **kwargs):
        key = (kwargs["Bucket"], kwargs["Key"])
        if key not in self.objects:
            error = RuntimeError("NotFound"); error.response = {"Error": {"Code": "NotFound"}}; raise error
        return {"Body": _Body(self.objects[key])}
    def head_object(self, **kwargs):
        if (kwargs["Bucket"], kwargs["Key"]) not in self.objects:
            error = RuntimeError("NotFound"); error.response = {"Error": {"Code": "NotFound"}}; raise error

    def get_bucket_versioning(self, **kwargs): return {"Status": "Enabled"}
    def get_bucket_encryption(self, **kwargs): return {"ServerSideEncryptionConfiguration": {"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}}
    def get_bucket_lifecycle_configuration(self, **kwargs): return {"Rules": [{"Status": "Enabled", "Expiration": {"Days": 35}}]}
    def get_object_lock_configuration(self, **kwargs): return {"ObjectLockConfiguration": {"ObjectLockEnabled": "Enabled", "Rule": {"DefaultRetention": {"Days": 35}}}}


def test_s3_store_preserves_immutable_protocol_with_injected_client():
    store = S3EvidenceStore("evidence-bucket", client=_FakeS3())
    first = store.put("job-1/report.json", b"stable")
    assert isinstance(first, EvidenceObject)
    assert store.put("job-1/report.json", b"stable") == first
    with pytest.raises(EvidenceIntegrityError): store.put("job-1/report.json", b"changed")
    assert store.get("job-1/report.json") == first
    assert store.exists("job-1/report.json") is True
    assert store.exists("job-1/missing.json") is False
    controls = store.control_probe()
    assert controls["ready"] is True
    assert controls["versioning"] == "Enabled"
    assert controls["object_lock"] is True
    assert controls["object_lock_retention_days"] == 35


def test_s3_control_probe_rejects_object_lock_without_default_retention():
    class _NoDefaultRetention(_FakeS3):
        def get_object_lock_configuration(self, **kwargs):
            return {"ObjectLockConfiguration": {"ObjectLockEnabled": "Enabled"}}

    controls = S3EvidenceStore("evidence-bucket", client=_NoDefaultRetention()).control_probe()
    assert controls["object_lock"] is True
    assert controls["object_lock_retention_days"] == 0
    assert controls["ready"] is False
    assert "object lock default retention" in controls["missing"]
