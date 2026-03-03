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
echo "  Frontend UI:  http://localhost:5173"
echo
echo "Press Ctrl+C to stop both servers."
echo

cd frontend && npm run dev

# If frontend exits, clean up backend
cleanup
