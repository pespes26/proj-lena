"""Shared pytest fixtures for the backend test suite.

The auth tests need a real RS256 key pair (per the Phase C brief) so the
PyJWT verify path runs unmodified — only the OIDC discovery + JWKS HTTP
calls are stubbed out.

The storage tests need a live Postgres reachable at ``DATABASE_URL``.
Tests that need it use the ``live_db`` fixture below, which skips with a
clear message when the env var is missing.
"""

from __future__ import annotations

import base64
import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Iterator

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


# Make `backend/` importable as a top-level package root so tests can do
# `from auth import ...` and `from storage import ...` like the rest of
# the codebase does.
_BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))


# --- Entra fixtures ------------------------------------------------------

TEST_TENANT_ID = "00000000-0000-0000-0000-000000000001"
TEST_CLIENT_ID = "11111111-1111-1111-1111-111111111111"
TEST_AUTHORITY = "https://logfi-test.ciamlogin.com"
TEST_ISSUER = f"{TEST_AUTHORITY}/{TEST_TENANT_ID}/v2.0"
TEST_JWKS_URI = f"{TEST_AUTHORITY}/{TEST_TENANT_ID}/discovery/v2.0/keys"
TEST_DISCOVERY_URL = (
    f"{TEST_AUTHORITY}/{TEST_TENANT_ID}/v2.0/.well-known/openid-configuration"
)


def _b64url_uint(n: int) -> str:
    raw = n.to_bytes((n.bit_length() + 7) // 8 or 1, "big")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


@pytest.fixture(scope="session")
def rsa_keypair() -> Dict[str, Any]:
    """A fresh RSA-2048 key pair used to sign test tokens."""
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_nums = private.public_key().public_numbers()
    return {
        "private": private,
        "private_pem": private.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ),
        "kid": "test-kid-1",
        "jwk": {
            "kty": "RSA",
            "use": "sig",
            "alg": "RS256",
            "kid": "test-kid-1",
            "n": _b64url_uint(public_nums.n),
            "e": _b64url_uint(public_nums.e),
        },
    }


@pytest.fixture
def make_token(rsa_keypair):
    """Factory returning a signed RS256 JWT with override-able claims."""

    def _make(
        *,
        aud: str = TEST_CLIENT_ID,
        iss: str = TEST_ISSUER,
        oid: str = "user-guid-abc",
        email: str = "alice@example.com",
        name: str = "Alice Example",
        exp_offset: int = 3600,
        nbf_offset: int = 0,
        kid: str = "test-kid-1",
        extra_claims: Dict[str, Any] | None = None,
        sign_with: Any = None,
    ) -> str:
        now = int(time.time())
        payload: Dict[str, Any] = {
            "aud": aud,
            "iss": iss,
            "oid": oid,
            "preferred_username": email,
            "name": name,
            "iat": now,
            "nbf": now + nbf_offset,
            "exp": now + exp_offset,
        }
        if extra_claims:
            payload.update(extra_claims)
        key = sign_with if sign_with is not None else rsa_keypair["private_pem"]
        return jwt.encode(payload, key, algorithm="RS256", headers={"kid": kid})

    return _make


@pytest.fixture
def mock_entra_http(monkeypatch, rsa_keypair):
    """Replace httpx.Client.get with canned OIDC discovery + JWKS responses.

    Auto-applied to every test that depends on it. The JWKS response is
    keyed by the real public key from ``rsa_keypair`` so the signature
    verification step runs unmodified.
    """
    discovery_body = {
        "issuer": TEST_ISSUER,
        "jwks_uri": TEST_JWKS_URI,
    }
    jwks_body = {"keys": [rsa_keypair["jwk"]]}

    class _FakeResponse:
        def __init__(self, body: Dict[str, Any], status: int = 200) -> None:
            self._body = body
            self.status_code = status

        def raise_for_status(self) -> None:
            if self.status_code >= 400:
                raise httpx.HTTPStatusError(
                    "boom", request=None, response=None  # type: ignore[arg-type]
                )

        def json(self) -> Dict[str, Any]:
            return self._body

    def _fake_get(self, url, *args, **kwargs):
        if "well-known/openid-configuration" in url:
            return _FakeResponse(discovery_body)
        if "discovery/v2.0/keys" in url or url == TEST_JWKS_URI:
            return _FakeResponse(jwks_body)
        raise AssertionError(f"unexpected URL fetched in test: {url}")

    monkeypatch.setattr(httpx.Client, "get", _fake_get)


@pytest.fixture
def entra_env(monkeypatch):
    """Set the ENTRA_* env vars to the test tenant before each test."""
    monkeypatch.setenv("ENTRA_TENANT_ID", TEST_TENANT_ID)
    monkeypatch.setenv("ENTRA_CLIENT_ID", TEST_CLIENT_ID)
    monkeypatch.setenv("ENTRA_AUTHORITY", TEST_AUTHORITY)
    # Force DEV_MODE off so the JWT path is exercised. We set it to "" rather
    # than deleting it so the .env-loader at the top of auth.py — which uses
    # setdefault — can't quietly re-enable DEV_MODE from a developer's local
    # backend/.env when the module is reloaded.
    monkeypatch.setenv("DEV_MODE", "")

    # auth.py reads DEV_MODE at import time, so we have to reload it after
    # tweaking the env. Also reset the JWKS cache between tests.
    import importlib
    import auth as _auth
    importlib.reload(_auth)
    yield _auth
    _auth._reset_jwks_cache_for_tests()


# --- Postgres fixtures ---------------------------------------------------

@pytest.fixture
def live_db():
    """Provide a connection-string-backed live Postgres for storage tests.

    Skips the test when no DATABASE_URL is set. Wipes the three tables
    around each test so ordering doesn't matter. The schema must already
    be applied (see backend/migrations/001_init.sql).
    """
    if not os.environ.get("DATABASE_URL"):
        pytest.skip("DATABASE_URL not set — storage tests need a live Postgres")

    # Reload db module to pick up the env var (the pool is built lazily).
    import importlib
    import db as _db
    importlib.reload(_db)
    _db.close_pool()

    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM reports")
            cur.execute("DELETE FROM projects")
            cur.execute("DELETE FROM users")

    yield _db

    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM reports")
            cur.execute("DELETE FROM projects")
            cur.execute("DELETE FROM users")
    _db.close_pool()
