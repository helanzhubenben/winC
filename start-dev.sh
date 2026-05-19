#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
RUNTIME_DIR="$ROOT_DIR/.runtime"
BACKEND_VENV="$BACKEND_DIR/.venv"
BACKEND_PYTHON="$BACKEND_VENV/bin/python"
BACKEND_PIP="$BACKEND_VENV/bin/pip"
BACKEND_PID_FILE="$RUNTIME_DIR/backend.pid"
FRONTEND_PID_FILE="$RUNTIME_DIR/frontend.pid"

mkdir -p "$RUNTIME_DIR"

log() {
  printf '[%s] %s\n' "$(date '+%H:%M:%S')" "$*"
}

fail() {
  printf '[ERROR] %s\n' "$*" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "Missing command: $1"
}

is_running() {
  local pid_file="$1"
  [[ -f "$pid_file" ]] || return 1
  local pid
  pid="$(cat "$pid_file")"
  [[ -n "$pid" ]] && kill -0 "$pid" >/dev/null 2>&1
}

start_background() {
  local name="$1"
  local pid_file="$2"
  local work_dir="$3"
  shift 3

  if is_running "$pid_file"; then
    log "$name is already running with PID $(cat "$pid_file")."
    return 0
  fi

  log "Starting $name..."
  setsid bash -c 'cd "$1" || exit 1; shift; exec "$@"' _ "$work_dir" "$@" \
    >"$RUNTIME_DIR/${name}.out.log" 2>"$RUNTIME_DIR/${name}.err.log" < /dev/null &
  echo "$!" >"$pid_file"
  sleep 2

  if is_running "$pid_file"; then
    log "$name started with PID $(cat "$pid_file")."
  else
    fail "$name failed to start. Check $RUNTIME_DIR/${name}.err.log"
  fi
}

require_command python3
require_command node
require_command npm

if [[ -d "$BACKEND_VENV" && (! -x "$BACKEND_PYTHON" || ! -x "$BACKEND_PIP") ]]; then
  log "Removing incomplete backend virtual environment: $BACKEND_VENV"
  rm -rf "$BACKEND_VENV"
fi

if [[ ! -d "$BACKEND_VENV" ]]; then
  log "Creating backend virtual environment: $BACKEND_VENV"
  if ! python3 -m venv "$BACKEND_VENV"; then
    rm -rf "$BACKEND_VENV"
    fail "Failed to create backend virtual environment. On Ubuntu/Debian, run: sudo apt-get install python3.12-venv"
  fi
fi

log "Installing backend dependencies..."
"$BACKEND_PIP" install -r "$BACKEND_DIR/requirements.txt"

log "Applying backend migrations..."
(
  cd "$BACKEND_DIR"
  "$BACKEND_PYTHON" manage.py migrate
)

if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
  log "Installing frontend dependencies..."
  (
    cd "$FRONTEND_DIR"
    npm install
  )
fi

start_background backend "$BACKEND_PID_FILE" "$BACKEND_DIR" "$BACKEND_PYTHON" manage.py runserver 127.0.0.1:8000
start_background frontend "$FRONTEND_PID_FILE" "$FRONTEND_DIR" npm run dev -- --host 127.0.0.1

log "Backend:  http://127.0.0.1:8000"
log "Frontend: http://127.0.0.1:5173"
log "Logs:     $RUNTIME_DIR"
log "Stop:     ./stop-dev.sh"
