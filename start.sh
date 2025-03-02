#!/bin/bash
set -e
source "./.venv/bin/activate"
PYTHON_BIN="$(which python)"
PYTHONUNBUFFERED=1 "$PYTHON_BIN" "./main.py"
