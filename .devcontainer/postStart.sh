#!/usr/bin/env bash
set -euo pipefail

echo "[devcontainer] postStart: ensuring MCP Content Library is bootstrapped and running"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# Non-interactive bootstrap (creates .venv and installs deps)
if [ -f "./bootstrap.sh" ]; then
  echo "[devcontainer] Running bootstrap (non-interactive)"
  bash ./bootstrap.sh --non-interactive || true
fi

# Activate venv if present
if [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

# Ensure storage directory exists
export MCP_SNIPPETS_ROOT="${MCP_SNIPPETS_ROOT:-$HOME/.mcp_snippets}"
mkdir -p "$MCP_SNIPPETS_ROOT"

# Start server in background if not already running
PID_FILE="/tmp/mcp_server.pid"
LOG_FILE="/tmp/mcp_server.log"

is_running() {
  if [ -f "$PID_FILE" ]; then
    pid=$(cat "$PID_FILE")
    if kill -0 "$pid" 2>/dev/null; then
      return 0
    else
      return 1
    fi
  fi
  return 1
}

if is_running; then
  echo "[devcontainer] MCP server already running (pid $(cat "$PID_FILE"))"
  exit 0
fi

HOST="${MCP_HTTP_HOST:-0.0.0.0}"
PORT="${MCP_HTTP_PORT:-8000}"

echo "[devcontainer] Starting MCP server on $HOST:$PORT"

# Start via the project's python entrypoint so our server_http runner is used
# Use nohup to keep it running in background across sessions in Codespaces
nohup ${ROOT_DIR}/.venv/bin/python ${ROOT_DIR}/server_http.py > "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"

echo "[devcontainer] MCP server started (pid $(cat "$PID_FILE")); logs: $LOG_FILE"

exit 0
