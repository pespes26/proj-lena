"""Phase B/C — storage layer tests against a live Postgres.

Exercises every public function in ``storage.py`` and the new
``get_or_create_user`` helper. Requires ``DATABASE_URL`` to point at a
Postgres with the Phase B schema already applied; otherwise the suite
skips.
"""

from __future__ import annotations

import pytest


def test_load_empty_returns_empty_dict(live_db):
    from storage import load_projects_firestore, load_reports_firestore
    assert load_projects_firestore() == {}
    assert load_reports_firestore() == []


def test_save_and_load_single_project(live_db):
    from storage import save_project_firestore, load_projects_firestore
    save_project_firestore("alpha", {
        "manager": "Lena", "axis": "north", "area": "ops",
        "total_revenue": 100000,
    })
    out = load_projects_firestore()
    assert "alpha" in out
    assert out["alpha"]["manager"] == "Lena"
    assert out["alpha"]["axis"] == "north"
    # JSONB blob round-trips
    assert out["alpha"]["total_revenue"] == 100000


def test_save_with_missing_fields_applies_defaults(live_db):
    from storage import save_project_firestore, load_projects_firestore
    save_project_firestore("bare", {})
    out = load_projects_firestore()["bare"]
    assert out["manager"] == ""
    assert out["axis"] == ""
    assert out["status"] == "active"
    assert out["source"] == "form"


def test_save_project_upsert(live_db):
    from storage import save_project_firestore, load_projects_firestore
    save_project_firestore("up", {"manager": "A", "axis": "x"})
    save_project_firestore("up", {"manager": "B", "axis": "y"})
    out = load_projects_firestore()["up"]
    assert out["manager"] == "B"
    assert out["axis"] == "y"


def test_delete_nonexistent_project_is_noop(live_db):
    from storage import delete_project_firestore
    delete_project_firestore("never-existed")  # should not raise


def test_save_all_replaces_table(live_db):
    from storage import (
        save_project_firestore, save_all_projects_firestore,
        load_projects_firestore,
    )
    save_project_firestore("keep", {"manager": "K"})
    save_project_firestore("drop", {"manager": "D"})
    save_all_projects_firestore({"only": {"manager": "Z"}})
    out = load_projects_firestore()
    assert set(out.keys()) == {"only"}


def test_save_all_empty_wipes_everything(live_db):
    from storage import (
        save_project_firestore, save_all_projects_firestore,
        load_projects_firestore,
    )
    save_project_firestore("x", {"manager": "X"})
    save_all_projects_firestore({})
    assert load_projects_firestore() == {}


def test_hebrew_project_name_roundtrip(live_db):
    from storage import save_project_firestore, load_projects_firestore
    name = "פרויקט עברי"
    save_project_firestore(name, {"manager": "לנה"})
    out = load_projects_firestore()
    assert name in out
    assert out[name]["manager"] == "לנה"


# --- Reports -----------------------------------------------------------

def test_save_report_requires_project(live_db):
    from storage import save_report_firestore
    with pytest.raises(ValueError):
        save_report_firestore({"title": "no project"})


def test_save_report_for_unknown_project_fk_rejects(live_db):
    import psycopg
    from storage import save_report_firestore
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        save_report_firestore({"project": "missing", "type": "x", "title": "y"})


def test_report_roundtrip_and_cascade(live_db):
    from storage import (
        save_project_firestore, save_report_firestore,
        load_reports_firestore, delete_project_firestore,
    )
    save_project_firestore("p", {"manager": "M"})
    save_report_firestore({
        "project": "p", "month": 5, "type": "incident",
        "title": "fire", "amount": 999.50, "description": "smoke alarm",
    })
    reports = load_reports_firestore()
    assert len(reports) == 1
    r = reports[0]
    assert r["project"] == "p"
    assert r["title"] == "fire"
    assert r["amount"] == 999.50

    delete_project_firestore("p")
    assert load_reports_firestore() == []


# --- Users -------------------------------------------------------------

def test_get_or_create_user_inserts_default_viewer(live_db):
    from storage import get_or_create_user
    u = get_or_create_user(uid="oid-1", email="a@b.com", full_name="A B")
    assert u["uid"] == "oid-1"
    assert u["email"] == "a@b.com"
    assert u["full_name"] == "A B"
    assert u["role"] == "viewer"
    assert u["linked_manager"] == ""


def test_get_or_create_user_is_idempotent(live_db):
    from storage import get_or_create_user
    first = get_or_create_user(uid="oid-2", email="x@y.com", full_name="X Y")
    second = get_or_create_user(uid="oid-2", email="other@z.com", full_name="Z")
    # Same row, original values preserved (don't trample on re-login).
    assert second["uid"] == "oid-2"
    assert second["email"] == first["email"]
    assert second["full_name"] == first["full_name"]
    assert second["role"] == "viewer"


def test_get_or_create_user_preserves_promoted_role(live_db):
    """If an admin promoted the user, a subsequent login keeps the role."""
    from db import get_conn
    from storage import get_or_create_user

    get_or_create_user(uid="oid-3", email="m@b.com", full_name="M B")
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET role='admin', linked_manager='Lena' WHERE uid=%s",
                ("oid-3",),
            )
    again = get_or_create_user(uid="oid-3", email="m@b.com", full_name="M B")
    assert again["role"] == "admin"
    assert again["linked_manager"] == "Lena"
