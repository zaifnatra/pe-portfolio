#!/bin/bash
set -e

# Run from the project root regardless of where the script is invoked from.
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

VENV_PYTHON="$PROJECT_DIR/python3-virtualenv/bin/python"

if [ -x "$VENV_PYTHON" ]; then
  PYTHON="$VENV_PYTHON"
else
  # No virtualenv here (e.g. the VPS, where the app runs in Docker).
  echo "No virtualenv at $VENV_PYTHON, falling back to system python3."
  PYTHON="$(command -v python3)"
fi

"$PYTHON" -m unittest discover -v tests/
