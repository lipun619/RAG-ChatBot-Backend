#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if command -v python3.12 >/dev/null 2>&1; then
  PYTHON=python3.12
elif command -v python >/dev/null 2>&1; then
  PYTHON=python
elif command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
else
  echo "ERROR: Python 3.12 is required and not found on PATH. Install Python 3.12.x and try again."
  exit 1
fi

if "$PYTHON" - <<'PY'
import sys
raise SystemExit(0 if sys.version_info[:2] == (3, 12) else 1)
PY
then
  echo "Using Python $($PYTHON -V 2>&1)"
else
  echo "ERROR: This project requires Python 3.12.x. Current interpreter: $($PYTHON -V 2>&1)"
  echo "Install Python 3.12.x or run: python3.12 -m venv venv"
  exit 1
fi

if [ ! -d "venv" ]; then
  echo "Creating virtual environment in ./venv using $PYTHON..."
  "$PYTHON" -m venv venv
else
  echo "Using existing virtual environment in ./venv"
  VENV_PYTHON="./venv/bin/python"
  if "$VENV_PYTHON" - <<'PY'
import sys
raise SystemExit(0 if sys.version_info[:2] == (3, 12) else 1)
PY
  then
    echo "Existing venv is already on Python 3.12."
  else
    echo "Existing venv is not Python 3.12.x. Recreating it..."
    rm -rf venv
    "$PYTHON" -m venv venv
  fi
fi

PYTHON_BIN="./venv/bin/python"
PIP_CMD="$PYTHON_BIN -m pip"

echo "Upgrading pip, setuptools, and wheel..."
$PIP_CMD install --upgrade pip setuptools wheel

if [ "$(uname)" = "Darwin" ] && [ "$(uname -m)" = "arm64" ]; then
  echo "Detected macOS Apple Silicon. Installing compatible CPU PyTorch wheels..."
  $PIP_CMD install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
fi

echo "Installing requirements from requirements.txt..."
$PIP_CMD install -r requirements.txt

echo
echo "Setup complete."
echo "Activate your environment with: source venv/bin/activate"
echo "Then run the app with: uvicorn app.main:app --reload --port 3000"
