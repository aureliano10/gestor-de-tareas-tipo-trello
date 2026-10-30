#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

if [ -x "$ROOT_DIR/.venv/bin/python" ]; then
  PYTHON="$ROOT_DIR/.venv/bin/python"
else
  PYTHON="python3"
fi

if ! "$PYTHON" -c "import uvicorn" >/dev/null 2>&1; then
  echo "No se encontró uvicorn. Creá el .venv e instalá backend/requirements.txt." >&2
  exit 1
fi

cd "$SCRIPT_DIR"
exec "$PYTHON" -m uvicorn app.main:app --reload --host "${HOST:-127.0.0.1}" --port "${PORT:-8000}"
