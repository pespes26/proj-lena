#!/bin/bash
set -euo pipefail

# Only run in remote Claude Code on the web environments
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# ── PostgreSQL ────────────────────────────────────────────────────────────────
echo "[startup] Starting PostgreSQL..."
service postgresql start || true
sleep 1

# Ensure the logfi DB user and database exist (idempotent)
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='logfi'" | grep -q 1 || \
  sudo -u postgres psql -c "CREATE USER logfi WITH PASSWORD 'logfi123';"

sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='logfi'" | grep -q 1 || \
  sudo -u postgres psql -c "CREATE DATABASE logfi OWNER logfi;"

sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE logfi TO logfi;" > /dev/null

# Apply schema (IF NOT EXISTS guards make this idempotent)
sudo -u postgres psql -d logfi -f "$CLAUDE_PROJECT_DIR/backend/migrations/001_init.sql" > /dev/null

sudo -u postgres psql -d logfi -c "GRANT ALL ON ALL TABLES IN SCHEMA public TO logfi;" > /dev/null
sudo -u postgres psql -d logfi -c "GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO logfi;" > /dev/null

# Persist DATABASE_URL for the session
echo 'export DATABASE_URL="postgresql://logfi:logfi123@localhost:5432/logfi"' >> "$CLAUDE_ENV_FILE"
echo 'export DEV_MODE="true"' >> "$CLAUDE_ENV_FILE"

echo "[startup] PostgreSQL ready."

# ── Python dependencies ───────────────────────────────────────────────────────
echo "[startup] Installing Python dependencies..."
pip install -q -r "$CLAUDE_PROJECT_DIR/backend/requirements.txt"
# The system ships a broken PyJWT/cryptography; force pip's version to win.
pip install -q --ignore-installed "PyJWT[crypto]" cryptography
# Test dependencies
pip install -q pytest cryptography
echo "[startup] Python dependencies installed."

# ── Frontend dependencies ─────────────────────────────────────────────────────
echo "[startup] Installing frontend dependencies..."
cd "$CLAUDE_PROJECT_DIR/frontend"
npm install --prefer-offline --no-audit --no-fund
echo "[startup] Frontend dependencies installed."

echo "[startup] Done."
