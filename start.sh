#!/usr/bin/env bash
set -euo pipefail

# Cleanup function to kill background processes
cleanup() {
    echo
    echo "Shutting down..."
    if [ -n "${BACKEND_PID:-}" ]; then
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    exit 0
}
trap cleanup SIGINT SIGTERM

# Load config.yaml values as defaults (env vars take priority)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config.yaml"
if [ -f "$CONFIG_FILE" ]; then
    yaml_val() {
        grep "^$1:" "$CONFIG_FILE" 2>/dev/null | sed 's/^[^:]*:\s*//' | sed 's/\s*#.*//' | xargs
    }
    : "${PORT:=$(yaml_val port)}"
    : "${FRONTEND_PORT:=$(yaml_val frontend_port)}"
    : "${PROBLEMS_ROOT:=$(yaml_val problems_root)}"
    : "${CACHE_ROOT:=$(yaml_val cache_root)}"
    export PORT FRONTEND_PORT PROBLEMS_ROOT CACHE_ROOT
fi

echo "=== GM Problem Viewer ==="
echo

# Start backend
echo "Starting backend on port ${PORT:-8001}..."
uv run python -m api &
BACKEND_PID=$!

# Give the backend a moment to start
sleep 1

# Start frontend
echo "Starting frontend dev server..."
echo
echo "  Backend API:  http://localhost:${PORT:-8001}  (docs at /docs)"
echo "  Frontend UI:  http://localhost:${FRONTEND_PORT:-5173}"
echo
echo "Press Ctrl+C to stop both servers."
echo

cd frontend && npm run dev

# If frontend exits, clean up backend
cleanup
