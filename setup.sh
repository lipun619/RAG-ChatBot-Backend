#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if command -v python >/dev/null 2>&1; then
  PYTHON=python
elif command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
else
  echo "ERROR: python or python3 must be installed and on PATH."
  exit 1
fi

if [ ! -d "venv" ]; then
  echo "Creating virtual environment in ./venv..."
  "$PYTHON" -m venv venv
else
  echo "Using existing virtual environment in ./venv"
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
