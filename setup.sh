#!/usr/bin/env bash
set -euo pipefail

echo "=== GM Problem Viewer — Setup ==="
echo

# Check for uv
if ! command -v uv &>/dev/null; then
    echo "ERROR: 'uv' is not installed."
    echo "Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi
echo "Found uv: $(uv --version)"

# Check for node
if ! command -v node &>/dev/null; then
    echo "ERROR: 'node' is not installed."
    echo "Install Node 24+ via nvm: nvm install v24"
    exit 1
fi

NODE_MAJOR=$(node --version | sed 's/v\([0-9]*\).*/\1/')
if [ "$NODE_MAJOR" -lt 24 ]; then
    echo "WARNING: Node $(node --version) detected, but v24+ is recommended."
    echo "Switch with: nvm use v24"
fi
echo "Found node: $(node --version)"

# Install Python dependencies
echo
echo "Installing Python dependencies..."
uv sync

# Install frontend dependencies
echo
echo "Installing frontend dependencies..."
(cd frontend && npm install)

echo
echo "=== Setup complete! ==="
echo "Run ./start.sh to launch the application."
