#!/usr/bin/env bash
# Wrapper to start server in background and capture debug info for devcontainer postStartCommand
# This script is safe to run non-interactively. It will create two files in the workspace:
# - server_http.log (server stdout/stderr)
# - server_http.debug.log (wrapper debug information)
# - server_http.pid (PID of backgrounded process)

WS="$(pwd)"
LOG="$WS/server_http.log"
DBG="$WS/server_http.debug.log"
PIDFILE="$WS/server_http.pid"

{
  echo "=== start-server.sh ==="
  date
  echo "PWD: $(pwd)"
  echo "Workspace: $WS"
  echo "--- Environment ---"
  env
  echo "-------------------"
} >> "$DBG"

# Start the server in the background using nohup so it survives the shell exit
nohup python server_http.py >> "$LOG" 2>&1 &
PID=$!
echo $PID > "$PIDFILE"
sleep 1

if kill -0 "$PID" 2>/dev/null; then
  echo "Server started, pid=$PID" >> "$DBG"
else
  echo "Server failed to start, pid=$PID" >> "$DBG"
  echo "Last 200 lines of $LOG:" >> "$DBG"
  tail -n 200 "$LOG" >> "$DBG" 2>/dev/null || true
fi

# Give it a moment and report listening sockets for port 8000
sleep 1
{
  echo "--- Listening sockets (ss/netstat) ---"
  if command -v ss >/dev/null 2>&1; then
    ss -ltnp | grep ":8000" || true
  elif command -v netstat >/dev/null 2>&1; then
    netstat -ltnp | grep ":8000" || true
  else
    echo "(ss/netstat not available)"
  fi
  echo "--------------------------------------"
} >> "$DBG"

echo "start-server.sh finished" >> "$DBG"

exit 0
