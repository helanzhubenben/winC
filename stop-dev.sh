#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_DIR="$ROOT_DIR/.runtime"

stop_service() {
  local name="$1"
  local pid_file="$RUNTIME_DIR/${name}.pid"

  if [[ ! -f "$pid_file" ]]; then
    printf '[%s] No PID file found.\n' "$name"
    return 0
  fi

  local pid
  pid="$(cat "$pid_file")"
  if [[ -z "$pid" ]] || ! kill -0 "$pid" >/dev/null 2>&1; then
    printf '[%s] Not running.\n' "$name"
    rm -f "$pid_file"
    return 0
  fi

  printf '[%s] Stopping PID %s...\n' "$name" "$pid"
  kill -- "-$pid" >/dev/null 2>&1 || kill "$pid"
  rm -f "$pid_file"
}

stop_service backend
stop_service frontend
