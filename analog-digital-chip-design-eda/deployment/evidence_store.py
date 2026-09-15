"""Provider-neutral immutable evidence storage contract.

The open-source pilot uses ``FilesystemEvidenceStore``. Production can
replace it with an object-store implementation without changing job,
evidence, bundle, or signoff API payloads. Keys are logical, relative object
names; callers never supply filesystem paths.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Protocol


class InvalidEvidenceKey(ValueError):
    """Raised when a logical evidence key could escape its namespace."""


class EvidenceIntegrityError(ValueError):
    """Raised when an immutable evidence object would be changed."""


def validate_evidence_key(key: str) -> str:
    value = str(key or "")
    path = Path(value)
    raw_parts = value.replace("\\", "/").split("/")
    if not value or path.is_absolute() or "\\" in value or any(part in {"", ".", ".."} for part in raw_parts):
        raise InvalidEvidenceKey("evidence key must be a non-empty relative path")
    return "/".join(path.parts)


@dataclass(frozen=True)
class EvidenceObject:
    key: str
    content: bytes
    sha256: str


class EvidenceStore(Protocol):
    def put(self, key: str, content: bytes, *, overwrite: bool = False) -> EvidenceObject: ...
    def get(self, key: str) -> EvidenceObject | None: ...
    def exists(self, key: str) -> bool: ...


class S3EvidenceStore:
    """Immutable S3-compatible object store.

    The client is injectable for tests; production callers may omit it when
    boto3 is installed. Bucket versioning, retention, encryption, and IAM are
    deployment controls and are reported separately from this API contract.
    """

    def __init__(self, bucket: str, *, client=None):
        if not bucket or bucket.strip() != bucket:
            raise ValueError("object-store bucket must be a non-empty name")
        if client is None:
            try:
                import boto3
            except ImportError as error:  # pragma: no cover
                raise RuntimeError("boto3 is required for S3 evidence storage") from error
            client = boto3.client("s3")
        self.bucket = bucket
        self.client = client

    def put(self, key: str, content: bytes, *, overwrite: bool = False) -> EvidenceObject:
        normalized = validate_evidence_key(key)
        payload = bytes(content)
        digest = sha256(payload).hexdigest()
        try:
            self.client.put_object(Bucket=self.bucket, Key=normalized, Body=payload, Metadata={"sha256": digest}, **({} if overwrite else {"IfNoneMatch": "*"}))
        except Exception as error:
            if overwrite:
                raise EvidenceIntegrityError("immutable evidence objects cannot be overwritten") from error
            existing = self.get(normalized)
            if existing is None or existing.content != payload:
                raise EvidenceIntegrityError("immutable evidence key already contains different content") from error
            return existing
        return EvidenceObject(normalized, payload, digest)

    def get(self, key: str) -> EvidenceObject | None:
        normalized = validate_evidence_key(key)
        try:
            result = self.client.get_object(Bucket=self.bucket, Key=normalized)
        except Exception as error:
            if getattr(error, "response", {}).get("Error", {}).get("Code") in {"NoSuchKey", "404", "NotFound"}:
                return None
            raise
        body = result["Body"].read() if hasattr(result["Body"], "read") else bytes(result["Body"])
        return EvidenceObject(normalized, body, sha256(body).hexdigest())

    def exists(self, key: str) -> bool:
        normalized = validate_evidence_key(key)
        try:
            self.client.head_object(Bucket=self.bucket, Key=normalized)
            return True
        except Exception as error:
            if getattr(error, "response", {}).get("Error", {}).get("Code") in {"404", "NotFound", "NoSuchKey"}:
                return False
            raise

    def control_probe(self) -> dict[str, object]:
        """Inspect bucket controls required for customer evidence retention."""
        missing: list[str] = []
        try:
            versioning = self.client.get_bucket_versioning(Bucket=self.bucket).get("Status")
        except Exception as error:  # pragma: no cover - provider-specific
            versioning = None
            missing.append(f"versioning ({type(error).__name__})")
        if versioning != "Enabled":
            missing.append("versioning enabled")
        try:
            encryption = self.client.get_bucket_encryption(Bucket=self.bucket)
            encrypted = bool(encryption.get("ServerSideEncryptionConfiguration", {}).get("Rules"))
        except Exception as error:  # pragma: no cover - provider-specific
            encrypted = False
            missing.append(f"encryption ({type(error).__name__})")
        if not encrypted:
            missing.append("server-side encryption")
        try:
            lifecycle = self.client.get_bucket_lifecycle_configuration(Bucket=self.bucket)
            retained = bool(lifecycle.get("Rules"))
        except Exception as error:  # pragma: no cover - provider-specific
            retained = False
            missing.append(f"retention ({type(error).__name__})")
        if not retained:
            missing.append("retention lifecycle")
        try:
            lock_config = self.client.get_object_lock_configuration(Bucket=self.bucket).get("ObjectLockConfiguration", {})
            object_lock = lock_config.get("ObjectLockEnabled") == "Enabled"
            default_retention = lock_config.get("Rule", {}).get("DefaultRetention", {})
            retention_duration = int(default_retention.get("Days", 0) or 0) or int(default_retention.get("Years", 0) or 0) * 365
        except Exception as error:  # pragma: no cover - provider-specific
            object_lock = False
            retention_duration = 0
            missing.append(f"object lock ({type(error).__name__})")
        if not object_lock:
            missing.append("object lock enabled")
        if retention_duration < 1:
            missing.append("object lock default retention")
        return {"bucket": self.bucket, "versioning": versioning, "encrypted": encrypted, "retention": retained, "object_lock": object_lock, "object_lock_retention_days": retention_duration, "ready": not missing, "missing": missing}


class FilesystemEvidenceStore:
    """Content-addressed-safe local store used by the pilot and tests."""

    def __init__(self, root: Path):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> tuple[str, Path]:
        normalized = validate_evidence_key(key)
        target = (self.root / normalized).resolve()
        if target != self.root and self.root not in target.parents:
            raise InvalidEvidenceKey("evidence key escaped store root")
        return normalized, target

    def put(self, key: str, content: bytes, *, overwrite: bool = False) -> EvidenceObject:
        normalized, target = self._path(key)
        payload = bytes(content)
        if target.is_symlink():
            raise EvidenceIntegrityError("evidence object cannot be a symlink")
        if target.exists() and not overwrite:
            existing = self.get(normalized)
            assert existing is not None
            if existing.content != payload:
                raise EvidenceIntegrityError("immutable evidence key already contains different content")
            return existing
        if target.exists() and overwrite:
            raise EvidenceIntegrityError("immutable evidence objects cannot be overwritten")
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(target.name + ".tmp")
        temporary.write_bytes(payload)
        temporary.replace(target)
        return EvidenceObject(normalized, payload, sha256(payload).hexdigest())

    def get(self, key: str) -> EvidenceObject | None:
        normalized, target = self._path(key)
        if not target.is_file():
            return None
        payload = target.read_bytes()
        return EvidenceObject(normalized, payload, sha256(payload).hexdigest())

    def exists(self, key: str) -> bool:
        _, target = self._path(key)
        return target.is_file()
