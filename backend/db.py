"""PostgreSQL connection pool.

Local dev: DATABASE_URL is read from .env (loaded by main.py/auth.py).
Production (Azure Container Apps): AZURE_KEY_VAULT_URL is set, and the
managed-identity-authenticated DefaultAzureCredential pulls the
POSTGRES-CONN secret from Key Vault.

The pool is created lazily on the first call to ``get_pool()`` so that
importing this module never reaches out to the network or the database.
This matters: it's the same trap that the firebase_admin/Firestore
boot path fell into pre-Phase-0.
"""

from __future__ import annotations

import os
import threading
from contextlib import contextmanager
from typing import Iterator, Optional

from psycopg import Connection
from psycopg_pool import ConnectionPool


_POOL: Optional[ConnectionPool] = None
_POOL_LOCK = threading.Lock()

# Tuned for an internal tool with 5-15 users on a Burstable B1ms.
_MIN_SIZE = 1
_MAX_SIZE = 8


def _resolve_conn_string() -> str:
    """Return a libpq connection string from the environment."""
    kv_url = os.environ.get("AZURE_KEY_VAULT_URL", "").strip()
    if kv_url:
        # Imported lazily so local dev doesn't need azure-* installed.
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient

        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=kv_url, credential=credential)
        secret_name = os.environ.get("POSTGRES_SECRET_NAME", "POSTGRES-CONN")
        return client.get_secret(secret_name).value

    conn = os.environ.get("DATABASE_URL", "").strip()
    if not conn:
        raise RuntimeError(
            "No database connection configured. Set DATABASE_URL for local "
            "dev or AZURE_KEY_VAULT_URL (with POSTGRES-CONN in the vault) "
            "for production."
        )
    return conn


def get_pool() -> ConnectionPool:
    """Return the process-wide pool, creating it on first use."""
    global _POOL
    if _POOL is not None:
        return _POOL
    with _POOL_LOCK:
        if _POOL is None:
            _POOL = ConnectionPool(
                conninfo=_resolve_conn_string(),
                min_size=_MIN_SIZE,
                max_size=_MAX_SIZE,
                kwargs={"autocommit": False},
                open=True,
            )
    return _POOL


@contextmanager
def get_conn() -> Iterator[Connection]:
    """Yield a pooled connection. Commits on normal exit, rolls back on error."""
    pool = get_pool()
    with pool.connection() as conn:
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise


def close_pool() -> None:
    """Close the pool. Useful for tests and graceful shutdown."""
    global _POOL
    with _POOL_LOCK:
        if _POOL is not None:
            _POOL.close()
            _POOL = None
