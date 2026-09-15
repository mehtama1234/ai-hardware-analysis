#!/usr/bin/env python3
"""Run a credential-free OIDC signing-key rotation rehearsal."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import sys

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from deployment.oidc_identity import OIDCIdentityVerifier


def _keypair(kid: str):
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public = jwt.algorithms.RSAAlgorithm.to_jwk(private.public_key(), as_dict=True)
    public.update({"kid": kid, "alg": "RS256", "use": "sig"})
    return private, public


def run(output: Path) -> dict[str, object]:
    old_private, old_public = _keypair("old-key")
    new_private, new_public = _keypair("new-key")
    documents = [{"keys": [old_public]}, {"keys": [old_public, new_public]}, {"keys": [new_public]}]
    calls = 0

    def fetch() -> dict[str, object]:
        nonlocal calls
        document = documents[min(calls, len(documents) - 1)]
        calls += 1
        return document

    verifier = OIDCIdentityVerifier("https://issuer.example", "verification", "https://issuer.example/jwks", fetch_jwks=fetch, cache_seconds=600)
    claims = {"sub": "rotation-canary", "iss": "https://issuer.example", "aud": "verification"}
    old_token = jwt.encode(claims, old_private, algorithm="RS256", headers={"kid": "old-key"})
    new_token = jwt.encode(claims, new_private, algorithm="RS256", headers={"kid": "new-key"})
    verifier.verify(old_token)
    overlap_ok = verifier.verify(new_token).subject == "rotation-canary"
    verifier._expires = 0.0  # force the documented post-grace JWKS refresh
    retired_rejected = False
    try:
        verifier.verify(old_token)
    except Exception:
        retired_rejected = True
    result: dict[str, object] = {
        "schema_version": "verification-oidc-key-rotation-drill-v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "stages": {"old_key_canary": True, "overlap_new_key_canary": overlap_ok, "retired_old_key_rejected": retired_rejected},
        "jwks_refresh_total": verifier.metrics()["jwks_refresh_total"],
        "unknown_kid_total": verifier.metrics()["jwks_unknown_kid_total"],
        "verified": overlap_ok and retired_rejected,
        "claim_boundary": "Credential-free verifier rotation semantics only; this does not prove customer IdP availability, tenant mapping, administrative RBAC, or production key-management controls.",
    }
    result["sha256"] = sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.output)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
