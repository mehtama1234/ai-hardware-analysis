"""Small, provider-neutral OIDC JWT verifier for the production ingress path."""
from __future__ import annotations

from dataclasses import dataclass
import json
import time
from typing import Callable
from urllib.request import Request, urlopen
from urllib.parse import urlparse

import jwt


@dataclass(frozen=True)
class IdentityClaims:
    subject: str
    roles: frozenset[str]
    issuer: str
    audience: str


class OIDCIdentityVerifier:
    def __init__(self, issuer: str, audience: str, jwks_url: str, *, fetch_jwks: Callable[[], dict] | None = None, cache_seconds: int = 300):
        if not issuer or not audience or not jwks_url:
            raise ValueError("OIDC issuer, audience, and JWKS URL are required")
        if urlparse(jwks_url).scheme != "https":
            raise ValueError("OIDC JWKS URL must use HTTPS")
        self.issuer, self.audience, self.jwks_url = issuer, audience, jwks_url
        self.fetch_jwks = fetch_jwks or self._fetch_jwks
        self.cache_seconds = max(1, cache_seconds)
        self._keys: dict[str, dict] = {}
        self._expires = 0.0
        self.refresh_count = 0
        self.unknown_kid_count = 0

    def refresh(self) -> None:
        document = self.fetch_jwks()
        keys = document.get("keys", []) if isinstance(document, dict) else []
        self._keys = {str(item["kid"]): item for item in keys if isinstance(item, dict) and item.get("kid")}
        self._expires = time.monotonic() + self.cache_seconds
        self.refresh_count += 1

    def _fetch_jwks(self) -> dict:
        request = Request(self.jwks_url, headers={"Accept": "application/json"})
        with urlopen(request, timeout=5) as response:  # nosec B310 - URL is deployment configuration
            return json.loads(response.read().decode("utf-8"))

    def _key(self, kid: str):
        now = time.monotonic()
        if now >= self._expires or kid not in self._keys:
            if kid not in self._keys:
                self.unknown_kid_count += 1
            self.refresh()
        jwk = self._keys.get(kid)
        if jwk is None:
            raise ValueError("OIDC signing key is unavailable")
        algorithm = str(jwk.get("alg", "RS256"))
        if algorithm not in {"RS256", "RS384", "RS512", "ES256", "ES384", "ES512"}:
            raise ValueError("OIDC signing algorithm is not allowed")
        return jwt.algorithms.get_default_algorithms()[algorithm].from_jwk(json.dumps(jwk))

    def verify(self, token: str) -> IdentityClaims:
        if not token or token.count(".") != 2:
            raise ValueError("malformed bearer token")
        header = jwt.get_unverified_header(token)
        kid = str(header.get("kid", ""))
        if not kid:
            raise ValueError("bearer token has no key id")
        claims = jwt.decode(token, self._key(kid), algorithms=["RS256", "RS384", "RS512", "ES256", "ES384", "ES512"], issuer=self.issuer, audience=self.audience)
        subject = str(claims.get("sub", "")).strip()
        if not subject:
            raise ValueError("bearer token has no subject")
        raw_roles = claims.get("roles", claims.get("permissions", []))
        if isinstance(raw_roles, str):
            raw_roles = raw_roles.split()
        roles = frozenset(str(role).strip() for role in (raw_roles if isinstance(raw_roles, (list, tuple, set)) else []) if str(role).strip())
        return IdentityClaims(subject=subject, roles=roles, issuer=self.issuer, audience=self.audience)

    def metrics(self) -> dict[str, int]:
        return {"jwks_refresh_total": self.refresh_count, "jwks_unknown_kid_total": self.unknown_kid_count, "cached_key_count": len(self._keys)}
