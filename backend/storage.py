"""Persistence layer — PostgreSQL via psycopg3 sync pool.

Phase B: replaces the JSON-file stubs that Phase 0 left behind. Function
names keep their ``_firestore`` suffix so call sites in
``services/unified.py``, ``routers/reports.py``, and
``create_test_projects.py`` need zero changes (renamed in a later pass).

Data model (see ``migrations/001_init.sql``):

* ``projects(id, manager, axis, area, status, source, last_updated, data JSONB)``
  — a few hot fields are first-class columns for indexing; the rest of
  the form payload lives in ``data``.
* ``reports(id, project_id, month, type, title, amount, description, created_at)``
  — normalized; ``project_id`` references ``projects.id``.

All public functions preserve their pre-Phase-B sync signatures.
"""

from __future__ import annotations

import os
import json
import datetime as dt
from typing import Any, Dict, List, Optional

from psycopg.types.json import Jsonb

from db import get_conn


# --- JSON helpers (kept for callers that still touch local files) ---

def load_json(path: str, default: Any = None) -> Any:
    if not os.path.exists(path):
        return default if default is not None else {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# --- Projects ---

# Hot columns that get hoisted out of `data` for indexing/filtering. Kept
# in sync with the form payload on every write; on read we merge them
# back into the dict so callers see the same shape as before.
_HOT_COLS = ("manager", "axis", "area", "status", "source")


def _parse_last_updated(value: Any) -> Optional[dt.datetime]:
    if not value:
        return None
    if isinstance(value, dt.datetime):
        return value
    if isinstance(value, str):
        try:
            return dt.datetime.fromisoformat(value)
        except ValueError:
            return None
    return None


def _row_to_project(row: tuple) -> Dict[str, Any]:
    """Reassemble a project dict from a row, merging hot cols back into data."""
    pid, manager, axis, area, status, source, last_updated, data = row
    payload: Dict[str, Any] = dict(data) if data else {}
    payload.setdefault("project_name", pid)
    payload["manager"] = manager
    payload["axis"] = axis
    payload["area"] = area
    payload["status"] = status
    payload["source"] = source
    if last_updated is not None:
        payload["last_updated"] = last_updated.isoformat()
    return payload


def load_projects_firestore() -> Dict[str, Dict[str, Any]]:
    """Return every project, keyed by id (project name)."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, manager, axis, area, status, source, last_updated, data "
                "FROM projects"
            )
            return {row[0]: _row_to_project(row) for row in cur.fetchall()}


def save_project_firestore(name: str, data: Dict[str, Any]) -> None:
    """Insert or update one project."""
    payload = dict(data or {})
    hot = {col: payload.get(col, "") or "" for col in _HOT_COLS}
    if "status" not in payload or not payload.get("status"):
        hot["status"] = "active"
    if "source" not in payload or not payload.get("source"):
        hot["source"] = "form"
    last_updated = _parse_last_updated(payload.get("last_updated"))

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO projects (id, manager, axis, area, status, source, last_updated, data)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    manager      = EXCLUDED.manager,
                    axis         = EXCLUDED.axis,
                    area         = EXCLUDED.area,
                    status       = EXCLUDED.status,
                    source       = EXCLUDED.source,
                    last_updated = EXCLUDED.last_updated,
                    data         = EXCLUDED.data
                """,
                (
                    name,
                    hot["manager"],
                    hot["axis"],
                    hot["area"],
                    hot["status"],
                    hot["source"],
                    last_updated,
                    Jsonb(payload),
                ),
            )


def save_all_projects_firestore(data: Dict[str, Dict[str, Any]]) -> None:
    """Replace the projects table with the given dict, in a single transaction."""
    rows = []
    for name, project in (data or {}).items():
        payload = dict(project or {})
        manager = payload.get("manager", "") or ""
        axis = payload.get("axis", "") or ""
        area = payload.get("area", "") or ""
        status = payload.get("status", "") or "active"
        source = payload.get("source", "") or "form"
        last_updated = _parse_last_updated(payload.get("last_updated"))
        rows.append((name, manager, axis, area, status, source, last_updated, Jsonb(payload)))

    with get_conn() as conn:
        with conn.cursor() as cur:
            # DELETE (not TRUNCATE) — doesn't require table ownership and
            # still cascades to `reports` via the FK's ON DELETE CASCADE.
            cur.execute("DELETE FROM projects")
            if rows:
                cur.executemany(
                    """
                    INSERT INTO projects
                        (id, manager, axis, area, status, source, last_updated, data)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    rows,
                )


def delete_project_firestore(name: str) -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM projects WHERE id = %s", (name,))


# --- Users ---

def get_or_create_user(uid: str, email: str = "", full_name: str = "") -> Dict[str, Any]:
    """Look up a user by uid, inserting a default-role row on first sight.

    Called from the auth layer immediately after a token verifies. The
    role/linked_manager/avatar fields are managed in-app (Phase D), never
    from the token, so first-time logins land as ``role='viewer'`` until
    an admin promotes them.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT uid, email, full_name, role, linked_manager, avatar "
                "FROM users WHERE uid = %s",
                (uid,),
            )
            row = cur.fetchone()
            if row:
                u, e, n, r, lm, av = row
                return {
                    'uid': u, 'email': e, 'full_name': n,
                    'role': r, 'linked_manager': lm, 'avatar': av,
                }
            # First time we've seen this principal — insert as viewer.
            # ON CONFLICT(uid) silently no-ops if a concurrent request
            # inserted first; we re-read in that case.
            cur.execute(
                """
                INSERT INTO users (uid, email, full_name, role)
                VALUES (%s, %s, %s, 'viewer')
                ON CONFLICT (uid) DO NOTHING
                RETURNING uid, email, full_name, role, linked_manager, avatar
                """,
                (uid, email, full_name),
            )
            inserted = cur.fetchone()
            if inserted:
                u, e, n, r, lm, av = inserted
                return {
                    'uid': u, 'email': e, 'full_name': n,
                    'role': r, 'linked_manager': lm, 'avatar': av,
                }
            cur.execute(
                "SELECT uid, email, full_name, role, linked_manager, avatar "
                "FROM users WHERE uid = %s",
                (uid,),
            )
            u, e, n, r, lm, av = cur.fetchone()
            return {
                'uid': u, 'email': e, 'full_name': n,
                'role': r, 'linked_manager': lm, 'avatar': av,
            }


# --- Reports ---

def _row_to_report(row: tuple) -> Dict[str, Any]:
    rid, project_id, month, rtype, title, amount, description, created_at = row
    return {
        "_doc_id": str(rid),
        "project": project_id,
        "month": month,
        "type": rtype,
        "title": title,
        "amount": float(amount) if amount is not None else None,
        "description": description,
        "created_at": created_at.isoformat() if created_at else None,
    }


def load_reports_firestore() -> List[Dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, project_id, month, type, title, amount, description, created_at "
                "FROM reports ORDER BY created_at"
            )
            return [_row_to_report(r) for r in cur.fetchall()]


def save_report_firestore(report: Dict[str, Any]) -> None:
    project = report.get("project")
    if not project:
        raise ValueError("report.project is required")

    created_at = _parse_last_updated(report.get("created_at"))
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO reports (project_id, month, type, title, amount, description, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, COALESCE(%s, now()))
                """,
                (
                    project,
                    report.get("month"),
                    report.get("type", ""),
                    report.get("title", ""),
                    report.get("amount"),
                    report.get("description"),
                    created_at,
                ),
            )
