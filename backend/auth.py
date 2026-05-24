"""Authentication — Entra External ID JWT verification.

Phase C: replaces the Phase-0 DEV_MODE-only stub with a real OAuth/OIDC
verification path. DEV_MODE stays untouched so local dev keeps working
while the CIO finalizes the Entra External ID tenant.

JWT verification flow (per request):
1. Pull the bearer token off the Authorization header.
2. If DEV_MODE is on and the token is the local dev token, short-circuit.
3. Otherwise decode the JWT header to read ``kid``.
4. Look ``kid`` up in the per-process JWKS cache. On miss (or TTL expiry),
   fetch the OIDC discovery document, then the JWKS, and repopulate the
   cache. Cache misses also handle Entra's normal key-rotation cadence.
5. Verify the signature with the matching public key (RS256), and let
   PyJWT validate ``aud``, ``iss``, ``exp``, ``nbf``, ``iat``.
6. Extract ``oid`` (immutable user GUID) as the local ``uid``. Email comes
   from ``preferred_username`` falling back to ``email``.
7. Role + linked_manager + full_name come from the ``users`` table in
   Postgres, NOT from token claims. First-time logins get a row inserted
   with ``role='viewer'``.

Required env vars in production (no defaults — failure is loud):
    ENTRA_TENANT_ID   tenant GUID, e.g. 00000000-0000-0000-0000-000000000000
    ENTRA_CLIENT_ID   app-registration GUID; checked as the expected ``aud``
    ENTRA_AUTHORITY   base URL. Defaults to https://{ENTRA_TENANT_ID}.ciamlogin.com
                      for Entra External ID. Override to
                      https://login.microsoftonline.com for vanilla Entra ID.

The discovery URL is built as ``{authority}/{tenant}/v2.0/.well-known/openid-configuration``
which works for both External ID and vanilla Entra ID.
"""

from __future__ import annotations

import os
import threading
import time
from typing import Any, Dict, Optional

import httpx
import jwt
from fastapi import Depends, Header, HTTPException
from jwt import PyJWKClient  # noqa: F401  (imported for clarity; we use jwt.algorithms below)
from jwt.algorithms import RSAAlgorithm

# Load .env if present (local dev) ----------------------------------------
_env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and '=' in _line and not _line.startswith('#'):
                _k, _v = _line.split('=', 1)
                os.environ.setdefault(_k.strip(), _v.strip())


DEV_MODE = os.environ.get('DEV_MODE', '').lower() in ('true', '1')
DEV_TOKEN = 'dev-admin-local'

ROLES = {
    'admin': 'מנהל מערכת',
    'economist': 'כלכלנית',
    'viewer': 'צופה מלא',
    'project_manager': 'מנהל פרויקט',
}

# JWKS cache --------------------------------------------------------------
# In-memory, per-process. Tiny — internal tool, 5-15 users; the cache
# typically holds 2-3 active signing keys at any moment.

_JWKS_TTL_SECONDS = 60 * 60  # 1 hour; Microsoft rotates roughly every 24h


class _JwksCache:
    """Thread-safe JWKS cache keyed by ``kid``.

    A separate "config" cache stores the OIDC discovery doc (jwks_uri +
    issuer) so we don't re-fetch it on every JWKS refresh.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._keys: Dict[str, Any] = {}
        self._issuer: Optional[str] = None
        self._jwks_uri: Optional[str] = None
        self._expires_at: float = 0.0

    def get_key(self, kid: str) -> Any:
        """Return the public key for ``kid``. Refresh on miss or TTL expiry."""
        now = time.time()
        with self._lock:
            if kid in self._keys and now < self._expires_at:
                return self._keys[kid]
        # Refresh outside the lock to avoid holding it across network I/O,
        # then take the lock to swap the cache atomically.
        new_issuer, new_jwks_uri, new_keys = self._refresh()
        with self._lock:
            self._issuer = new_issuer
            self._jwks_uri = new_jwks_uri
            self._keys = new_keys
            self._expires_at = time.time() + _JWKS_TTL_SECONDS
        if kid not in new_keys:
            raise HTTPException(status_code=401, detail="לא מחובר")
        return new_keys[kid]

    def issuer(self) -> Optional[str]:
        """Return the cached issuer string (set as a side-effect of get_key)."""
        with self._lock:
            return self._issuer

    @staticmethod
    def _refresh() -> tuple[str, str, Dict[str, Any]]:
        """Fetch OIDC discovery + JWKS. Returns (issuer, jwks_uri, {kid: key})."""
        tenant = os.environ.get('ENTRA_TENANT_ID', '').strip()
        if not tenant:
            raise HTTPException(
                status_code=503,
                detail="Authentication is not configured. Set ENTRA_TENANT_ID.",
            )
        authority = os.environ.get('ENTRA_AUTHORITY', '').strip()
        if not authority:
            authority = f"https://{tenant}.ciamlogin.com"
        authority = authority.rstrip('/')

        discovery_url = f"{authority}/{tenant}/v2.0/.well-known/openid-configuration"
        with httpx.Client(timeout=10.0) as client:
            r = client.get(discovery_url)
            r.raise_for_status()
            cfg = r.json()
            issuer = cfg['issuer']
            jwks_uri = cfg['jwks_uri']
            r2 = client.get(jwks_uri)
            r2.raise_for_status()
            jwks = r2.json()

        keys: Dict[str, Any] = {}
        for jwk in jwks.get('keys', []):
            kid = jwk.get('kid')
            if not kid:
                continue
            # Only RSA signing keys we can use for verification.
            if jwk.get('kty') != 'RSA':
                continue
            if jwk.get('use') and jwk['use'] != 'sig':
                continue
            keys[kid] = RSAAlgorithm.from_jwk(jwk)
        return issuer, jwks_uri, keys


_JWKS = _JwksCache()


def _reset_jwks_cache_for_tests() -> None:
    """Test-only: wipe the JWKS cache so the next request refetches."""
    global _JWKS
    _JWKS = _JwksCache()


def _verify_entra_token(token: str) -> Dict[str, Any]:
    """Verify an Entra-issued JWT. Returns the decoded claims.

    Raises HTTPException(401) on any signature/claim failure.
    Raises HTTPException(503) if the auth backend is unreachable or
    misconfigured.
    """
    client_id = os.environ.get('ENTRA_CLIENT_ID', '').strip()
    if not client_id:
        raise HTTPException(
            status_code=503,
            detail="Authentication is not configured. Set ENTRA_CLIENT_ID.",
        )

    try:
        unverified_header = jwt.get_unverified_header(token)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="לא מחובר")

    kid = unverified_header.get('kid')
    if not kid:
        raise HTTPException(status_code=401, detail="לא מחובר")

    try:
        public_key = _JWKS.get_key(kid)
    except HTTPException:
        raise
    except httpx.HTTPError:
        # JWKS/discovery endpoint failure — surface as 503 so the caller
        # knows it's an upstream problem, not a malformed token.
        raise HTTPException(status_code=503, detail="Authentication backend unreachable")

    expected_issuer = _JWKS.issuer()
    try:
        claims = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            audience=client_id,
            issuer=expected_issuer,
            options={'require': ['exp', 'iat', 'aud', 'iss', 'oid']},
        )
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="לא מחובר")

    return claims


def _claims_to_user(claims: Dict[str, Any]) -> Dict[str, Any]:
    """Project token claims onto the local user dict, then merge DB role.

    The shape must stay identical to what Phase 0 returned, since every
    router and downstream service reads ``user['uid']``, ``user['email']``,
    ``user['role']``, etc.
    """
    uid = claims['oid']
    email = claims.get('preferred_username') or claims.get('email') or ''
    full_name = claims.get('name') or ''

    # Role + linked_manager come from the local users table, never the token.
    # Import inline to keep auth.py importable when the DB isn't reachable
    # (tests / cold-boot).
    from storage import get_or_create_user
    db_user = get_or_create_user(uid=uid, email=email, full_name=full_name)

    return {
        'uid': uid,
        'email': db_user.get('email') or email,
        'username': email,
        'role': db_user.get('role', 'viewer'),
        'linked_manager': db_user.get('linked_manager', ''),
        'full_name': db_user.get('full_name') or full_name,
    }


async def get_current_user(authorization: str = Header(None)) -> dict:
    """FastAPI dependency: verify the bearer token and return the user.

    DEV_MODE is honored first so local development never depends on a
    reachable Entra tenant. Everything else goes through the JWT
    verification path.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="לא מחובר")
    token = authorization.split(" ", 1)[1]

    if DEV_MODE and token == DEV_TOKEN:
        return {
            'uid': 'dev-admin',
            'email': 'dev@local',
            'username': 'dev@local',
            'role': 'admin',
            'linked_manager': '',
            'full_name': 'Dev Admin',
        }

    claims = _verify_entra_token(token)
    return _claims_to_user(claims)


async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="נדרשת הרשאת מנהל מערכת")
    return user


async def require_editor(user: dict = Depends(get_current_user)) -> dict:
    if user['role'] not in ('admin', 'economist'):
        raise HTTPException(status_code=403, detail="נדרשת הרשאת עריכה")
    return user


def check_project_owner(project_name: str, user: dict) -> bool:
    """Project-manager scoped edit check.

    admin/economist can edit anything; project_manager can edit only the
    projects whose ``manager`` field matches the user's ``linked_manager``.
    """
    if user['role'] in ('admin', 'economist'):
        return True
    if user['role'] == 'project_manager':
        from services.unified import load_form_data
        form_data = load_form_data()
        project = form_data.get(project_name, {})
        return project.get('manager', '') == user.get('linked_manager', '')
    return False
