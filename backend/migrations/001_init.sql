-- Phase B initial schema.
-- Apply with:  psql "$DATABASE_URL" -f backend/migrations/001_init.sql
-- Idempotent: every CREATE uses IF NOT EXISTS.

BEGIN;

-- ---------------------------------------------------------------------------
-- users
-- Mirrors the identity that previously lived in Firebase Auth + Firestore.
-- uid stays a TEXT primary key so callers can keep using the same opaque ID
-- (today: DEV_MODE 'dev-admin'; later: Entra External ID 'oid' / 'sub').
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    uid             TEXT        PRIMARY KEY,
    email           TEXT        NOT NULL UNIQUE,
    full_name       TEXT        NOT NULL DEFAULT '',
    role            TEXT        NOT NULL DEFAULT 'viewer',
    linked_manager  TEXT        NOT NULL DEFAULT '',
    avatar          TEXT        NOT NULL DEFAULT '',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- projects
-- Hybrid: a few hot fields are first-class columns for indexing/filtering;
-- the rest of the form payload (subcontractors, expense_lines_*, actuals,
-- revenue_payment_terms, etc.) lives in `data` JSONB.
-- id is the project_name (Hebrew strings allowed — TEXT is UTF-8).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS projects (
    id            TEXT        PRIMARY KEY,
    manager       TEXT        NOT NULL DEFAULT '',
    axis          TEXT        NOT NULL DEFAULT '',
    area          TEXT        NOT NULL DEFAULT '',
    status        TEXT        NOT NULL DEFAULT 'active',
    source        TEXT        NOT NULL DEFAULT 'form',
    last_updated  TIMESTAMPTZ,
    data          JSONB       NOT NULL DEFAULT '{}'::JSONB
);

CREATE INDEX IF NOT EXISTS idx_projects_manager ON projects (manager);
CREATE INDEX IF NOT EXISTS idx_projects_axis    ON projects (axis);
CREATE INDEX IF NOT EXISTS idx_projects_status  ON projects (status);
CREATE INDEX IF NOT EXISTS idx_projects_data    ON projects USING GIN (data);

-- ---------------------------------------------------------------------------
-- reports
-- Normalized — the old Firestore `reports` collection stored flat docs.
-- project_id references projects.id; on project deletion, reports go too.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reports (
    id           SERIAL      PRIMARY KEY,
    project_id   TEXT        NOT NULL REFERENCES projects (id) ON DELETE CASCADE,
    month        INTEGER,
    type         TEXT        NOT NULL,
    title        TEXT        NOT NULL,
    amount       NUMERIC(18, 2),
    description  TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_reports_project  ON reports (project_id);
CREATE INDEX IF NOT EXISTS idx_reports_created  ON reports (created_at);

COMMIT;
