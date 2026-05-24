"""Phase C — Entra External ID JWT verification tests.

These tests exercise the real RS256 verification path inside auth.py.
The only thing mocked is the OIDC discovery + JWKS HTTP fetch (see
``mock_entra_http`` in conftest); everything else — signature
verification, audience check, issuer check, expiry — runs unmodified
through PyJWT.
"""

from __future__ import annotations

import pytest
from fastapi import HTTPException


pytestmark = pytest.mark.usefixtures("mock_entra_http", "entra_env")


# --- DEV_MODE bypass ----------------------------------------------------

def test_dev_mode_token_bypasses_verification(monkeypatch):
    """DEV_MODE=true + the local token returns the admin shape without DB."""
    monkeypatch.setenv("DEV_MODE", "true")
    import importlib
    import auth
    importlib.reload(auth)

    import asyncio
    user = asyncio.get_event_loop().run_until_complete(
        auth.get_current_user(authorization="Bearer dev-admin-local")
    )
    assert user["uid"] == "dev-admin"
    assert user["role"] == "admin"
    assert user["email"] == "dev@local"


def test_dev_mode_off_rejects_dev_token():
    """When DEV_MODE is unset the dev token is treated as a real JWT and fails."""
    import asyncio
    import auth
    with pytest.raises(HTTPException) as exc:
        asyncio.get_event_loop().run_until_complete(
            auth.get_current_user(authorization="Bearer dev-admin-local")
        )
    assert exc.value.status_code == 401


# --- Header-shape validation --------------------------------------------

def test_missing_authorization_header_returns_401():
    import asyncio
    import auth
    with pytest.raises(HTTPException) as exc:
        asyncio.get_event_loop().run_until_complete(
            auth.get_current_user(authorization=None)
        )
    assert exc.value.status_code == 401
    assert exc.value.detail == "לא מחובר"


def test_non_bearer_scheme_returns_401():
    import asyncio
    import auth
    with pytest.raises(HTTPException) as exc:
        asyncio.get_event_loop().run_until_complete(
            auth.get_current_user(authorization="Basic abcdef")
        )
    assert exc.value.status_code == 401


# --- Happy path ---------------------------------------------------------

def test_valid_token_extracts_claims(make_token, monkeypatch):
    """A correctly-signed token returns the expected user dict."""
    # Stub get_or_create_user so this test doesn't need a live Postgres.
    import storage
    monkeypatch.setattr(
        storage, "get_or_create_user",
        lambda uid, email="", full_name="": {
            "uid": uid, "email": email, "full_name": full_name,
            "role": "viewer", "linked_manager": "", "avatar": "",
        },
    )

    import asyncio
    import auth
    token = make_token(oid="alice-oid", email="alice@example.com", name="Alice")
    user = asyncio.get_event_loop().run_until_complete(
        auth.get_current_user(authorization=f"Bearer {token}")
    )
    assert user["uid"] == "alice-oid"
    assert user["email"] == "alice@example.com"
    assert user["full_name"] == "Alice"
    assert user["role"] == "viewer"


def test_role_comes_from_db_not_token(make_token, monkeypatch):
    """Even if the token claims role=admin, the DB lookup is authoritative."""
    import storage
    monkeypatch.setattr(
        storage, "get_or_create_user",
        lambda uid, email="", full_name="": {
            "uid": uid, "email": email, "full_name": full_name,
            "role": "economist", "linked_manager": "Lena", "avatar": "",
        },
    )

    import asyncio
    import auth
    token = make_token(extra_claims={"roles": ["admin"]})
    user = asyncio.get_event_loop().run_until_complete(
        auth.get_current_user(authorization=f"Bearer {token}")
    )
    assert user["role"] == "economist"
    assert user["linked_manager"] == "Lena"


# --- Negative paths -----------------------------------------------------

def test_expired_token_rejected(make_token):
    import asyncio
    import auth
    token = make_token(exp_offset=-60)  # expired 60s ago
    with pytest.raises(HTTPException) as exc:
        asyncio.get_event_loop().run_until_complete(
            auth.get_current_user(authorization=f"Bearer {token}")
        )
    assert exc.value.status_code == 401


def test_wrong_audience_rejected(make_token):
    import asyncio
    import auth
    token = make_token(aud="some-other-client-id")
    with pytest.raises(HTTPException) as exc:
        asyncio.get_event_loop().run_until_complete(
            auth.get_current_user(authorization=f"Bearer {token}")
        )
    assert exc.value.status_code == 401


def test_wrong_issuer_rejected(make_token):
    import asyncio
    import auth
    token = make_token(iss="https://evil.example.com/v2.0")
    with pytest.raises(HTTPException) as exc:
        asyncio.get_event_loop().run_until_complete(
            auth.get_current_user(authorization=f"Bearer {token}")
        )
    assert exc.value.status_code == 401


def test_tampered_signature_rejected(make_token):
    """Flip one byte of the signature segment — verify should fail."""
    import asyncio
    import auth
    token = make_token()
    head, payload, sig = token.split(".")
    # Flip a single character (avoid the padding '=' which would still decode).
    sig_bad = ("A" if sig[0] != "A" else "B") + sig[1:]
    tampered = f"{head}.{payload}.{sig_bad}"
    with pytest.raises(HTTPException) as exc:
        asyncio.get_event_loop().run_until_complete(
            auth.get_current_user(authorization=f"Bearer {tampered}")
        )
    assert exc.value.status_code == 401


def test_unknown_kid_triggers_refresh_then_rejects(make_token):
    """A token signed with a kid the JWKS doesn't know about should 401.

    The cache will refresh once (since the kid isn't cached) and still
    not find a match, so the request is rejected.
    """
    import asyncio
    import auth
    token = make_token(kid="ghost-kid")
    with pytest.raises(HTTPException) as exc:
        asyncio.get_event_loop().run_until_complete(
            auth.get_current_user(authorization=f"Bearer {token}")
        )
    assert exc.value.status_code == 401


def test_garbage_token_rejected():
    import asyncio
    import auth
    with pytest.raises(HTTPException) as exc:
        asyncio.get_event_loop().run_until_complete(
            auth.get_current_user(authorization="Bearer not-a-jwt")
        )
    assert exc.value.status_code == 401


def test_missing_client_id_returns_503(make_token, monkeypatch):
    """If ENTRA_CLIENT_ID is unset, the failure is 503 (config), not 401."""
    monkeypatch.delenv("ENTRA_CLIENT_ID", raising=False)
    import importlib
    import auth
    importlib.reload(auth)

    import asyncio
    token = make_token()
    with pytest.raises(HTTPException) as exc:
        asyncio.get_event_loop().run_until_complete(
            auth.get_current_user(authorization=f"Bearer {token}")
        )
    assert exc.value.status_code == 503


# --- Role gates ---------------------------------------------------------

def test_require_admin_passes_admin(monkeypatch):
    import asyncio
    import auth
    user = {"uid": "u", "email": "", "username": "", "role": "admin",
            "linked_manager": "", "full_name": ""}
    result = asyncio.get_event_loop().run_until_complete(auth.require_admin(user=user))
    assert result is user


def test_require_admin_blocks_viewer():
    import asyncio
    import auth
    user = {"uid": "u", "email": "", "username": "", "role": "viewer",
            "linked_manager": "", "full_name": ""}
    with pytest.raises(HTTPException) as exc:
        asyncio.get_event_loop().run_until_complete(auth.require_admin(user=user))
    assert exc.value.status_code == 403


def test_require_editor_admin_and_economist_only():
    import asyncio
    import auth
    for role, ok in [("admin", True), ("economist", True),
                     ("project_manager", False), ("viewer", False)]:
        user = {"uid": "u", "email": "", "username": "", "role": role,
                "linked_manager": "", "full_name": ""}
        if ok:
            assert asyncio.get_event_loop().run_until_complete(
                auth.require_editor(user=user)
            ) is user
        else:
            with pytest.raises(HTTPException) as exc:
                asyncio.get_event_loop().run_until_complete(
                    auth.require_editor(user=user)
                )
            assert exc.value.status_code == 403
