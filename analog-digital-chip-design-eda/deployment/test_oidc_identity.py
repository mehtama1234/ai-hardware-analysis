import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from deployment.oidc_identity import OIDCIdentityVerifier


def test_oidc_verifier_validates_claims_and_roles():
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public = private.public_key()
    jwk = jwt.algorithms.RSAAlgorithm.to_jwk(public, as_dict=True)
    jwk.update({"kid": "test-key", "alg": "RS256", "use": "sig"})
    token = jwt.encode({"sub": "oidc|alice", "iss": "https://issuer", "aud": "verification", "roles": ["verification-reviewer", "engineer"]}, private, algorithm="RS256", headers={"kid": "test-key"})
    verifier = OIDCIdentityVerifier("https://issuer", "verification", "https://issuer/jwks", fetch_jwks=lambda: {"keys": [jwk]})
    claims = verifier.verify(token)
    assert claims.subject == "oidc|alice"
    assert "verification-reviewer" in claims.roles


@pytest.mark.parametrize("change", ["issuer", "audience"])
def test_oidc_verifier_rejects_claim_mismatch(change):
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public = private.public_key()
    jwk = jwt.algorithms.RSAAlgorithm.to_jwk(public, as_dict=True)
    jwk.update({"kid": "test-key", "alg": "RS256", "use": "sig"})
    claims = {"sub": "alice", "iss": "https://issuer", "aud": "verification"}
    claims["iss" if change == "issuer" else "aud"] = "wrong"
    token = jwt.encode(claims, private, algorithm="RS256", headers={"kid": "test-key"})
    verifier = OIDCIdentityVerifier("https://issuer", "verification", "https://issuer/jwks", fetch_jwks=lambda: {"keys": [jwk]})
    with pytest.raises(jwt.InvalidTokenError):
        verifier.verify(token)


def test_oidc_verifier_refreshes_jwks_after_key_rotation():
    first = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    second = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    def key_for(private, kid):
        value = jwt.algorithms.RSAAlgorithm.to_jwk(private.public_key(), as_dict=True)
        value.update({"kid": kid, "alg": "RS256", "use": "sig"})
        return value
    documents = [{"keys": [key_for(first, "old")]}, {"keys": [key_for(second, "new")]}]
    calls = []
    def fetch():
        calls.append(1)
        return documents[min(len(calls) - 1, 1)]
    verifier = OIDCIdentityVerifier("https://issuer", "verification", "https://issuer/jwks", fetch_jwks=fetch, cache_seconds=600)
    old = jwt.encode({"sub": "alice", "iss": "https://issuer", "aud": "verification"}, first, algorithm="RS256", headers={"kid": "old"})
    new = jwt.encode({"sub": "alice", "iss": "https://issuer", "aud": "verification"}, second, algorithm="RS256", headers={"kid": "new"})
    assert verifier.verify(old).subject == "alice"
    assert verifier.verify(new).subject == "alice"
    assert len(calls) == 2
    assert verifier.metrics() == {"jwks_refresh_total": 2, "jwks_unknown_kid_total": 2, "cached_key_count": 1}


def test_oidc_verifier_requires_https_jwks_url():
    with pytest.raises(ValueError, match="HTTPS"):
        OIDCIdentityVerifier("https://issuer", "verification", "http://issuer/jwks")
